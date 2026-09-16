"""Mide overlay_rect() original vs optimizada sobre un frame Full HD.

No usa la cámara ni YOLO: solo numpy y OpenCV, para poder correrlo en
cualquier laptop con el entorno del juego instalado:

    python3 medir_overlay.py

Imprime el tiempo por llamada de cada versión, el speedup y verifica que
las dos produzcan exactamente el mismo frame.
"""
import time
import cv2
import numpy as np

ANCHO, ALTO = 1920, 1080          # SCREEN_W x SCREEN_H del juego
REPETICIONES = 200
# Panel de bienvenida del juego: (w/2-320, h/2-120) a (w/2+320, h/2+120)
X1, Y1, X2, Y2 = ANCHO//2 - 320, ALTO//2 - 120, ANCHO//2 + 320, ALTO//2 + 120
COLOR, ALPHA = (30, 0, 50), 0.75


def overlay_rect_original(frame, x1, y1, x2, y2, color, alpha=0.45):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def overlay_rect_optimizada(frame, x1, y1, x2, y2, color, alpha=0.45):
    h, w = frame.shape[:2]
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2 + 1), min(h, y2 + 1)
    if x2 <= x1 or y2 <= y1:
        return
    roi  = frame[y1:y2, x1:x2]
    capa = np.empty_like(roi)
    capa[:] = color
    roi[:] = cv2.addWeighted(capa, alpha, roi, 1 - alpha, 0)


def medir(fn, base):
    frame = base.copy()
    t0 = time.perf_counter()
    for _ in range(REPETICIONES):
        fn(frame, X1, Y1, X2, Y2, COLOR, ALPHA)
    t = (time.perf_counter() - t0) / REPETICIONES
    return t, frame


if __name__ == "__main__":
    ys, xs = np.mgrid[0:ALTO, 0:ANCHO]
    base = np.empty((ALTO, ANCHO, 3), dtype=np.uint8)
    for c in range(3):
        base[:, :, c] = (xs * 7 + ys * 13 + c * 31) % 256   # mismo patrón que benchmark_juego.c

    t_orig, f_orig = medir(overlay_rect_original, base)
    t_opt,  f_opt  = medir(overlay_rect_optimizada, base)

    print(f"\n=== overlay_rect sobre {ANCHO}x{ALTO}x3, {REPETICIONES} repeticiones ===")
    print(f"Original  (copia + mezcla de todo el frame): {t_orig*1000:8.3f} ms/llamada | Speedup: 1.00x")
    print(f"Optimizada (solo la region del rectangulo) : {t_opt*1000:8.3f} ms/llamada | Speedup: {t_orig/t_opt:.2f}x")
    iguales = np.array_equal(f_orig, f_opt)
    print(f"[{'OK' if iguales else 'ERROR'}] Frames identicos pixel a pixel: {iguales}")
    if not iguales:
        print("     Bytes distintos:", int(np.count_nonzero(f_orig != f_opt)))
