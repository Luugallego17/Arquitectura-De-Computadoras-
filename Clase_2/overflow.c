#include <stdio.h>
#include <stdint.h>

int main(void) {
    int8_t a = 120;
    int8_t b = 20;
    int8_t suma = a + b;   // 140 no cabe en un int8_t (rango: -128 a 127)
    printf("a = %d\n", a);
    printf("b = %d\n", b);
    printf("a + b = %d\n", suma);
    return 0;
}
