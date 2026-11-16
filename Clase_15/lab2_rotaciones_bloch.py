#!/usr/bin/env python3
"""Práctica 2 — Rotaciones Ry(θ) en la esfera de Bloch.

    python3 lab2_rotaciones_bloch.py

P(|0⟩) = cos²(θ/2) y P(|1⟩) = sin²(θ/2), con 10 000 disparos en cada ángulo
de la guía: θ = 0, π/4, π/2 y π.
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

# Cuatro posiciones de la guía: polo norte, 45°, ecuador |+⟩ y polo sur.
ANGULOS = [
    (0.0, "Polo Norte (theta = 0)"),
    (math.pi / 4, "Ángulo 45° (theta = pi/4)"),
    (math.pi / 2, "Ecuador (theta = pi/2, Estado |+>)"),
    (math.pi, "Polo Sur (theta = pi, Estado |1>)"),
]


def simular_angulo(theta):
    # 1. Un cúbit y un bit clásico. El cúbit nace en |0⟩, el polo norte.
    qc = QuantumCircuit(1, 1)
    # 2. Ry(θ) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]].
    #    Rota del polo norte hacia el polo sur, en el plano X-Z, con fase nula.
    qc.ry(theta, 0)
    # 3. Proyección sobre el eje Z (base computacional).
    #    P(|0⟩) = |⟨0|ψ⟩|² = cos²(θ/2),  P(|1⟩) = sin²(θ/2).
    qc.measure(0, 0)
    # 4. 10 000 mediciones en Aer.
    backend = AerSimulator(seed_simulator=SEMILLA)
    counts = backend.run(qc, shots=SHOTS).result().get_counts()
    return qc, counts


def teorico(theta):
    """Probabilidades exactas de la regla de Born para Ry(θ)|0⟩."""
    p0 = math.cos(theta / 2) ** 2
    return p0, 1.0 - p0


def main():
    print("ROTACIONES Ry(θ) EN LA ESFERA DE BLOCH")
    print(f"{SHOTS} disparos por ángulo. Teórico: P(|0⟩) = cos²(θ/2), P(|1⟩) = sin²(θ/2).")
    ok = True
    for theta, desc in ANGULOS:
        qc, counts = simular_angulo(theta)
        n0 = counts.get("0", 0)
        n1 = counts.get("1", 0)
        p0 = (n0 / SHOTS) * 100
        p1 = (n1 / SHOTS) * 100
        t0, t1 = teorico(theta)
        print()
        print(desc)
        print("CIRCUITO CUÁNTICO:")
        print(qc.draw(output="text"))
        # Misma forma que la guía, y al lado el valor analítico que pide la tarea.
        print(
            f"{desc:35s} -> P(|0⟩): {p0:5.1f}% | P(|1⟩): {p1:5.1f}%"
            f" | teórico P(|0⟩): {t0 * 100:5.1f}% | P(|1⟩): {t1 * 100:5.1f}%"
        )
        print(f"  cuentas: |0⟩ = {n0}, |1⟩ = {n1}")
        if abs(p0 - t0 * 100) > 2.0 or abs(p1 - t1 * 100) > 2.0:
            print("  [FALLO] la medida se aleja más de 2 puntos del teórico")
            ok = False
        else:
            print("  [OK] a menos de 2 puntos porcentuales del valor teórico")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
