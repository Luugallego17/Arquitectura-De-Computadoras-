.intel_syntax noprefix

.section .data
x:
    .long   8

formato:
    .asciz  "x = %d\n"

.section .text
.global main
.extern printf

main:
    push    rbp
    mov     rbp, rsp

    mov     eax, DWORD PTR x[rip]
    add     eax, 2
    mov     DWORD PTR x[rip], eax

    lea     rdi, formato[rip]
    mov     esi, DWORD PTR x[rip]
    xor     eax, eax
    call    printf

    xor     eax, eax
    pop     rbp
    ret

.section .note.GNU-stack, "", @progbits
