/*
 * Benchmark de optimización en la jerarquía de memoria aplicado al juego
 * "UCB - IA Experience" (Juego_VA.py).
 *
 * La operación medida es la de overlay_rect(): pintar un rectángulo
 * semitransparente sobre el frame de la cámara. En el juego se hace con
 *     overlay = frame.copy()                         (copia de TODO el frame)
 *     cv2.rectangle(overlay, ...)                    (rectángulo en la copia)
 *     cv2.addWeighted(overlay, a, frame, 1-a, frame) (mezcla de TODO el frame)
 * y se ejecuta entre 6 y 8 veces por cada frame de 1920x1080.
 *
 * La mezcla es la misma de cv2.addWeighted, en punto flotante:
 *     dst = (unsigned char)(src * (1 - alpha) + overlay * alpha + 0.5f)
 * o sea 2 multiplicaciones y 2 sumas en float por cada byte: 4 FLOP/byte.
 *
 * Fases (mismas ideas que la guía de laboratorio):
 *   1. Naive: copia + mezcla de todo el frame recorriendo por COLUMNAS
 *      (cada paso salta una fila entera: 5760 bytes) -> cache miss masivo.
 *   2. Localidad espacial: lo mismo recorriendo por FILAS (acceso contiguo,
 *      se aprovechan los 64 bytes de cada línea de caché).
 *   3. Localidad temporal + registros: alpha y (1 - alpha) se calculan una
 *      sola vez y viven en registros de la FPU; punteros por fila.
 *   4. Loop unrolling 4x + ILP: 4 bytes por iteración.
 *   5. ROI (la optimización aplicada al juego): se mezcla SOLO la región
 *      del rectángulo, sin copiar el frame.
 *
 * Compilar:  gcc -Wall -Wextra -O1 benchmark_juego.c -o benchmark_juego -lm
 */
#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#define ANCHO   1920                       /* SCREEN_W del juego (Full HD)  */
#define ALTO    1080                       /* SCREEN_H del juego            */
#define CANALES 3                          /* BGR, 1 byte por canal (uint8) */
#define STRIDE  (ANCHO * CANALES)          /* bytes por fila: 5760          */
#define BYTES   ((size_t)ALTO * STRIDE)    /* bytes por frame: 6 220 800    */
#ifndef FRAMES
#define FRAMES  30                         /* repeticiones por fase         */
#endif
#define FLOP_POR_BYTE 4.0                  /* 2 mul + 2 add en float        */

/* Panel de bienvenida del juego: (w/2-320, h/2-120) a (w/2+320, h/2+120),
 * color (30, 0, 50) y alpha = 0.75 */
#define RX1 (ANCHO / 2 - 320)
#define RY1 (ALTO  / 2 - 120)
#define RX2 (ANCHO / 2 + 320)
#define RY2 (ALTO  / 2 + 120)
static const unsigned char COLOR[CANALES] = {30, 0, 50};
static const float ALPHA = 0.75f;

typedef unsigned char u8;

static double medir_tiempo_segundos(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

/* Lo que hace el juego antes de addWeighted: overlay = frame.copy() y
 * cv2.rectangle(overlay, ..., -1). Se comparte entre las fases 1 a 4. */
static void copiar_y_pintar_rectangulo(const u8 *frame, u8 *ovl) {
    memcpy(ovl, frame, BYTES);
    for (int y = RY1; y < RY2; y++) {
        u8 *fila = ovl + (size_t)y * STRIDE;
        for (int x = RX1; x < RX2; x++)
            for (int c = 0; c < CANALES; c++)
                fila[x * CANALES + c] = COLOR[c];
    }
}

/* 1. NAIVE: todo el frame, recorrido por columnas (salto de fila: 5760 B) */
void fase1_naive(u8 *frame, u8 *ovl) {
    copiar_y_pintar_rectangulo(frame, ovl);
    for (int x = 0; x < ANCHO; x++) {
        for (int y = 0; y < ALTO; y++) {
            for (int c = 0; c < CANALES; c++) {
                float a = ALPHA, b = 1.0f - ALPHA;          /* se recalcula por byte */
                size_t i = (size_t)y * STRIDE + x * CANALES + c;
                frame[i] = (u8)(frame[i] * b + ovl[i] * a + 0.5f);
            }
        }
    }
}

/* 2. LOCALIDAD ESPACIAL: todo el frame, recorrido por filas (contiguo) */
void fase2_localidad_espacial(u8 *frame, u8 *ovl) {
    copiar_y_pintar_rectangulo(frame, ovl);
    for (int y = 0; y < ALTO; y++) {
        for (int x = 0; x < ANCHO; x++) {
            for (int c = 0; c < CANALES; c++) {
                float a = ALPHA, b = 1.0f - ALPHA;
                size_t i = (size_t)y * STRIDE + x * CANALES + c;
                frame[i] = (u8)(frame[i] * b + ovl[i] * a + 0.5f);
            }
        }
    }
}

/* 3. LOCALIDAD TEMPORAL + REGISTROS: alpha y (1 - alpha) calculados una
 *    sola vez y mantenidos en registros de la FPU; punteros a la fila */
void fase3_registros_cpu(u8 *frame, u8 *ovl) {
    copiar_y_pintar_rectangulo(frame, ovl);
    register const float a = ALPHA;                     /* En registro de la FPU */
    register const float b = 1.0f - ALPHA;
    for (int y = 0; y < ALTO; y++) {
        u8 *pf = frame + (size_t)y * STRIDE;
        const u8 *po = ovl + (size_t)y * STRIDE;
        for (int j = 0; j < STRIDE; j++) {
            pf[j] = (u8)(pf[j] * b + po[j] * a + 0.5f);
        }
    }
}

/* 4. LOOP UNROLLING 4X + ILP: cuatro bytes por iteración */
void fase4_loop_unrolling(u8 *frame, u8 *ovl) {
    copiar_y_pintar_rectangulo(frame, ovl);
    register const float a = ALPHA;
    register const float b = 1.0f - ALPHA;
    for (int y = 0; y < ALTO; y++) {
        u8 *pf = frame + (size_t)y * STRIDE;
        const u8 *po = ovl + (size_t)y * STRIDE;
        for (int j = 0; j < STRIDE; j += 4) {          /* STRIDE es múltiplo de 4 */
            pf[j]     = (u8)(pf[j]     * b + po[j]     * a + 0.5f);
            pf[j + 1] = (u8)(pf[j + 1] * b + po[j + 1] * a + 0.5f);
            pf[j + 2] = (u8)(pf[j + 2] * b + po[j + 2] * a + 0.5f);
            pf[j + 3] = (u8)(pf[j + 3] * b + po[j + 3] * a + 0.5f);
        }
    }
}

/* 5. ROI: solo la región del rectángulo, sin copiar el frame.
 *    Fuera del rectángulo overlay == frame, así que la mezcla no cambia
 *    nada: no hay que tocar esos bytes. Es lo que hace Juego_VA_optimizado.py */
void fase5_roi(u8 *frame) {
    register const float a = ALPHA;
    register const float b = 1.0f - ALPHA;
    const float pre[CANALES] = { COLOR[0] * a + 0.5f, COLOR[1] * a + 0.5f, COLOR[2] * a + 0.5f };
    for (int y = RY1; y < RY2; y++) {
        u8 *pf = frame + (size_t)y * STRIDE + RX1 * CANALES;
        for (int x = 0; x < RX2 - RX1; x++) {
            pf[0] = (u8)(pf[0] * b + pre[0]);
            pf[1] = (u8)(pf[1] * b + pre[1]);
            pf[2] = (u8)(pf[2] * b + pre[2]);
            pf += CANALES;
        }
    }
}

static double calcular_checksum(const u8 *frame) {
    double sum = 0.0;
    for (size_t i = 0; i < BYTES; i++) sum += (double)frame[i];
    return sum;
}

static void generar_frame(u8 *frame) {
    /* patrón determinístico que imita una imagen de cámara */
    for (int y = 0; y < ALTO; y++)
        for (int x = 0; x < ANCHO; x++)
            for (int c = 0; c < CANALES; c++)
                frame[(size_t)y * STRIDE + x * CANALES + c] = (u8)((x * 7 + y * 13 + c * 31) % 256);
}

typedef void (*fase_fn)(u8 *frame, u8 *ovl);

static double correr_fase(fase_fn fn, const u8 *original, u8 *frame, u8 *ovl, double *chk) {
    memcpy(frame, original, BYTES);
    double t0 = medir_tiempo_segundos();
    for (int f = 0; f < FRAMES; f++) fn(frame, ovl);
    double t = medir_tiempo_segundos() - t0;
    *chk = calcular_checksum(frame);
    return t;
}

static void fase5_wrapper(u8 *frame, u8 *ovl) { (void)ovl; fase5_roi(frame); }

int main(void) {
    u8 *original = (u8*)malloc(BYTES), *frame = (u8*)malloc(BYTES), *ovl = (u8*)malloc(BYTES);
    if (!original || !frame || !ovl) {
        fprintf(stderr, "Error: no se pudo reservar memoria para los frames\n");
        return 1;
    }
    generar_frame(original);

    const char *nombres[5] = {
        "1. Naive (por columnas)      ",
        "2. Localidad Espacial (filas)",
        "3. Registros de CPU          ",
        "4. Loop Unrolling 4x (ILP)   ",
        "5. Solo ROI (juego optimiz.) ",
    };
    fase_fn fases[5] = { fase1_naive, fase2_localidad_espacial, fase3_registros_cpu,
                         fase4_loop_unrolling, fase5_wrapper };
    /* bytes mezclados por frame en cada fase (todo el frame, o solo el ROI) */
    double bytes_fase[5] = { (double)BYTES, (double)BYTES, (double)BYTES, (double)BYTES,
                             (double)(RX2 - RX1) * (RY2 - RY1) * CANALES };

    double t[5], chk[5];
    for (int i = 0; i < 5; i++) t[i] = correr_fase(fases[i], original, frame, ovl, &chk[i]);

    printf("\n=== RESULTADOS DETERMINISTICOS: overlay_rect sobre %dx%dx%d, %d frames ===\n",
           ANCHO, ALTO, CANALES, FRAMES);
    printf("Frame: %.1f MB | Rectangulo: %dx%d px | %.0f FLOP por byte mezclado\n\n",
           BYTES / 1e6, RX2 - RX1, RY2 - RY1, FLOP_POR_BYTE);
    for (int i = 0; i < 5; i++) {
        double ms = t[i] / FRAMES * 1000.0;
        double gflops = FLOP_POR_BYTE * bytes_fase[i] * FRAMES / t[i] / 1e9;
        printf("%s: %7.4f s | %7.2f ms/frame | %6.2f GFLOPS | Speedup: %6.2fx\n",
               nombres[i], t[i], ms, gflops, t[0] / t[i]);
    }
    printf("\n[OK] Validacion de Checksum: %.4e\n", chk[0]);
    for (int i = 1; i < 5; i++)
        printf("     Fase %d vs Fase 1: Error = %.4e\n", i + 1, fabs(chk[i] - chk[0]));

    free(original); free(frame); free(ovl);
    return 0;
}
