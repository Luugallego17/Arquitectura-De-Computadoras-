# Clase 8 — Tiempo de CPU, CPI y el ciclo de instrucción

**Fecha:** 07/09/2026
**Tareas:** [#15 — Tiempo de CPU y CPI: traducir x = x + 2 a ensamblador](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/15) · [#16 — Ciclo Fetch-Decode-Execute-Write-Back: de C++ a ensamblador](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/16)

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`x_mas_2.s`](x_mas_2.s) | La traducción del pizarrón: `x = x + 2` en ensamblador (`MOV EAX, [x]` → `ADD EAX, 2` → `MOV [x], EAX`), funcionando en x86-64. |
| [`tiempo_cpu.c`](tiempo_cpu.c) | El ejemplo del `if/else` con los ciclos de cada instrucción: ejecuta las dos ramas y calcula **NI**, **CPI** y **T_CPU** de cada una. |
| [`suma_ab.cpp`](suma_ab.cpp) | El programa de la diapositiva: `int a = 5; int b = 3; int c = a + b;`. |
| [`suma_ab.s`](suma_ab.s) | La misma suma en ensamblador con las cuatro instrucciones de la diapositiva: `mov eax, [a]`, `mov ebx, [b]`, `add eax, ebx`, `mov [c], eax`. |

## Parte 1 — Tiempo de CPU y CPI (tarea #15)

La fórmula de la latencia (tiempo de CPU) es:

```
T_CPU = NI × CPI × Tc
```

- **NI** — número de instrucciones ejecutadas en un programa.
- **CPI** — ciclos por instrucción (promedio).
- **Tc** — duración del ciclo máquina.

El punto clave de la clase: **el CPI depende de la mezcla de
instrucciones que realmente se ejecuta**, no del código fuente. En el
ejemplo del pizarrón:

```c
x = x + 2;          /* 3 ciclos */
if ( x == 10 ) {    /* 4 ciclos */
    x = x - 2;      /* 4 ciclos */
} else {
    x = x + 4;      /* 3 ciclos */
    y = 0;          /* 3 ciclos */
}
```

- Si se toma la rama del `if`: `CPI = (3 + 4 + 4) / 3 ≈ 3.67`
- Si se toma la rama del `else`: `CPI = (3 + 4 + 3 + 3) / 4 = 3.25`

**El mismo código tiene dos CPI distintos dependiendo de la ejecución.**
`tiempo_cpu.c` ejecuta las dos ramas (empezando con `x = 8`, que cae en
el `if`, y con `x = 3`, que cae en el `else`) y calcula el CPI y el
T_CPU de cada una con `Tc = 0.5 ns`.

La primera línea (`x = x + 2`) es justo la que tradujimos a mano en el
pizarrón, y está funcionando en [`x_mas_2.s`](x_mas_2.s):

```asm
mov     eax, DWORD PTR x[rip]   ; MOV EAX, [x]
add     eax, 2                  ; ADD EAX, 2
mov     DWORD PTR x[rip], eax   ; MOV [x], EAX
```

Una sola línea de C son **tres** instrucciones de máquina: leer de RAM,
operar en la ALU y escribir de vuelta a RAM. Por eso "3 ciclos".

## Parte 2 — Conexión con C++ y ASM (tarea #16)

El programa `int a = 5; int b = 3; int c = a + b;` se compila a cuatro
instrucciones, y cada una pasa por el ciclo de instrucción:

| Instrucción | Fetch | Decode | Execute | Write-Back |
|-------------|-------|--------|---------|------------|
| `mov eax, [a]` | Busca la instrucción | Es una carga de memoria | Carga el valor de `a` | El 5 queda en `eax` |
| `mov ebx, [b]` | Busca la instrucción | Es una carga de memoria | Carga el valor de `b` | El 3 queda en `ebx` |
| `add eax, ebx` | Busca la instrucción | Es una suma | La ALU suma `eax` + `ebx` (5+3) | El 8 queda en `eax` |
| `mov [c], eax` | Busca la instrucción | Es un almacenamiento | Mueve `eax` a la dirección de `c` | El 8 queda en la memoria de `c` |

Las dos versiones ([`suma_ab.cpp`](suma_ab.cpp) y
[`suma_ab.s`](suma_ab.s)) imprimen lo mismo, porque son el mismo
programa: una escrita para humanos y otra escrita como la ejecuta el
procesador.

## Cómo compilar y ejecutar

```bash
# x = x + 2 en ensamblador
gcc x_mas_2.s -no-pie -o x_mas_2
./x_mas_2

# CPI y tiempo de CPU
gcc tiempo_cpu.c -o tiempo_cpu
./tiempo_cpu

# c = a + b en C++
g++ suma_ab.cpp -o suma_ab_cpp
./suma_ab_cpp

# c = a + b en ensamblador
gcc suma_ab.s -no-pie -o suma_ab
./suma_ab
```

## Salidas

```
x = 10
```

```
--- x inicial = 8 ---
x final = 8, y final = 5
NI = 3, ciclos = 11
CPI = 11 / 3 = 3.67
T_CPU = NI x CPI x Tc = 3 x 3.67 x 0.5 ns = 5.5 ns

--- x inicial = 3 ---
x final = 9, y final = 0
NI = 4, ciclos = 13
CPI = 13 / 4 = 3.25
T_CPU = NI x CPI x Tc = 4 x 3.25 x 0.5 ns = 6.5 ns
```

```
c = a + b = 8
```

> 🖼️ Las fotos originales del pizarrón y las diapositivas están en los
> comentarios de los issues
> [#15](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/15) y
> [#16](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/16).
