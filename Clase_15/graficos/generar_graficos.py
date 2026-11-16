#!/usr/bin/env python3
"""Genera los gráficos de la Clase 15 (SVG y PNG) a partir de los scripts.

Importa cada laboratorio y lo ejecuta con su semilla. Los conteos del dibujo
son los que devuelve Aer; no hay valores escritos a mano.

Uso: python3 generar_graficos.py
Los PNG necesitan node y playwright (Chromium, o Chrome del sistema).
"""
import math
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.dirname(AQUI)
sys.path.insert(0, CARPETA)

import lab1_hola_mundo as lab1
import lab2_rotaciones_bloch as lab2
import lab3_algoritmo_deutsch as lab3
import lab4_teletransportacion as lab4

ROSA, VERDE, OSC, CLARO, TXT, GRID, GRIS = "#d9487d", "#2a8f7b", "#b8325f", "#f0a6c0", "#2b2b2b", "#dddddd", "#7a7a7a"
FONT = "font-family='DejaVu Sans, Arial, sans-serif'"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size=13, anchor="middle", weight="normal", fill=TXT):
    return (
        f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' "
        f"font-weight='{weight}' fill='{fill}' {FONT}>{esc(s)}</text>"
    )


def guardar(nombre, w, h, cuerpo, titulo, sub):
    cab = t(w / 2, 28, titulo, 18, weight="bold") + t(w / 2, 48, sub, 12, fill="#666")
    with open(os.path.join(AQUI, nombre), "w") as f:
        f.write(
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>"
            f"<rect width='{w}' height='{h}' fill='white'/>{cab}{cuerpo}</svg>"
        )


def eje_y(x0, y0, w, h, ymax, paso, fmt=str):
    o = []
    v = 0
    while v <= ymax + 1e-9:
        y = y0 + h - h * v / ymax
        o.append(f"<line x1='{x0}' y1='{y:.1f}' x2='{x0 + w}' y2='{y:.1f}' stroke='{GRID}'/>")
        o.append(t(x0 - 8, y + 4, fmt(v), 11, "end", fill="#777"))
        v += paso
    o.append(f"<line x1='{x0}' y1='{y0}' x2='{x0}' y2='{y0 + h}' stroke='{TXT}'/>")
    o.append(f"<line x1='{x0}' y1='{y0 + h}' x2='{x0 + w}' y2='{y0 + h}' stroke='{TXT}'/>")
    return "".join(o)


def leyenda(x, y, items):
    o = []
    cursor = x
    for color, nombre in items:
        o.append(f"<rect x='{cursor}' y='{y}' width='12' height='12' fill='{color}' rx='2'/>")
        o.append(t(cursor + 16, y + 11, nombre, 12, "start"))
        cursor += 16 + 7 * len(nombre) + 28
    return "".join(o)


def grafico_bell():
    phi = lab1.medir(lab1.construir_circuito("phi_plus"))
    psi = lab1.medir(lab1.construir_circuito("psi_plus"))
    x0, y0, w, h = 70, 80, 800, 280
    ymax = lab1.SHOTS
    o = [eje_y(x0, y0, w, h, ymax, 2000, lambda v: f"{v//1000}k" if v else "0")]
    grupo = w / 4
    ancho = grupo * 0.28
    for i, bit in enumerate(lab1.BASE):
        cx = x0 + grupo * i + grupo / 2
        for dx, counts, color in ((-ancho * 0.7, phi, ROSA), (ancho * 0.7, psi, VERDE)):
            n = counts.get(bit, 0)
            bh = h * n / ymax
            o.append(
                f"<rect x='{cx + dx - ancho / 2:.1f}' y='{y0 + h - bh:.1f}' width='{ancho:.1f}' "
                f"height='{bh:.1f}' fill='{color}' rx='2'/>"
            )
            o.append(t(cx + dx, y0 + h - bh - 6, str(n), 11, weight="bold", fill=color if n else GRIS))
        o.append(t(cx, y0 + h + 20, f"|{bit}⟩", 14, weight="bold"))
    o.append(leyenda(x0, y0 + h + 42, [(ROSA, "|Φ⁺⟩  H + CNOT"), (VERDE, "|Ψ⁺⟩  H + CNOT + X en q1")]))
    o.append(t(x0 + w / 2, y0 + h + 78,
               "Conteos reales de lab1_hola_mundo.py (10 000 disparos, semilla 42). "
               "En |Φ⁺⟩ solo hay |00⟩ y |11⟩; la X en q1 los pasa a |01⟩ y |10⟩.",
               11, fill="#666"))
    guardar("tarea41_bell.svg", 920, 480, "".join(o),
            "Tarea #41 — Estados de Bell |Φ⁺⟩ y |Ψ⁺⟩",
            "Ausencia de las cadenas cruzadas: el entrelazamiento prohíbe la mitad de la base")


def grafico_bloch():
    medidos = []
    for theta, desc in lab2.ANGULOS:
        _qc, counts = lab2.simular_angulo(theta)
        n0 = counts.get("0", 0)
        medidos.append((math.degrees(theta), n0 / lab2.SHOTS * 100, (lab2.SHOTS - n0) / lab2.SHOTS * 100, desc))
    x0, y0, w, h = 70, 80, 800, 280
    o = [eje_y(x0, y0, w, h, 100, 20, lambda v: f"{v:.0f}")]

    def x_de(grados):
        return x0 + w * grados / 180

    def y_de(porcentaje):
        return y0 + h - h * porcentaje / 100

    curva0, curva1 = [], []
    for grado in range(0, 181, 3):
        p0, p1 = lab2.teorico(math.radians(grado))
        curva0.append(f"{x_de(grado):.1f},{y_de(p0 * 100):.1f}")
        curva1.append(f"{x_de(grado):.1f},{y_de(p1 * 100):.1f}")
    o.append(f"<polyline points='{' '.join(curva0)}' fill='none' stroke='{ROSA}' stroke-width='2' stroke-dasharray='6 4'/>")
    o.append(f"<polyline points='{' '.join(curva1)}' fill='none' stroke='{VERDE}' stroke-width='2' stroke-dasharray='6 4'/>")
    for grados, p0, p1, _desc in medidos:
        o.append(f"<circle cx='{x_de(grados):.1f}' cy='{y_de(p0):.1f}' r='5' fill='{ROSA}'/>")
        o.append(f"<circle cx='{x_de(grados):.1f}' cy='{y_de(p1):.1f}' r='5' fill='{VERDE}'/>")
        o.append(t(x_de(grados), y0 + h + 20, f"{grados:.0f}°", 12, weight="bold"))
        o.append(t(x_de(grados), y_de(p0) - 10, f"{p0:.1f}", 10, fill=ROSA))
    o.append(t(x0 + w / 2, y0 + h + 44, "θ (grados)", 12, fill="#666"))
    o.append(t(22, y0 + h / 2, "%", 12, fill="#777"))
    o.append(leyenda(x0, y0 + h + 64, [
        (ROSA, "P(|0⟩) medido"),
        (VERDE, "P(|1⟩) medido"),
        (ROSA, "cos²(θ/2)"),
        (VERDE, "sin²(θ/2)"),
    ]))
    o.append(t(x0 + w / 2, y0 + h + 96,
               "Puntos: lab2_rotaciones_bloch.py, 10 000 disparos, semilla 42. "
               "Líneas punteadas: la regla de Born, sin simulación.",
               11, fill="#666"))
    guardar("tarea42_bloch.svg", 920, 500, "".join(o),
            "Tarea #42 — Rotaciones Ry(θ) en la esfera de Bloch",
            "Del polo norte (θ = 0) al polo sur (θ = π): P(|0⟩) = cos²(θ/2)")


def grafico_deutsch():
    con, sin = [], []
    for caso in lab3.CASOS:
        _qc, counts = lab3.ejecutar_deutsch(caso, con_x_ancilla=True)
        con.append(counts.get("1", 0) / lab3.SHOTS)
        _qc, counts = lab3.ejecutar_deutsch(caso, con_x_ancilla=False)
        sin.append(counts.get("1", 0) / lab3.SHOTS)
    x0, y0, w, h = 90, 80, 780, 250
    o = [eje_y(x0, y0, w, h, 1, 0.25, lambda v: f"{v:.2f}")]
    grupo = w / 4
    ancho = grupo * 0.28
    etiquetas = ["constante_0", "constante_1", "balanceada\nidentidad", "balanceada\ninversa"]
    for i, (c, s, etq) in enumerate(zip(con, sin, etiquetas)):
        cx = x0 + grupo * i + grupo / 2
        for dx, valor, color in ((-ancho * 0.7, c, ROSA), (ancho * 0.7, s, GRIS)):
            bh = h * valor
            o.append(
                f"<rect x='{cx + dx - ancho / 2:.1f}' y='{y0 + h - bh:.1f}' width='{ancho:.1f}' "
                f"height='{max(bh, 0):.1f}' fill='{color}' rx='2'/>"
            )
            o.append(t(cx + dx, y0 + h - bh - 8, f"{valor:.0f}", 12, weight="bold", fill=color))
        linea1, _, linea2 = etq.partition("\n")
        o.append(t(cx, y0 + h + 20, linea1, 12, weight="bold"))
        if linea2:
            o.append(t(cx, y0 + h + 36, linea2, 12, weight="bold"))
    o.append(leyenda(x0, y0 + h + 58, [
        (ROSA, "con X en q1: fracción de '1'"),
        (GRIS, "reto, sin X: fracción de '1'"),
    ]))
    o.append(t(x0 + w / 2, y0 + h + 90,
               "lab3_algoritmo_deutsch.py, 10 000 disparos. Con la ancilla en |−⟩ el bit sale seguro. "
               "Sin la X previa, las cuatro funciones miden '0'.",
               11, fill="#666"))
    guardar("tarea43_deutsch.svg", 920, 460, "".join(o),
            "Tarea #43 — Deutsch y el reto del phase kickback",
            "Fracción de disparos en los que q0 mide '1' (balanceada). 0 = constante")


def grafico_teleportacion():
    qc = lab4.construir_circuito()
    counts = lab4.medir(qc)
    bob = lab4.conteos_bob(counts)
    cadenas = [format(i, "03b") for i in range(8)]
    x0, y0, w, h = 60, 80, 520, 240
    ymax = 2500
    o = [eje_y(x0, y0, w, h, ymax, 500, lambda v: str(int(v)))]
    ancho = w / 8 * 0.62
    for i, bit in enumerate(cadenas):
        n = counts.get(bit, 0)
        cx = x0 + w / 8 * i + w / 16
        color = ROSA if bit[0] == "0" else VERDE
        bh = h * n / ymax
        o.append(
            f"<rect x='{cx - ancho / 2:.1f}' y='{y0 + h - bh:.1f}' width='{ancho:.1f}' "
            f"height='{bh:.1f}' fill='{color}' rx='2'/>"
        )
        o.append(t(cx, y0 + h - bh - 6, str(n), 10, weight="bold", fill=color))
        o.append(t(cx, y0 + h + 18, bit, 11))
    o.append(t(x0 + w / 2, y0 + h + 40, "cadena c2 c1 c0  (c2 = Bob)", 12, fill="#666"))

    # Marginal de Bob frente al 75/25 teórico.
    bx, by, bw, bh = 640, 80, 230, 240
    o.append(eje_y(bx, by, bw, bh, 100, 25, lambda v: f"{v:.0f}"))
    pares = [
        ("|0⟩", bob["0"] / lab4.SHOTS * 100, 75.0),
        ("|1⟩", bob["1"] / lab4.SHOTS * 100, 25.0),
    ]
    for i, (nombre, medido, teoria) in enumerate(pares):
        cx = bx + bw / 2 * i + bw / 4
        for dx, valor, color in ((-16, medido, OSC), (16, teoria, CLARO)):
            altura = bh * valor / 100
            o.append(
                f"<rect x='{cx + dx - 12:.1f}' y='{by + bh - altura:.1f}' width='24' "
                f"height='{altura:.1f}' fill='{color}' rx='2'/>"
            )
        o.append(t(cx, by + bh + 20, nombre, 14, weight="bold"))
        o.append(t(cx, by - 8, f"{medido:.2f}%", 11, weight="bold", fill=OSC))
    o.append(leyenda(60, y0 + h + 62, [
        (ROSA, "Bob mide 0"),
        (VERDE, "Bob mide 1"),
        (OSC, "marginal medida"),
        (CLARO, "teórico 75/25"),
    ]))
    o.append(t(460, y0 + h + 96,
               f"Bob: |0⟩ = {bob['0']} ({bob['0'] / lab4.SHOTS * 100:.2f} %), "
               f"|1⟩ = {bob['1']} ({bob['1'] / lab4.SHOTS * 100:.2f} %). "
               "lab4_teletransportacion.py, 10 000 disparos, semilla 42.",
               11, fill="#666"))
    guardar("tarea44_teleportacion.svg", 920, 500, "".join(o),
            "Tarea #44 — Teletransportación: histograma y cúbit de Bob",
            "Ry(π/3) sale de Alice y reaparece en q2, cerca de 75 % / 25 %")


def pngs():
    js = (
        "const {chromium}=require('playwright');(async()=>{let b;"
        "try{b=await chromium.launch();}catch(e){b=await chromium.launch({channel:'chrome'});}"
        "const fs=require('fs');for(const f of process.argv.slice(1)){const s=fs.readFileSync(f,'utf8');"
        "const m=s.match(/width='(\\d+)' height='(\\d+)'/);"
        "const p=await b.newPage({viewport:{width:+m[1],height:+m[2]}});"
        "await p.setContent('<body style=\"margin:0\">'+s+'</body>');"
        "await p.screenshot({path:f.replace('.svg','.png')});}await b.close();})()"
    )
    svgs = [os.path.join(AQUI, n) for n in sorted(os.listdir(AQUI)) if n.startswith("tarea") and n.endswith(".svg")]
    r = subprocess.run(["node", "-e", js] + svgs, capture_output=True, text=True)
    if r.returncode != 0:
        print("PNG no generados:", (r.stderr or r.stdout)[:500])
        return 1
    print("PNG generados")
    return 0


def main():
    grafico_bell()
    grafico_bloch()
    grafico_deutsch()
    grafico_teleportacion()
    print("SVG generados")
    return pngs()


if __name__ == "__main__":
    sys.exit(main())
