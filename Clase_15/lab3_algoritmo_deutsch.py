#!/usr/bin/env python3
"""Práctica 3 — Algoritmo de Deutsch y reto del phase kickback.

    python3 lab3_algoritmo_deutsch.py

Una sola consulta al oráculo clasifica f:{0,1}→{0,1}:
medición de q0 igual a '0' → CONSTANTE, '1' → BALANCEADA.

Al final se repite el circuito sin la X de la ancilla (reto práctico 2)
para mostrar que, sin |−⟩, el phase kickback no distingue las funciones.
"""
import os
import sys
import warnings

os.environ.setdefault("MPLBACKEND", "Agg")
warnings.filterwarnings("ignore", category=DeprecationWarning)

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# La guía usa 1 000 disparos. Aquí son 10 000, como en el resto del
# laboratorio: el algoritmo es determinista y el bit no cambia.
SHOTS = 10000
SEMILLA = 42
CASOS = (
    "constante_0",
    "constante_1",
    "balanceada_identidad",
    "balanceada_inversa",
)
ESPERADO = {
    "constante_0": "0",
    "constante_1": "0",
    "balanceada_identidad": "1",
    "balanceada_inversa": "1",
}


def construir_oraculo(tipo):
    """U_f |x⟩|y⟩ = |x⟩|y ⊕ f(x)⟩ para cada una de las cuatro f booleanas."""
    oraculo = QuantumCircuit(2, name=f"U_f ({tipo})")
    if tipo == "constante_0":
        pass  # f(x) = 0. El oráculo es la identidad.
    elif tipo == "constante_1":
        oraculo.x(1)  # f(x) = 1. Voltea la ancilla para cualquier x.
    elif tipo == "balanceada_identidad":
        oraculo.cx(0, 1)  # f(x) = x.
    elif tipo == "balanceada_inversa":
        oraculo.x(0)
        oraculo.cx(0, 1)
        oraculo.x(0)  # f(x) = NOT x. Las X enmarcan el CNOT.
    else:
        raise ValueError(tipo)
    return oraculo


def ejecutar_deutsch(tipo, con_x_ancilla=True):
    qc = QuantumCircuit(2, 1)
    if con_x_ancilla:
        # 1. Ancilla q1 en |1⟩. Sin esta X, q1 sigue en |0⟩ y el Hadamard
        #    siguiente produce |+⟩ en lugar de |−⟩: no hay phase kickback.
        qc.x(1)
    # 2. Superposición dual. q0 → |+⟩. q1 → |−⟩ si hubo X, o |+⟩ si no.
    #    |−⟩ es el autoestado de X con autovalor −1, y eso es lo que hace
    #    rebotar f(x) como fase: U_f |x⟩|−⟩ = (−1)^f(x) |x⟩|−⟩.
    qc.h(0)
    qc.h(1)
    # 3. Una sola consulta al oráculo.
    qc.compose(construir_oraculo(tipo), inplace=True)
    # 4. El segundo Hadamard interfiere q0 y se mide ese cúbit.
    #    Constante → |0⟩. Balanceada → |1⟩.
    qc.h(0)
    qc.measure(0, 0)
    counts = AerSimulator(seed_simulator=SEMILLA).run(qc, shots=SHOTS).result().get_counts()
    return qc, counts


def bit_medido(counts):
    """El resultado de q0. Con el simulador ideal solo aparece un bit."""
    return max(counts, key=counts.get)


def informar(tipo, counts):
    bit = bit_medido(counts)
    conclusion = "CONSTANTE" if bit == "0" else "BALANCEADA"
    n = counts.get(bit, 0)
    print(
        f"Oráculo: {tipo:22s} | Medición q0: '{bit}' -> Función {conclusion}"
        f" | {n}/{SHOTS}"
    )
    return bit


def main():
    print("ALGORITMO DE DEUTSCH (ancilla en |−⟩, phase kickback activo)")
    print(f"{SHOTS} disparos por oráculo. Una consulta decide constante o balanceada.")
    ok = True
    for caso in CASOS:
        qc, counts = ejecutar_deutsch(caso, con_x_ancilla=True)
        print()
        print(f"CIRCUITO CUÁNTICO ({caso}):")
        print(qc.draw(output="text"))
        bit = informar(caso, counts)
        if bit == ESPERADO[caso] and counts.get(bit, 0) == SHOTS:
            print("  [OK] el bit coincide con la guía y salió en los", SHOTS, "disparos")
        else:
            print(f"  [FALLO] se esperaba '{ESPERADO[caso]}' en los {SHOTS} disparos, salió {counts}")
            ok = False

    print()
    print("RETO PRÁCTICO 2: sin la compuerta X sobre la ancilla q1")
    print("q1 queda en |+⟩. U_f no pega el signo (−1)^f(x) y el segundo")
    print("Hadamard devuelve q0 a |0⟩ para las cuatro funciones.")
    for caso in CASOS:
        _qc, counts = ejecutar_deutsch(caso, con_x_ancilla=False)
        bit = informar(caso, counts)
        if bit == "0" and counts.get("0", 0) == SHOTS:
            print("  [OK] sin phase kickback la medición es '0' (el algoritmo no distingue)")
        else:
            print(f"  [FALLO] sin la X se esperaba '0' en todos los disparos, salió {counts}")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
