.intel_syntax noprefix

.section .data
a:
    .long   5
b:
    .long   3
c:
    .long   0

formato:
    .asciz  "c = a + b = %d\n"

.section .text
.global main
.extern printf

main:
    push    rbp
    mov     rbp, rsp
    push    rbx
    sub     rsp, 8

    mov     eax, DWORD PTR a[rip]
    mov     ebx, DWORD PTR b[rip]
    add     eax, ebx
    mov     DWORD PTR c[rip], eax

    lea     rdi, formato[rip]
    mov     esi, DWORD PTR c[rip]
    xor     eax, eax
    call    printf

    xor     eax, eax
    add     rsp, 8
    pop     rbx
    pop     rbp
    ret

.section .note.GNU-stack, "", @progbits
