#include <stdio.h>

#define TC_NS 0.5

static void ejecutar(int x)
{
    int y = 5;
    int ni = 0;
    int ciclos = 0;

    printf("--- x inicial = %d ---\n", x);

    x = x + 2;
    ni++; ciclos += 3;

    ni++; ciclos += 4;
    if (x == 10) {
        x = x - 2;
        ni++; ciclos += 4;
    } else {
        x = x + 4;
        ni++; ciclos += 3;

        y = 0;
        ni++; ciclos += 3;
    }

    printf("x final = %d, y final = %d\n", x, y);
    printf("NI = %d, ciclos = %d\n", ni, ciclos);
    printf("CPI = %d / %d = %.2f\n", ciclos, ni, (double)ciclos / ni);
    printf("T_CPU = NI x CPI x Tc = %d x %.2f x %.1f ns = %.1f ns\n\n",
           ni, (double)ciclos / ni, TC_NS, ciclos * TC_NS);
}

int main(void)
{
    ejecutar(8);
    ejecutar(3);
    return 0;
}
