/*
 * Reto integrador: terminal con Backspace.
 *
 * Une los tres experimentos: el teclado deposita la tecla en el puerto
 * 0x02 (exp1), la CPU la lee por E/S aislada y la encola en la cola FIFO
 * de la RAM (exp2), la terminal la desencola y la dibuja en la VRAM
 * (exp3). Backspace (0x08) o DEL (0x7F) retrocede el cursor y borra.
 *
 *   gcc -std=c99 -Wall -Wextra -pedantic reto_integrador_terminal.c -o terminal
 *
 * Uso:   ./terminal            -> pruebas automaticas (evidencias)
 *        ./terminal -i         -> modo interactivo (escribe y ENTER envia)
 */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PUERTO_STATUS  0x01
#define PUERTO_DATA    0x02
#define COLA_BASE_DIR  0x70
#define COLA_CAPACIDAD 8
#define DIR_KB_HEAD    0x78
#define DIR_KB_TAIL    0x79
#define DIR_KB_COUNT   0x7A
#define VRAM_BASE      0xF0
#define VRAM_FIN       0xFF

typedef struct {
    uint8_t address_bus, data_bus;
    bool io_read, mem_read;
} SystemBuses;

typedef struct { uint8_t reg_status, reg_data; } TecladoHardware;

typedef struct {
    uint8_t  ram[256];
    uint16_t cursor_vram; /* 16 bits: 0x100 = pantalla llena, sin desbordar */
} PC;

static SystemBuses     g_bus;
static TecladoHardware g_teclado;
static PC              g_pc;

/* ---- Hardware del teclado y E/S por puerto (exp1) ---- */
static void teclado_presionar(uint8_t c) { g_teclado.reg_data = c; g_teclado.reg_status = 1; }

static void tick_controlador_teclado(SystemBuses *bus, TecladoHardware *kb)
{
    if (bus->io_read) {
        if (bus->address_bus == PUERTO_STATUS) bus->data_bus = kb->reg_status;
        else if (bus->address_bus == PUERTO_DATA) { bus->data_bus = kb->reg_data; kb->reg_status = 0; }
    }
}

static uint8_t cpu_instruccion_in(uint8_t puerto)
{
    g_bus.address_bus = puerto; g_bus.io_read = true; g_bus.mem_read = false;
    tick_controlador_teclado(&g_bus, &g_teclado);
    uint8_t dato = g_bus.data_bus;
    g_bus.io_read = false;
    return dato;
}

/* ---- Cola FIFO en RAM (exp2) ---- */
static bool cola_teclado_encolar(uint8_t ascii)
{
    uint8_t tail = g_pc.ram[DIR_KB_TAIL], count = g_pc.ram[DIR_KB_COUNT];
    if (count >= COLA_CAPACIDAD) return false;
    g_pc.ram[COLA_BASE_DIR + tail] = ascii;
    g_pc.ram[DIR_KB_TAIL]  = (uint8_t)((tail + 1) % COLA_CAPACIDAD);
    g_pc.ram[DIR_KB_COUNT] = (uint8_t)(count + 1);
    return true;
}

static bool cola_teclado_desencolar(uint8_t *salida_ascii)
{
    uint8_t head = g_pc.ram[DIR_KB_HEAD], count = g_pc.ram[DIR_KB_COUNT];
    if (count == 0) return false;
    *salida_ascii = g_pc.ram[COLA_BASE_DIR + head];
    g_pc.ram[DIR_KB_HEAD]  = (uint8_t)((head + 1) % COLA_CAPACIDAD);
    g_pc.ram[DIR_KB_COUNT] = (uint8_t)(count - 1);
    return true;
}

/* ---- Monitor (exp3) ---- */
static void monitor_actualizar_pantalla(void)
{
    printf("  +----+\n");
    for (int f = 0; f < 4; f++) {
        printf("  |");
        for (int c = 0; c < 4; c++) {
            uint8_t b = g_pc.ram[VRAM_BASE + f * 4 + c];
            putchar((b >= 32 && b <= 126) ? b : '?');
        }
        printf("|\n");
    }
    printf("  +----+  cursor=0x%02X\n", g_pc.cursor_vram);
}

static void pc_iniciar(void)
{
    memset(&g_pc, 0, sizeof g_pc);
    memset(&g_teclado, 0, sizeof g_teclado);
    for (int i = VRAM_BASE; i <= VRAM_FIN; i++) g_pc.ram[i] = 0x20;
    g_pc.cursor_vram = VRAM_BASE;
}

/* ---- Terminal (reto) ---- */
static bool g_mostrar = false; /* dibujar el monitor tras cada tecla */

static bool terminal_procesar_siguiente_tecla(void)
{
    uint8_t tecla;
    if (!cola_teclado_desencolar(&tecla)) return false;

    if (tecla == 0x08 || tecla == 0x7F) { /* BACKSPACE */
        if (g_pc.cursor_vram > VRAM_BASE) {
            g_pc.cursor_vram--;
            g_pc.ram[g_pc.cursor_vram] = 0x20; /* Borra caracter */
        }
    } else if (tecla >= 32 && tecla <= 126) {
        if (g_pc.cursor_vram <= VRAM_FIN) {
            g_pc.ram[g_pc.cursor_vram] = tecla;
            g_pc.cursor_vram++;
        }
    }
    if (g_mostrar) monitor_actualizar_pantalla();
    return true;
}

/* Una pulsacion completa: teclado -> puerto -> CPU -> cola. */
static bool pulsar(uint8_t tecla)
{
    teclado_presionar(tecla);
    if (cpu_instruccion_in(PUERTO_STATUS) & 1) {
        return cola_teclado_encolar(cpu_instruccion_in(PUERTO_DATA));
    }
    return false;
}

static void drenar(void) { while (terminal_procesar_siguiente_tecla()) { } }

static void fila_texto(int f, char out[5])
{
    for (int c = 0; c < 4; c++) out[c] = (char)g_pc.ram[VRAM_BASE + f * 4 + c];
    out[4] = '\0';
}

static int g_fallos = 0;
static void verificar(const char *descripcion, bool condicion)
{
    printf("  [%s] %s\n", condicion ? "OK" : "FALLO", descripcion);
    if (!condicion) g_fallos++;
}

static void pruebas(void)
{
    char f[5];
    printf("=== RETO INTEGRADOR: terminal con Backspace ===\n");
    g_mostrar = true;

    printf("\nPrueba 1: escribir \"HOLA\" (teclado -> puerto -> cola -> VRAM)\n");
    pc_iniciar();
    pulsar('H'); pulsar('O'); pulsar('L'); pulsar('A');
    printf("  COUNT en la cola antes de procesar = %u\n", g_pc.ram[DIR_KB_COUNT]);
    drenar();
    fila_texto(0, f);
    verificar("la fila 0 muestra HOLA", strcmp(f, "HOLA") == 0);
    verificar("el cursor avanzo a 0xF4", g_pc.cursor_vram == 0xF4);

    printf("\nPrueba 2: Backspace (0x08) borra el ultimo caracter\n");
    pulsar(0x08);
    drenar();
    fila_texto(0, f);
    verificar("la fila 0 queda \"HOL \"", strcmp(f, "HOL ") == 0);
    verificar("el cursor retrocedio a 0xF3", g_pc.cursor_vram == 0xF3);

    printf("\nPrueba 3: DEL (0x7F) tambien borra y se puede reescribir\n");
    pulsar(0x7F); pulsar('A'); pulsar('B');
    drenar();
    fila_texto(0, f);
    verificar("la fila 0 queda \"HOAB\" (borro 'L', escribio 'A','B')", strcmp(f, "HOAB") == 0);

    printf("\nPrueba 4: Backspace con la pantalla vacia no se sale de la VRAM\n");
    pc_iniciar();
    pulsar(0x08); pulsar(0x08); pulsar(0x08);
    drenar();
    verificar("el cursor sigue en 0xF0", g_pc.cursor_vram == 0xF0);
    verificar("0xEF (fuera de la VRAM) no se modifico", g_pc.ram[0xEF] == 0);

    printf("\nPrueba 5: pantalla llena (16 caracteres) y tecla extra\n");
    g_mostrar = false;
    pc_iniciar();
    const char *txt = "ABCDEFGHIJKLMNOP";
    for (int i = 0; txt[i]; i++) { pulsar((uint8_t)txt[i]); drenar(); }
    g_mostrar = true;
    pulsar('Z'); drenar();
    fila_texto(3, f);
    verificar("la ultima fila es MNOP", strcmp(f, "MNOP") == 0);
    verificar("el cursor se detiene en 0x100 (no vuelve a 0x00)", g_pc.cursor_vram == 0x100);
    verificar("la tecla 'Z' extra se descarta y no pisa la RAM de codigo", g_pc.ram[0x00] == 0);

    printf("\nPrueba 6: Backspace estando la pantalla llena\n");
    pulsar(0x08); drenar();
    fila_texto(3, f);
    verificar("borra la 'P' y la fila 3 queda \"MNO \"", strcmp(f, "MNO ") == 0);

    printf("\nPrueba 7: caracteres no imprimibles se ignoran\n");
    pc_iniciar();
    pulsar('A'); pulsar(0x01); pulsar(0x1B); pulsar('B');
    drenar();
    fila_texto(0, f);
    verificar("solo se dibujan A y B", strcmp(f, "AB  ") == 0);

    printf("\nPrueba 8: rafaga de 10 teclas sin procesar desborda la cola de 8\n");
    g_mostrar = false;
    pc_iniciar();
    int perdidas = 0;
    for (int i = 0; i < 10; i++) if (!pulsar((uint8_t)('0' + i))) perdidas++;
    printf("  encoladas=%u, perdidas por overflow=%d\n", g_pc.ram[DIR_KB_COUNT], perdidas);
    drenar();
    fila_texto(0, f);
    char f1[5]; fila_texto(1, f1);
    verificar("se perdieron exactamente 2 teclas", perdidas == 2);
    verificar("se dibujaron las primeras 8: 0123 4567", strcmp(f, "0123") == 0 && strcmp(f1, "4567") == 0);

    printf("\nResultado: %s (%d fallos)\n", g_fallos == 0 ? "TODAS LAS PRUEBAS OK" : "HAY FALLOS", g_fallos);
}

/* Modo -t: traza CSV del cursor tras cada tecla (la usa generar_graficos.py). */
static void traza(void)
{
    const uint8_t teclas[] = { 'H','O','L','A', 0x08, 0x08, 'U', 'N', 'A', 0x7F, 'O', 'S', 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08 };
    pc_iniciar();
    g_mostrar = false;
    printf("TRAZA,paso,tecla,cursor,pantalla\n");
    printf("TRAZA,0,inicio,%u,\"                \"\n", g_pc.cursor_vram);
    for (unsigned i = 0; i < sizeof teclas; i++) {
        pulsar(teclas[i]);
        drenar();
        char pant[17];
        for (int j = 0; j < 16; j++) pant[j] = (char)g_pc.ram[VRAM_BASE + j];
        pant[16] = '\0';
        printf("TRAZA,%u,0x%02X,%u,\"%s\"\n", i + 1, teclas[i], g_pc.cursor_vram, pant);
    }
}

int main(int argc, char **argv)
{
    if (argc > 1 && strcmp(argv[1], "-t") == 0) { traza(); return 0; }
    if (argc > 1 && strcmp(argv[1], "-i") == 0) {
        char linea[128];
        pc_iniciar();
        g_mostrar = true;
        printf("Terminal interactiva. Escribe texto; usa '<' como Backspace; ENTER envia; Ctrl+D sale.\n");
        monitor_actualizar_pantalla();
        while (fgets(linea, sizeof linea, stdin)) {
            for (int i = 0; linea[i] && linea[i] != '\n'; i++) {
                uint8_t t = (uint8_t)(linea[i] == '<' ? 0x08 : linea[i]);
                if (!pulsar(t)) printf("  (overflow: tecla perdida)\n");
                if (g_pc.ram[DIR_KB_COUNT] >= COLA_CAPACIDAD) drenar();
            }
            drenar();
        }
        return 0;
    }
    pruebas();
    return g_fallos == 0 ? 0 : 1;
}
