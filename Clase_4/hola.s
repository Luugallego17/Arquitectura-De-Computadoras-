.intel_syntax noprefix

.section .data
mensaje:
    .ascii "Hola desde ensamblador :3\n"
    largo = . - mensaje

.section .text
.global _start

_start:
    mov     rax, 1
    mov     rdi, 1
    lea     rsi, mensaje[rip]
    mov     rdx, largo
    syscall

    mov     rax, 60
    xor     rdi, rdi
    syscall

.section .note.GNU-stack, "", @progbits
