# Clase 12 — Control de afinidad de CPU en C/C++

**Fecha:** 23/09/2026
**Tarea:** Práctica de la diapositiva *Control de Afinidad de CPU en C/C++*:

> Crear un programa que permita seleccionar núcleos específicos de la CPU
> y elevar su procesamiento al ~100 %.
>
> 1. **Detección:** identificar e informar el número total de núcleos lógicos (N).
> 2. **Configuración:** preguntar al usuario *cuántos* y *cuáles* núcleos (del 0 al N−1) desea utilizar.
> 3. **Ejecución:** crear un hilo por núcleo seleccionado y fijar su afinidad (`pthread_setaffinity_np` / `SetThreadAffinityMask`).
> 4. **Estrés:** correr una rutina intensiva de cómputo en los hilos elegidos.
> 5. **Control:** finalizar todos los hilos de manera limpia al presionar ENTER.
>
> **Entregable:** código fuente + captura del Monitor de Recursos / Administrador de Tareas.

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`afinidad_cpu.c`](afinidad_cpu.c) | El programa en C con POSIX threads: detecta N, pide cuántos y cuáles núcleos (con validación), crea un hilo fijado a cada núcleo, los estresa hasta el ~100 % y los detiene limpiamente con ENTER. |
| [`monitor_nucleos.sh`](monitor_nucleos.sh) | Muestra cada segundo el % de uso de cada núcleo calculado desde `/proc/stat` (no hace falta instalar `htop` ni `sysstat`). Es la "captura del monitor" en texto. |

## Conceptos

- **Núcleo lógico.** Cada CPU que ve el sistema operativo. Con
  *Hyper-Threading* un núcleo físico aparece como dos lógicos. Se cuentan
  con `nproc`, `lscpu` o, desde C, `sysconf(_SC_NPROCESSORS_ONLN)`.
- **Afinidad de CPU.** Normalmente el planificador del kernel mueve los
  hilos entre núcleos según la carga. La afinidad es una **máscara de
  bits** (`cpu_set_t`) que dice en qué núcleos *puede* correr un hilo;
  si la máscara tiene un solo bit, el hilo queda **fijado** a ese núcleo.
  Sirve para aprovechar la caché L1/L2 del núcleo (el hilo no la pierde
  al migrar), aislar cargas o, como aquí, estresar núcleos concretos.
- **`pthread_setaffinity_np`** (Linux) fija la máscara de un hilo;
  `_np` significa *non-portable* (es una extensión de GNU). En Windows el
  equivalente es `SetThreadAffinityMask(hilo, 1ULL << núcleo)`.
- **~100 % de uso.** Un hilo que solo calcula (sin E/S, sin `sleep`, sin
  esperar locks) nunca cede la CPU, así que ocupa su núcleo por completo.

## Cómo funciona `afinidad_cpu.c`

| Requisito | Implementación |
|-----------|----------------|
| 1. Detección | `sysconf(_SC_NPROCESSORS_ONLN)` → imprime `N` y el rango `0..N-1`. |
| 2. Configuración | Pregunta *cuántos* (1..N) y luego *cuáles*. Rechaza números fuera de rango, repetidos, de más, de menos o texto, y vuelve a preguntar. |
| 3. Ejecución | Por cada núcleo elegido arma una `cpu_set_t` con un solo bit (`CPU_ZERO` + `CPU_SET`), la pone en los atributos del hilo (`pthread_attr_setaffinity_np`, así el hilo nunca arranca en otro núcleo), crea el hilo con `pthread_create` y aplica `pthread_setaffinity_np`. Después lee la máscara con `pthread_getaffinity_np` y cada hilo informa su TID y el núcleo donde realmente corre (`sched_getcpu`). |
| 4. Estrés | `estresar()`: bucle de punto flotante (`sqrt`, `sin`, multiplicaciones) sin pausas; cuenta los bloques de 100 000 operaciones que completa. |
| 5. Control | El hilo principal espera ENTER; entonces pone la bandera `atomic_int en_ejecucion` en 0, cada hilo sale de su bucle y el principal hace `pthread_join` de todos. Imprime iteraciones y rendimiento por hilo. |

La bandera es `_Atomic` (C11) para que la escritura del hilo principal
sea visible en los otros núcleos sin carreras de datos; el resultado del
cálculo se guarda e imprime para que `-O2` no elimine el bucle.

## Cómo compilar y ejecutar

```bash
nproc                                          # núcleos lógicos (comprobación)
gcc -Wall -Wextra -O2 -pthread afinidad_cpu.c -o afinidad_cpu -lm
./afinidad_cpu

# En otra terminal, mientras corre:
bash monitor_nucleos.sh                        # % por núcleo cada segundo
htop                                           # barras por núcleo (captura del monitor)
mpstat -P ALL 1                                # si está instalado sysstat
ps -L -o pid,tid,psr,pcpu,comm -p $(pgrep afinidad_cpu)   # PSR = núcleo de cada hilo
for t in /proc/$(pgrep afinidad_cpu)/task/*; do taskset -cp ${t##*/}; done   # máscara de cada hilo
```

## Salidas

Compila **sin advertencias** con `-Wall -Wextra`. Pruebas en un equipo
Linux con 4 núcleos lógicos.

### Validación de la entrada

Se probaron entradas inválidas seguidas (`0`, `9`, luego `2`; `0 7`,
`1 1`, `0 2 3`, `hola` y por fin `0 2`):

```
=== Control de Afinidad de CPU ===
Núcleos lógicos detectados: N = 4 (del 0 al 3)

¿Cuántos núcleos desea utilizar? (1-4): 0
  Valor inválido.
¿Cuántos núcleos desea utilizar? (1-4): 9
  Valor inválido.
¿Cuántos núcleos desea utilizar? (1-4): 2
¿Cuáles núcleos? Escriba 2 número(s) del 0 al 3 separados por espacios: 0 7
  El núcleo 7 no existe.
¿Cuáles núcleos? Escriba 2 número(s) del 0 al 3 separados por espacios: 1 1
  El núcleo 1 está repetido.
¿Cuáles núcleos? Escriba 2 número(s) del 0 al 3 separados por espacios: 0 2 3
  Se indicaron más de 2 núcleos.
¿Cuáles núcleos? Escriba 2 número(s) del 0 al 3 separados por espacios: hola
  Entrada inválida: "hola".
¿Cuáles núcleos? Escriba 2 número(s) del 0 al 3 separados por espacios: 0 2
```

### Ejecución con los núcleos 0 y 2

```
Creando 2 hilo(s) de estrés (PID del proceso: 784)...
  Hilo 0 -> afinidad fijada al núcleo 0 (núcleos en la máscara: 1)
  Hilo 1 -> afinidad fijada al núcleo 2 (núcleos en la máscara: 1)

Hilos en ejecución:
  Hilo 0: TID 786, corriendo en el núcleo 0
  Hilo 1: TID 787, corriendo en el núcleo 2

Los núcleos elegidos deberían estar al ~100 %.
Verifíquelo con htop, con 'mpstat -P ALL 1' o con 'bash monitor_nucleos.sh'.
Presione ENTER para detener todos los hilos...
Todos los hilos terminaron de forma limpia tras 7.13 s.
  Hilo  Núcleo    Iteraciones      Iteraciones/s
     0        0           2567              359.8   (x = 707.0239)
     1        2           2506              351.3   (x = 707.0239)
```

Monitor de recursos al mismo tiempo (`bash monitor_nucleos.sh 5`):
**solo los núcleos elegidos están al 100 %**, el 1 y el 3 siguen libres.

```
15:01:43  cpu0:100%  cpu1:  1%  cpu2:100%  cpu3:  0%
15:01:44  cpu0:100%  cpu1:  1%  cpu2:100%  cpu3:  2%
15:01:45  cpu0:100%  cpu1:  0%  cpu2:100%  cpu3:  1%
15:01:46  cpu0:100%  cpu1:  0%  cpu2:100%  cpu3:  1%
15:01:47  cpu0:100%  cpu1:  0%  cpu2:100%  cpu3:  0%
```

Comprobación desde el sistema operativo: `ps` muestra cada hilo de
estrés en su núcleo (`PSR`) al ~100 %, y `taskset` confirma que la
máscara de cada hilo tiene un solo núcleo (el hilo principal conserva
`0-3` porque solo espera el ENTER):

```
$ ps -L -o pid,tid,psr,pcpu,comm -p 784
  PID   TID PSR %CPU COMMAND
  784   784   3  0.0 afinidad_cpu
  784   786   0 97.1 afinidad_cpu
  784   787   2 98.0 afinidad_cpu

$ for t in /proc/784/task/*; do taskset -cp ${t##*/}; done
pid 784's current affinity list: 0-3
pid 786's current affinity list: 0
pid 787's current affinity list: 2
```

### Ejecución con los 4 núcleos (`3 2 1 0`)

```
15:02:15  cpu0:100%  cpu1:100%  cpu2:100%  cpu3:100%
15:02:16  cpu0:100%  cpu1:100%  cpu2:100%  cpu3:100%
15:02:17  cpu0:100%  cpu1:100%  cpu2:100%  cpu3:100%

Todos los hilos terminaron de forma limpia tras 5.13 s.
  Hilo  Núcleo    Iteraciones      Iteraciones/s
     0        3           1850              360.8   (x = 707.0239)
     1        2           1834              357.7   (x = 707.0239)
     2        1           1826              356.1   (x = 707.0239)
     3        0           1848              360.4   (x = 707.0239)
```

Cada núcleo rinde lo mismo (~358 iteraciones/s) haya uno o cuatro hilos:
como cada hilo tiene su propio núcleo, no compiten entre sí.

> 🖼️ La captura gráfica del monitor (`htop` o el *Monitor del sistema* de
> Ubuntu, pestaña *Recursos*) con los núcleos elegidos al 100 % se toma
> en la laptop y se guarda junto a este README.
