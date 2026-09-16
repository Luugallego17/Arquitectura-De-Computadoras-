# Clase 10 — Optimización en la jerarquía de memoria

**Fecha:** 16/09/2026
**Tareas:**

- [#21 — Verificación del hardware: jerarquía de caché y línea de 64 bytes (`lscpu`, `getconf`, sysfs)](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/21)
- [#22 — Benchmark en ANSI C: producto matricial 1024×1024 con 4 fases de optimización](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/22)
- [#23 — Ejecución del benchmark y análisis de fallos de caché con `perf`](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/23)
- [#24 — Informe del laboratorio: cuestionario de análisis crítico y entrega](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/24)

Guía de laboratorio: *Optimización en la Jerarquía de Memoria — Análisis
empírico de líneas de caché (64 B), registros de CPU y paralelismo ILP
en Linux*. La idea es comprobar con mediciones reales cuánto cuesta un
fallo de caché frente a un acierto, y cuánto se acelera un producto de
matrices 1024×1024 solo con reordenar los bucles, usar registros y
desenrollar el bucle interno.

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`verificacion_hardware.md`](verificacion_hardware.md) | Tarea #21: qué hace cada comando de verificación previa, las salidas del equipo y por qué una línea de 64 bytes guarda 16 `float`. |
| [`verificar_hardware.sh`](verificar_hardware.sh) | Script que corre los tres comandos de la guía y calcula cuántos `float` caben en una línea de caché. |
| [`benchmark_arquitectura.c`](benchmark_arquitectura.c) | Tarea #22: el benchmark oficial en ANSI C. Producto matricial 1024×1024 en cuatro fases (naive, localidad espacial, registros de CPU y loop unrolling 4x), con medición de tiempo, GFLOPS, speedup y checksum de validación. |

## Parte 1 — Verificación previa del hardware (tarea #21)

```bash
lscpu | grep -E "L1|L2|L3|Model name"                              # jerarquía L1/L2/L3
getconf LEVEL1_DCACHE_LINESIZE                                      # línea de la caché de datos L1
cat /sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size   # bloque de coherencia (sysfs)
```

Los dos últimos devuelven **64**: la línea de caché mide 64 bytes, y
como `sizeof(float) = 4`, cada línea trae **16 float contiguos**. Ese
número explica el resto del laboratorio: recorrer la matriz en orden
aprovecha 16 elementos por transferencia (1 fallo cada 16 lecturas,
~93.75 % de aciertos), y saltar de fila en fila desperdicia 15 de cada
16. El detalle y las salidas están en
[`verificacion_hardware.md`](verificacion_hardware.md).

## Parte 2 — Benchmark en ANSI C con 4 fases (tarea #22)

El experimento es siempre el mismo: el producto matricial **C = A × B**
con matrices de 1024 × 1024 `float` (4 MB cada una; 24 MB de huella
activa en RAM contando las seis matrices). Lo que cambia entre fases es
*cómo* se recorre la memoria:

| Fase | Función | Qué cambia | Por qué mejora |
|------|---------|------------|----------------|
| 1. Naive `i-j-k` | `algoritmo_naive` | El bucle interno avanza `k`, así que en `B[k][j]` salta de fila en fila: **4096 bytes** por paso. | No mejora: cada lectura de `B` cae en una línea de caché distinta y se desperdicia el 93.75 % de los 64 bytes que trae el bus. |
| 2. Localidad espacial `i-k-j` | `algoritmo_localidad_espacial` | Se intercambian los bucles: el interno avanza `j`, y tanto `B[k][j]` como `C[i][j]` se leen contiguos. | 1 fallo de caché cada 16 lecturas (los 16 `float` de la línea se usan todos). |
| 3. Localidad temporal + registros | `algoritmo_registros_cpu` | `A[i][k]` no cambia en todo el bucle `j`, así que se guarda en `register const float reg_a` y se usan punteros a las filas de `B` y `C`. | El operando repetido vive en un registro de la FPU y no se vuelve a pedir a memoria en cada iteración. |
| 4. Loop unrolling 4x + ILP | `algoritmo_loop_unrolling` | El bucle `j` procesa `j`, `j+1`, `j+2`, `j+3` en cada paso. | Menos saltos y comparaciones por elemento, y cuatro operaciones independientes que el procesador superescalar puede ejecutar en paralelo en sus pipelines. |

Además el programa:

- mide cada fase con `clock_gettime(CLOCK_MONOTONIC)`, que es un reloj
  monotónico (no lo afectan cambios de hora del sistema);
- calcula el rendimiento como `2·N³ / tiempo` en GFLOPS (cada producto
  escalar hace una multiplicación y una suma);
- calcula el **speedup** `S = T_base / T_opt` tomando la fase naive
  como base;
- valida el determinismo con un **checksum**: suma todos los elementos
  de `C` de la fase 1 y de la fase 4, que deben coincidir porque las
  cuatro fases calculan exactamente la misma matriz.

## Cómo compilar y ejecutar

```bash
# Parte 1 — verificación del hardware
bash verificar_hardware.sh

# Parte 2 — benchmark (flags oficiales de la guía)
gcc -Wall -Wextra -O1 benchmark_arquitectura.c -o benchmark_arquitectura -lm
./benchmark_arquitectura
```

Se usa `-O1` a propósito: activa optimizaciones básicas pero **no
reordena bucles** automáticamente como haría `-O3`, así que lo que se
mide es el efecto real de cómo está escrito el código.

## Salidas

### Parte 1 — `verificar_hardware.sh`

```
=== 1. Jerarquía y tamaños de memoria caché L1, L2 y L3 ===
$ lscpu | grep -E "L1|L2|L3|Model name"
Model name:                              Intel(R) Xeon(R) Processor @ 2.80GHz
L1d cache:                               128 KiB (4 instances)
L1i cache:                               128 KiB (4 instances)
L2 cache:                                4 MiB (4 instances)
L3 cache:                                33 MiB (1 instance)
Vulnerability L1tf:                      Not affected

=== 2. Tamaño de la línea de caché de datos L1 (getconf) ===
$ getconf LEVEL1_DCACHE_LINESIZE
64

=== 3. Tamaño del bloque de coherencia según el sysfs del kernel ===
$ cat /sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size
64

=== Detalle de cada nivel de caché del cpu0 (sysfs) ===
index0: L1 Data        tamaño=32K     línea=64 bytes
index1: L1 Instruction tamaño=32K     línea=64 bytes
index2: L2 Unified     tamaño=1024K   línea=64 bytes
index3: L3 Unified     tamaño=33792K  línea=64 bytes

=== Principio físico ===
getconf y sysfs coinciden: la línea de caché mide 64 bytes.
Un float ocupa 4 bytes, así que una línea guarda 16 float contiguos.
Al pedir un solo float, el bus trae la línea completa: 1 fallo de caché por cada 16 lecturas.
```

### Parte 2 — `benchmark_arquitectura`

Compila sin ninguna advertencia con `-Wall -Wextra`. Salida en el mismo
equipo de la Parte 1 (Intel Xeon @ 2.80 GHz, 4 núcleos):

```
=== RESULTADOS DETERMINISTICOS (N=1024) ===
1. Naive (i-j-k)              :  3.4543 s |   0.62 GFLOPS | Speedup: 1.00x
2. Localidad Espacial (Cache) :  0.5488 s |   3.91 GFLOPS | Speedup: 6.29x
3. Registros de CPU           :  0.5478 s |   3.92 GFLOPS | Speedup: 6.31x
4. Loop Unrolling 4x (ILP)    :  0.3819 s |   5.62 GFLOPS | Speedup: 9.04x
[OK] Validacion de Checksum: 1.5839e+09 (Error = 0.0000e+00)
```

Lo que se ve:

- Solo con cambiar el orden de los bucles (fase 2) el mismo cálculo se
  hace **6.3 veces más rápido**. Es la diferencia entre desperdiciar y
  aprovechar la línea de caché de 64 bytes que se verificó en la Parte 1.
- La fase 3 casi no cambia respecto a la 2: con `-O1` el compilador ya
  estaba dejando `r = A[i*N+k]` en un registro, así que `register` solo
  hace explícito lo que ya pasaba.
- El unrolling (fase 4) suma otro **1.4x** sobre la fase 3 sin hacer ni
  una operación matemática más: se ahorran saltos y se deja que el
  procesador ejecute varias instrucciones a la vez.
- El **error del checksum es 0**: las cuatro fases producen exactamente
  la misma matriz. La optimización cambió el tiempo, no el resultado.

El análisis con `perf` y la tabla de métricas completa quedan para la
tarea #23.
