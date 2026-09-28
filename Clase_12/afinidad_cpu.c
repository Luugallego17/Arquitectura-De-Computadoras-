/*
 * Control de afinidad de CPU en C (Linux, POSIX threads).
 *
 * 1. Detección     : informa el número total de núcleos lógicos N.
 * 2. Configuración : pregunta cuántos y cuáles núcleos (0 a N-1) usar.
 * 3. Ejecución     : crea un hilo por núcleo elegido y fija su afinidad
 *                    con pthread_setaffinity_np.
 * 4. Estrés        : cada hilo corre una rutina de cómputo intensivo que
 *                    lleva su núcleo al ~100 %.
 * 5. Control       : al presionar ENTER todos los hilos terminan de forma
 *                    limpia (bandera atómica + pthread_join).
 *
 * Compilar:  gcc -Wall -Wextra -O2 -pthread afinidad_cpu.c -o afinidad_cpu -lm
 * Ejecutar:  ./afinidad_cpu
 */

#define _GNU_SOURCE
#include <math.h>
#include <pthread.h>
#include <sched.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

/* Bandera que comparten todos los hilos: mientras valga 1, siguen trabajando. */
static atomic_int en_ejecucion = 1;

struct hilo {
    pthread_t id;
    int nucleo;                 /* núcleo al que se fija el hilo      */
    int nucleo_real;            /* núcleo donde corre (sched_getcpu)  */
    pid_t tid;                  /* id del hilo en el kernel (para ps) */
    unsigned long long iteraciones;
    double resultado;           /* se imprime para que el compilador no borre el cálculo */
};

/* 4. Rutina de estrés: cómputo en punto flotante sin pausas ni E/S. */
static void *estresar(void *arg)
{
    struct hilo *h = arg;
    double x = 1.0 + h->nucleo;
    unsigned long long n = 0;

    h->tid = (pid_t)syscall(SYS_gettid);
    h->nucleo_real = sched_getcpu();

    while (atomic_load_explicit(&en_ejecucion, memory_order_relaxed)) {
        int i;
        for (i = 0; i < 100000; i++)
            x = sqrt(x * x + 1.0) * 0.999999 + sin(x) * 1e-6;
        n++;
    }

    h->iteraciones = n;
    h->resultado = x;
    return NULL;
}

/* Lee una línea de la entrada estándar; devuelve 0 si hubo EOF. */
static int leer_linea(char *buf, size_t tam)
{
    if (fgets(buf, (int)tam, stdin) == NULL)
        return 0;
    buf[strcspn(buf, "\n")] = '\0';
    return 1;
}

int main(void)
{
    char linea[1024];
    int n_nucleos, cantidad = 0, i;
    int *elegidos;
    char *usado;
    struct hilo *hilos;
    struct timespec t0, t1;
    double segundos;

    setvbuf(stdout, NULL, _IONBF, 0);

    /* ---------- 1. Detección ---------- */
    n_nucleos = (int)sysconf(_SC_NPROCESSORS_ONLN);
    if (n_nucleos < 1) {
        fprintf(stderr, "No se pudo detectar el número de núcleos.\n");
        return 1;
    }
    printf("=== Control de Afinidad de CPU ===\n");
    printf("Núcleos lógicos detectados: N = %d (del 0 al %d)\n\n", n_nucleos, n_nucleos - 1);

    /* ---------- 2. Configuración ---------- */
    while (cantidad < 1 || cantidad > n_nucleos) {
        char *fin;
        printf("¿Cuántos núcleos desea utilizar? (1-%d): ", n_nucleos);
        if (!leer_linea(linea, sizeof linea))
            return 1;
        cantidad = (int)strtol(linea, &fin, 10);
        if (fin == linea || *fin != '\0' || cantidad < 1 || cantidad > n_nucleos) {
            printf("  Valor inválido.\n");
            cantidad = 0;
        }
    }

    elegidos = malloc((size_t)cantidad * sizeof *elegidos);
    usado = calloc((size_t)n_nucleos, 1);
    hilos = calloc((size_t)cantidad, sizeof *hilos);
    if (elegidos == NULL || usado == NULL || hilos == NULL) {
        fprintf(stderr, "Sin memoria.\n");
        return 1;
    }

    for (;;) {
        char *p = linea, *fin;
        int k = 0, valido = 1;

        memset(usado, 0, (size_t)n_nucleos);
        printf("¿Cuáles núcleos? Escriba %d número(s) del 0 al %d separados por espacios: ",
               cantidad, n_nucleos - 1);
        if (!leer_linea(linea, sizeof linea))
            return 1;

        while (valido) {
            long v = strtol(p, &fin, 10);
            if (fin == p)                   /* no hay más números */
                break;
            if (v < 0 || v >= n_nucleos) {
                printf("  El núcleo %ld no existe.\n", v);
                valido = 0;
            } else if (usado[v]) {
                printf("  El núcleo %ld está repetido.\n", v);
                valido = 0;
            } else if (k == cantidad) {
                printf("  Se indicaron más de %d núcleos.\n", cantidad);
                valido = 0;
            } else {
                usado[v] = 1;
                elegidos[k++] = (int)v;
            }
            p = fin;
        }
        while (*p == ' ' || *p == '\t' || *p == ',')
            p++;
        if (valido && *p != '\0') {
            printf("  Entrada inválida: \"%s\".\n", p);
            valido = 0;
        }
        if (valido && k < cantidad) {
            printf("  Faltan núcleos: se indicaron %d de %d.\n", k, cantidad);
            valido = 0;
        }
        if (valido)
            break;
    }

    /* ---------- 3. Ejecución: un hilo por núcleo, con afinidad fija ---------- */
    printf("\nCreando %d hilo(s) de estrés (PID del proceso: %d)...\n", cantidad, (int)getpid());
    clock_gettime(CLOCK_MONOTONIC, &t0);

    for (i = 0; i < cantidad; i++) {
        pthread_attr_t attr;
        cpu_set_t mascara;
        int err;

        hilos[i].nucleo = elegidos[i];
        hilos[i].nucleo_real = -1;

        /* La afinidad se fija en los atributos antes de crear el hilo, así
         * el hilo nunca llega a ejecutarse fuera de su núcleo. */
        CPU_ZERO(&mascara);
        CPU_SET(elegidos[i], &mascara);
        pthread_attr_init(&attr);
        err = pthread_attr_setaffinity_np(&attr, sizeof mascara, &mascara);
        if (err == 0)
            err = pthread_create(&hilos[i].id, &attr, estresar, &hilos[i]);
        pthread_attr_destroy(&attr);
        if (err != 0) {
            fprintf(stderr, "No se pudo crear el hilo del núcleo %d: %s\n",
                    elegidos[i], strerror(err));
            atomic_store(&en_ejecucion, 0);
            cantidad = i;           /* solo se esperan los hilos ya creados */
            break;
        }

        /* Además se aplica pthread_setaffinity_np sobre el hilo ya creado,
         * que es la llamada que pide la práctica, y se lee de vuelta la
         * máscara para comprobar que quedó fijado a un único núcleo. */
        err = pthread_setaffinity_np(hilos[i].id, sizeof mascara, &mascara);
        if (err != 0)
            fprintf(stderr, "pthread_setaffinity_np (núcleo %d): %s\n", elegidos[i], strerror(err));
        CPU_ZERO(&mascara);
        pthread_getaffinity_np(hilos[i].id, sizeof mascara, &mascara);
        printf("  Hilo %d -> afinidad fijada al núcleo %d (núcleos en la máscara: %d)\n",
               i, elegidos[i], CPU_COUNT(&mascara));
    }

    if (atomic_load(&en_ejecucion)) {
        usleep(200000);  /* deja que cada hilo registre su TID y su núcleo */
        printf("\nHilos en ejecución:\n");
        for (i = 0; i < cantidad; i++)
            printf("  Hilo %d: TID %d, corriendo en el núcleo %d\n",
                   i, (int)hilos[i].tid, hilos[i].nucleo_real);

        printf("\nLos núcleos elegidos deberían estar al ~100 %%.\n");
        printf("Verifíquelo con htop, con 'mpstat -P ALL 1' o con 'bash monitor_nucleos.sh'.\n");
        /* ---------- 5. Control ---------- */
        printf("Presione ENTER para detener todos los hilos...");
        leer_linea(linea, sizeof linea);
        atomic_store(&en_ejecucion, 0);
    }

    for (i = 0; i < cantidad; i++)
        pthread_join(hilos[i].id, NULL);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    segundos = (double)(t1.tv_sec - t0.tv_sec) + (double)(t1.tv_nsec - t0.tv_nsec) / 1e9;

    printf("\nTodos los hilos terminaron de forma limpia tras %.2f s.\n", segundos);
    printf("%6s %8s %14s %18s\n", "Hilo", "Núcleo", "Iteraciones", "Iteraciones/s");
    for (i = 0; i < cantidad; i++)
        printf("%6d %8d %14llu %18.1f   (x = %.4f)\n", i, hilos[i].nucleo,
               hilos[i].iteraciones, (double)hilos[i].iteraciones / segundos,
               hilos[i].resultado);

    free(hilos);
    free(usado);
    free(elegidos);
    return 0;
}
