/*
 * Experimento 1: lectura directa desde puerto (E/S aislada).
 *
 * Modela la linea IO_READ del Bus de Control y el handshake del
 * controlador de teclado: leer el puerto de datos (0x02) pone en 0 el
 * registro de estado (0x01), asi la CPU sabe que la tecla ya fue
 * consumida.
 *
 *   gcc -std=c99 -Wall -Wextra -pedantic exp1_puerto_teclado.c -o exp1
 */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PUERTO_STATUS 0x01
#define PUERTO_DATA   0x02

typedef struct {
    uint8_t address_bus;
    uint8_t data_bus;
    bool    io_read;   /* Bus de Control: IO_READ  */
    bool    mem_read;  /* Bus de Control: MEM_READ */
} SystemBuses;

typedef struct {
    uint8_t reg_status; /* bit 0 = tecla lista */
    uint8_t reg_data;   /* ultimo ASCII recibido */
} TecladoHardware;

static SystemBuses     g_bus;
static TecladoHardware g_teclado;

/* El teclado fisico deposita una tecla y levanta el bit 0 del status. */
static void teclado_presionar(char c)
{
    g_teclado.reg_data   = (uint8_t)c;
    g_teclado.reg_status = 1;
}

/* Un ciclo de reloj del controlador: responde si IO_READ esta activa. */
static void tick_controlador_teclado(SystemBuses *bus, TecladoHardware *kb)
{
    if (bus->io_read) {
        if (bus->address_bus == PUERTO_STATUS) {
            bus->data_bus = kb->reg_status;
        } else if (bus->address_bus == PUERTO_DATA) {
            bus->data_bus = kb->reg_data;
            kb->reg_status = 0; /* Handshake automatico */
        }
    }
}

/* Instruccion IN de la CPU: pone la direccion, activa IO_READ y lee. */
static uint8_t cpu_instruccion_in(uint8_t puerto)
{
    g_bus.address_bus = puerto;
    g_bus.io_read     = true;
    g_bus.mem_read    = false;
    tick_controlador_teclado(&g_bus, &g_teclado);
    uint8_t dato = g_bus.data_bus;
    g_bus.io_read = false;
    return dato;
}

static int g_fallos = 0;

static void verificar(const char *descripcion, bool condicion)
{
    printf("  [%s] %s\n", condicion ? "OK" : "FALLO", descripcion);
    if (!condicion) g_fallos++;
}

/* Modo -t: traza CSV de las senales del bus (la usa generar_graficos.py). */
static void traza(void)
{
    const uint8_t secuencia[] = { PUERTO_STATUS, PUERTO_STATUS, PUERTO_DATA, PUERTO_STATUS };
    int paso = 0;
    printf("TRAZA,paso,evento,address_bus,io_read,data_bus,reg_status\n");
    printf("TRAZA,%d,reposo,0x00,0,0x00,%u\n", paso++, g_teclado.reg_status);
    teclado_presionar('A');
    printf("TRAZA,%d,tecla_A,0x00,0,0x00,%u\n", paso++, g_teclado.reg_status);
    for (unsigned i = 0; i < sizeof secuencia; i++) {
        uint8_t d = cpu_instruccion_in(secuencia[i]);
        printf("TRAZA,%d,IN_0x%02X,0x%02X,1,0x%02X,%u\n", paso++, secuencia[i], secuencia[i], d, g_teclado.reg_status);
    }
}

int main(int argc, char **argv)
{
    if (argc > 1 && strcmp(argv[1], "-t") == 0) { traza(); return 0; }
    printf("=== EXPERIMENTO 1: lectura por puerto (IO_READ + handshake) ===\n\n");

    printf("Prueba 1: sin tecla presionada\n");
    uint8_t st = cpu_instruccion_in(PUERTO_STATUS);
    printf("  IN 0x01 -> status = %u\n", st);
    verificar("status = 0 (no hay tecla lista)", st == 0);

    printf("\nPrueba 2: se presiona 'A' (0x41)\n");
    teclado_presionar('A');
    st = cpu_instruccion_in(PUERTO_STATUS);
    printf("  IN 0x01 -> status = %u\n", st);
    verificar("status = 1 (tecla lista)", st == 1);

    printf("\nPrueba 3: leer el status no limpia la bandera\n");
    st = cpu_instruccion_in(PUERTO_STATUS);
    printf("  IN 0x01 (segunda vez) -> status = %u\n", st);
    verificar("status sigue en 1 tras releer el puerto 0x01", st == 1);

    printf("\nPrueba 4: leer el puerto de datos entrega el ASCII y limpia el status\n");
    uint8_t dato = cpu_instruccion_in(PUERTO_DATA);
    printf("  IN 0x02 -> dato = 0x%02X ('%c')\n", dato, dato);
    verificar("dato = 0x41 ('A')", dato == 0x41);
    st = cpu_instruccion_in(PUERTO_STATUS);
    printf("  IN 0x01 -> status = %u\n", st);
    verificar("status = 0 (handshake automatico)", st == 0);

    printf("\nPrueba 5: tres teclas seguidas con sondeo (polling)\n");
    const char *entrada = "OK!";
    char leidas[4] = {0};
    for (int i = 0; entrada[i] != '\0'; i++) {
        teclado_presionar(entrada[i]);
        int consultas = 0;
        while (cpu_instruccion_in(PUERTO_STATUS) == 0 && consultas < 1000) consultas++;
        leidas[i] = (char)cpu_instruccion_in(PUERTO_DATA);
        printf("  tecla %d: leida '%c' (status=%u tras leer)\n", i + 1, leidas[i],
               cpu_instruccion_in(PUERTO_STATUS));
    }
    verificar("se leyo \"OK!\" completo y en orden", leidas[0] == 'O' && leidas[1] == 'K' && leidas[2] == '!');

    printf("\nPrueba 6: las senales del bus vuelven a reposo despues de cada IN\n");
    verificar("io_read = false tras la instruccion IN", g_bus.io_read == false);
    verificar("mem_read = false durante E/S aislada", g_bus.mem_read == false);

    printf("\nResultado: %s (%d fallos)\n", g_fallos == 0 ? "TODAS LAS PRUEBAS OK" : "HAY FALLOS", g_fallos);
    return g_fallos == 0 ? 0 : 1;
}
