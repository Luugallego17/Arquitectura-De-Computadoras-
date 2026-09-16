# Práctica: Verificación previa del hardware — jerarquía de caché y línea de 64 bytes

**Materia:** Arquitectura de Computadoras
**Alumna:** Luna Saleth Gallego Martinez
**Fecha:** 16/09/2026
**Tarea:** [#21 — Verificación del hardware: jerarquía de caché y línea de 64 bytes (`lscpu`, `getconf`, sysfs)](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/21)

---

Antes de compilar el benchmark del laboratorio hay que conocer la
topología de memoria del procesador: cuántos niveles de caché tiene,
de qué tamaño son y, sobre todo, **cuánto mide una línea de caché**,
porque de eso depende todo el análisis de las fases siguientes.

Los tres comandos de la guía se ejecutan desde una terminal de Linux
(están juntos en [`verificar_hardware.sh`](verificar_hardware.sh)).

## 1. Jerarquía y tamaños de caché — `lscpu`

```bash
lscpu | grep -E "L1|L2|L3|Model name"
```

`lscpu` ya lo usamos en la [Clase 3](../Clase_3/); esta vez se filtra
con `grep` para quedarnos solo con el modelo del procesador y las
líneas de caché. Salida en el equipo donde se corrió la práctica:

```
Model name:                              Intel(R) Xeon(R) Processor @ 2.80GHz
L1d cache:                               128 KiB (4 instances)
L1i cache:                               128 KiB (4 instances)
L2 cache:                                4 MiB (4 instances)
L3 cache:                                33 MiB (1 instance)
Vulnerability L1tf:                      Not affected
```

(La última línea no es una caché: `grep "L1"` también atrapa la
vulnerabilidad *L1 Terminal Fault*. Se ignora.)

Cómo se lee:

- **L1d / L1i** — la caché de nivel 1 está partida en dos: datos (`d`)
  e instrucciones (`i`). `128 KiB (4 instances)` quiere decir que hay
  4 núcleos y cada uno tiene su propia L1 de 32 KiB (128 / 4).
- **L2** — 1 MiB por núcleo (4 MiB entre 4 instancias). Es unificada:
  guarda datos e instrucciones.
- **L3** — 33 MiB en una sola instancia: es la caché grande y
  **compartida** entre todos los núcleos.

Entre más cerca del núcleo, la caché es más chica y más rápida; por
eso el benchmark del laboratorio se enfoca en aprovechar bien la L1.

## 2. Tamaño de la línea de caché de datos — `getconf`

```bash
getconf LEVEL1_DCACHE_LINESIZE
```

```
64
```

`getconf` consulta los valores de configuración del sistema que expone
la librería de C. `LEVEL1_DCACHE_LINESIZE` es el tamaño, en bytes, de
una **línea de la caché de datos L1**: la unidad mínima que se mueve
entre la memoria RAM y la caché. Aquí vale **64 bytes**, el valor
típico en x86-64.

## 3. Tamaño del bloque de coherencia — sysfs

```bash
cat /sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size
```

```
64
```

El kernel expone la información de cada caché del `cpu0` en el
pseudo-sistema de archivos `sysfs`. `index0` es la L1 de datos, y
`coherency_line_size` es el tamaño del bloque que el protocolo de
coherencia mueve y marca como válido/inválido entre núcleos. Coincide
con `getconf`: **64 bytes**.

Mirando los otros `index*` se confirma toda la jerarquía y que la
línea mide lo mismo en todos los niveles:

```
index0: L1 Data        tamaño=32K     línea=64 bytes
index1: L1 Instruction tamaño=32K     línea=64 bytes
index2: L2 Unified     tamaño=1024K   línea=64 bytes
index3: L3 Unified     tamaño=33792K  línea=64 bytes
```

Estos tamaños por núcleo (32K de L1d, 1024K de L2) son los que
`lscpu` mostraba multiplicados por las 4 instancias.

## Principio físico: 64 bytes = 16 float

Un `float` ocupa 4 bytes (`sizeof(float) = 4`), así que:

```
64 bytes / 4 bytes por float = 16 float por línea de caché
```

Cuando el procesador pide **un solo** elemento de un arreglo, el bus no
trae ese elemento: trae la línea completa de 64 bytes, o sea los
**16 float contiguos** que lo rodean. De ahí salen los dos números que
usa la guía:

- Si el programa recorre el arreglo en orden (acceso contiguo), la
  primera lectura falla en caché y las 15 siguientes aciertan: **1
  fallo cada 16 lecturas**, una tasa de aciertos teórica de
  15/16 = **93.75 %**.
- Si el programa salta de fila en fila (en la matriz de 1024 float
  cada salto son 4096 bytes), cada lectura cae en una línea distinta:
  se usa 1 de los 16 elementos que se trajeron y se **desperdicia el
  93.75 %** de cada transferencia.

Ese es exactamente el contraste entre la Fase 1 (naive `i-j-k`) y la
Fase 2 (localidad espacial `i-k-j`) del benchmark que viene en las
siguientes tareas.

## Resumen de lo verificado

| Dato | Valor |
|------|-------|
| Procesador | Intel Xeon @ 2.80 GHz, 4 núcleos (x86_64) |
| L1 datos / L1 instrucciones | 32 KiB + 32 KiB por núcleo |
| L2 | 1 MiB por núcleo |
| L3 | 33 MiB compartida |
| Línea de caché (`getconf`) | 64 bytes |
| Línea de caché (sysfs) | 64 bytes |
| Float por línea | 16 |

> 🖥️ Los valores de esta página son los del equipo Linux donde se corrió
> la práctica. En otra computadora cambian los tamaños de L1/L2/L3 y el
> modelo, pero la línea de caché de 64 bytes es prácticamente universal
> en x86-64. Para repetir la verificación en cualquier equipo basta con
> `bash verificar_hardware.sh`.
