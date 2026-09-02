/*
 * Práctica: overflow con mensajes de aviso
 * Materia:  Arquitectura de Computadoras
 * Alumna:   Luna Saleth Gallego Martinez
 *
 * Suma dos números de 8 bits con signo (int8_t) y avisa por consola
 * cuando la suma genera overflow: dos positivos que dan negativo o
 * dos negativos que dan positivo.
 *
 * Compilar:  gcc overflow_mensajes.c -o overflow_mensajes
 * Ejecutar:  ./overflow_mensajes
 */
#include <stdio.h>
#include <stdint.h>

/* Suma a + b en 8 bits e imprime el resultado, avisando si hubo overflow. */
void sumar_con_aviso(int8_t a, int8_t b)
{
    int8_t resultado = (int8_t)(a + b);

    printf("%4d + %4d = %4d", a, b, resultado);

    if (a > 0 && b > 0 && resultado < 0) {
        printf("   ¡OVERFLOW! dos positivos dieron negativo\n");
    } else if (a < 0 && b < 0 && resultado >= 0) {
        printf("   ¡OVERFLOW! dos negativos dieron positivo\n");
    } else {
        printf("   sin overflow\n");
    }
}

int main(void)
{
    printf("Sumas en 8 bits con signo (rango: -128 a 127)\n\n");

    sumar_con_aviso(100, 27);    /* 127: justo en el límite, sin overflow  */
    sumar_con_aviso(120, 20);    /* 140 no cabe -> -116, overflow          */
    sumar_con_aviso(127, 1);     /* el clásico: 127 + 1 = -128             */
    sumar_con_aviso(-100, -50);  /* -150 no cabe -> 106, overflow          */
    sumar_con_aviso(-128, 1);    /* -127: sin overflow                     */
    sumar_con_aviso(-1, 1);      /* 0: hay carry pero no overflow          */

    return 0;
}
