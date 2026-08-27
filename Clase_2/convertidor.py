#!/usr/bin/env python3
"""Convertidor de bases y complemento a dos.
Práctica: Sistemas Numéricos y Aritmética Binaria
Autora: Luna Saleth Gallego Martinez
Uso: python3 convertidor.py <numero_entero_decimal>
"""
import sys


def complemento_a_dos(n, bits):
    """Devuelve la representación en complemento a dos de n con 'bits' bits,
    o None si el número no cabe en ese ancho."""
    if -(2 ** (bits - 1)) <= n <= 2 ** (bits - 1) - 1:
        return format(n & (2 ** bits - 1), '0{}b'.format(bits))
    return None


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 convertidor.py <numero_entero_decimal>")
        sys.exit(1)
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Error: debes ingresar un número entero.")
        sys.exit(1)

    print("Número decimal:", n)
    print("Binario      :", format(abs(n), 'b') if n >= 0 else '-' + format(abs(n), 'b'))
    print("Octal        :", format(abs(n), 'o') if n >= 0 else '-' + format(abs(n), 'o'))
    print("Hexadecimal  :", format(abs(n), 'X') if n >= 0 else '-' + format(abs(n), 'X'))

    for bits in (8, 16, 32):
        c2 = complemento_a_dos(n, bits)
        if c2 is not None:
            print("Complemento a dos ({:2d} bits): {}".format(bits, c2))
        else:
            print("Complemento a dos ({:2d} bits): no aplica (fuera de rango)".format(bits))

    # ¿Overflow al representarlo en 8 bits con signo?
    if -128 <= n <= 127:
        print("Overflow en 8 bits con signo: NO (está dentro del rango -128 a 127)")
    else:
        print("Overflow en 8 bits con signo: SÍ (fuera del rango -128 a 127)")


if __name__ == "__main__":
    main()
