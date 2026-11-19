#!/usr/bin/env python3
"""Arma las diapositivas de la Clase 15.

La diapositiva central cita investigaciones en tres niveles: internacional,
nacional (Bolivia) y local (La Paz). Las citas son trabajos publicados o
actos académicos comprobables; el laboratorio de Qiskit no se presenta como
si fuera uno de esos papers.

    python3 generar_diapositivas.py
"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "clase15_investigaciones.pptx")

AZUL = RGBColor(0x1B, 0x3A, 0x4B)
AZUL_SUAVE = RGBColor(0xE8, 0xF0, 0xF4)
VERDE = RGBColor(0x1E, 0x6B, 0x4F)
VERDE_SUAVE = RGBColor(0xE7, 0xF4, 0xEE)
ROSA = RGBColor(0x9C, 0x2F, 0x56)
ROSA_SUAVE = RGBColor(0xF8, 0xEC, 0xF1)
TINTA = RGBColor(0x1F, 0x2A, 0x32)
GRIS = RGBColor(0x5C, 0x6B, 0x73)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
CREMA = RGBColor(0xF7, 0xF5, 0xF2)
LINEA = RGBColor(0xD5, 0xDD, 0xE2)

ANCHO = 13.333
ALTO = 7.5


def rgb(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def rect(slide, l, t, w, h, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    rgb(shape, color)
    return shape


def rrect(slide, l, t, w, h, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    rgb(shape, color)
    # Ajuste del redondeo para que no se coma el texto.
    shape.adjustments[0] = 0.08
    return shape


def anclar(shape, ancla):
    shape.text_frame.auto_size = None
    shape.text_frame.word_wrap = True
    body = shape._element.find(qn("p:txBody"))
    bodyPr = body.find(qn("a:bodyPr"))
    bodyPr.set("anchor", ancla)


def escribir(shape, bloques, alineacion=PP_ALIGN.LEFT):
    """bloques: lista de (texto, tamaño, negrita, color, espacio_antes, espacio_despues)."""
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    for i, (texto, tam, negrita, color, antes, despues) in enumerate(bloques):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = alineacion
        p.space_before = Pt(antes)
        p.space_after = Pt(despues)
        run = p.add_run()
        run.text = texto
        run.font.name = "Calibri"
        run.font.size = Pt(tam)
        run.font.bold = negrita
        run.font.color.rgb = color


def caja(slide, l, t, w, h, bloques, alineacion=PP_ALIGN.LEFT, ancla="t"):
    shape = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)
    anclar(shape, ancla)
    escribir(shape, bloques, alineacion)
    return shape


def lienzo(prs, numero, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, ANCHO, ALTO, CREMA)
    rect(slide, 0, 0, 0.12, ALTO, AZUL)
    rect(slide, 0, 7.22, ANCHO, 0.28, AZUL)
    caja(
        slide, 0.35, 7.22, 9.5, 0.28,
        [("Arquitectura de Computadoras  ·  UCB San Pablo, sede La Paz  ·  Clase 15", 11, False, BLANCO, 0, 0)],
        ancla="ctr",
    )
    caja(
        slide, 11.4, 7.22, 1.6, 0.28,
        [(f"{numero}  /  {total}", 11, False, BLANCO, 0, 0)],
        alineacion=PP_ALIGN.RIGHT, ancla="ctr",
    )
    return slide


def titulo(slide, texto, subtitulo):
    caja(slide, 0.4, 0.22, 12.4, 0.48, [(texto, 28, True, AZUL, 0, 0)])
    caja(slide, 0.4, 0.72, 12.4, 0.38, [(subtitulo, 14, False, GRIS, 0, 0)])


def portada(prs, total):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, ANCHO, ALTO, AZUL)
    rect(slide, 0, 0, 0.18, ALTO, ROSA)
    caja(slide, 0.7, 1.35, 11.5, 0.4, [("UNIVERSIDAD CATÓLICA BOLIVIANA «SAN PABLO»  ·  SEDE LA PAZ", 14, False, RGBColor(0xC5, 0xD8, 0xE4), 0, 0)])
    caja(slide, 0.7, 1.9, 11.8, 1.6, [("Computación cuántica con Qiskit", 40, True, BLANCO, 0, 0)])
    caja(slide, 0.7, 3.45, 11.5, 0.9, [("Investigaciones internacionales, nacionales y locales\nque sostienen el laboratorio de la Clase 15", 22, False, RGBColor(0xF3, 0xD5, 0xE0), 0, 0)])
    caja(slide, 0.7, 5.15, 11.5, 1.1, [
        ("Arquitectura de Computadoras  ·  Ingeniería en Inteligencia Artificial", 16, False, BLANCO, 0, 4),
        ("16 de noviembre de 2026", 16, False, BLANCO, 0, 0),
    ])


def laboratorio(prs, total):
    slide = lienzo(prs, 2, total)
    titulo(slide, "De dónde salen los cuatro circuitos", "Los números son la corrida de Aer guardada en evidencias/. Las citas, las diapositivas que siguen.")
    filas = [
        ("Bell  |Φ⁺⟩", "Lab 1", "4932 veces |00⟩ (49,32 %) y 5068 veces |11⟩ (50,68 %). Las otras dos cadenas salieron 0.", "Bell, 1964"),
        ("Bloch  Ry(θ)", "Lab 2", "A 45°: 8555 / 1445, es decir 85,5 % / 14,4 %. El teórico cos²(π/8) es 85,4 % / 14,6 %.", "Born, 1926"),
        ("Deutsch", "Lab 3", "Constantes miden «0» y balanceadas miden «1», las 10 000 veces. Sin la X de la ancilla, las cuatro miden «0».", "Deutsch, 1985"),
        ("Teletransportación", "Lab 4", "Bob recupera 7487 / 2513: 74,87 % / 25,13 %, frente al 75 / 25 de Ry(π/3).", "Bennett y otros, 1993"),
    ]
    y = 1.4
    for nombre, lab, dato, cita in filas:
        rrect(slide, 0.4, y, 12.5, 1.3, BLANCO)
        rect(slide, 0.4, y, 0.1, 1.3, ROSA)
        caja(slide, 0.65, y + 0.1, 3.1, 0.4, [(nombre, 18, True, AZUL, 0, 0)])
        caja(slide, 0.65, y + 0.52, 3.1, 0.35, [(lab, 13, False, ROSA, 0, 0)])
        caja(slide, 3.9, y + 0.18, 6.3, 0.95, [(dato, 15, False, TINTA, 0, 0)])
        caja(slide, 10.2, y + 0.35, 2.5, 0.6, [(cita, 13, True, VERDE, 0, 0)], alineacion=PP_ALIGN.RIGHT)
        y += 1.42


def tres_niveles(prs, total):
    slide = lienzo(prs, 3, total)
    titulo(slide, "Investigaciones de referencia", "Internacional, nacional y local. Cada tarjeta nombra un trabajo que existe y dice qué aporta a esta clase.")
    columnas = [
        (AZUL, AZUL_SUAVE, "INTERNACIONAL", [
            ("Deutsch, 1985", "Proc. R. Soc. A 400, 97-117. Una consulta basta para saber si la función es constante o balanceada."),
            ("Bennett y otros, 1993", "Phys. Rev. Lett. 70, 1895. El estado viaja con un par EPR y dos bits clásicos."),
            ("Bell, 1964", "Physics 1, 195. La correlación de |Φ⁺⟩ no la reproduce un modelo local."),
        ]),
        (VERDE, VERDE_SUAVE, "NACIONAL  ·  BOLIVIA", [
            ("Bacarreza y otros, 2025", "arXiv:2508.19857. Investigador boliviano. Latentes cuánticos en modelos generativos, con un procesador fotónico."),
            ("ORCA Computing, Londres", "El experimento no se hizo en Bolivia. Es la publicación de computación cuántica de un investigador del país."),
            ("Unifranz, mayo de 2026", "Master class de Bacarreza. Divulgación: agricultura, industria y energía. No sustituye al paper."),
        ]),
        (ROSA, ROSA_SUAVE, "LOCAL  ·  LA PAZ", [
            ("Calle y Rivera, 2018", "Rev. Boliviana de Física 33, 3-12. IIF-UMSA, Cota Cota. Eficiencia del arreglo ALPACA en Chacaltaya."),
            ("UMSA, 16 ago 2019", "Conferencia de computación cuántica de Sáenz de Cabezón, en el Paraninfo."),
            ("CIDIMEC, UCB La Paz", "RR 017/2017. Cómputo de alto rendimiento y co-diseño hardware-software de esta facultad."),
        ]),
    ]
    x = 0.38
    ancho = 4.15
    for color, suave, encabezado, items in columnas:
        rrect(slide, x, 1.35, ancho, 5.55, BLANCO)
        rect(slide, x, 1.35, ancho, 0.58, color)
        caja(slide, x + 0.1, 1.4, ancho - 0.2, 0.48, [(encabezado, 15, True, BLANCO, 0, 0)], ancla="ctr")
        y = 2.1
        for titulo_item, cuerpo in items:
            rrect(slide, x + 0.15, y, ancho - 0.3, 1.45, suave)
            caja(slide, x + 0.25, y + 0.06, ancho - 0.5, 0.36, [(titulo_item, 13, True, color, 0, 0)])
            caja(slide, x + 0.25, y + 0.4, ancho - 0.5, 0.95, [(cuerpo, 12, False, TINTA, 0, 0)])
            y += 1.55
        x += ancho + 0.18


def internacional(prs, total):
    slide = lienzo(prs, 4, total)
    titulo(slide, "Internacional  ·  los protocolos del laboratorio", "Estos papers son los que el código de la guía implementa. El simulador Aer los corre sin ruido.")
    bloques = [
        ("Deutsch, D. (1985). Quantum theory, the Church–Turing principle and the universal quantum computer. Proceedings of the Royal Society A, 400, 97-117.",
         "Lab 3. Con la ancilla en |−⟩, la fase (−1)^f(x) rebota al primer cúbit. Una medición dice si f es constante o balanceada. La guía lo llama phase kickback."),
        ("Bennett, C. H., Brassard, G., Crépeau, C., Jozsa, R., Peres, A. y Wootters, W. K. (1993). Teleporting an unknown quantum state… Physical Review Letters, 70, 1895-1899.",
         "Lab 4. El propio artículo dice que el protocolo no es instantáneo: Bob necesita el mensaje clásico de Alice. Por eso el 75/25 de q2 llega después de las correcciones."),
        ("Bell, J. S. (1964). On the Einstein Podolsky Rosen paradox. Physics, 1, 195-200.  ·  Ekert, A. K. (1991). Phys. Rev. Lett. 67, 661.",
         "Lab 1. |Φ⁺⟩ es el recurso del curso para el entrelazamiento y para el protocolo de criptografía E91. En la corrida, las cadenas cruzadas quedan en cero."),
        ("Wootters, W. K. y Zurek, W. H. (1982). A single quantum cannot be cloned. Nature, 299, 802-803.  ·  Koch, J. y otros (2007). Phys. Rev. A 76, 042319.",
         "No-clonación: el estado de Alice se destruye al medir. El Transmon de Koch y otros es el cúbit superconductor del módulo de hardware, a 15 mK. Aquí no se fabrica: se simula."),
    ]
    y = 1.32
    for cita, lectura in bloques:
        caja(slide, 0.45, y, 12.4, 0.42, [(cita, 13, True, AZUL, 0, 0)])
        caja(slide, 0.45, y + 0.4, 12.4, 0.55, [(lectura, 14, False, TINTA, 0, 0)])
        y += 1.4


def nacional(prs, total):
    slide = lienzo(prs, 5, total)
    titulo(slide, "Nacional  ·  un investigador boliviano", "La publicación es de computación cuántica. El laboratorio que la midió está en Londres, no en Bolivia.")
    rrect(slide, 0.4, 1.35, 12.5, 2.55, BLANCO)
    rect(slide, 0.4, 1.35, 0.1, 2.55, VERDE)
    caja(slide, 0.7, 1.5, 11.9, 0.7, [("Bacarreza, O., Farnsworth, T., Makarovskiy, A., Wallner, H., Hicks, T., Sempere-Llagostera, S., Price, J., Francis-Jones, R. J. A. y Clements, W. R. (2025).", 15, True, VERDE, 0, 0)])
    caja(slide, 0.7, 2.15, 11.9, 1.5, [
        ("Quantum latent distributions in deep generative models. arXiv:2508.19857.", 16, True, TINTA, 0, 8),
        ("Muestran que una distribución latente salida de un procesador cuántico fotónico puede generar datos que una latente clásica no produce con la misma facilidad. Lo prueban en un conjunto sintético y en moléculas QM9, en simulación y en hardware de ORCA Computing.", 15, False, TINTA, 0, 0),
    ])
    rrect(slide, 0.4, 4.1, 6.05, 2.85, VERDE_SUAVE)
    caja(slide, 0.55, 4.25, 5.75, 2.55, [
        ("Qué se puede afirmar", 16, True, VERDE, 0, 8),
        ("Omar Bacarreza es investigador boliviano, paceño de origen, y firma como primer autor un paper de computación cuántica.", 14, False, TINTA, 0, 8),
        ("El preprint está en arXiv desde agosto de 2025 (versión 3, junio de 2026). El autor anunció su aceptación en ICML 2026.", 14, False, TINTA, 0, 0),
    ])
    rrect(slide, 6.65, 4.1, 6.25, 2.85, BLANCO)
    caja(slide, 6.8, 4.25, 5.95, 2.55, [
        ("Qué no se debe afirmar", 16, True, ROSA, 0, 8),
        ("El procesador es fotónico y está en ORCA Computing (Londres). No es un resultado medido en una universidad boliviana.", 14, False, TINTA, 0, 8),
        ("La master class de Unifranz, en mayo de 2026, acerca el tema al país. Es divulgación: no reemplaza al artículo.", 14, False, TINTA, 0, 0),
    ])


def local(prs, total):
    slide = lienzo(prs, 6, total)
    titulo(slide, "Local  ·  La Paz", "En la ciudad no hay un criostato de cúbits. Hay física experimental de detectores y el centro de arquitectura de esta facultad.")
    tarjetas = [
        ("Calle García, C. A. y Rivera Bretel, H. M. (2018)",
         "Estudio analítico-simulado de la eficiencia de disparo del arreglo superficial de detectores del experimento ALPACA. Revista Boliviana de Física, 33, 3-12.",
         "Instituto de Investigaciones Físicas, UMSA, calle 27 de Cota Cota, La Paz. El arreglo se planea en el cerro Estuquería, junto a Chacaltaya, a 4740 m. Miden, con Monte Carlo, cuándo el disparo del arreglo de superficie es eficiente para protones, hierro y rayos gamma."),
        ("Universidad Mayor de San Andrés (2019)",
         "Conferencia internacional de computación cuántica. Eduardo Sáenz de Cabezón. 16 de agosto de 2019, 16:00 a 18:00, Paraninfo del Monoblock central.",
         "Es el acto académico local, en La Paz, que puso el nombre del tema en la universidad pública. No es un paper del Instituto de Investigaciones Físicas."),
        ("CIDIMEC, UCB sede La Paz",
         "Centro de Investigación, Desarrollo e Innovación en Mecatrónica. Resolución Rectoral 017/2017. Facultad de Ingeniería.",
         "Líneas publicadas: computación de alto rendimiento, co-diseño software-hardware y sistemas reconfigurables. Es el centro de investigación de la casa, en la misma sede. Su registro no abre una línea de cúbits."),
    ]
    y = 1.28
    for cabeza, medio, pie in tarjetas:
        rrect(slide, 0.4, y, 12.5, 1.85, BLANCO)
        rect(slide, 0.4, y, 0.1, 1.85, ROSA)
        caja(slide, 0.7, y + 0.08, 12.0, 0.32, [(cabeza, 15, True, ROSA, 0, 0)])
        caja(slide, 0.7, y + 0.4, 12.0, 0.5, [(medio, 13, True, TINTA, 0, 0)])
        caja(slide, 0.7, y + 0.92, 12.0, 0.82, [(pie, 13, False, GRIS, 0, 0)])
        y += 1.95


def bibliografia(prs, total):
    slide = lienzo(prs, 7, total)
    titulo(slide, "Bibliografía usada en estas diapositivas", "Lo que no tiene página de revista se cita con la URL institucional. No se inventan autores ni resultados.")
    entradas = [
        "Deutsch, D. (1985). Proceedings of the Royal Society A, 400, 97-117.",
        "Bennett, C. H. y otros (1993). Physical Review Letters, 70, 1895-1899. https://doi.org/10.1103/PhysRevLett.70.1895",
        "Bell, J. S. (1964). Physics, 1, 195-200.   ·   Ekert, A. K. (1991). Physical Review Letters, 67, 661-663.",
        "Wootters, W. K. y Zurek, W. H. (1982). Nature, 299, 802-803.   ·   Koch, J. y otros (2007). Physical Review A, 76, 042319.",
        "Bacarreza, O. y otros (2025). Quantum latent distributions in deep generative models. arXiv:2508.19857.",
        "Calle García, C. A. y Rivera Bretel, H. M. (2018). Revista Boliviana de Física, 33, 3-12. https://www.scielo.org.bo/pdf/rbf/v33n33/v33n33_a02.pdf",
        "UMSA (2019). Conferencia internacional de computación cuántica, 16 de agosto, Paraninfo. https://www.umsa.bo/eventos-umsa/",
        "UCB (2017/2025). CIDIMEC, sede La Paz. Registro de centros: https://www.ucb.edu.bo/wp-content/uploads/2025/05/CIDIMEC_Datos-Generales.pdf",
        "Unifranz (11 de mayo de 2026). Omar Bacarreza, el boliviano que apuesta por la revolución de la computación cuántica. https://unifranz.edu.bo/blog/",
    ]
    y = 1.25
    for entrada in entradas:
        caja(slide, 0.5, y, 12.4, 0.58, [(entrada, 14, False, TINTA, 0, 0)])
        y += 0.6


def main():
    prs = Presentation()
    prs.slide_width = Inches(ANCHO)
    prs.slide_height = Inches(ALTO)
    prs.core_properties.title = "Clase 15 — Investigaciones internacionales, nacionales y locales"
    prs.core_properties.subject = "Arquitectura de Computadoras, UCB sede La Paz"
    prs.core_properties.category = "Clase 15"
    total = 7
    portada(prs, total)
    laboratorio(prs, total)
    tres_niveles(prs, total)
    internacional(prs, total)
    nacional(prs, total)
    local(prs, total)
    bibliografia(prs, total)
    prs.save(SALIDA)
    print(SALIDA)


if __name__ == "__main__":
    main()
