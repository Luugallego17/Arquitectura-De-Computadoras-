/*
 * Práctica: sumar un arreglo almacenado en RAM (versión en C)
 * Materia:  Arquitectura de Computadoras
 * Alumna:   Luna Saleth Gallego Martinez
 *
 * El arreglo vive en memoria principal y un bucle lo recorre
 * acumulando cada elemento. Es la misma suma que hace suma_arreglo.s,
 * pero escrita en C para comparar ambos niveles: lo que aquí es un
 * for de tres líneas, en ensamblador son los movs, adds y saltos
 * que ejecuta realmente el procesador.
 *
 * Compilar:  gcc suma_arreglo.c -o suma_arreglo_c
 * Ejecutar:  ./suma_arreglo_c
 */
#include <stdio.h>

int main(void)
{
    int arreglo[] = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100};
    int longitud = sizeof(arreglo) / sizeof(arreglo[0]);
    long suma = 0;

    for (int i = 0; i < longitud; i++) {
        suma += arreglo[i];      /* lee arreglo[i] de RAM y lo acumula */
    }

    printf("La suma del arreglo es: %ld\n", suma);
    return 0;
}
