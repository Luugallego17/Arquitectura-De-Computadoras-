/*
 * Benchmark de optimización en la jerarquía de memoria aplicado al juego
 * "UCB - IA Experience" (Proyecto/Juego_VA.py).
 *
 * La operación medida es la de overlay_rect(): pintar un rectángulo
 * semitransparente sobre el frame de la cámara. En el juego se hace con
 *     overlay = frame.copy()                         (copia de TODO el frame)
 *     cv2.rectangle(overlay, ...)                    (rectángulo en la copia)
 *     cv2.addWeighted(overlay, a, frame, 1-a, frame) (mezcla de TODO el frame)
 * y se ejecuta entre 6 y 8 veces por cada frame de 1920x1080.
 *
 * Fases (mismas ideas que la guía de laboratorio):
 *   1. Naive: copia + mezcla de todo el frame recorriendo por COLUMNAS
 *      (cada paso salta una fila entera: 5760 bytes) -> cache miss masivo.
 *   2. Localidad espacial: lo mismo recorriendo por FILAS (acceso contiguo,
 *      se aprovechan los 64 bytes de cada línea de caché).
 *   3. Localidad temporal + registros: alpha y (1 - alpha) en punto fijo
 *      se calculan una sola vez y viven en registros; punteros por fila.
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
#define FRAMES  30                         /* repeticiones por fase         */

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

/* Mezcla en punto fijo de 8 bits, igual para todas las fases:
 *   dst = (src * (256 - a) + ovl * a + 128) >> 8,  con a = round(alpha * 256) */
static inline u8 mezclar(u8 src, u8 ovl, int a) {
    return (u8)((src * (256 - a) + ovl * a + 128) >> 8);
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
                int a = (int)(ALPHA * 256.0f + 0.5f);      /* se recalcula por byte */
                size_t i = (size_t)y * STRIDE + x * CANALES + c;
                frame[i] = mezclar(frame[i], ovl[i], a);
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
                int a = (int)(ALPHA * 256.0f + 0.5f);
                size_t i = (size_t)y * STRIDE + x * CANALES + c;
                frame[i] = mezclar(frame[i], ovl[i], a);
            }
        }
    }
}

/* 3. LOCALIDAD TEMPORAL + REGISTROS: alpha en punto fijo calculado una
 *    sola vez y mantenido en registros; punteros a la fila actual */
void fase3_registros_cpu(u8 *frame, u8 *ovl) {
    copiar_y_pintar_rectangulo(frame, ovl);
    register const int a  = (int)(ALPHA * 256.0f + 0.5f);
    register const int ia = 256 - a;
    for (int y = 0; y < ALTO; y++) {
        u8 *pf = frame + (size_t)y * STRIDE;
        const u8 *po = ovl + (size_t)y * STRIDE;
        for (int j = 0; j < STRIDE; j++) {
            pf[j] = (u8)((pf[j] * ia + po[j] * a + 128) >> 8);
        }
    }
}

/* 4. LOOP UNROLLING 4X + ILP: cuatro bytes por iteración */
void fase4_loop_unrolling(u8 *frame, u8 *ovl) {
    copiar_y_pintar_rectangulo(frame, ovl);
    register const int a  = (int)(ALPHA * 256.0f + 0.5f);
    register const int ia = 256 - a;
    for (int y = 0; y < ALTO; y++) {
        u8 *pf = frame + (size_t)y * STRIDE;
        const u8 *po = ovl + (size_t)y * STRIDE;
        for (int j = 0; j < STRIDE; j += 4) {          /* STRIDE es múltiplo de 4 */
            pf[j]     = (u8)((pf[j]     * ia + po[j]     * a + 128) >> 8);
            pf[j + 1] = (u8)((pf[j + 1] * ia + po[j + 1] * a + 128) >> 8);
            pf[j + 2] = (u8)((pf[j + 2] * ia + po[j + 2] * a + 128) >> 8);
            pf[j + 3] = (u8)((pf[j + 3] * ia + po[j + 3] * a + 128) >> 8);
        }
    }
}

/* 5. ROI: solo la región del rectángulo, sin copiar el frame.
 *    Fuera del rectángulo overlay == frame, así que la mezcla no cambia
 *    nada: no hay que tocar esos bytes. Es lo que hace Juego_VA_optimizado.py */
void fase5_roi(u8 *frame) {
    register const int a  = (int)(ALPHA * 256.0f + 0.5f);
    register const int ia = 256 - a;
    const int pre[CANALES] = { COLOR[0] * a + 128, COLOR[1] * a + 128, COLOR[2] * a + 128 };
    for (int y = RY1; y < RY2; y++) {
        u8 *pf = frame + (size_t)y * STRIDE + RX1 * CANALES;
        for (int x = 0; x < RX2 - RX1; x++) {
            pf[0] = (u8)((pf[0] * ia + pre[0]) >> 8);
            pf[1] = (u8)((pf[1] * ia + pre[1]) >> 8);
            pf[2] = (u8)((pf[2] * ia + pre[2]) >> 8);
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
    /* bytes que cada fase procesa por frame (copia + mezcla, o solo el ROI) */
    double bytes_fase[5] = { 2.0 * BYTES, 2.0 * BYTES, 2.0 * BYTES, 2.0 * BYTES,
                             (double)(RX2 - RX1) * (RY2 - RY1) * CANALES };

    double t[5], chk[5];
    for (int i = 0; i < 5; i++) t[i] = correr_fase(fases[i], original, frame, ovl, &chk[i]);

    printf("\n=== RESULTADOS DETERMINISTICOS: overlay_rect sobre %dx%dx%d, %d frames ===\n",
           ANCHO, ALTO, CANALES, FRAMES);
    printf("Frame: %.1f MB | Rectangulo: %dx%d px | Linea de cache: 64 B = 64 bytes de pixel\n\n",
           BYTES / 1e6, RX2 - RX1, RY2 - RY1);
    for (int i = 0; i < 5; i++) {
        double ms = t[i] / FRAMES * 1000.0;
        double gbs = bytes_fase[i] * FRAMES / t[i] / 1e9;
        printf("%s: %7.4f s | %7.2f ms/frame | %6.2f GB/s | Speedup: %6.2fx\n",
               nombres[i], t[i], ms, gbs, t[0] / t[i]);
    }
    printf("\n[OK] Validacion de Checksum: %.4e\n", chk[0]);
    for (int i = 1; i < 5; i++)
        printf("     Fase %d vs Fase 1: Error = %.4e\n", i + 1, fabs(chk[i] - chk[0]));

    free(original); free(frame); free(ovl);
    return 0;
}
