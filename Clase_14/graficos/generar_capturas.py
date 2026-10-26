#!/usr/bin/env python3
"""Genera las capturas de terminal (PNG) a partir de los archivos de evidencias.

Cada captura renderiza el texto ORIGINAL guardado en evidencias/*.txt (el mismo
texto que produjo el programa), con un marco de terminal. Uso:
    python3 generar_capturas.py
"""
import html
import os
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(AQUI), "evidencias")
SALIDA = os.path.join(EV, "capturas")

# (nombre de la captura, archivo, primera linea, ultima linea o None)
CAPTURAS = [
    ("36_ejecucion_exp1", "02_exp1_puerto_teclado.txt", 0, None),
    ("37_ejecucion_exp2", "03_exp2_cola_teclado.txt", 0, None),
    ("38_ejecucion_exp3", "04_exp3_vram_monitor.txt", 0, None),
    ("39_ejecucion_terminal", "05_reto_integrador_terminal.txt", 0, None),
    ("39_terminal_interactiva", "06_terminal_interactiva.txt", 0, 36),
    ("39_fallo_cursor_uint8", "07_fallo_cursor_uint8.txt", 0, None),
    ("39_sanitizers_valgrind", "08_sanitizers_valgrind.txt", 0, None),
    ("39_cobertura_gcov", "09_cobertura_gcov.txt", 0, None),
    ("39_entorno_y_compilacion", None, 0, None),
]

CSS = """body{margin:0;background:#fff}.t{background:#1e1e2e;color:#cdd6f4;font:13px/1.45 'DejaVu Sans Mono',monospace;
padding:14px 18px;display:inline-block;border-radius:8px;min-width:560px}.b{color:#f38ba8;margin-bottom:10px;font-family:'DejaVu Sans',sans-serif}
.b span{color:#f5c2e7}pre{margin:0;white-space:pre}.ok{color:#a6e3a1}.no{color:#f38ba8}"""


def colorear(linea):
    s = html.escape(linea)
    return s.replace("[OK]", "<span class='ok'>[OK]</span>").replace("[FALLO]", "<span class='no'>[FALLO]</span>")


def main():
    os.makedirs(SALIDA, exist_ok=True)
    paginas = []
    for nombre, archivo, a, b in CAPTURAS:
        if archivo is None:
            texto = open(os.path.join(EV, "00_entorno.txt")).read() + "\n" + open(os.path.join(EV, "01_compilacion.txt")).read()
        else:
            texto = open(os.path.join(EV, archivo)).read()
        lineas = texto.rstrip("\n").split("\n")[a:b]
        cuerpo = "\n".join(colorear(l) for l in lineas)
        pag = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='t'><div class='b'>● ● ● <span>Terminal — Clase_14</span></div><pre>{cuerpo}</pre></div></body></html>"
        ruta = os.path.join(SALIDA, nombre + ".html")
        open(ruta, "w").write(pag)
        paginas.append(ruta)
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:900,height:400}});"
          "for(const f of process.argv.slice(1)){await p.goto('file://'+f);const e=await p.$('.t');await e.screenshot({path:f.replace('.html','.png')});}await b.close();})()")
    r = subprocess.run(["node", "-e", js] + paginas, capture_output=True, text=True)
    for p in paginas:
        os.remove(p)
    print("capturas generadas" if r.returncode == 0 else r.stderr[:300])


if __name__ == "__main__":
    main()
