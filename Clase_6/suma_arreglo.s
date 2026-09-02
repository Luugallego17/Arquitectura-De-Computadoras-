.intel_syntax noprefix

.section .data
arreglo:
    .long   10, 20, 30, 40, 50, 60, 70, 80, 90, 100
longitud    = (. - arreglo) / 4

formato:
    .asciz  "La suma del arreglo es: %ld\n"

.section .text
.global main
.extern printf

main:
    push    rbp
    mov     rbp, rsp

    xor     rax, rax
    xor     rcx, rcx
    lea     rsi, arreglo[rip]

bucle:
    movsxd  rdx, DWORD PTR [rsi + rcx*4]
    add     rax, rdx
    inc     rcx
    cmp     rcx, longitud
    jl      bucle

    lea     rdi, formato[rip]
    mov     rsi, rax
    xor     eax, eax
    call    printf

    xor     eax, eax
    pop     rbp
    ret

.section .note.GNU-stack, "", @progbits
