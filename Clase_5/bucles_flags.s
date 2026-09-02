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

.macro imprimir buf, largo
    mov     rax, 1
    mov     rdi, 1
    lea     rsi, \buf[rip]
    mov     rdx, \largo
    syscall
.endm

_start:
    mov     r12, 5
bucle:
    imprimir msj_bucle, largo_bucle
    dec     r12
    jnz     bucle

    mov     rax, 10
    mov     rbx, 10
    cmp     rax, rbx
    je      zf_encendido
    jmp     parte_carry
zf_encendido:
    imprimir msj_zf, largo_zf

parte_carry:
    mov     al, 255
    add     al, 1
    jc      cf_encendido
    jmp     parte_overflow
cf_encendido:
    imprimir msj_cf, largo_cf

parte_overflow:
    mov     al, 127
    add     al, 1
    jo      of_encendido
    jmp     fin
of_encendido:
    imprimir msj_of, largo_of

fin:
    mov     rax, 60
    xor     rdi, rdi
    syscall

.section .note.GNU-stack, "", @progbits
