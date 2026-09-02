# Práctica: sumar un arreglo almacenado en RAM
# Materia:  Arquitectura de Computadoras
# Alumna:   Luna Saleth Gallego Martinez
#
# El arreglo vive en la sección .data (memoria principal). Un bucle lo
# recorre acumulando cada elemento en un registro y al final se imprime
# el resultado con printf de la biblioteca de C.
#
# Compilar y ejecutar:
#   gcc suma_arreglo.s -no-pie -o suma_arreglo
#   ./suma_arreglo

.intel_syntax noprefix

.section .data
arreglo:
    .long   10, 20, 30, 40, 50, 60, 70, 80, 90, 100
longitud    = (. - arreglo) / 4      # cuántos enteros de 4 bytes hay

formato:
    .asciz  "La suma del arreglo es: %ld\n"

.section .text
.global main
.extern printf

main:
    push    rbp                      # prólogo (deja la pila alineada)
    mov     rbp, rsp

    xor     rax, rax                 # rax = acumulador de la suma
    xor     rcx, rcx                 # rcx = índice del arreglo
    lea     rsi, arreglo[rip]        # rsi = dirección base del arreglo

bucle:
    movsxd  rdx, DWORD PTR [rsi + rcx*4]   # rdx = arreglo[rcx] (leído de RAM)
    add     rax, rdx                 # suma += arreglo[rcx]
    inc     rcx                      # siguiente índice
    cmp     rcx, longitud
    jl      bucle                    # repetir mientras rcx < longitud

    # printf(formato, suma)
    lea     rdi, formato[rip]        # 1er argumento: la cadena de formato
    mov     rsi, rax                 # 2do argumento: la suma
    xor     eax, eax                 # 0 argumentos en registros vectoriales
    call    printf

    xor     eax, eax                 # return 0
    pop     rbp
    ret

# marca la pila como no ejecutable (evita una advertencia del enlazador)
.section .note.GNU-stack, "", @progbits
