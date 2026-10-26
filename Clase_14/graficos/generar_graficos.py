#!/usr/bin/env python3
"""Genera los graficos de la Clase 14 (SVG y PNG) a partir de las trazas reales.

Compila los programas, ejecuta cada uno con la opcion -t (traza CSV) y dibuja
lo que realmente hizo el codigo; no hay valores escritos a mano.

Uso: python3 generar_graficos.py      (los PNG necesitan node + playwright)
"""
import csv
import io
import os
import subprocess
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.dirname(AQUI)
ROSA, VERDE, OSC, CLARO, TXT, GRID, GRIS = "#d9487d", "#2a8f7b", "#b8325f", "#f0a6c0", "#2b2b2b", "#dddddd", "#7a7a7a"
FONT = "font-family='DejaVu Sans, Arial, sans-serif'"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def t(x, y, s, size=13, anchor="middle", weight="normal", fill=TXT):
    return f"<text x='{x}' y='{y}' font-size='{size}' text-anchor='{anchor}' font-weight='{weight}' fill='{fill}' {FONT}>{esc(s)}</text>"


def guardar(nombre, w, h, cuerpo, titulo, sub):
    cab = t(w / 2, 30, titulo, 19, weight="bold") + t(w / 2, 50, sub, 12, fill="#666")
    with open(os.path.join(AQUI, nombre), "w") as f:
        f.write(f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>"
                f"<rect width='{w}' height='{h}' fill='white'/>{cab}{cuerpo}</svg>")


def trazas():
    tmp = tempfile.mkdtemp()
    salida = {}
    for nombre in ["exp1_puerto_teclado", "exp2_cola_teclado", "exp3_vram_monitor", "reto_integrador_terminal"]:
        exe = os.path.join(tmp, nombre)
        subprocess.run(["gcc", "-std=c99", "-Wall", "-Wextra", "-pedantic", os.path.join(CARPETA, nombre + ".c"), "-o", exe], check=True)
        salida[nombre] = subprocess.run([exe, "-t"], capture_output=True, text=True, check=True).stdout
    return salida


def filas_csv(texto, prefijo):
    lineas = [l.split(",", 1)[1] for l in texto.splitlines() if l.startswith(prefijo + ",")]
    return list(csv.DictReader(io.StringIO("\n".join(lineas))))


def eje(x0, y0, w, h, ymax, paso, fmt=str):
    o = []
    v = 0
    while v <= ymax + 1e-9:
        y = y0 + h - h * v / ymax
        o.append(f"<line x1='{x0}' y1='{y}' x2='{x0 + w}' y2='{y}' stroke='{GRID}'/>")
        o.append(t(x0 - 6, y + 4, fmt(v), 11, "end", fill="#777"))
        v += paso
    return "".join(o)


def leyenda(x, y, items):
    o = []
    for k, (c, nom) in enumerate(items):
        lx = x + k * 150
        o.append(f"<rect x='{lx}' y='{y}' width='12' height='12' fill='{c}' rx='2'/>")
        o.append(t(lx + 17, y + 11, nom, 12, "start"))
    return "".join(o)


def main():
    tr = trazas()

    # ---------- #36: puerto de teclado (IO_READ + handshake) ----------
    f = filas_csv(tr["exp1_puerto_teclado"], "TRAZA")
    n = len(f)
    x0, w, ancho = 150, 700, 700 / len(f)
    senales = [("reg_status (bit 0)", lambda r: int(r["reg_status"]), ROSA),
               ("IO_READ", lambda r: int(r["io_read"]), VERDE),
               ("data_bus != 0", lambda r: 1 if int(r["data_bus"], 16) else 0, OSC)]
    o = []
    for k, (nom, fn, col) in enumerate(senales):
        y = 100 + k * 90
        o.append(t(x0 - 10, y + 30, nom, 12, "end"))
        o.append(f"<line x1='{x0}' y1='{y + 50}' x2='{x0 + w}' y2='{y + 50}' stroke='{GRID}'/>")
        d, prev = "", 0
        for i, r in enumerate(f):
            v = fn(r)
            xa, xb = x0 + i * ancho, x0 + (i + 1) * ancho
            yv = y + 50 - 40 * v
            d += f"{'M' if i == 0 else 'L'}{xa},{yv} L{xb},{yv} " if i == 0 else f"L{xa},{yv} L{xb},{yv} "
        o.append(f"<path d='{d}' fill='none' stroke='{col}' stroke-width='3'/>")
    for i, r in enumerate(f):
        xc = x0 + i * ancho + ancho / 2
        o.append(t(xc, 385, r["evento"].replace("_0x", " 0x"), 11))
        if r["evento"].startswith("IN_"):
            o.append(t(xc, 402, f"data=0x{int(r['data_bus'], 16):02X}", 11, fill="#666"))
        o.append(f"<line x1='{x0 + i * ancho}' y1='90' x2='{x0 + i * ancho}' y2='370' stroke='{GRID}' stroke-dasharray='3 4'/>")
    o.append(t(x0 + w / 2, 430, "Pasos de la traza real de exp1 (./exp1_puerto_teclado -t). Al leer el puerto de datos (IN 0x02) el status vuelve a 0.", 11, fill="#666"))
    guardar("tarea36_puerto.svg", 900, 450, "".join(o), "Tarea #36 — E/S por puerto y handshake",
            "Señales del bus de control y del controlador de teclado, paso a paso")

    # ---------- #37: cola circular ----------
    f = filas_csv(tr["exp2_cola_teclado"], "TRAZA")
    x0, y0, w, h = 70, 100, 780, 230
    pasos = len(f)
    ag = w / pasos
    o = [eje(x0, y0, w, h, 8, 2)]
    series = [("count", ROSA, "COUNT (0x7A)"), ("head", VERDE, "HEAD (0x78)"), ("tail", OSC, "TAIL (0x79)")]
    for key, col, _ in series:
        pts = " ".join(f"{x0 + i * ag + ag / 2},{y0 + h - h * int(r[key]) / 8}" for i, r in enumerate(f))
        o.append(f"<polyline points='{pts}' fill='none' stroke='{col}' stroke-width='3' stroke-linejoin='round'/>")
        for i, r in enumerate(f):
            o.append(f"<circle cx='{x0 + i * ag + ag / 2}' cy='{y0 + h - h * int(r[key]) / 8}' r='3.5' fill='{col}'/>")
    for i, r in enumerate(f):
        xc = x0 + i * ag + ag / 2
        etq = r["operacion"].replace("enc_", "+").replace("des", "−")
        o.append(t(xc, y0 + h + 16, etq, 10, fill=ROSA if r["resultado"] in ("OVERFLOW", "VACIA") else TXT, weight="bold" if r["resultado"] in ("OVERFLOW", "VACIA") else "normal"))
        if r["resultado"] == "OVERFLOW":
            o.append(f"<rect x='{xc - ag / 2}' y='{y0}' width='{ag}' height='{h}' fill='{ROSA}' opacity='0.13'/>")
            if i == 0 or f[i - 1]["resultado"] != "OVERFLOW":
                o.append(t(xc + ag / 2, y0 + 12, "overflow ×2", 10, fill=ROSA, weight="bold"))
        if r["resultado"] == "VACIA":
            o.append(f"<rect x='{xc - ag / 2}' y='{y0}' width='{ag}' height='{h}' fill='{GRIS}' opacity='0.15'/>")
            if i == 0 or f[i - 1]["resultado"] != "VACIA":
                o.append(t(xc + ag / 2, y0 + 12, "cola vacía", 10, "end", fill=GRIS, weight="bold"))
    o.append(leyenda(x0, y0 + h + 38, [(c, n_) for _, c, n_ in series]))
    o.append(t(x0 + w / 2, y0 + h + 70, "+X = encolar la tecla X · − = desencolar. HEAD y TAIL dan la vuelta al llegar a 8 (aritmética módulo 8). Traza real de ./exp2_cola_teclado -t.", 11, fill="#666"))
    guardar("tarea37_cola.svg", 900, 450, "".join(o), "Tarea #37 — Cola circular FIFO en RAM",
            "HEAD, TAIL y COUNT en cada operación · 10 teclas en una cola de 8 · 2 overflows · vuelta de los punteros")

    # ---------- #38: VRAM y scroll ----------
    etapas = []
    for l in tr["exp3_vram_monitor"].splitlines():
        if l.startswith("VRAM,"):
            p = l.split(",")
            etapas.append((p[1], [int(v) for v in p[2:]]))
    o = []
    cel = 30
    gap = 40
    ancho_total = len(etapas) * (4 * cel) + (len(etapas) - 1) * gap
    ox = (900 - ancho_total) / 2
    for k, (nom, vals) in enumerate(etapas):
        bx = ox + k * (4 * cel + gap)
        by = 110
        o.append(t(bx + 2 * cel, by - 12, "escrita" if nom == "escrita" else f"scroll ×{nom[-1]}", 14, weight="bold"))
        for i, v in enumerate(vals):
            fila, col = divmod(i, 4)
            ch = chr(v) if 32 <= v <= 126 else "?"
            vacio = v == 0x20
            o.append(f"<rect x='{bx + col * cel}' y='{by + fila * cel}' width='{cel}' height='{cel}' fill='{'#fafafa' if vacio else CLARO}' stroke='{GRID}'/>")
            if not vacio:
                o.append(t(bx + col * cel + cel / 2, by + fila * cel + cel / 2 + 5, ch, 15, weight="bold"))
        for fila in range(4):
            o.append(t(bx - 6, by + fila * cel + cel / 2 + 4, f"{0xF0 + fila * 4:02X}", 10, "end", fill="#777"))
        if k < len(etapas) - 1:
            o.append(f"<path d='M{bx + 4 * cel + 6},{by + 2 * cel} l{gap - 12},0' stroke='{GRIS}' stroke-width='2' marker-end='url(#p)'/>")
    o.insert(0, "<defs><marker id='p' markerUnits='userSpaceOnUse' markerWidth='10' markerHeight='10' refX='8' refY='5' orient='auto'><path d='M0,0 L10,5 L0,10 z' fill='#7a7a7a'/></marker></defs>")
    # ocupacion por fila
    o.append(t(450, 290, "Celdas con carácter (de 16) tras cada etapa", 14, weight="bold"))
    bx0, bw = 150, 600
    for k, (nom, vals) in enumerate(etapas):
        ocupadas = sum(1 for v in vals if v != 0x20)
        y = 310 + k * 26
        o.append(t(bx0 - 8, y + 13, "escrita" if nom == "escrita" else f"scroll ×{nom[-1]}", 12, "end"))
        o.append(f"<rect x='{bx0}' y='{y}' width='{bw}' height='18' fill='#f4f4f4' rx='3'/>")
        o.append(f"<rect x='{bx0}' y='{y}' width='{bw * ocupadas / 16}' height='18' fill='{ROSA}' rx='3'/>")
        o.append(t(bx0 + bw + 8, y + 13, f"{ocupadas}", 12, "start", weight="bold"))
    guardar("tarea38_vram.svg", 900, 450, "".join(o), "Tarea #38 — VRAM 4×4 (0xF0..0xFF) y scroll",
            "Contenido real de los 16 bytes tras escribir y tras cada scroll hacia arriba · a la izquierda, dirección de cada fila")

    # ---------- #39: terminal con Backspace ----------
    f = filas_csv(tr["reto_integrador_terminal"], "TRAZA")
    x0, y0, w, h = 70, 100, 780, 190
    ag = w / len(f)
    o = [eje(x0, y0, w, h, 16, 4)]
    o.append(t(28, y0 + h / 2, "celdas ocupadas", 11, "middle", fill="#777").replace("<text ", f"<text transform='rotate(-90 28 {y0 + h / 2})' "))
    pts = []
    for i, r in enumerate(f):
        ocup = int(r["cursor"]) - 0xF0
        pts.append(f"{x0 + i * ag + ag / 2},{y0 + h - h * ocup / 16}")
    o.append(f"<polyline points='{' '.join(pts)}' fill='none' stroke='{ROSA}' stroke-width='3'/>")
    for i, r in enumerate(f):
        ocup = int(r["cursor"]) - 0xF0
        xc = x0 + i * ag + ag / 2
        tecla = r["tecla"]
        if tecla in ("0x08", "0x7F"):
            col, etq = OSC, "⌫" if tecla == "0x08" else "DEL"
        elif tecla == "inicio":
            col, etq = GRIS, "·"
        else:
            col, etq = VERDE, chr(int(tecla, 16))
        o.append(f"<circle cx='{xc}' cy='{y0 + h - h * ocup / 16}' r='5' fill='{col}'/>")
        o.append(t(xc, y0 + h + 18, etq, 13, weight="bold", fill=col))
        o.append(t(xc, y0 + h + 34, str(i), 9, fill="#999"))
    o.append(leyenda(x0, y0 + h + 52, [(VERDE, "carácter imprimible"), (OSC, "Backspace / DEL"), (ROSA, "posición del cursor")]))
    fin = f[len(f) - 1]
    o.append(t(x0 + w / 2, y0 + h + 94, f"Con 8 Backspace al final el cursor vuelve a 0xF0 y se queda ahí (no retrocede por debajo de la VRAM): cursor final = 0x{int(fin['cursor']):02X}.", 11, fill="#666"))
    # pantalla en 3 momentos
    for k, idx in enumerate([4, 6, 11]):
        r = f[idx]
        pant = r["pantalla"]
        bx = 150 + k * 250
        by = y0 + h + 140
        o.append(t(bx + 60, by - 8, f"tras la tecla {idx}", 12, weight="bold"))
        for fila in range(4):
            for col in range(4):
                ch = pant[fila * 4 + col]
                o.append(f"<rect x='{bx + col * 30}' y='{by + fila * 22}' width='30' height='22' fill='{'#fafafa' if ch == ' ' else CLARO}' stroke='{GRID}'/>")
                if ch != " ":
                    o.append(t(bx + col * 30 + 15, by + fila * 22 + 16, ch, 13, weight="bold"))
    guardar("tarea39_terminal.svg", 900, 560, "".join(o), "Tarea #39 — Terminal integradora con Backspace",
            "Cursor de la VRAM tras cada pulsación: teclado → puerto 0x02 → cola FIFO → VRAM · 20 pulsaciones")
    print("SVG generados")

    # SVG -> PNG con Chromium (playwright de node)
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
          "const fs=require('fs');for(const f of process.argv.slice(1)){const s=fs.readFileSync(f,'utf8');"
          "const m=s.match(/width='(\\d+)' height='(\\d+)'/);const p=await b.newPage({viewport:{width:+m[1],height:+m[2]}});"
          "await p.setContent('<body style=\"margin:0\">'+s+'</body>');await p.screenshot({path:f.replace('.svg','.png')});}await b.close();})()")
    svgs = [os.path.join(AQUI, n) for n in sorted(os.listdir(AQUI)) if n.endswith(".svg")]
    r = subprocess.run(["node", "-e", js] + svgs, capture_output=True, text=True)
    print("PNG generados" if r.returncode == 0 else "PNG no generados: " + r.stderr[:300])


if __name__ == "__main__":
    main()
