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

## Cómo ejecutar

```bash
bash verificar_hardware.sh
```

## Salida

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
