#!/usr/bin/env python3
"""Práctica 4 — Teletransportación cuántica (Bennett et al., 1993).

    python3 lab4_teletransportacion.py

q0 es el cúbit de Alice, preparado con Ry(π/3) para que P(|0⟩) = 75 %
y P(|1⟩) = 25 %. q1 y q2 comparten un par de Bell. Alice mide en la base
de Bell y Bob corrige q2. Al medir q2 deben recuperarse esas probabilidades.
"""
import math
import os
import sys
import warnings

os.environ.setdefault("MPLBACKEND", "Agg")
warnings.filterwarnings("ignore", category=DeprecationWarning)

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SHOTS = 10000
SEMILLA = 42


def construir_circuito():
    # Tres cúbits y tres bits clásicos.
    # q0: estado a teletransportar (Alice).
    # q1: mitad del par de Bell, en manos de Alice.
    # q2: la otra mitad, en manos de Bob.
    qc = QuantumCircuit(3, 3)
    # 1. Estado arbitrario en q0. Ry(π/3)|0⟩ = cos(π/6)|0⟩ + sin(π/6)|1⟩
    #    = (√3/2)|0⟩ + (1/2)|1⟩, así P(|0⟩) = 75 % y P(|1⟩) = 25 %.
    qc.ry(math.pi / 3, 0)
    qc.barrier()
    # 2. Par de Bell |Φ⁺⟩ entre Alice (q1) y Bob (q2).
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier()
    # 3. Alice mide en la base de Bell: CNOT y Hadamard, y luego mide.
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()
    qc.measure(0, 0)
    qc.measure(1, 1)
    # 4. Corrección de Bob. En la guía no es una compuerta clásicamente
    #    controlada: después de medir, q0 y q1 ya colapsaron al bit leído,
    #    y el CX/CZ usa ese estado como control. Es el mismo efecto que
    #    aplicar X en q2 si el bit 1 vale 1, y Z en q2 si el bit 0 vale 1.
    qc.barrier()
    qc.cx(1, 2)  # bit 1 = 1 → Pauli-X en el cúbit de Bob
    qc.cz(0, 2)  # bit 0 = 1 → Pauli-Z en el cúbit de Bob
    # 5. Medición de q2 para comprobar que el estado llegó.
    qc.barrier()
    qc.measure(2, 2)
    return qc


def medir(qc):
    backend = AerSimulator(seed_simulator=SEMILLA)
    return backend.run(qc, shots=SHOTS).result().get_counts(qc)


def conteos_bob(counts):
    """Suma el bit de Bob.

    Qiskit escribe la cadena con el bit clásico de mayor índice a la
    izquierda. c2 es la medición de q2, así que el primer carácter es Bob.
    """
    bob = {"0": 0, "1": 0}
    for bitstring, n in counts.items():
        bob[bitstring[0]] += n
    return bob


def main():
    qc = construir_circuito()
    counts = medir(qc)
    bob = conteos_bob(counts)
    p0 = bob["0"] / SHOTS * 100
    p1 = bob["1"] / SHOTS * 100
    print("TELETRANSPORTACIÓN: Ry(π/3) en q0, de Alice hacia Bob (q2)")
    print("Estado teórico en q0: (√3/2)|0⟩ + (1/2)|1⟩ → P(|0⟩) = 75 %, P(|1⟩) = 25 %.")
    print("CIRCUITO CUÁNTICO:")
    print(qc.draw(output="text"))
    print()
    print(f"CONTEOS COMPLETOS ({SHOTS} disparos, bit izquierdo = q2 de Bob):")
    for bitstring in sorted(counts):
        n = counts[bitstring]
        print(f"  |{bitstring}⟩: {n} ({n / SHOTS * 100:.2f}%)")
    print()
    print("VERIFICACIÓN EN EL CÚBIT DE BOB (q2):")
    print(f"P(|0⟩): {p0:.2f}% (Teórico: 75.00%)")
    print(f"P(|1⟩): {p1:.2f}% (Teórico: 25.00%)")
    print(f"cuentas q2: |0⟩ = {bob['0']}, |1⟩ = {bob['1']}")
    if abs(p0 - 75.0) <= 2.0 and abs(p1 - 25.0) <= 2.0 and bob["0"] + bob["1"] == SHOTS:
        print("[OK] el cúbit de Bob queda a menos de 2 puntos de 75/25")
        return 0
    print("[FALLO] el cúbit de Bob no recuperó 75/25")
    return 1


if __name__ == "__main__":
    sys.exit(main())
