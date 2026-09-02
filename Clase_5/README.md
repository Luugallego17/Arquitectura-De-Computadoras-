# Clase 5 — Bucles, bifurcaciones y flags (ZF, CF, OF)

**Fecha:** 26/08/2026
**Tarea:** [#7 — Bucles, Bifurcaciones y Flags](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/7)

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`bucles_flags.s`](bucles_flags.s) | Programa en ensamblador x86-64 con las 4 partes de la práctica: un bucle con `dec`/`jnz`, y la evaluación del **Zero Flag**, el **Carry Flag** y el **Overflow Flag** con saltos condicionales. |

## Idea de la práctica

Las **banderas (flags)** son bits del registro de estado que el
procesador enciende o apaga según el resultado de la última operación,
y las **bifurcaciones** son los saltos condicionales que las leen:

| Bandera | Se enciende cuando... | Salto que la lee |
|---------|----------------------|------------------|
| **ZF** (Zero) | el resultado fue cero (p. ej. `cmp` de dos iguales) | `je` / `jz` |
| **CF** (Carry) | la suma sin signo no cupo y un bit "se cayó" (255 + 1 en 8 bits) | `jc` |
| **OF** (Overflow) | la suma con signo cambió de signo sin sentido (127 + 1 = −128) | `jo` |

Los bucles se arman con esas mismas piezas: `dec` baja el contador y
actualiza ZF, y `jnz` repite el cuerpo mientras el contador no llegue
a cero.

## Cómo ensamblar y ejecutar

```bash
as bucles_flags.s -o bucles_flags.o
ld bucles_flags.o -o bucles_flags
./bucles_flags
```

## Salida

```
iteracion del bucle
iteracion del bucle
iteracion del bucle
iteracion del bucle
iteracion del bucle
ZF=1: los valores son iguales (resultado cero)
CF=1: 255 + 1 no cabe en 8 bits sin signo (carry)
OF=1: 127 + 1 desborda los 8 bits con signo (overflow)
```

> 🖼️ Las capturas originales de la clase (primera y segunda parte, Carry
> Flag y Overflow) están en los comentarios del issue
> [#7](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/7).
