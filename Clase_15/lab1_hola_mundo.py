#!/usr/bin/env python3
"""Práctica 1 — Estado de Bell |Φ⁺⟩ y reto del estado |Ψ⁺⟩.

Guía «Programación Cuántica con Qiskit en Linux Ubuntu».

    python3 lab1_hola_mundo.py              # |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
    python3 lab1_hola_mundo.py --psi-plus   # |Ψ⁺⟩ = (|01⟩ + |10⟩)/√2
"""
import os
import sys
import warnings

# Sin servidor X11 el backend gráfico de matplotlib avisa (FigureCanvasAgg).
# El circuito se dibuja en ASCII, así que no hace falta una ventana.
os.environ.setdefault("MPLBACKEND", "Agg")
# Qiskit 1.4 consulta Instruction.condition (obsoleto desde 1.3) al dibujar
# y al compilar en Aer. El aviso no cambia el resultado; se oculta para que
# la terminal muestre solo el circuito y los conteos de la guía.
warnings.filterwarnings("ignore", category=DeprecationWarning)

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# 10 000 disparos, como pide la guía. La semilla deja quieto el generador
# de Aer: la misma ejecución vuelve a dar los mismos conteos.
SHOTS = 10000
SEMILLA = 42
BASE = ("00", "01", "10", "11")


def construir_circuito(variante):
    """Arma |Φ⁺⟩ o, si variante == 'psi_plus', el reto |Ψ⁺⟩."""
    # 1. Dos cúbits (nacen en |00⟩) y dos bits clásicos para la medición.
    qc = QuantumCircuit(2, 2)
    # 2. Hadamard en q0. Rota π alrededor del eje (X+Z):
    #    |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2. El estado compuesto queda (|00⟩ + |10⟩)/√2.
    qc.h(0)
    # 3. CNOT con control en q0 y objetivo en q1. El control está en
    #    superposición, así que la CNOT entrelaza las dos ramas:
    #    |Φ⁺⟩ = (|00⟩ + |11⟩)/√2.
    qc.cx(0, 1)
    if variante == "psi_plus":
        # Reto práctico 1. Pauli-X sobre q1, después del CNOT:
        #    X|0⟩ = |1⟩ y X|1⟩ = |0⟩, luego
        #    |Φ⁺⟩ → (|01⟩ + |10⟩)/√2 = |Ψ⁺⟩.
        qc.x(1)
    # 4. Medición en la base computacional: colapso y copia a los bits clásicos.
    qc.measure([0, 1], [0, 1])
    return qc


def medir(qc):
    # 6. Aer, el simulador en C++, corre el circuito SHOTS veces.
    backend = AerSimulator(seed_simulator=SEMILLA)
    job = backend.run(qc, shots=SHOTS)
    # 7. Diccionario de conteos. Aer omite las cadenas que no salieron.
    return job.result().get_counts(qc)


def imprimir_conteos(counts):
    # Se listan las cuatro cadenas, también las de cero cuentas, para dejar
    # escrita la ausencia de los estados que el entrelazamiento prohíbe.
    print(f"RESULTADOS DE LA MEDICIÓN ({SHOTS} disparos):")
    for bitstring in BASE:
        count = counts.get(bitstring, 0)
        porcentaje = (count / SHOTS) * 100
        print(f"Estado |{bitstring}⟩: {count} ocurrencias ({porcentaje:.2f}%)")


def verificar(counts, permitidos):
    ok = True
    for bitstring in BASE:
        if bitstring not in permitidos and counts.get(bitstring, 0) != 0:
            print(f"[FALLO] |{bitstring}⟩ apareció y no debería")
            ok = False
    for bitstring in permitidos:
        fraccion = counts.get(bitstring, 0) / SHOTS
        if not 0.45 <= fraccion <= 0.55:
            print(f"[FALLO] |{bitstring}⟩ = {fraccion:.2%} fuera de 45 %–55 %")
            ok = False
    if ok:
        a, b = permitidos
        print(f"[OK] solo |{a}⟩ y |{b}⟩, cerca del 50/50, y el resto en cero")
    return ok


def main(argv):
    if any(arg not in ("--psi-plus",) for arg in argv):
        print("Uso: python3 lab1_hola_mundo.py [--psi-plus]", file=sys.stderr)
        return 2
    variante = "psi_plus" if "--psi-plus" in argv else "phi_plus"
    qc = construir_circuito(variante)
    counts = medir(qc)
    if variante == "phi_plus":
        print("Estado de Bell |Φ⁺⟩ = (|00⟩ + |11⟩)/√2")
    else:
        print("Reto práctico 1: Estado de Bell |Ψ⁺⟩ = (|01⟩ + |10⟩)/√2")
        print("Compuerta Pauli intercalada: X (Pauli-X) sobre el cúbit q1,")
        print("después del CNOT. X cambia |0⟩ por |1⟩ en ese cúbit y |Φ⁺⟩ pasa a |Ψ⁺⟩.")
    # 5. Visualización del circuito en consola (ASCII, sin display gráfico).
    print("CIRCUITO CUÁNTICO:")
    print(qc.draw(output="text"))
    print()
    imprimir_conteos(counts)
    permitidos = ("01", "10") if variante == "psi_plus" else ("00", "11")
    return 0 if verificar(counts, permitidos) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
