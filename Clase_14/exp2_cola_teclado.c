/*
 * Experimento 2: cola circular FIFO de teclado en la RAM.
 *
 * El buffer (8 bytes en 0x70..0x77) y sus punteros KB_HEAD (0x78),
 * KB_TAIL (0x79) y KB_COUNT (0x7A) viven estrictamente dentro del
 * arreglo g_ram; no hay variables auxiliares fuera de la RAM.
 *
 *   gcc -std=c99 -Wall -Wextra -pedantic exp2_cola_teclado.c -o exp2
 */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RAM_TAMANO       256
#define COLA_BASE_DIR    0x70
#define COLA_CAPACIDAD   8
#define DIR_KB_HEAD      0x78
#define DIR_KB_TAIL      0x79
#define DIR_KB_COUNT     0x7A

static uint8_t g_ram[RAM_TAMANO];

static void cola_teclado_iniciar(void)
{
    memset(&g_ram[COLA_BASE_DIR], 0, COLA_CAPACIDAD);
    g_ram[DIR_KB_HEAD]  = 0;
    g_ram[DIR_KB_TAIL]  = 0;
    g_ram[DIR_KB_COUNT] = 0;
}

static bool cola_teclado_encolar(uint8_t ascii)
{
    uint8_t tail = g_ram[DIR_KB_TAIL], count = g_ram[DIR_KB_COUNT];
    if (count >= COLA_CAPACIDAD) return false; /* BUFFER OVERFLOW */
    g_ram[COLA_BASE_DIR + tail] = ascii;
    g_ram[DIR_KB_TAIL]  = (uint8_t)((tail + 1) % COLA_CAPACIDAD);
    g_ram[DIR_KB_COUNT] = (uint8_t)(count + 1);
    return true;
}

static bool cola_teclado_desencolar(uint8_t *salida_ascii)
{
    uint8_t head = g_ram[DIR_KB_HEAD], count = g_ram[DIR_KB_COUNT];
    if (count == 0) return false; /* COLA VACIA */
    *salida_ascii = g_ram[COLA_BASE_DIR + head];
    g_ram[DIR_KB_HEAD]  = (uint8_t)((head + 1) % COLA_CAPACIDAD);
    g_ram[DIR_KB_COUNT] = (uint8_t)(count - 1);
    return true;
}

/* Volcado de la RAM 0x70..0x7A para ver el estado real de la cola. */
static void volcar_ram(const char *titulo)
{
    printf("  %s\n", titulo);
    printf("    0x70..0x77 (buffer): ");
    for (int i = 0; i < COLA_CAPACIDAD; i++) {
        uint8_t b = g_ram[COLA_BASE_DIR + i];
        printf("%02X(%c) ", b, (b >= 32 && b <= 126) ? b : '.');
    }
    printf("\n    HEAD(0x78)=%u  TAIL(0x79)=%u  COUNT(0x7A)=%u\n",
           g_ram[DIR_KB_HEAD], g_ram[DIR_KB_TAIL], g_ram[DIR_KB_COUNT]);
}

static int g_fallos = 0;

static void verificar(const char *descripcion, bool condicion)
{
    printf("  [%s] %s\n", condicion ? "OK" : "FALLO", descripcion);
    if (!condicion) g_fallos++;
}

/* Modo -t: traza CSV de HEAD/TAIL/COUNT (la usa generar_graficos.py). */
static void traza(void)
{
    uint8_t x = 0;
    int paso = 0;
    cola_teclado_iniciar();
    printf("TRAZA,paso,operacion,resultado,head,tail,count\n");
    printf("TRAZA,%d,inicio,-,%u,%u,%u\n", paso++, g_ram[DIR_KB_HEAD], g_ram[DIR_KB_TAIL], g_ram[DIR_KB_COUNT]);
    for (char c = 'A'; c <= 'J'; c++) { /* 10 teclas: las ultimas dos desbordan */
        bool ok = cola_teclado_encolar((uint8_t)c);
        printf("TRAZA,%d,enc_%c,%s,%u,%u,%u\n", paso++, c, ok ? "ok" : "OVERFLOW", g_ram[DIR_KB_HEAD], g_ram[DIR_KB_TAIL], g_ram[DIR_KB_COUNT]);
    }
    for (int i = 0; i < 5; i++) {
        bool ok = cola_teclado_desencolar(&x);
        printf("TRAZA,%d,des,%s,%u,%u,%u\n", paso++, ok ? "ok" : "VACIA", g_ram[DIR_KB_HEAD], g_ram[DIR_KB_TAIL], g_ram[DIR_KB_COUNT]);
    }
    for (char c = 'K'; c <= 'N'; c++) { /* TAIL da la vuelta */
        bool ok = cola_teclado_encolar((uint8_t)c);
        printf("TRAZA,%d,enc_%c,%s,%u,%u,%u\n", paso++, c, ok ? "ok" : "OVERFLOW", g_ram[DIR_KB_HEAD], g_ram[DIR_KB_TAIL], g_ram[DIR_KB_COUNT]);
    }
    for (int i = 0; i < 9; i++) {
        bool ok = cola_teclado_desencolar(&x);
        printf("TRAZA,%d,des,%s,%u,%u,%u\n", paso++, ok ? "ok" : "VACIA", g_ram[DIR_KB_HEAD], g_ram[DIR_KB_TAIL], g_ram[DIR_KB_COUNT]);
    }
}

int main(int argc, char **argv)
{
    uint8_t x = 0;
    if (argc > 1 && strcmp(argv[1], "-t") == 0) { traza(); return 0; }
    printf("=== EXPERIMENTO 2: cola circular FIFO en RAM (8 bytes) ===\n\n");

    printf("Prueba 1: cola vacia\n");
    cola_teclado_iniciar();
    volcar_ram("estado inicial");
    verificar("desencolar con la cola vacia devuelve false", !cola_teclado_desencolar(&x));

    printf("\nPrueba 2: llenar la cola con A..H (8 teclas)\n");
    for (char c = 'A'; c <= 'H'; c++) {
        if (!cola_teclado_encolar((uint8_t)c)) g_fallos++;
    }
    volcar_ram("cola llena");
    verificar("COUNT = 8", g_ram[DIR_KB_COUNT] == 8);
    verificar("TAIL volvio a 0 (aritmetica modular)", g_ram[DIR_KB_TAIL] == 0);

    printf("\nPrueba 3: Buffer Overflow al encolar la tecla numero 9\n");
    bool ok9 = cola_teclado_encolar('I');
    volcar_ram("despues del intento de encolar 'I'");
    verificar("encolar con la cola llena devuelve false", !ok9);
    verificar("COUNT sigue en 8 y no se piso ningun dato", g_ram[DIR_KB_COUNT] == 8 && g_ram[COLA_BASE_DIR] == 'A');

    printf("\nPrueba 4: orden FIFO al desencolar\n");
    char sacadas[9] = {0};
    for (int i = 0; i < 8; i++) { if (cola_teclado_desencolar(&x)) sacadas[i] = (char)x; }
    printf("  desencoladas: %s\n", sacadas);
    verificar("salen en el mismo orden: ABCDEFGH", strcmp(sacadas, "ABCDEFGH") == 0);
    verificar("COUNT = 0 y HEAD = TAIL", g_ram[DIR_KB_COUNT] == 0 && g_ram[DIR_KB_HEAD] == g_ram[DIR_KB_TAIL]);

    printf("\nPrueba 5: vuelta circular (wrap-around) de los punteros\n");
    cola_teclado_iniciar();
    for (char c = '1'; c <= '6'; c++) cola_teclado_encolar((uint8_t)c);
    for (int i = 0; i < 5; i++) cola_teclado_desencolar(&x); /* HEAD = 5 */
    for (char c = 'a'; c <= 'f'; c++) cola_teclado_encolar((uint8_t)c); /* TAIL cruza el 7 */
    volcar_ram("HEAD en 5 y TAIL ya dio la vuelta");
    verificar("TAIL < HEAD (el puntero cruzo el final del buffer)", g_ram[DIR_KB_TAIL] < g_ram[DIR_KB_HEAD]);
    char resto[8] = {0};
    int n = 0;
    while (cola_teclado_desencolar(&x) && n < 7) resto[n++] = (char)x;
    printf("  desencoladas: %s\n", resto);
    verificar("el orden se conserva tras la vuelta: 6abcdef", strcmp(resto, "6abcdef") == 0);

    printf("\nPrueba 6: la cola no toca nada fuera de 0x70..0x7A\n");
    cola_teclado_iniciar();
    for (int i = 0; i < RAM_TAMANO; i++) g_ram[i] = 0xEE;
    cola_teclado_iniciar();
    for (char c = 'A'; c <= 'Z'; c++) { cola_teclado_encolar((uint8_t)c); if (c % 3 == 0) cola_teclado_desencolar(&x); }
    bool intacta = true;
    for (int i = 0; i < RAM_TAMANO; i++) {
        if ((i < COLA_BASE_DIR || i > DIR_KB_COUNT) && g_ram[i] != 0xEE) intacta = false;
    }
    verificar("el resto de la RAM conserva 0xEE", intacta);

    printf("\nResultado: %s (%d fallos)\n", g_fallos == 0 ? "TODAS LAS PRUEBAS OK" : "HAY FALLOS", g_fallos);
    return g_fallos == 0 ? 0 : 1;
}
