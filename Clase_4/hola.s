# Práctica: primer programa en ensamblador (x86-64, sintaxis Intel)
# Materia:  Arquitectura de Computadoras
# Alumna:   Luna Saleth Gallego Martinez
#
# Imprime un mensaje usando directamente las llamadas al sistema de
# Linux (sys_write y sys_exit), sin pasar por la biblioteca de C.
#
# Ensamblar y enlazar:
#   as hola.s -o hola.o
#   ld hola.o -o hola
#   ./hola

.intel_syntax noprefix

.section .data
mensaje:
    .ascii "Hola desde ensamblador :3\n"
    largo = . - mensaje          # el punto es "aquí": largo del mensaje

.section .text
.global _start

_start:
    # write(1, mensaje, largo)
    mov     rax, 1               # número de la syscall write
    mov     rdi, 1               # descriptor 1 = salida estándar
    lea     rsi, mensaje[rip]    # dirección del mensaje
    mov     rdx, largo           # cuántos bytes escribir
    syscall

    # exit(0)
    mov     rax, 60              # número de la syscall exit
    xor     rdi, rdi             # código de salida 0
    syscall

# marca la pila como no ejecutable (evita una advertencia del enlazador)
.section .note.GNU-stack, "", @progbits
