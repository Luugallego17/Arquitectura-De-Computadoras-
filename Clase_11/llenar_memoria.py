#!/usr/bin/env python3
"""Versión en Python de llenar_memoria.c.

Pide bloques de memoria en un bucle (bytearray lleno con un patrón
distinto de cero, para que cada página ocupe RAM de verdad) hasta llenar
la RAM disponible y obligar al kernel a usar la swap. Después de cada
bloque muestra la RAM disponible y la swap usada, leyendo /proc/meminfo
y /proc/self/status.

Uso:  python3 llenar_memoria.py [--bloque-mb N] [--max-mb N]
                                [--reserva-ram MB] [--reserva-swap MB]
"""

import argparse
import os
import sys
import time

MB = 1024 * 1024


def leer_campo_mb(archivo, campo):
    """Devuelve en MB el valor de una línea 'Campo:   valor kB' de /proc."""
    with open(archivo) as f:
        for linea in f:
            nombre, _, valor = linea.partition(":")
            if nombre == campo:
                return int(valor.split()[0]) // 1024
    return -1


def leer_memoria():
    return {
        "total": leer_campo_mb("/proc/meminfo", "MemTotal"),
        "disponible": leer_campo_mb("/proc/meminfo", "MemAvailable"),
        "swap_total": leer_campo_mb("/proc/meminfo", "SwapTotal"),
        "swap_libre": leer_campo_mb("/proc/meminfo", "SwapFree"),
    }


def main():
    ap = argparse.ArgumentParser(description="Llena la RAM y fuerza el uso de swap.")
    ap.add_argument("--bloque-mb", type=int, default=256)
    ap.add_argument("--max-mb", type=int, default=0, help="0 = sin tope")
    ap.add_argument("--reserva-ram", type=int, default=256)
    ap.add_argument("--reserva-swap", type=int, default=512)
    a = ap.parse_args()

    inicio = leer_memoria()
    swap_inicial = inicio["swap_total"] - inicio["swap_libre"]
    print("=== Llenar la RAM y forzar el uso de swap (Python) ===")
    print(f"PID del proceso      : {os.getpid()}")
    print(f"RAM total            : {inicio['total']} MB")
    print(f"RAM disponible       : {inicio['disponible']} MB")
    print(f"Swap total           : {inicio['swap_total']} MB (usada al inicio: {swap_inicial} MB)")
    print(f"Tamaño de cada bloque: {a.bloque_mb} MB")
    if a.max_mb:
        print(f"Tope de asignación   : {a.max_mb} MB")
    if inicio["swap_total"] == 0:
        print("AVISO: el sistema no tiene swap activa; el programa se detendrá "
              f"al quedar {a.reserva_ram} MB de RAM disponible.")
    print(f"\n{'Bloque':>6} {'Asignado MB':>12} {'RAM disp. MB':>16} "
          f"{'Swap usada':>12} {'VmRSS MB':>10} {'VmSwap MB':>10}", flush=True)

    bloques = []
    asignado = 0
    avisado_swap = False
    motivo = ""
    t0 = time.monotonic()

    try:
        while True:
            if a.max_mb and asignado + a.bloque_mb > a.max_mb:
                motivo = "se alcanzó el tope indicado con --max-mb"
                break
            m = leer_memoria()
            if m["swap_total"] > 0:
                if m["swap_libre"] < a.reserva_swap + a.bloque_mb:
                    motivo = "la swap libre llegó al margen de seguridad"
                    break
            elif m["disponible"] < a.reserva_ram + a.bloque_mb:
                motivo = "la RAM disponible llegó al margen de seguridad (no hay swap)"
                break

            patron = bytes([0xA5 ^ (len(bloques) & 0xFF)])
            bloques.append(bytearray(patron) * (a.bloque_mb * MB))
            asignado += a.bloque_mb

            m = leer_memoria()
            vm_swap = leer_campo_mb("/proc/self/status", "VmSwap")
            print(f"{len(bloques):>6} {asignado:>12} {m['disponible']:>16} "
                  f"{m['swap_total'] - m['swap_libre']:>12} "
                  f"{leer_campo_mb('/proc/self/status', 'VmRSS'):>10} {vm_swap:>10}",
                  flush=True)
            if not avisado_swap and vm_swap > 0:
                print(">>> La RAM se llenó: el kernel empezó a mover páginas de este "
                      "proceso a la swap (VmSwap > 0).", flush=True)
                avisado_swap = True
    except KeyboardInterrupt:
        motivo = "se presionó Ctrl+C"
    except MemoryError:
        motivo = "Python lanzó MemoryError"

    m = leer_memoria()
    print(f"\n=== Fin del bucle: {motivo} ===")
    print(f"Memoria asignada y escrita : {asignado} MB en {len(bloques)} bloques "
          f"({time.monotonic() - t0:.2f} s)")
    print(f"RAM disponible             : {m['disponible']} MB (al inicio {inicio['disponible']} MB)")
    print(f"Swap usada por el sistema  : {m['swap_total'] - m['swap_libre']} MB "
          f"(al inicio {swap_inicial} MB)")
    print(f"VmRSS del proceso (en RAM) : {leer_campo_mb('/proc/self/status', 'VmRSS')} MB")
    print(f"VmSwap del proceso (swap)  : {leer_campo_mb('/proc/self/status', 'VmSwap')} MB")
    if not avisado_swap:
        print("El proceso no llegó a usar swap.")

    if sys.stdin.isatty():
        input("\nPresione ENTER para liberar la memoria y terminar...")
    bloques.clear()
    print("Memoria liberada.")


if __name__ == "__main__":
    main()
