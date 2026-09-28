/*
 * Práctica: llenar la memoria RAM y forzar el uso del espacio de
 * intercambio (swap) en Linux.
 *
 * El programa pide bloques de memoria en un bucle, los escribe completos
 * (para que el kernel les asigne marcos de página reales) y después de
 * cada bloque muestra cuánta RAM queda disponible y cuánta swap se está
 * usando, leyendo /proc/meminfo y /proc/self/status.
 *
 * Cuando la RAM disponible se acaba, el kernel empieza a mover páginas
 * del proceso a la swap: se ve como SwapUsada y VmSwap creciendo.
 *
 * Para no congelar el equipo ni despertar al OOM killer, el bucle se
 * detiene solo cuando:
 *   - la swap libre baja del margen de seguridad (--reserva-swap), o
 *   - no hay swap y la RAM disponible baja de --reserva-ram, o
 *   - se llegó al máximo pedido con --max-mb, o
 *   - se presiona Ctrl+C.
 *
 * Compilar:  gcc -Wall -Wextra -O2 llenar_memoria.c -o llenar_memoria
 * Uso:       ./llenar_memoria [--bloque-mb N] [--max-mb N]
 *                             [--reserva-ram MB] [--reserva-swap MB]
 */

#define _GNU_SOURCE
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define MB (1024L * 1024L)

static volatile sig_atomic_t detener = 0;

static void al_recibir_sigint(int sig)
{
    (void)sig;
    detener = 1;
}

/* Valores de /proc/meminfo que interesan, en MB. */
struct memoria {
    long total;
    long disponible;
    long swap_total;
    long swap_libre;
};

/* Lee un campo "Nombre:   valor kB" de un archivo de /proc y lo devuelve en MB. */
static long leer_campo_mb(const char *archivo, const char *campo)
{
    FILE *f = fopen(archivo, "r");
    char linea[256];
    size_t largo = strlen(campo);
    long kb = -1;

    if (f == NULL)
        return -1;
    while (fgets(linea, sizeof linea, f) != NULL) {
        if (strncmp(linea, campo, largo) == 0 && linea[largo] == ':') {
            kb = atol(linea + largo + 1);
            break;
        }
    }
    fclose(f);
    return kb < 0 ? -1 : kb / 1024;
}

static void leer_memoria(struct memoria *m)
{
    m->total      = leer_campo_mb("/proc/meminfo", "MemTotal");
    m->disponible = leer_campo_mb("/proc/meminfo", "MemAvailable");
    m->swap_total = leer_campo_mb("/proc/meminfo", "SwapTotal");
    m->swap_libre = leer_campo_mb("/proc/meminfo", "SwapFree");
}

static long leer_argumento(int argc, char **argv, const char *nombre, long defecto)
{
    int i;
    for (i = 1; i < argc - 1; i++)
        if (strcmp(argv[i], nombre) == 0)
            return atol(argv[i + 1]);
    return defecto;
}

int main(int argc, char **argv)
{
    long bloque_mb    = leer_argumento(argc, argv, "--bloque-mb", 256);
    long max_mb       = leer_argumento(argc, argv, "--max-mb", 0);      /* 0 = sin tope */
    long reserva_ram  = leer_argumento(argc, argv, "--reserva-ram", 256);
    long reserva_swap = leer_argumento(argc, argv, "--reserva-swap", 512);

    struct memoria m, inicio;
    char **bloques = NULL;
    long n_bloques = 0, capacidad = 0, asignado_mb = 0;
    long swap_inicial;
    int avisado_swap = 0;
    const char *motivo = "";
    struct timespec t0, t1;

    if (bloque_mb <= 0) {
        fprintf(stderr, "El tamaño de bloque debe ser mayor que 0.\n");
        return 1;
    }

    signal(SIGINT, al_recibir_sigint);
    setvbuf(stdout, NULL, _IOLBF, 0);

    leer_memoria(&inicio);
    swap_inicial = inicio.swap_total - inicio.swap_libre;

    printf("=== Llenar la RAM y forzar el uso de swap ===\n");
    printf("PID del proceso      : %d\n", (int)getpid());
    printf("RAM total            : %ld MB\n", inicio.total);
    printf("RAM disponible       : %ld MB\n", inicio.disponible);
    printf("Swap total           : %ld MB (usada al inicio: %ld MB)\n",
           inicio.swap_total, swap_inicial);
    printf("Tamaño de cada bloque: %ld MB\n", bloque_mb);
    if (max_mb > 0)
        printf("Tope de asignación   : %ld MB\n", max_mb);
    if (inicio.swap_total == 0)
        printf("AVISO: el sistema no tiene swap activa; el programa se detendrá "
               "al quedar %ld MB de RAM disponible.\n", reserva_ram);
    printf("\n%6s %12s %16s %12s %10s %10s\n",
           "Bloque", "Asignado MB", "RAM disp. MB", "Swap usada", "VmRSS MB", "VmSwap MB");

    clock_gettime(CLOCK_MONOTONIC, &t0);

    while (!detener) {
        char *p;

        if (max_mb > 0 && asignado_mb + bloque_mb > max_mb) {
            motivo = "se alcanzó el tope indicado con --max-mb";
            break;
        }

        leer_memoria(&m);
        if (m.swap_total > 0) {
            if (m.swap_libre < reserva_swap + bloque_mb) {
                motivo = "la swap libre llegó al margen de seguridad";
                break;
            }
        } else if (m.disponible < reserva_ram + bloque_mb) {
            motivo = "la RAM disponible llegó al margen de seguridad (no hay swap)";
            break;
        }

        p = malloc((size_t)bloque_mb * MB);
        if (p == NULL) {
            motivo = "malloc devolvió NULL";
            break;
        }
        /* malloc solo reserva direcciones virtuales: hasta que no se escribe,
         * el kernel no le da páginas físicas. Se escribe todo el bloque con un
         * patrón distinto de cero para que cada página ocupe RAM de verdad. */
        memset(p, 0xA5 ^ (int)(n_bloques & 0xFF), (size_t)bloque_mb * MB);

        if (n_bloques == capacidad) {
            long nueva = capacidad ? capacidad * 2 : 64;
            char **tmp = realloc(bloques, (size_t)nueva * sizeof *bloques);
            if (tmp == NULL) {
                free(p);
                motivo = "no hubo memoria para la lista de bloques";
                break;
            }
            bloques = tmp;
            capacidad = nueva;
        }
        bloques[n_bloques++] = p;
        asignado_mb += bloque_mb;

        leer_memoria(&m);
        printf("%6ld %12ld %16ld %12ld %10ld %10ld\n",
               n_bloques, asignado_mb, m.disponible,
               m.swap_total - m.swap_libre,
               leer_campo_mb("/proc/self/status", "VmRSS"),
               leer_campo_mb("/proc/self/status", "VmSwap"));

        if (!avisado_swap && leer_campo_mb("/proc/self/status", "VmSwap") > 0) {
            printf(">>> La RAM se llenó: el kernel empezó a mover páginas de este "
                   "proceso a la swap (VmSwap > 0).\n");
            avisado_swap = 1;
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    if (detener)
        motivo = "se presionó Ctrl+C";

    leer_memoria(&m);
    printf("\n=== Fin del bucle: %s ===\n", motivo);
    printf("Memoria asignada y escrita : %ld MB en %ld bloques (%.2f s)\n",
           asignado_mb, n_bloques,
           (double)(t1.tv_sec - t0.tv_sec) + (double)(t1.tv_nsec - t0.tv_nsec) / 1e9);
    printf("RAM disponible             : %ld MB (al inicio %ld MB)\n",
           m.disponible, inicio.disponible);
    printf("Swap usada por el sistema  : %ld MB (al inicio %ld MB)\n",
           m.swap_total - m.swap_libre, swap_inicial);
    printf("VmRSS del proceso (en RAM) : %ld MB\n", leer_campo_mb("/proc/self/status", "VmRSS"));
    printf("VmSwap del proceso (swap)  : %ld MB\n", leer_campo_mb("/proc/self/status", "VmSwap"));
    if (!avisado_swap)
        printf("El proceso no llegó a usar swap.\n");

    /* Pausa para tomar las capturas (free -h, swapon --show, htop...). */
    if (isatty(STDIN_FILENO)) {
        signal(SIGINT, SIG_DFL);
        printf("\nPresione ENTER para liberar la memoria y terminar...");
        getchar();
    }

    while (n_bloques > 0)
        free(bloques[--n_bloques]);
    free(bloques);
    printf("Memoria liberada.\n");
    return 0;
}
