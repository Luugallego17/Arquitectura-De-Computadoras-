# Práctica: Sistemas Numéricos y Aritmética Binaria

**Materia:** Arquitectura de Computadoras
**Alumna:** Luna Saleth Gallego Martinez
**Fecha:** 05/08/2026

---

## Nivel 1 — Conversión de bases

**1.1 Decimal a binario**

Fui dividiendo cada número entre 2 y tomando los residuos de abajo hacia arriba.

- 45 = `101101`
- 128 = `10000000`
- 255 = `11111111`
- 1000 = `1111101000`

**1.2 Binario a decimal**

Sumé el valor de cada posición donde hay un 1 (1, 2, 4, 8, 16...).

- `1011` = 8 + 2 + 1 = 11
- `10110110` = 128 + 32 + 16 + 4 + 2 = 182
- `11111111` = 255
- `100000000` = 256

**1.3 Binario a hexadecimal**

Agrupé los bits de 4 en 4 empezando por la derecha y convertí cada grupo.

- `1010 1100` = AC
- `1111 0000 1111` = F0F
- `1010 1010 1010 1010` = AAAA

**1.4 Octal a decimal**

Cada dígito se multiplica por potencias de 8.

- 17 = 1×8 + 7 = 15
- 254 = 2×64 + 5×8 + 4 = 172
- 777 = 7×64 + 7×8 + 7 = 511

---

## Nivel 2 — Aritmética binaria básica

**2.1 Sumas** (los acarreos van arriba)

```
   111            11111
   1011 (11)      11101 (29)
 + 0110 ( 6)    + 01011 (11)
 ------         -------
  10001 (17)    101000 (40)
```

Igual que sumar en decimal, solo que aquí 1 + 1 = 10, así que se escribe 0 y se lleva 1.

**2.2 Restas** (con préstamo)

```
   1100 (12)      10000 (16)
 - 0101 ( 5)    - 00111 ( 7)
 ------         -------
   0111 ( 7)      01001 ( 9)
```

Cuando toca hacer 0 − 1 se pide préstamo a la columna de la izquierda, como en las restas normales.

**2.3 Multiplicación**

```
      1011 (11)
    × 0101 ( 5)
    ------
      1011
     0000
    1011
  --------
    110111 (55)
```

Se multiplica igual que en decimal: una fila por cada dígito, recorriendo una posición, y al final se suman.

---

## Nivel 3 — Complemento a dos (8 bits)

**3.1**

Para los negativos usé la regla: escribir el positivo, invertir todos los bits y sumar 1. Los positivos se escriben directo.

- −45 → 45 = `00101101` → invierto `11010010` → +1 = **`11010011`**
- −1 → 1 = `00000001` → invierto `11111110` → +1 = **`11111111`**
- −128 → es el caso especial, el límite del rango: **`10000000`**
- 27 → es positivo, va directo: **`00011011`**

**3.2**

`11010110` empieza con 1, así que es negativo. Para saber cuánto vale hago el proceso al revés: invierto (`00101001`) y sumo 1 (`00101010` = 42).

Respuesta: **−42**

**3.3** Resta 45 − 60

La computadora no resta, convierte la resta en suma: 45 + (−60).

Primero saqué el −60: 60 = `00111100` → invierto → +1 → `11000100`. Y sumé:

```
   00101101 ( 45)
 + 11000100 (−60)
 ----------
   11110001
```

El resultado empieza en 1 (negativo). Lo decodifico: invierto y sumo 1, me da 15. O sea el resultado es **−15**, que es correcto porque 45 − 60 = −15.

---

## Nivel 4 — Overflow y banderas

**4.1**

- `01111111 + 00000001` = `10000000`. O sea 127 + 1 dio −128. **Sí hay overflow**, porque sumé dos positivos y me dio negativo, lo cual es imposible.
- `10000000 + 11111111` = `01111111` (y un carry que se descarta). O sea −128 − 1 dio +127. **Sí hay overflow**, dos negativos dieron positivo.

**4.2 Diferencia entre carry y overflow (con mis palabras)**

El carry es el bit que se "cae" por la izquierda cuando el resultado ya no cabe en el registro, y es importante cuando los números se leen sin signo. El overflow es cuando el resultado sale con un signo que no tiene sentido (dos positivos dan negativo o dos negativos dan positivo), y aplica cuando los números se leen con signo. No son lo mismo, y uno puede aparecer sin el otro.

Ejemplos con 4 bits:

- `1111 + 0001 = 1|0000` → hay carry (se cayó un bit) pero no hay overflow, porque con signo la cuenta es (−1) + 1 = 0 y eso está bien.
- `0111 + 0001 = 1000` → no hay carry, pero sí overflow: 7 + 1 debería dar 8, pero salió −8.

**4.3 Programa en C**

`overflow.c`:

```c
#include <stdio.h>
#include <stdint.h>

int main(void) {
    int8_t a = 120, b = 20;
    int8_t suma = a + b;
    printf("a + b = %d\n", suma);
    return 0;
}
```

Lo compilé y ejecuté en Ubuntu:

```bash
osboxes@osboxes:~/Downloads/practica_archivos$ gcc -o overflow overflow.c
osboxes@osboxes:~/Downloads/practica_archivos$ ./overflow
a + b = -116
```

**¿Por qué no imprime 140?** Porque un `int8_t` solo llega hasta 127. El 140 no cabe, y sus bits (`10001100`) invaden el bit del signo, así que el programa lo lee como número negativo: 140 − 256 = −116. Es el mismo overflow del ejercicio 4.1 pero visto en un programa real.

---

## Nivel 5 — Punto flotante (IEEE 754)

**5.1 Representar 10.25**

Primero lo pasé a binario: 10 = `1010` y 0.25 = `.01` (porque el segundo bit después del punto vale 0.25). Queda `1010.01`.

Después moví el punto para dejar un solo 1 adelante: `1.01001 × 2³` (lo moví 3 lugares).

Y llené los tres campos:

- Signo: `0` (es positivo)
- Exponente: 3 + 127 = 130 = `10000010` (siempre se le suma 127)
- Mantisa: lo que quedó después del punto, rellenado con ceros: `01001000000000000000000` (el 1 de adelante no se guarda porque siempre es 1)

Resultado: `0 10000010 01001000000000000000000`

**5.2 Decodificar `1 10000010 01100000000000000000000`**

- Signo = 1 → negativo
- Exponente = `10000010` = 130, le resto 127 → 3
- Mantisa: le pongo el 1. adelante → `1.011` = 1 + 0.25 + 0.125 = 1.375

Valor = −1.375 × 2³ = **−11.0**

**5.3 Pérdida de precisión**

Igual que 1/3 en decimal es 0.3333... infinito, el 0.1 en binario también es infinito, pero la mantisa tiene bits limitados, así que la computadora lo corta y guarda una aproximación. Por eso al sumar se nota el error:

```python
>>> 0.1 + 0.2
0.30000000000000004
```

No da exactamente 0.3 porque ni 0.1 ni 0.2 se pueden guardar exactos en binario.

---

## Nivel 6 — Script de verificación

**6.1**

Hice el script en Python. Recibe un número y hace lo de los niveles 1, 3 y 4 automáticamente: lo convierte a binario, octal y hexadecimal, saca su complemento a dos en 8, 16 y 32 bits (si cabe), y dice si habría overflow en 8 bits con signo.

`convertidor.py`:

```python
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
```

Lo probé en Ubuntu con los casos límite (127 y −128 son los últimos que caben en 8 bits, 128 y −129 ya no caben, y el 0 de control):

```
osboxes@osboxes:~/Downloads/practica_archivos$ python3 convertidor.py 127
Número decimal: 127
Binario      : 1111111
Octal        : 177
Hexadecimal  : 7F
Complemento a dos ( 8 bits): 01111111
Complemento a dos (16 bits): 0000000001111111
Complemento a dos (32 bits): 00000000000000000000000001111111
Overflow en 8 bits con signo: NO (está dentro del rango -128 a 127)

osboxes@osboxes:~/Downloads/practica_archivos$ python3 convertidor.py 128
Número decimal: 128
Binario      : 10000000
Octal        : 200
Hexadecimal  : 80
Complemento a dos ( 8 bits): no aplica (fuera de rango)
Complemento a dos (16 bits): 0000000010000000
Complemento a dos (32 bits): 00000000000000000000000010000000
Overflow en 8 bits con signo: SÍ (fuera del rango -128 a 127)

osboxes@osboxes:~/Downloads/practica_archivos$ python3 convertidor.py -128
Número decimal: -128
Binario      : -10000000
Octal        : -200
Hexadecimal  : -80
Complemento a dos ( 8 bits): 10000000
Complemento a dos (16 bits): 1111111110000000
Complemento a dos (32 bits): 11111111111111111111111110000000
Overflow en 8 bits con signo: NO (está dentro del rango -128 a 127)

osboxes@osboxes:~/Downloads/practica_archivos$ python3 convertidor.py -129
Número decimal: -129
Binario      : -10000001
Octal        : -201
Hexadecimal  : -81
Complemento a dos ( 8 bits): no aplica (fuera de rango)
Complemento a dos (16 bits): 1111111101111111
Complemento a dos (32 bits): 11111111111111111111111101111111
Overflow en 8 bits con signo: SÍ (fuera del rango -128 a 127)

osboxes@osboxes:~/Downloads/practica_archivos$ python3 convertidor.py 0
Número decimal: 0
Binario      : 0
Octal        : 0
Hexadecimal  : 0
Complemento a dos ( 8 bits): 00000000
Complemento a dos (16 bits): 0000000000000000
Complemento a dos (32 bits): 00000000000000000000000000000000
Overflow en 8 bits con signo: NO (está dentro del rango -128 a 127)
```

**6.2**

Si un sensor guarda la temperatura en 8 bits con signo, solo puede representar de −128 a 127. Si la temperatura real llega por ejemplo a 130 °C, los bits dan la vuelta y el sistema leería −126 °C, sin marcar ningún error. A eso se le llama overflow silencioso. En un sistema embebido esto es muy peligroso, porque el software pensaría que el aparato está congelado justo cuando en realidad se está sobrecalentando, y podría hasta apagar el ventilador o prender la calefacción, empeorando todo hasta dañar el equipo o causar un accidente. Por eso hay que elegir tipos de datos con rango suficiente para lo que se va a medir y validar que las lecturas estén dentro de los límites.
