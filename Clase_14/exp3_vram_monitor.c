/*
 * Experimento 3: memoria de video (VRAM) y scroll vertical.
 *
 * La pantalla es una matriz de 4x4 caracteres mapeada en la RAM,
 * direcciones 0xF0..0xFF. La celda (fila, col) esta en 0xF0 + fila*4 + col.
 *
 *   gcc -std=c99 -Wall -Wextra -pedantic exp3_vram_monitor.c -o exp3
 */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RAM_TAMANO 256
#define VRAM_BASE  0xF0
#define FILAS      4
#define COLUMNAS   4

static uint8_t g_ram[RAM_TAMANO];

static void vram_limpiar(void)
{
    for (int i = 0; i < FILAS * COLUMNAS; i++) g_ram[VRAM_BASE + i] = 0x20;
}

static bool vram_escribir(uint8_t fila, uint8_t col, char c)
{
    if (fila >= FILAS || col >= COLUMNAS) return false;
    uint8_t dir = (uint8_t)(VRAM_BASE + (fila * COLUMNAS) + col); /* Direccion VRAM */
    g_ram[dir] = (uint8_t)c;
    return true;
}

static bool vram_leer(uint8_t fila, uint8_t col, char *c)
{
    if (fila >= FILAS || col >= COLUMNAS) return false;
    *c = (char)g_ram[VRAM_BASE + (fila * COLUMNAS) + col];
    return true;
}

static void vram_scroll_arriba(void)
{
    for (int f = 0; f < FILAS - 1; f++) {
        for (int c = 0; c < COLUMNAS; c++) {
            g_ram[VRAM_BASE + (f * COLUMNAS) + c] = g_ram[VRAM_BASE + ((f + 1) * COLUMNAS) + c];
        }
    }
    for (int c = 0; c < COLUMNAS; c++) g_ram[VRAM_BASE + ((FILAS - 1) * COLUMNAS) + c] = 0x20;
}

/* Dibuja el monitor 4x4 y, al lado, la direccion de cada fila. */
static void monitor_mostrar(const char *titulo)
{
    printf("  %s\n  +----+\n", titulo);
    for (int f = 0; f < FILAS; f++) {
        printf("  |");
        for (int c = 0; c < COLUMNAS; c++) {
            uint8_t b = g_ram[VRAM_BASE + f * COLUMNAS + c];
            putchar((b >= 32 && b <= 126) ? b : '?');
        }
        printf("|  0x%02X..0x%02X\n", VRAM_BASE + f * COLUMNAS, VRAM_BASE + f * COLUMNAS + 3);
    }
    printf("  +----+\n");
}

/* Devuelve la fila como cadena para compararla en las pruebas. */
static void fila_a_texto(int f, char out[COLUMNAS + 1])
{
    for (int c = 0; c < COLUMNAS; c++) out[c] = (char)g_ram[VRAM_BASE + f * COLUMNAS + c];
    out[COLUMNAS] = '\0';
}

static int g_fallos = 0;

static void verificar(const char *descripcion, bool condicion)
{
    printf("  [%s] %s\n", condicion ? "OK" : "FALLO", descripcion);
    if (!condicion) g_fallos++;
}

/* Modo -t: volcado CSV de los 16 bytes de la VRAM en cada etapa. */
static void traza_etapa(const char *etapa)
{
    printf("VRAM,%s", etapa);
    for (int i = 0; i < FILAS * COLUMNAS; i++) printf(",%u", g_ram[VRAM_BASE + i]);
    printf("\n");
}

static void traza(void)
{
    const char *texto = "HOLAARQ!1234WXYZ";
    vram_limpiar();
    for (int i = 0; i < 16; i++) vram_escribir((uint8_t)(i / 4), (uint8_t)(i % 4), texto[i]);
    traza_etapa("escrita");
    for (int s = 1; s <= 4; s++) {
        vram_scroll_arriba();
        char nombre[16];
        snprintf(nombre, sizeof nombre, "scroll%d", s);
        traza_etapa(nombre);
    }
}

int main(int argc, char **argv)
{
    char f[COLUMNAS + 1];
    if (argc > 1 && strcmp(argv[1], "-t") == 0) { traza(); return 0; }
    printf("=== EXPERIMENTO 3: VRAM 4x4 (0xF0..0xFF) y scroll ===\n\n");

    printf("Prueba 1: pantalla limpia\n");
    memset(g_ram, 0, sizeof g_ram);
    vram_limpiar();
    monitor_mostrar("monitor vacio");
    fila_a_texto(0, f);
    verificar("toda la VRAM vale 0x20 (espacio)", strcmp(f, "    ") == 0);

    printf("\nPrueba 2: escribir en coordenadas (fila, columna)\n");
    vram_escribir(0, 0, 'H'); vram_escribir(0, 1, 'O'); vram_escribir(0, 2, 'L'); vram_escribir(0, 3, 'A');
    vram_escribir(1, 0, 'A'); vram_escribir(1, 1, 'R'); vram_escribir(1, 2, 'Q'); vram_escribir(1, 3, '!');
    vram_escribir(2, 0, '1'); vram_escribir(2, 1, '2'); vram_escribir(2, 2, '3'); vram_escribir(2, 3, '4');
    vram_escribir(3, 0, 'W'); vram_escribir(3, 1, 'X'); vram_escribir(3, 2, 'Y'); vram_escribir(3, 3, 'Z');
    monitor_mostrar("monitor con 4 filas");
    verificar("(2,3) esta en la direccion 0xFB", g_ram[0xFB] == '4');
    verificar("(0,0) esta en 0xF0 y (3,3) en 0xFF", g_ram[0xF0] == 'H' && g_ram[0xFF] == 'Z');

    printf("\nPrueba 3: leer de vuelta una celda\n");
    char leido = 0;
    bool ok = vram_leer(1, 2, &leido);
    printf("  vram_leer(1,2) -> '%c'\n", leido);
    verificar("se lee 'Q' en (1,2)", ok && leido == 'Q');

    printf("\nPrueba 4: coordenadas fuera de rango se rechazan sin tocar la RAM\n");
    uint8_t antes_ff = g_ram[0xFF], antes_100 = g_ram[0x00];
    verificar("fila 4 rechazada", !vram_escribir(4, 0, 'x'));
    verificar("columna 4 rechazada", !vram_escribir(0, 4, 'x'));
    verificar("lectura fuera de rango rechazada", !vram_leer(4, 4, &leido));
    verificar("0xFF y 0x00 no cambiaron", g_ram[0xFF] == antes_ff && g_ram[0x00] == antes_100);

    printf("\nPrueba 5: scroll vertical hacia arriba\n");
    vram_scroll_arriba();
    monitor_mostrar("despues de un scroll");
    fila_a_texto(0, f); verificar("fila 0 = antigua fila 1 (ARQ!)", strcmp(f, "ARQ!") == 0);
    fila_a_texto(1, f); verificar("fila 1 = antigua fila 2 (1234)", strcmp(f, "1234") == 0);
    fila_a_texto(2, f); verificar("fila 2 = antigua fila 3 (WXYZ)", strcmp(f, "WXYZ") == 0);
    fila_a_texto(3, f); verificar("fila 3 queda en blanco (0x20)", strcmp(f, "    ") == 0);

    printf("\nPrueba 6: cuatro scrolls borran toda la pantalla\n");
    for (int i = 0; i < 3; i++) vram_scroll_arriba();
    monitor_mostrar("despues de 4 scrolls en total");
    bool vacia = true;
    for (int i = 0; i < 16; i++) if (g_ram[VRAM_BASE + i] != 0x20) vacia = false;
    verificar("la VRAM quedo completamente en blanco", vacia);

    printf("\nResultado: %s (%d fallos)\n", g_fallos == 0 ? "TODAS LAS PRUEBAS OK" : "HAY FALLOS", g_fallos);
    return g_fallos == 0 ? 0 : 1;
}
