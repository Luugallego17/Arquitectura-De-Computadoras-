# Clase 6 — Suma de un arreglo almacenado en RAM

**Fecha:** 31/08/2026
**Tarea:** [#8 — Sumar un arreglo almacenado en RAM](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/8)

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`suma_arreglo.c`](suma_arreglo.c) | La suma en **C**: un `for` recorre el arreglo en RAM acumulando cada elemento. |
| [`suma_arreglo.s`](suma_arreglo.s) | **La misma suma en ensamblador x86-64**: el arreglo vive en la sección `.data` (memoria principal), un bucle lo recorre leyendo cada elemento de RAM y acumulando en un registro, y el resultado se imprime con `printf`. |

Tener las dos versiones lado a lado deja ver qué hace realmente el
procesador: el `for` de tres líneas de C se convierte en los `mov`,
`add`, `cmp` y saltos del ensamblador.

## Idea de la práctica

El arreglo está **en memoria** (sección `.data`) y el acumulador está
**en un registro** (`rax`). En cada vuelta del bucle el procesador:

1. Lee `arreglo[rcx]` de RAM con direccionamiento base + índice×4
   (`[rsi + rcx*4]`).
2. Lo suma al acumulador (`add rax, rdx`).
3. Incrementa el índice y compara contra la longitud (`cmp` + `jl`).

Es decir, cada iteración es un viaje RAM → registro → ALU, que es
exactamente el ciclo que estudiamos: la memoria guarda los datos y el
procesador opera sobre copias en registros.

## Cómo compilar y ejecutar

```bash
# Versión en C
gcc suma_arreglo.c -o suma_arreglo_c
./suma_arreglo_c

# Versión en ensamblador
gcc suma_arreglo.s -no-pie -o suma_arreglo
./suma_arreglo
```

## Salida (idéntica en las dos versiones)

```
La suma del arreglo es: 550
```

(El arreglo es 10, 20, 30, ..., 100, así que 550 es el resultado esperado.)

> 🖼️ Las capturas originales del código y su ejecución están en los
> comentarios del issue
> [#8](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/8).
