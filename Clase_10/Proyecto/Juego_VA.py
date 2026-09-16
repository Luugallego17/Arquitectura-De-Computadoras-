import random
import time
import tkinter as tk
import cv2
import numpy as np
from ultralytics import YOLO

# ============================================================
# PALETA GIRLY (BGR)
# ============================================================
ROSA       = (180, 105, 255)
MAGENTA    = (255,   0, 255)
LILA       = (211,   0, 148)
ROSA_CLARO = (200, 180, 255)
DORADO     = (0,   215, 255)
BLANCO     = (255, 255, 255)
NEGRO      = (0,     0,   0)
ROJO       = (80,   40, 220)

# ============================================================
# FUNCIONES DECORATIVAS
# ============================================================

def draw_heart(frame, cx, cy, size, color, filled=True):
    r = size // 2
    cv2.circle(frame, (cx - r // 2, cy - r // 4), r // 2, color, -1 if filled else 2)
    cv2.circle(frame, (cx + r // 2, cy - r // 4), r // 2, color, -1 if filled else 2)
    pts = np.array([
        [cx - r, cy - r // 4],
        [cx + r, cy - r // 4],
        [cx,     cy + r     ]
    ], dtype=np.int32)
    cv2.fillPoly(frame, [pts], color)


def draw_sparkle(frame, x, y, size, color):
    s = size
    pts_list = [
        [(x, y - s), (x + s//4, y - s//4), (x, y), (x - s//4, y - s//4)],
        [(x + s, y), (x + s//4, y + s//4), (x, y), (x + s//4, y - s//4)],
        [(x, y + s), (x - s//4, y + s//4), (x, y), (x + s//4, y + s//4)],
        [(x - s, y), (x - s//4, y - s//4), (x, y), (x - s//4, y + s//4)],
    ]
    for pts in pts_list:
        cv2.fillPoly(frame, [np.array(pts, dtype=np.int32)], color)


def overlay_rect(frame, x1, y1, x2, y2, color, alpha=0.45):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_decorative_border(frame, h, w, t):
    cv2.rectangle(frame, (4, 4), (w - 5, h - 5), ROSA, 2)
    size = 22 + int(4 * abs(np.sin(t * 2)))
    corners = [(40, 40), (w - 40, 40), (40, h - 40), (w - 40, h - 40)]
    colors  = [ROSA, MAGENTA, LILA, ROSA_CLARO]
    for (cx, cy), col in zip(corners, colors):
        draw_heart(frame, cx, cy, size, col)
    for sx, sy in [(w//2, 15), (w//2, h-15), (15, h//2), (w-15, h//2)]:
        draw_sparkle(frame, sx, sy, 8, DORADO)


def draw_girly_text(frame, text, x, y, scale=1.0, color=ROSA, thickness=2, shadow=True):
    font = cv2.FONT_HERSHEY_SIMPLEX
    if shadow:
        cv2.putText(frame, text, (x + 2, y + 2), font, scale, (60, 20, 80), thickness + 1)
    cv2.putText(frame, text, (x, y), font, scale, color, thickness)


def draw_score_panel(frame, label, score, x, y, color):
    overlay_rect(frame, x, y, x + 180, y + 100, (40, 10, 60), alpha=0.6)
    cv2.rectangle(frame, (x, y), (x + 180, y + 100), color, 2)
    draw_girly_text(frame, label, x + 15, y + 35, 0.9, color)
    draw_girly_text(frame, str(score), x + 15, y + 80, 2.2, BLANCO)
    hx = x + 110
    for i in range(min(score, 5)):
        draw_heart(frame, hx + i * 16, y + 20, 12, color)


# ============================================================
# CONFIGURACION DEL JUEGO
# ============================================================

TRADUCCION = {
    'bottle':      'Botella',
    'cup':         'Vaso',
    'fork':        'Tenedor',
    'spoon':       'Cuchara',
    'cell phone':  'Celular',
    'remote':      'Control remoto',
    'book':        'Cuaderno',
    'scissors':    'Tijeras',
    'clock':       'Reloj',
    'teddy bear':  'Oso de peluche',
    'toothbrush':  'Cepillo de dientes',
    'sports ball': 'Pelota',
}

OBJETOS_AULA  = list(TRADUCCION.keys())
_cola_objetos = []   # cola barajada — garantiza que todos se usen

def siguiente_objeto():
    """Saca el siguiente objeto de la cola barajada.
    Cuando se agota, rellena con todos los objetos y vuelve a barajar."""
    global _cola_objetos
    if not _cola_objetos:
        nuevo_bloque = OBJETOS_AULA.copy()
        random.shuffle(nuevo_bloque)
        _cola_objetos.extend(nuevo_bloque)
    return _cola_objetos.pop(0)


# ============================================================
# INICIALIZACION
# ============================================================
model = YOLO('yolov8n.pt')

# ✅ FIX 1: Filtrar inferencia — solo detectar las clases del juego
# Esto evita que YOLO procese las 80 clases de COCO en cada frame
CLASES_VALIDAS = [
    cid for cid, nombre in model.names.items()
    if nombre in OBJETOS_AULA
]

cap   = cv2.VideoCapture(0)

# Detectar resolucion real de la pantalla
_root = tk.Tk()
SCREEN_W = _root.winfo_screenwidth()
SCREEN_H = _root.winfo_screenheight()
_root.destroy()

window_name = "UCB - IA Experience"
cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# ── Botones ──────────────────────────────────────────────────
BTN_W,  BTN_H  = 110, 38
SKIP_W, SKIP_H = 140, 38
BTN_MARGIN     = 12

def get_btn_coords(w):
    x2 = w - BTN_MARGIN
    x1 = x2 - BTN_W
    y1 = BTN_MARGIN
    y2 = y1 + BTN_H
    return x1, y1, x2, y2

def get_skip_coords(w):
    ex1, ey1, ex2, ey2 = get_btn_coords(w)
    x2 = ex1 - 10
    x1 = x2 - SKIP_W
    y1 = BTN_MARGIN
    y2 = y1 + SKIP_H
    return x1, y1, x2, y2

def draw_exit_button(frame, w):
    x1, y1, x2, y2 = get_btn_coords(w)
    overlay_rect(frame, x1, y1, x2, y2, (20, 0, 40), alpha=0.85)
    cv2.rectangle(frame, (x1, y1), (x2, y2), ROJO, 2)
    pad = 8
    cv2.line(frame, (x1+pad, y1+pad), (x1+pad+14, y1+pad+14), BLANCO, 2)
    cv2.line(frame, (x1+pad+14, y1+pad), (x1+pad, y1+pad+14), BLANCO, 2)
    draw_girly_text(frame, "SALIR", x1+30, y2-10, 0.6, BLANCO, thickness=1, shadow=False)

def draw_skip_button(frame, w):
    x1, y1, x2, y2 = get_skip_coords(w)
    overlay_rect(frame, x1, y1, x2, y2, (20, 0, 50), alpha=0.85)
    cv2.rectangle(frame, (x1, y1), (x2, y2), DORADO, 2)
    ax, ay = x1 + 10, (y1 + y2) // 2
    cv2.arrowedLine(frame, (ax, ay),     (ax + 16, ay), DORADO, 2, tipLength=0.5)
    cv2.arrowedLine(frame, (ax + 8, ay), (ax + 24, ay), DORADO, 2, tipLength=0.5)
    draw_girly_text(frame, "SALTAR", x1+32, y2-10, 0.6, DORADO, thickness=1, shadow=False)

# Estado del juego — declarado antes del callback
salir_juego     = False
inicio_juego    = False
juego_terminado = False
_mouse_w        = [SCREEN_W]
objetivo_actual = siguiente_objeto()

def mouse_callback(event, x, y, flags, param):
    global salir_juego, objetivo_actual
    if event == cv2.EVENT_LBUTTONDOWN:
        w = _mouse_w[0]
        # Boton SALIR
        bx1, by1, bx2, by2 = get_btn_coords(w)
        if bx1 <= x <= bx2 and by1 <= y <= by2:
            salir_juego = True
        # Boton SALTAR
        if inicio_juego and not juego_terminado:
            sx1, sy1, sx2, sy2 = get_skip_coords(w)
            if sx1 <= x <= sx2 and sy1 <= y <= sy2:
                objetivo_actual = siguiente_objeto()

cv2.setMouseCallback(window_name, mouse_callback)

# Variables de juego
puntos_izq     = 0
puntos_der     = 0
tiempo_limite  = 60   # ← CAMBIA ESTE NÚMERO para ajustar la duración (en segundos)
tiempo_inicial = 0
mensaje_punto  = ""
tiempo_mensaje = 0


def reset_juego():
    global puntos_izq, puntos_der, tiempo_inicial, juego_terminado, objetivo_actual
    puntos_izq      = 0
    puntos_der      = 0
    tiempo_inicial  = time.time()
    juego_terminado = False
    objetivo_actual = siguiente_objeto()


# ============================================================
# BUCLE PRINCIPAL
# ============================================================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (SCREEN_W, SCREEN_H), interpolation=cv2.INTER_LINEAR)

    h, w, _ = frame.shape
    ahora = time.time()
    t     = ahora

    _mouse_w[0] = w

    draw_decorative_border(frame, h, w, t)
    draw_exit_button(frame, w)
    if inicio_juego and not juego_terminado:
        draw_skip_button(frame, w)

    # ----------------------------------------------------------
    # PANTALLA DE INICIO
    # ----------------------------------------------------------
    if not inicio_juego:
        overlay_rect(frame, w//2-320, h//2-120, w//2+320, h//2+120, (30,0,50), alpha=0.75)
        cv2.rectangle(frame, (w//2-320, h//2-120), (w//2+320, h//2+120), MAGENTA, 2)
        draw_heart(frame, w//2-280, h//2-80, 18, ROSA_CLARO)
        draw_heart(frame, w//2+280, h//2-80, 18, ROSA_CLARO)
        draw_girly_text(frame, "BIENVENIDAS AL JUEGO", w//2-255, h//2-20, 1.3, ROSA)
        draw_girly_text(frame, "Presiona 'S' para empezar", w//2-180, h//2+50, 0.85, ROSA_CLARO)
        pulse = int(20 + 6 * abs(np.sin(t * 1.5)))
        draw_heart(frame, w//2, h//2-90, pulse, MAGENTA)

    # ----------------------------------------------------------
    # PANTALLA FINAL
    # ----------------------------------------------------------
    elif juego_terminado:
        overlay_rect(frame, w//2-320, h//2-120, w//2+320, h//2+120, (30,0,50), alpha=0.8)
        cv2.rectangle(frame, (w//2-320, h//2-120), (w//2+320, h//2+120), DORADO, 2)

        if puntos_izq > puntos_der:
            msg, winner_color = "GANO EQUIPO A!", ROSA
        elif puntos_der > puntos_izq:
            msg, winner_color = "GANO EQUIPO B!", LILA
        else:
            msg, winner_color = "EMPATE!",        DORADO

        draw_girly_text(frame, msg, w//2-180, h//2, 1.6, winner_color)
        draw_girly_text(frame, f"A: {puntos_izq}  vs  B: {puntos_der}", w//2-140, h//2+55, 0.95, BLANCO)
        draw_girly_text(frame, "Presiona 'R' para reiniciar", w//2-200, h//2+95, 0.7, ROSA_CLARO)

        for _ in range(5):
            rx = random.randint(60, w-60)
            ry = random.randint(60, h-60)
            draw_heart(frame, rx, ry, random.randint(10, 22),
                       random.choice([ROSA, MAGENTA, LILA, ROSA_CLARO]))

    # ----------------------------------------------------------
    # JUEGO ACTIVO
    # ----------------------------------------------------------
    else:
        tiempo_restante = max(0, int(tiempo_limite - (ahora - tiempo_inicial)))
        if tiempo_restante == 0:
            juego_terminado = True

        # ✅ FIX 2: Inferencia solo sobre las clases del juego (más rápido y preciso)
        results = model(frame, stream=True, conf=0.5, verbose=False, classes=CLASES_VALIDAS)

        e_izq, e_der = set(), set()

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label_en = model.names[int(box.cls[0])]
                cx_box   = (x1 + x2) // 2

                if label_en == objetivo_actual:
                    label_es = TRADUCCION.get(label_en, label_en)
                    is_left  = cx_box < w // 2
                    color    = ROSA if is_left else LILA

                    if is_left:
                        e_izq.add(label_en)
                    else:
                        e_der.add(label_en)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                    (tw, th_), _ = cv2.getTextSize(label_es, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                    overlay_rect(frame, x1, y1-th_-14, x1+tw+10, y1, (30,0,60), alpha=0.7)
                    draw_girly_text(frame, label_es, x1+5, y1-8, 0.7, color, thickness=2, shadow=False)
                    draw_heart(frame, x2-12, y1+12, 14, color)

        # ✅ FIX 3: Lógica "gana el primero en mostrar"
        # El cooldown de 2s evita puntos dobles por el mismo objeto.
        # if/elif garantiza que solo UN equipo puntúa por ronda:
        #   - Si izquierda muestra el objeto → punto para A (aunque derecha también lo muestre)
        #   - Solo si izquierda NO lo muestra → se evalúa derecha
        if ahora - tiempo_mensaje > 2:
            if e_izq:
                puntos_izq     += 1
                mensaje_punto   = "PUNTO EQUIPO A!"
                tiempo_mensaje  = ahora
                objetivo_actual = siguiente_objeto()
            elif e_der:
                puntos_der     += 1
                mensaje_punto   = "PUNTO EQUIPO B!"
                tiempo_mensaje  = ahora
                objetivo_actual = siguiente_objeto()

        # ---------- INTERFAZ ----------
        cv2.line(frame, (w//2, 0), (w//2, h), ROSA, 2)
        draw_sparkle(frame, w//2, h//2, 10, MAGENTA)

        draw_score_panel(frame, "EQUIPO A", puntos_izq, 20, 15, ROSA)
        draw_score_panel(frame, "EQUIPO B", puntos_der, w-200, 15, LILA)

        # Temporizador
        tiempo_txt = f"TIEMPO: {tiempo_restante}s"
        overlay_rect(frame, w//2-130, 10, w//2+130, 65, (30,0,60), alpha=0.7)
        cv2.rectangle(frame, (w//2-130, 10), (w//2+130, 65), DORADO, 2)
        draw_girly_text(frame, tiempo_txt, w//2-110, 52, 1.1, DORADO, thickness=2)

        # ---------- PANEL DE OBJETIVO ----------
        obj_nombre = TRADUCCION[objetivo_actual]
        obj_txt    = f"Encuentra:  {obj_nombre}"
        (ow, _), _ = cv2.getTextSize(obj_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.85, 2)
        ox = (w - ow) // 2
        overlay_rect(frame, ox-20, h-75, ox+ow+20, h-10, (30,0,60), alpha=0.75)
        cv2.rectangle(frame, (ox-20, h-75), (ox+ow+20, h-10), MAGENTA, 2)
        draw_girly_text(frame, obj_txt, ox, h-32, 0.85, ROSA_CLARO)
        draw_heart(frame, ox-32,    h-44, 18, MAGENTA)
        draw_heart(frame, ox+ow+30, h-44, 18, MAGENTA)

        # ---------- MENSAJE DE PUNTO ----------
        if ahora - tiempo_mensaje < 1.8:
            pulse_s   = 1.2 + 0.3 * abs(np.sin((ahora - tiempo_mensaje) * 8))
            msg_color = ROSA if "A" in mensaje_punto else LILA
            draw_girly_text(frame, mensaje_punto, w//2-200, h//2, pulse_s, msg_color, thickness=3)
            for i in range(7):
                angle = (i / 7) * 2 * np.pi
                hx = int(w//2 + 80 * np.cos(angle))
                hy = int(h//2 + 80 * np.sin(angle))
                draw_heart(frame, hx, hy, 18, msg_color)

    # ----------------------------------------------------------
    cv2.imshow(window_name, frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s') and not inicio_juego:
        inicio_juego = True
        reset_juego()
    if key == ord('r') and juego_terminado:
        reset_juego()
    if key == ord('n') and inicio_juego and not juego_terminado:
        objetivo_actual = siguiente_objeto()
    if key == ord('q') or salir_juego:
        break

cap.release()
cv2.destroyAllWindows()
