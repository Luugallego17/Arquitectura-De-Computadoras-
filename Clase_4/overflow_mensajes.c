#include <stdio.h>
#include <stdint.h>

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

    sumar_con_aviso(100, 27);
    sumar_con_aviso(120, 20);
    sumar_con_aviso(127, 1);
    sumar_con_aviso(-100, -50);
    sumar_con_aviso(-128, 1);
    sumar_con_aviso(-1, 1);

    return 0;
}
