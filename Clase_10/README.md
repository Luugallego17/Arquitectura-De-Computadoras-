# Clase 10 — Optimización en la jerarquía de memoria (aplicada al juego con YOLO)

**Fecha:** 16/09/2026
**Tareas:**

- [#21 — Verificación del hardware: jerarquía de caché y línea de 64 bytes (`lscpu`, `getconf`, sysfs)](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/21)
- [#22 — Benchmark en ANSI C del juego con YOLO: `overlay_rect` sobre un frame Full HD con 4 fases de optimización](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/22)
- [#23 — Ejecución del benchmark del juego y análisis de fallos de caché con `perf`](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/23)
- [#24 — Informe del laboratorio: cuestionario de análisis crítico y entrega](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/24)

Guía de laboratorio: *Optimización en la Jerarquía de Memoria — Análisis
empírico de líneas de caché (64 B), registros de CPU y paralelismo ILP
en Linux*. La guía propone medir un producto de matrices; aquí las
mismas cuatro fases (naive, localidad espacial, registros y loop
unrolling) se aplican a una operación real de mi proyecto: el juego
**"UCB - IA Experience"**, que detecta objetos del aula con la webcam
usando YOLOv8 y dibuja toda la interfaz con OpenCV.

## El proyecto: `Proyecto/Juego_VA.py`

Dos equipos compiten mostrando a la cámara el objeto que pide la
pantalla (botella, vaso, celular, tijeras...). YOLOv8 (`yolov8n.pt`)
detecta el objeto; si aparece en la mitad izquierda puntúa el equipo A
y si aparece en la derecha, el equipo B. Cada frame de la cámara se
voltea, se escala a la resolución de la pantalla (típicamente
1920×1080) y se decora con paneles semitransparentes, corazones,
marcador y temporizador.

El punto que conecta con el laboratorio es la función que pinta esos
paneles:

```python
def overlay_rect(frame, x1, y1, x2, y2, color, alpha=0.45):
    overlay = frame.copy()                                   # copia TODO el frame (6.2 MB)
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)    # pinta un rectángulo en la copia
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)  # mezcla TODO el frame
```

Para pintar un panel de unos cientos de píxeles se copian y se mezclan
los 1920 × 1080 × 3 = **6 220 800 bytes** del frame completo, y esto
pasa **entre 6 y 8 veces por frame** (paneles de marcador, temporizador,
objetivo, botones, etiquetas de detección...). Fuera del rectángulo la
copia es idéntica al frame, así que la mezcla no cambia ni un byte:
es tráfico de memoria desperdiciado. Exactamente lo que el laboratorio
llama "desaprovechar la transferencia".

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`verificacion_hardware.md`](verificacion_hardware.md) | Tarea #21: qué hace cada comando de verificación previa, las salidas del equipo y por qué una línea de 64 bytes guarda 16 `float` (o 64 bytes de píxel). |
| [`verificar_hardware.sh`](verificar_hardware.sh) | Script que corre los tres comandos de la guía y calcula cuántos `float` caben en una línea de caché. |
| [`benchmark_juego.c`](benchmark_juego.c) | Tarea #22: el benchmark en ANSI C. Reproduce `overlay_rect()` sobre un frame Full HD en las cuatro fases de la guía más una quinta con la optimización real del juego (solo la región), con tiempo, ms por frame, GB/s, speedup y checksum. |
| [`Proyecto/Juego_VA.py`](Proyecto/Juego_VA.py) | El juego original, tal como se entregó. |
| [`Proyecto/Juego_VA_optimizado.py`](Proyecto/Juego_VA_optimizado.py) | El juego con `overlay_rect()` optimizada: mezcla solo la región del rectángulo sin copiar el frame. Es el único cambio. |
| [`Proyecto/medir_overlay.py`](Proyecto/medir_overlay.py) | Mide en Python (numpy + OpenCV, sin cámara ni YOLO) la `overlay_rect()` original vs la optimizada y verifica que el frame resultante sea idéntico. Para correrlo en la laptop del juego. |
| [`Proyecto/yolov8n.pt`](Proyecto/yolov8n.pt) | Pesos del modelo YOLOv8 nano que usa el juego. |

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

## Parte 2 — Benchmark en ANSI C del juego (tarea #22)

[`benchmark_juego.c`](benchmark_juego.c) hace en C lo mismo que
`overlay_rect()`: sobre un frame de 1920×1080×3 bytes (`uint8`, BGR,
igual que OpenCV) pinta el panel de bienvenida del juego (640×240 px,
color `(30, 0, 50)`, `alpha = 0.75`) 30 veces, como si fueran 30 frames.
La mezcla es la misma fórmula en todas las fases, en punto fijo de 8
bits para que el resultado sea determinístico:

```
dst = (src · (256 − a) + overlay · a + 128) >> 8        con a = round(0.75 · 256) = 192
```

| Fase | Función | Qué cambia | Por qué mejora |
|------|---------|------------|----------------|
| 1. Naive (por columnas) | `fase1_naive` | Copia el frame, pinta el rectángulo y mezcla **todo** el frame recorriéndolo por columnas (`x` afuera, `y` adentro): cada paso salta una fila entera, **5760 bytes**. | No mejora: cada acceso cae en una línea de caché distinta; de los 64 bytes que trae el bus se usan 3 (un píxel) y el resto se desperdicia. Es el `i-j-k` de la guía. |
| 2. Localidad espacial (por filas) | `fase2_localidad_espacial` | Lo mismo, pero recorriendo por filas (`y` afuera, `x` adentro): los bytes se leen contiguos. | Cada línea de 64 bytes se usa completa: 1 fallo de caché cada 64 bytes de píxel. |
| 3. Localidad temporal + registros | `fase3_registros_cpu` | El alpha en punto fijo (`a` y `256 − a`) se calcula **una sola vez** y se guarda en `register const int`; se usan punteros a la fila actual en vez de recalcular `y·STRIDE + x·3 + c` por byte. | Los operandos repetidos viven en registros de la CPU; el bucle interno solo lee el píxel, la capa y escribe el resultado. |
| 4. Loop unrolling 4x + ILP | `fase4_loop_unrolling` | El bucle interno procesa 4 bytes por iteración. | Menos saltos y comparaciones por byte, y cuatro operaciones independientes que el procesador superescalar ejecuta en paralelo. |
| 5. Solo ROI (el juego optimizado) | `fase5_roi` | Ni copia ni mezcla el frame completo: solo recorre los 640×240×3 bytes del rectángulo y mezcla con el color directamente (`color · a + 128` precalculado por canal). | Toca 27 veces menos memoria. Es lo que hace `Juego_VA_optimizado.py`. |

Las fases 1 a 4 incluyen en el tiempo la copia del frame y el pintado
del rectángulo (el `frame.copy()` y `cv2.rectangle` del juego), porque
son parte del costo real de la función original. La fase 5 no los
necesita.

El programa además:

- mide cada fase con `clock_gettime(CLOCK_MONOTONIC)`;
- reporta ms por frame (lo que tarda **una** llamada a `overlay_rect`) y
  el ancho de banda efectivo en GB/s;
- calcula el **speedup** `S = T_base / T_opt` tomando la fase 1 como base;
- valida con un **checksum** (la suma de todos los bytes del frame
  final) que las cinco fases producen exactamente la misma imagen.

## Cómo compilar y ejecutar

```bash
# Parte 1 — verificación del hardware
bash verificar_hardware.sh

# Parte 2 — benchmark del juego (flags oficiales de la guía)
gcc -Wall -Wextra -O1 benchmark_juego.c -o benchmark_juego -lm
./benchmark_juego

# Medir overlay_rect original vs optimizada en Python (necesita numpy y opencv)
python3 Proyecto/medir_overlay.py

# El juego (necesita webcam, opencv-python y ultralytics)
cd Proyecto && python3 Juego_VA_optimizado.py
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

### Parte 2 — `benchmark_juego`

Compila sin ninguna advertencia con `-Wall -Wextra`. Salida en el mismo
equipo de la Parte 1 (Intel Xeon @ 2.80 GHz, 4 núcleos):

```
=== RESULTADOS DETERMINISTICOS: overlay_rect sobre 1920x1080x3, 30 frames ===
Frame: 6.2 MB | Rectangulo: 640x240 px | Linea de cache: 64 B = 64 bytes de pixel

1. Naive (por columnas)      :  0.4329 s |   14.43 ms/frame |   0.86 GB/s | Speedup:   1.00x
2. Localidad Espacial (filas):  0.1918 s |    6.39 ms/frame |   1.95 GB/s | Speedup:   2.26x
3. Registros de CPU          :  0.1477 s |    4.92 ms/frame |   2.53 GB/s | Speedup:   2.93x
4. Loop Unrolling 4x (ILP)   :  0.0983 s |    3.28 ms/frame |   3.80 GB/s | Speedup:   4.41x
5. Solo ROI (juego optimiz.) :  0.0052 s |    0.17 ms/frame |   2.63 GB/s | Speedup:  82.50x

[OK] Validacion de Checksum: 7.4670e+08
     Fase 2 vs Fase 1: Error = 0.0000e+00
     Fase 3 vs Fase 1: Error = 0.0000e+00
     Fase 4 vs Fase 1: Error = 0.0000e+00
     Fase 5 vs Fase 1: Error = 0.0000e+00
```

Lo que se ve:

- Recorrer el frame por filas en vez de por columnas (fase 2) hace el
  mismo trabajo **2.3 veces más rápido** sin cambiar ni una operación:
  es la línea de caché de 64 bytes de la Parte 1 usándose completa en
  vez de desperdiciar 61 de sus 64 bytes en cada acceso.
- Sacar el cálculo del alpha y las direcciones a registros (fase 3) suma
  otro 1.3x, y el unrolling (fase 4) otro 1.5x: en total **4.4x** sobre
  la versión naive, todavía tocando los 6.2 MB completos.
- La fase 5 es la lección grande para el proyecto: la memoria más rápida
  es la que **no se toca**. Mezclar solo el rectángulo tarda 0.17 ms en
  vez de 14.43 ms (**82.5x**). Con 6–8 paneles por frame, la versión
  original gasta unos 40–100 ms de puro `overlay_rect` por frame en la
  fase naive (menos de 25 fps solo por los paneles); la optimizada, ~1 ms.
- El **error del checksum es 0** en las cinco fases: la imagen final es
  idéntica. Se optimizó el tiempo, no el resultado.

### El cambio en el juego

`Juego_VA_optimizado.py` es el juego original con una sola función
distinta:

```python
def overlay_rect(frame, x1, y1, x2, y2, color, alpha=0.45):
    h, w = frame.shape[:2]
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2 + 1), min(h, y2 + 1)   # cv2.rectangle incluye la esquina (x2, y2)
    if x2 <= x1 or y2 <= y1:
        return
    roi  = frame[y1:y2, x1:x2]                 # solo la región del rectángulo
    capa = np.empty_like(roi)
    capa[:] = color
    roi[:] = cv2.addWeighted(capa, alpha, roi, 1 - alpha, 0)
```

`Proyecto/medir_overlay.py` corre las dos versiones sobre el mismo frame
sintético que usa el benchmark en C y comprueba con `np.array_equal`
que el resultado es idéntico píxel a píxel. Necesita `numpy` y
`opencv-python`, que no están en el entorno donde se compiló el
benchmark, así que su medición se hace en la laptop del proyecto
(tarea #23).

El análisis de fallos de caché con `perf`/`cachegrind` y la tabla de
métricas completa quedan para la tarea #23.
