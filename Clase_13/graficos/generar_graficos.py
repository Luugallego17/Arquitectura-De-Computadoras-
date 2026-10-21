#!/usr/bin/env python3
"""Genera los gráficos de la Clase 13 (SVG) con los valores medidos.

Uso: python3 generar_graficos.py
Luego se convierten a PNG con Chromium:
    chromium --headless --screenshot=salida.png --window-size=W,H archivo.svg
"""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
FIFO, SHM, SYS, USR, TXT, GRID = "#d9487d", "#2a8f7b", "#b8325f", "#f0a6c0", "#2b2b2b", "#dddddd"
FONT = "font-family='DejaVu Sans, Arial, sans-serif'"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def t(x, y, s, size=13, anchor="middle", weight="normal", fill=TXT, extra=""):
    return f"<text x='{x}' y='{y}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' fill='{fill}' {FONT} {extra}>{esc(s)}</text>"


def svg(w, h, body):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>"
            f"<rect width='{w}' height='{h}' fill='white'/>{body}</svg>")


def barras(x0, y0, w, h, titulo, etiquetas, series, colores, ymax, fmt, leyenda=None, unidad=""):
    """Gráfico de barras agrupadas. series = lista de listas (una por serie)."""
    o = [t(x0 + w / 2, y0 - 14, titulo, 15, weight="bold")]
    for k in range(5):
        v = ymax * k / 4
        y = y0 + h - h * k / 4
        o.append(f"<line x1='{x0}' y1='{y}' x2='{x0 + w}' y2='{y}' stroke='{GRID}' stroke-width='1'/>")
        o.append(t(x0 - 6, y + 4, fmt(v), 11, "end", fill="#777"))
    n, m = len(etiquetas), len(series)
    ancho_g = w / n
    bw = ancho_g * 0.7 / m
    for i, et in enumerate(etiquetas):
        gx = x0 + i * ancho_g + ancho_g * 0.15
        for j, s in enumerate(series):
            v = s[i]
            bh = h * v / ymax
            o.append(f"<rect x='{gx + j * bw}' y='{y0 + h - bh}' width='{bw - 3}' height='{bh}' fill='{colores[j]}' rx='3'/>")
            o.append(t(gx + j * bw + (bw - 3) / 2, y0 + h - bh - 6, fmt(v) + unidad, 11, weight="bold"))
        o.append(t(x0 + i * ancho_g + ancho_g / 2, y0 + h + 18, et, 12))
    if leyenda:
        lx = x0
        for c, nom in zip(colores, leyenda):
            o.append(f"<rect x='{lx}' y='{y0 + h + 34}' width='12' height='12' fill='{c}' rx='2'/>")
            o.append(t(lx + 17, y0 + h + 45, nom, 12, "start"))
            lx += 30 + 7.2 * len(nom)
    return "".join(o)


def apiladas(x0, y0, w, h, titulo, etiquetas, usr, sis, ymax):
    o = [t(x0 + w / 2, y0 - 14, titulo, 15, weight="bold")]
    for k in range(5):
        v = ymax * k / 4
        y = y0 + h - h * k / 4
        o.append(f"<line x1='{x0}' y1='{y}' x2='{x0 + w}' y2='{y}' stroke='{GRID}'/>")
        o.append(t(x0 - 6, y + 4, f"{v:.2f}", 11, "end", fill="#777"))
    n = len(etiquetas)
    ag = w / n
    bw = ag * 0.5
    for i, et in enumerate(etiquetas):
        bx = x0 + i * ag + (ag - bw) / 2
        hu, hs = h * usr[i] / ymax, h * sis[i] / ymax
        o.append(f"<rect x='{bx}' y='{y0 + h - hs}' width='{bw}' height='{hs}' fill='{SYS}' rx='3'/>")
        o.append(f"<rect x='{bx}' y='{y0 + h - hs - hu}' width='{bw}' height='{hu}' fill='{USR}' rx='3'/>")
        o.append(t(bx + bw / 2, y0 + h - hs / 2 + 4, f"kernel {sis[i]:.2f} s", 11, fill="white", weight="bold"))
        if hu > 14:
            o.append(t(bx + bw / 2, y0 + h - hs - hu / 2 + 4, f"{usr[i]:.2f} s", 11))
        else:
            o.append(t(bx + bw / 2, y0 + h - hs - hu - 6, f"usuario {usr[i]:.2f} s", 11))
        o.append(t(x0 + i * ag + ag / 2, y0 + h + 18, et, 12))
    for k, (c, nom) in enumerate([(USR, "tiempo de usuario"), (SYS, "tiempo de kernel (sys)")]):
        lx = x0 + k * 150
        o.append(f"<rect x='{lx}' y='{y0 + h + 34}' width='12' height='12' fill='{c}' rx='2'/>")
        o.append(t(lx + 17, y0 + h + 45, nom, 12, "start"))
    return "".join(o)


def guardar(nombre, w, h, cuerpo, titulo, sub):
    cab = t(w / 2, 30, titulo, 19, weight="bold") + t(w / 2, 50, sub, 12, fill="#666")
    with open(os.path.join(AQUI, nombre), "w") as f:
        f.write(svg(w, h, cab + cuerpo))


miles = lambda v: f"{v:,.0f}".replace(",", " ")

# ---------------- #31: FIFO ----------------
guardar("tarea31_fifo.svg", 900, 400,
        barras(70, 100, 360, 220, "Tiempo por repetición (s)", ["Rep. 1", "Rep. 2", "Rep. 3"],
               [[5.125, 5.089, 5.412]], [FIFO], 6, lambda v: f"{v:.2f}", ["Cons_NO (10 M paquetes)"], " s")
        + apiladas(520, 100, 340, 220, "¿Dónde se va el tiempo? (s)", ["Prod_NO", "Cons_NO"], [0.66, 0.69], [4.27, 4.21], 6),
        "Tarea #31 — Versión no optimizada (FIFO)", "10 000 000 paquetes de 64 B · 1 write() + 1 read() por paquete · más del 80 % del tiempo es kernel")

# ---------------- #32: SHM ----------------
guardar("tarea32_shm.svg", 900, 400,
        barras(70, 100, 360, 220, "Tiempo por repetición (s)", ["Rep. 1", "Rep. 2", "Rep. 3"],
               [[0.544, 0.592, 0.548], [0.481, 0.528, 0.485]], [SHM, "#7fc8b8"], 0.8, lambda v: f"{v:.2f}",
               ["Prod_OPT", "Cons_OPT"], " s")
        + apiladas(520, 100, 340, 220, "Consumidor: usuario vs kernel (s)", ["Cons_OPT"], [0.03], [0.20], 0.25),
        "Tarea #32 — Versión optimizada (memoria compartida + batching)", "10 000 000 paquetes · lotes de 500 · ≈ 22 000 futex por proceso y ninguna read/write por paquete")

# ---------------- #33: comparación ----------------
def panel(i, titulo, a, b, ymax, fmt, unidad=""):
    col, fila = i % 3, i // 3
    return barras(60 + col * 300, 110 + fila * 290, 220, 150, titulo, ["FIFO", "SHM"], [[a, b]], [FIFO], ymax, fmt, None, unidad)

cuerpo = ""
cuerpo += panel(0, "Tiempo total (s)", 5.21, 0.50, 6, lambda v: f"{v:.2f}")
cuerpo += panel(1, "Paquetes/s (millones)", 1.92, 20.1, 24, lambda v: f"{v:.1f}")
cuerpo += panel(2, "Rendimiento (MB/s)", 117, 1228, 1400, lambda v: f"{v:,.0f}".replace(",", " "))
cuerpo += panel(4, "Tiempo en kernel (s)", 4.21, 0.20, 5, lambda v: f"{v:.2f}")
# colorear la segunda barra de cada panel
cuerpo = cuerpo.replace("fill='#d9487d' rx='3'/><text", "fill='#d9487d' rx='3'/><text")
# syscalls en escala logarítmica (panel 3)
x0, y0, w, h = 60, 400, 220, 150
import math
o = [t(x0 + w / 2, y0 - 14, "Syscalls (escala log)", 15, weight="bold")]
for k, v in enumerate([1e3, 1e4, 1e5, 1e6, 1e7, 1e8]):
    y = y0 + h - h * k / 5
    o.append(f"<line x1='{x0}' y1='{y}' x2='{x0 + w}' y2='{y}' stroke='{GRID}'/>")
    o.append(t(x0 - 6, y + 4, {1e3: "1 k", 1e4: "10 k", 1e5: "100 k", 1e6: "1 M", 1e7: "10 M", 1e8: "100 M"}[v], 11, "end", fill="#777"))
for i, (nom, v, c) in enumerate([("FIFO", 20_000_000, FIFO), ("SHM", 44_000, SHM)]):
    bh = h * (math.log10(v) - 3) / 5
    bx = x0 + 30 + i * 100
    o.append(f"<rect x='{bx}' y='{y0 + h - bh}' width='70' height='{bh}' fill='{c}' rx='3'/>")
    o.append(t(bx + 35, y0 + h - bh - 6, miles(v), 11, weight="bold"))
    o.append(t(bx + 35, y0 + h + 18, nom, 12))
cuerpo += "".join(o)
# mejora medida vs esperada
x0, y0, w, h = 60 + 600, 400, 220, 150
o = [t(x0 + w / 2, y0 - 14, "Mejora de tiempo (×)", 15, weight="bold")]
for k in range(5):
    v = 60 * k / 4
    y = y0 + h - h * k / 4
    o.append(f"<line x1='{x0}' y1='{y}' x2='{x0 + w}' y2='{y}' stroke='{GRID}'/>")
    o.append(t(x0 - 6, y + 4, f"{v:.0f}", 11, "end", fill="#777"))
bh = h * 10.5 / 60
o.append(f"<rect x='{x0 + 25}' y='{y0 + h - bh}' width='70' height='{bh}' fill='{SHM}' rx='3'/>")
o.append(t(x0 + 60, y0 + h - bh - 6, "10.5×", 11, weight="bold"))
o.append(t(x0 + 60, y0 + h + 18, "medida", 12))
yb, yt = y0 + h - h * 50 / 60, y0 + h - h * 30 / 60
o.append(f"<rect x='{x0 + 125}' y='{yb}' width='70' height='{yt - yb}' fill='none' stroke='{FIFO}' stroke-width='2' stroke-dasharray='5 3' rx='3'/>")
o.append(t(x0 + 160, (yb + yt) / 2 + 4, "30–50×", 11, weight="bold"))
o.append(t(x0 + 160, y0 + h + 18, "esperada", 12))
cuerpo += "".join(o)
guardar("tarea33_comparacion.svg", 900, 620, cuerpo, "Tarea #33 — FIFO vs memoria compartida",
        "Promedio de 3 repeticiones · 10 000 000 paquetes de 64 B · gcc -O3 · 4 núcleos lógicos")

# ---------------- #34: diagrama de los caminos ----------------
def caja(x, y, w, h, txt, fill, tc="white"):
    lineas = txt.split("\n")
    s = f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='{fill}' rx='8'/>"
    for i, l in enumerate(lineas):
        s += t(x + w / 2, y + h / 2 + 4 + (i - (len(lineas) - 1) / 2) * 16, l, 12, fill=tc, weight="bold" if i == 0 else "normal")
    return s

def flecha(x1, y1, x2, y2, txt="", c="#555"):
    s = f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{c}' stroke-width='2.5' marker-end='url(#p)'/>"
    if txt:
        s += t((x1 + x2) / 2, (y1 + y2) / 2 - 7, txt, 11, fill=c)
    return s

defs = "<defs><marker id='p' markerUnits='userSpaceOnUse' markerWidth='12' markerHeight='12' refX='10' refY='6' orient='auto'><path d='M0,0 L12,6 L0,12 z' fill='#555'/></marker></defs>"
c = defs
c += t(450, 92, "NO optimizada: cada paquete (64 B) cruza al kernel y se copia dos veces", 14, weight="bold", fill=FIFO)
c += caja(40, 110, 150, 60, "Prod_NO\nespacio de usuario", "#7a7a7a")
c += caja(375, 100, 150, 80, "KERNEL\nbuffer del pipe (64 KiB)", FIFO)
c += caja(710, 110, 150, 60, "Cons_NO\nespacio de usuario", "#7a7a7a")
c += flecha(190, 140, 375, 140, "write() ×10 M · copia 1") + flecha(525, 140, 710, 140, "read() ×10 M · copia 2")
c += t(450, 205, "20 000 000 syscalls · ≈ 4.2 s de CPU en modo kernel por proceso", 12, fill="#555")

c += t(450, 262, "Optimizada: ambos procesos ven las mismas páginas físicas; se sincroniza 1 vez cada 500 paquetes", 14, weight="bold", fill=SHM)
c += caja(40, 285, 150, 60, "Prod_OPT\nespacio de usuario", "#7a7a7a")
c += caja(355, 275, 190, 80, "RAM compartida (mmap)\nlote de 500 × 64 B", SHM)
c += caja(710, 285, 150, 60, "Cons_OPT\nespacio de usuario", "#7a7a7a")
c += flecha(190, 315, 355, 315, "escribe el lote") + flecha(545, 315, 710, 315, "lee el lote")
c += f"<path d='M110,285 C110,255 360,255 400,275' fill='none' stroke='{SHM}' stroke-width='0'/>"
c += caja(190, 385, 190, 40, "sem_post(sem_read)", "#7fc8b8", TXT) + caja(520, 385, 190, 40, "sem_post(sem_write)", "#7fc8b8", TXT)
c += flecha(285, 385, 285, 357, "", SHM) + flecha(615, 385, 615, 357, "", SHM)
c += t(450, 455, "20 000 lotes · ≈ 44 000 futex en total (−99.78 % de syscalls) · ≈ 0.2 s de CPU en modo kernel", 12, fill="#555")
guardar("tarea34_mecanismo.svg", 900, 480, c, "Tarea #34 — Por qué la memoria compartida es más rápida",
        "Camino de los datos en cada versión")
print("SVG generados")
