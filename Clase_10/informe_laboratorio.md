# Informe técnico — Optimización en la jerarquía de memoria aplicada al juego "UCB - IA Experience"

**Materia:** Arquitectura de Computadoras (SIS-131)
**Alumna:** Luna Saleth Gallego Martinez
**Fecha:** 16/09/2026
**Tarea:** [#22](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/22)

---

## 1. Qué se midió

La función `overlay_rect()` del juego ([`../Clase_9/Juego_VA.py`](../Clase_9/Juego_VA.py))
pinta los paneles semitransparentes de la interfaz. Para cada panel copia
el frame completo de la pantalla (1920 × 1080 × 3 = 6 220 800 bytes),
pinta el rectángulo en la copia y mezcla el frame completo con
`cv2.addWeighted`, entre 6 y 8 veces por frame. `benchmark_juego.c`
reproduce esa operación en ANSI C con la misma fórmula que usa OpenCV,
en punto flotante:

```
dst = (unsigned char)(src · (1 − alpha) + overlay · alpha + 0.5)
```

Son 2 multiplicaciones y 2 sumas en `float` por cada byte del frame:
**4 FLOP por byte**. El rendimiento se calcula como
`GFLOPS = 4 · bytes mezclados · frames / tiempo / 10⁹`.

Las fases siguen la guía: **1** naive (todo el frame, recorrido por
columnas: cada paso salta una fila de 5760 bytes), **2** localidad
espacial (todo el frame por filas, acceso contiguo), **3** localidad
temporal + registros (alpha y 1 − alpha en `register const float`,
punteros por fila), **4** loop unrolling 4x, y una fase **5** adicional
con la optimización aplicada al juego: mezclar solo los 640 × 240
píxeles del rectángulo sin copiar el frame.

## 2. Hardware

Intel Xeon @ 2.80 GHz, 4 núcleos, x86_64. L1d 32 KiB por núcleo (8 vías),
L2 1 MiB por núcleo, L3 33 MiB compartida. Línea de caché: **64 bytes**
(`getconf LEVEL1_DCACHE_LINESIZE` = 64, `coherency_line_size` = 64).
Detalle en [`verificacion_hardware.md`](verificacion_hardware.md).

## 3. Ejecución

```
$ gcc -Wall -Wextra -O1 benchmark_juego.c -o benchmark_juego -lm
$ ./benchmark_juego

=== RESULTADOS DETERMINISTICOS: overlay_rect sobre 1920x1080x3, 30 frames ===
Frame: 6.2 MB | Rectangulo: 640x240 px | 4 FLOP por byte mezclado

1. Naive (por columnas)      :  0.4589 s |   15.30 ms/frame |   1.63 GFLOPS | Speedup:   1.00x
2. Localidad Espacial (filas):  0.2623 s |    8.74 ms/frame |   2.85 GFLOPS | Speedup:   1.75x
3. Registros de CPU          :  0.2556 s |    8.52 ms/frame |   2.92 GFLOPS | Speedup:   1.80x
4. Loop Unrolling 4x (ILP)   :  0.2639 s |    8.80 ms/frame |   2.83 GFLOPS | Speedup:   1.74x
5. Solo ROI (juego optimiz.) :  0.0113 s |    0.38 ms/frame |   4.89 GFLOPS | Speedup:  40.62x

[OK] Validacion de Checksum: 7.4670e+08
     Fase 2 vs Fase 1: Error = 0.0000e+00
     Fase 3 vs Fase 1: Error = 0.0000e+00
     Fase 4 vs Fase 1: Error = 0.0000e+00
     Fase 5 vs Fase 1: Error = 0.0000e+00
```

Compila sin advertencias. Una segunda corrida dio 0.4693 / 0.2575 /
0.2675 / 0.2668 / 0.0138 s: las fases 2, 3 y 4 están dentro del ruido
de medición entre sí.

## 4. Fallos de caché

La guía pide `perf stat`. En el equipo donde se corrió el benchmark
`perf` no está disponible, así que la tasa de aciertos se midió con el
simulador de caché de Valgrind, configurado con la L1d real del equipo
(32 KiB, 8 vías, líneas de 64 bytes) y un solo frame por fase para que
la simulación termine en un tiempo razonable:

```
$ gcc -Wall -Wextra -O1 -DFRAMES=1 benchmark_juego.c -o benchmark_juego_cg -lm
$ valgrind --tool=cachegrind --cache-sim=yes --I1=32768,8,64 --D1=32768,8,64 \
           --LL=33554432,16,64 --cachegrind-out-file=cg.out ./benchmark_juego_cg
$ cg_annotate cg.out
```

Resultado por función (`Ir` = instrucciones, `Dr` = lecturas de datos,
`D1mr` = fallos de lectura en L1d, `Dw` = escrituras, `D1mw` = fallos de
escritura):

```
Ir           Dr           D1mr        Dw          D1mw   función
103,689,616  12,441,606   4,276,802   6,220,803   0      fase1_naive
103,685,416  12,441,606     194,404   6,220,803   0      fase2_localidad_espacial
 93,317,416  12,441,606     194,404   6,220,803   0      fase3_registros_cpu
 80,877,978  12,441,606     194,404   6,220,803   0      fase4_loop_unrolling
  3,687,369     460,805       7,442     460,800   0      fase5_roi
```

Tasa de acierto de la caché L1 de datos en las lecturas = 1 − D1mr / Dr:

| Fase | Fallos / lecturas | Tasa de acierto | Instrucciones por byte |
|------|-------------------|-----------------|------------------------|
| 1. Naive (por columnas) | 4 276 802 / 12 441 606 | **65.6 %** | 16.7 |
| 2. Localidad espacial (por filas) | 194 404 / 12 441 606 | **98.4 %** | 16.7 |
| 3. Registros de CPU | 194 404 / 12 441 606 | **98.4 %** | 15.0 |
| 4. Loop unrolling 4x | 194 404 / 12 441 606 | **98.4 %** | 13.0 |
| 5. Solo ROI | 7 442 / 460 805 | **98.4 %** | 8.0 |

En la laptop del proyecto el mismo dato se obtiene con:

```
$ perf stat -e L1-dcache-loads,L1-dcache-load-misses,cycles,instructions ./benchmark_juego
```

## 5. Plantilla de registro de métricas

| Fase / Configuración | Tiempo Medido (s) | Rendimiento (GFLOPS) | Aceleración (Speedup) | Tasa Acierto Caché |
|----------------------|-------------------|----------------------|-----------------------|--------------------|
| 1. Naive (por columnas) | 0.4589 s | 1.63 GFLOPS | 1.00x (Base) | Baja: 65.6 % |
| 2. Localidad Espacial (por filas) | 0.2623 s | 2.85 GFLOPS | 1.75x | Alta: 98.4 % |
| 3. Uso de Registros CPU | 0.2556 s | 2.92 GFLOPS | 1.80x | Óptima: 98.4 % |
| 4. Loop Unrolling 4x (ILP) | 0.2639 s | 2.83 GFLOPS | 1.74x | Máxima: 98.4 % |
| 5. Solo ROI (optimización del juego) | 0.0113 s | 4.89 GFLOPS | 40.62x | 98.4 % |

Lectura de la tabla:

- El salto grande entre las fases 1 y 2 (1.75x) es solo por el orden de
  recorrido: mismas instrucciones (103.7 M en las dos), mismas
  operaciones, pero 22 veces menos fallos de caché.
- Las fases 3 y 4 reducen las instrucciones (−10 % y −22 %) pero no el
  tiempo: una vez arreglada la localidad, el bucle ya no espera a la
  memoria sino a la FPU, que por cada byte convierte entero → float,
  multiplica, suma y convierte float → entero. Con `-O1` esa cadena no
  se acorta ni con registros ni con unrolling (ver preguntas 2 y 3).
- La fase 5 es la que importa para el juego: 40x, porque toca 13.5
  veces menos memoria (0.46 MB del rectángulo contra 6.2 MB del frame
  más otros 6.2 MB de la copia).
- La tasa "baja" de la fase 1 es 65.6 % y no "< 15 %" como en la guía
  porque los píxeles del juego son `uint8`: los 3 bytes de un píxel
  caen en la misma línea, así que de cada 3 lecturas por arreglo la
  primera falla y las otras dos aciertan (2 fallos por píxel entre
  `frame` y `overlay`, sobre 6 lecturas = 66.7 % teórico).

## 6. Cuestionario de análisis crítico

### Pregunta 1 — Líneas de caché

*Si una línea de caché mide 64 bytes y cada `float` ocupa 4 bytes,
¿cuántos accesos a memoria consecutivos aprovechan una sola carga a la
caché L1 en la Fase 2? Demuestre la fórmula teórica del Hit Rate.*

Con `float` de 4 bytes, una línea de 64 bytes trae **64 / 4 = 16**
elementos contiguos. Al recorrer en orden, el primer acceso a la línea
falla (hay que traerla de RAM) y los 15 siguientes aciertan:

```
Hit Rate = (elementos por línea − 1) / elementos por línea
         = (64/4 − 1) / (64/4) = 15 / 16 = 93.75 %
```

En el juego los datos no son `float` sino píxeles `uint8` (1 byte por
canal), así que una línea trae **64 accesos consecutivos**:

```
Hit Rate = (64/1 − 1) / (64/1) = 63 / 64 = 98.44 %
```

La medición de `cachegrind` en la fase 2 lo confirma con exactitud:
12 441 606 lecturas / 64 = 194 400 líneas, y se midieron 194 404 fallos
(1.56 % de fallos, 98.4 % de aciertos). En la fase 1, al saltar de fila
en fila, cada píxel cae en una línea nueva: de los 64 bytes que trae el
bus se usan 3 y se desperdician 61 (95 %).

### Pregunta 2 — Localidad temporal y registros

*En la Fase 3, ¿qué ventaja física representa almacenar el operando
constante en un registro de la FPU/ALU en lugar de releerlo desde la
memoria en cada paso del bucle interior?*

`alpha` y `1 − alpha` no cambian en todo el bucle interior, pero en la
versión naive se "calculan" en cada byte. Un registro está **dentro del
núcleo**: se lee en el mismo ciclo en que se usa, sin pasar por el bus,
sin buscar en la caché y sin ocupar un puerto de carga. Releerlo desde
memoria cuesta como mínimo un acierto en L1 (unos 4–5 ciclos) y, si la
línea fue desalojada, cientos de ciclos hasta la RAM; además compite
con las cargas de los píxeles por el ancho de banda de L1. En el
benchmark, la fase 3 baja las instrucciones de 103.7 M a 93.3 M (−10 %)
porque también deja de recalcular la dirección `y·STRIDE + x·3 + c`
por byte: los punteros a la fila viven en registros. El tiempo casi no
cambia (8.74 → 8.52 ms) porque `-O1` ya aplica *loop-invariant code
motion*: el compilador había sacado `alpha` a un registro solo, y
`register` hace explícito lo que ya pasaba. Igual que en el producto de
matrices de la guía, la ventaja física existe; lo que muestra la medida
es que el compilador ya la estaba aprovechando.

### Pregunta 3 — Loop unrolling e ILP

*¿Por qué el desenrollado de bucles reduce el tiempo de ejecución
incluso cuando el número total de sumas y multiplicaciones matemáticas
es exactamente el mismo?*

Porque cada iteración de un bucle no solo hace la operación útil:
también incrementa el contador, lo compara con el límite y salta. Al
procesar 4 bytes por iteración esa sobrecarga se paga una vez cada 4
bytes en lugar de una vez por byte, y las 4 operaciones son
independientes entre sí, así que el procesador superescalar puede
tenerlas en vuelo a la vez en distintos pipelines (paralelismo a nivel
de instrucción) y el predictor de saltos tiene 4 veces menos saltos que
acertar. En el benchmark se ve en las instrucciones ejecutadas: de
103.7 M (fase 2) a 80.9 M (fase 4), −22 %, con las mismas 4 FLOP por
byte. El tiempo, sin embargo, no bajó (8.74 → 8.80 ms). La razón es
que el bucle de la mezcla está limitado por la **latencia de la FPU**,
no por la cantidad de instrucciones: cada byte pasa por
`cvtsi2ss` (entero → float), dos `mulss`, dos `addss` y `cvttss2si`
(float → entero), y con `-O1` el compilador no vectoriza, así que
desenrollar no acorta esa cadena. En el producto de matrices de la guía
las operaciones dominantes son multiplicar-acumular en `float` puro,
sin conversiones, y ahí el unrolling sí se traduce en tiempo. Con `-O3`
el compilador convertiría el bucle desenrollado en instrucciones SIMD
que mezclan 16–32 bytes por instrucción, que es justamente lo que hace
OpenCV por dentro.

### Pregunta 4 — Validación de determinismo

*¿Por qué el valor del checksum debe ser idéntico en todas las fases?
¿Qué indicaría si el checksum de la última fase difiere del de la
Fase 1?*

Porque las cinco fases calculan **la misma función sobre los mismos
datos**: la misma fórmula, en el mismo tipo (`float`), sobre el mismo
frame inicial y el mismo rectángulo. Lo único que cambia es en qué
orden se visitan los bytes y dónde viven los operandos; nada de eso
altera el resultado matemático de cada byte, así que la suma de todos
los bytes del frame final (7.4670 × 10⁸) tiene que coincidir bit a bit.
La optimización cambia el tiempo, no la respuesta.

Si el checksum de la fase 5 fuera distinto al de la fase 1, la versión
"solo ROI" estaría produciendo una imagen distinta, es decir, sería un
**bug y no una optimización**. Las causas posibles serían: un error de
límites en el rectángulo (por ejemplo olvidar que `cv2.rectangle` con
grosor −1 incluye la esquina `(x2, y2)`, por lo que faltaría una fila y
una columna), o que fuera del rectángulo la mezcla no fuera exactamente
la identidad. Esto último no pasa porque 0.75 y 0.25 son fracciones
binarias exactas: `src·0.25 + src·0.75 + 0.5` da `src + 0.5` sin error
de redondeo y la conversión a entero devuelve `src`. Con un `alpha`
como 0.45, que no es exacto en binario, la mezcla fuera del rectángulo
podría diferir en ±1 en algún byte y el checksum lo delataría. Por eso
el checksum es la prueba de que en el juego la versión optimizada
dibuja exactamente lo mismo que la original; `Proyecto/medir_overlay.py`
hace la misma comprobación píxel a píxel en Python.

## 7. Conclusión

El principio que más rinde en el juego no es una técnica de bucles
sino no tocar memoria que no hace falta: mezclar solo el rectángulo da
40x frente a 1.75x de arreglar la localidad. Con 6–8 paneles por frame,
la versión original gasta entre 50 y 120 ms por frame solo en
`overlay_rect` (recorrido naive) o 50–70 ms (recorrido por filas, que
es lo que hace OpenCV); la optimizada, 2–3 ms. Eso libera tiempo de CPU
para la inferencia de YOLO, que es el verdadero trabajo del juego.

> 🖼️ Capturas de la terminal de la laptop del proyecto (ejecución del
> benchmark, `perf stat` y `medir_overlay.py`): en los comentarios de
> el issue #22.
