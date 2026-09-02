# Práctica: bucles, bifurcaciones y flags (ZF, CF, OF)
# Materia:  Arquitectura de Computadoras
# Alumna:   Luna Saleth Gallego Martinez
#
# Cuatro partes:
#   1. Un bucle que imprime un mensaje 5 veces (dec + jnz).
#   2. Zero Flag  (ZF): cmp de dos valores iguales y salto je.
#   3. Carry Flag (CF): 255 + 1 en 8 bits sin signo y salto jc.
#   4. Overflow   (OF): 127 + 1 en 8 bits con signo y salto jo.
#
# Los saltos condicionales son las "bifurcaciones": el procesador decide
# a dónde saltar leyendo las banderas que dejó la última operación.
#
# Ensamblar y enlazar:
#   as bucles_flags.s -o bucles_flags.o
#   ld bucles_flags.o -o bucles_flags
#   ./bucles_flags

.intel_syntax noprefix

.section .data
msj_bucle:      .ascii "iteracion del bucle\n"
largo_bucle     = . - msj_bucle

msj_zf:         .ascii "ZF=1: los valores son iguales (resultado cero)\n"
largo_zf        = . - msj_zf

msj_cf:         .ascii "CF=1: 255 + 1 no cabe en 8 bits sin signo (carry)\n"
largo_cf        = . - msj_cf

msj_of:         .ascii "OF=1: 127 + 1 desborda los 8 bits con signo (overflow)\n"
largo_of        = . - msj_of

.section .text
.global _start

# --- macro casera: imprimir usando write(1, buf, largo) -----------
# (para no repetir las 4 instrucciones en cada parte)
.macro imprimir buf, largo
    mov     rax, 1
    mov     rdi, 1
    lea     rsi, \buf[rip]
    mov     rdx, \largo
    syscall
.endm

_start:
# ---- Parte 1: bucle ----------------------------------------------
# r12 es el contador; dec lo baja en 1 y jnz salta mientras no sea 0.
    mov     r12, 5
bucle:
    imprimir msj_bucle, largo_bucle
    dec     r12                  # r12 = r12 - 1 (actualiza ZF)
    jnz     bucle                # bifurcación: repite si ZF == 0

# ---- Parte 2: Zero Flag ------------------------------------------
# cmp hace una resta interna: 10 - 10 = 0, así que enciende ZF.
    mov     rax, 10
    mov     rbx, 10
    cmp     rax, rbx
    je      zf_encendido         # salta si ZF == 1
    jmp     parte_carry
zf_encendido:
    imprimir msj_zf, largo_zf

# ---- Parte 3: Carry Flag -----------------------------------------
# En 8 bits sin signo 255 + 1 = 256, que no cabe: el bit extra "se cae"
# por la izquierda y enciende CF.
parte_carry:
    mov     al, 255
    add     al, 1
    jc      cf_encendido         # salta si CF == 1
    jmp     parte_overflow
cf_encendido:
    imprimir msj_cf, largo_cf

# ---- Parte 4: Overflow Flag --------------------------------------
# En 8 bits con signo 127 es el máximo: 127 + 1 da -128, dos positivos
# dieron negativo y eso enciende OF.
parte_overflow:
    mov     al, 127
    add     al, 1
    jo      of_encendido         # salta si OF == 1
    jmp     fin
of_encendido:
    imprimir msj_of, largo_of

# ---- exit(0) ------------------------------------------------------
fin:
    mov     rax, 60
    xor     rdi, rdi
    syscall

# marca la pila como no ejecutable (evita una advertencia del enlazador)
.section .note.GNU-stack, "", @progbits
