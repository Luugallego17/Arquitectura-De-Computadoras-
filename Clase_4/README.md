# Clase 4 — Overflow en C y primer programa en ensamblador

**Fecha:** 24/08/2026
**Tarea:** [#6 — Práctica C: overflow y ensamblador](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/6)

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`overflow_mensajes.c`](overflow_mensajes.c) | Suma números de 8 bits con signo y **muestra un mensaje cuando se genera overflow** (dos positivos que dan negativo o dos negativos que dan positivo). |
| [`hola.s`](hola.s) | Primer programa en **ensamblador x86-64** (sintaxis Intel): imprime un mensaje usando directamente las syscalls `write` y `exit` de Linux. |

## Cómo compilar y ejecutar

```bash
# Programa en C con mensajes de overflow
gcc overflow_mensajes.c -o overflow_mensajes
./overflow_mensajes

# Programa en ensamblador
as hola.s -o hola.o
ld hola.o -o hola
./hola
```

## Salida del programa en C

```
Sumas en 8 bits con signo (rango: -128 a 127)

 100 +   27 =  127   sin overflow
 120 +   20 = -116   ¡OVERFLOW! dos positivos dieron negativo
 127 +    1 = -128   ¡OVERFLOW! dos positivos dieron negativo
-100 +  -50 =  106   ¡OVERFLOW! dos negativos dieron positivo
-128 +    1 = -127   sin overflow
  -1 +    1 =    0   sin overflow
```

## Salida del programa en ensamblador

```
Hola desde ensamblador :3
```

> 🖼️ La evidencia original de la clase está en los comentarios del issue
> [#6](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/6).
