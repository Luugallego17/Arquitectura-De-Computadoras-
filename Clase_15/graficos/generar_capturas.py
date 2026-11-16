#!/usr/bin/env python3
"""Genera las capturas de terminal (PNG) a partir de los archivos de evidencias.

Cada captura renderiza el texto ORIGINAL guardado en evidencias/*.txt (el mismo
texto que produjo el programa), con un marco de terminal. Uso:
    python3 generar_capturas.py
"""
import html
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(AQUI), "evidencias")
SALIDA = os.path.join(EV, "capturas")

# (nombre de la captura, archivo de evidencias)
CAPTURAS = [
    ("40_entorno", "00_entorno.txt"),
    ("41_ejecucion_lab1", "01_lab1_bell.txt"),
    ("42_ejecucion_lab2", "02_lab2_bloch.txt"),
    ("43_ejecucion_lab3", "03_lab3_deutsch.txt"),
    ("44_ejecucion_lab4", "04_lab4_teletransportacion.txt"),
]

CSS = """body{margin:0;background:#fff}.t{background:#1e1e2e;color:#cdd6f4;font:13px/1.45 'DejaVu Sans Mono',monospace;
padding:14px 18px;display:inline-block;border-radius:8px;min-width:640px}.b{color:#f38ba8;margin-bottom:10px;font-family:'DejaVu Sans',sans-serif}
.b span{color:#f5c2e7}pre{margin:0;white-space:pre}.ok{color:#a6e3a1}.no{color:#f38ba8}"""


def colorear(linea):
    s = html.escape(linea)
    return s.replace("[OK]", "<span class='ok'>[OK]</span>").replace("[FALLO]", "<span class='no'>[FALLO]</span>")


def main():
    os.makedirs(SALIDA, exist_ok=True)
    paginas = []
    for nombre, archivo in CAPTURAS:
        texto = open(os.path.join(EV, archivo), encoding="utf-8").read()
        lineas = texto.rstrip("\n").split("\n")
        cuerpo = "\n".join(colorear(linea) for linea in lineas)
        pagina = (
            f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
            f"<div class='t'><div class='b'>● ● ● <span>Terminal — Clase_15</span></div>"
            f"<pre>{cuerpo}</pre></div></body></html>"
        )
        ruta = os.path.join(SALIDA, nombre + ".html")
        open(ruta, "w", encoding="utf-8").write(pagina)
        paginas.append(ruta)
    js = (
        "const {chromium}=require('playwright');(async()=>{let b;"
        "try{b=await chromium.launch();}catch(e){b=await chromium.launch({channel:'chrome'});}"
        "const p=await b.newPage({viewport:{width:1100,height:800}});"
        "for(const f of process.argv.slice(1)){await p.goto('file://'+f);"
        "const e=await p.$('.t');await e.screenshot({path:f.replace('.html','.png')});}await b.close();})()"
    )
    r = subprocess.run(["node", "-e", js] + paginas, capture_output=True, text=True)
    for pagina in paginas:
        os.remove(pagina)
    if r.returncode != 0:
        print("capturas no generadas:", (r.stderr or r.stdout)[:400])
        return 1
    print("capturas generadas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
