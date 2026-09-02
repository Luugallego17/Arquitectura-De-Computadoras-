#include <stdio.h>

int main(void)
{
    int arreglo[] = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100};
    int longitud = sizeof(arreglo) / sizeof(arreglo[0]);
    long suma = 0;

    for (int i = 0; i < longitud; i++) {
        suma += arreglo[i];
    }

    printf("La suma del arreglo es: %ld\n", suma);
    return 0;
}
