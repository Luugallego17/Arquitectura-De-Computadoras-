/*
 * Demostracion de un fallo del codigo literal del enunciado.
 *
 * En el enunciado el cursor de la VRAM es un uint8_t y la condicion para
 * dibujar es `cursor_vram <= 0xFF`. Un uint8_t SIEMPRE es <= 0xFF, y al
 * pasar de 0xFF vuelve a 0x00: el caracter 17 se escribiria en la RAM de
 * codigo (0x00..0x5F) en vez de descartarse. Este programa reproduce ese
 * comportamiento y lo compara con la correccion (cursor de 16 bits).
 *
 *   gcc -std=c99 -Wall -Wextra -pedantic demo_cursor_uint8.c -o demo
 *   (con -Wextra GCC avisa -Wtype-limits en la comparacion siempre verdadera;
 *    ese aviso es justamente el sintoma del fallo y se deja a proposito)
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>

static uint8_t ram_literal[256], ram_corregida[256];

int main(void)
{
    uint8_t  cursor8  = 0xF0;  /* literal del enunciado */
    uint16_t cursor16 = 0xF0;  /* version corregida     */
    const char *txt = "ABCDEFGHIJKLMNOPQRS"; /* 19 caracteres, caben 16 */

    memset(ram_literal, 0, sizeof ram_literal);
    memset(ram_corregida, 0, sizeof ram_corregida);

    for (int i = 0; txt[i]; i++) {
        if (cursor8 <= 0xFF) { ram_literal[cursor8] = (uint8_t)txt[i]; cursor8++; }
        if (cursor16 <= 0xFF) { ram_corregida[cursor16] = (uint8_t)txt[i]; cursor16++; }
    }
    printf("Se escriben 19 caracteres en una VRAM de 16 celdas (0xF0..0xFF)\n\n");
    printf("                        literal(uint8_t)   corregida(uint16_t)\n");
    printf("cursor final           : 0x%02X               0x%03X\n", cursor8, cursor16);
    printf("RAM[0x00] (codigo)     : 0x%02X ('%c')          0x%02X\n", ram_literal[0], ram_literal[0] ? ram_literal[0] : '-', ram_corregida[0]);
    printf("RAM[0x01] (codigo)     : 0x%02X ('%c')          0x%02X\n", ram_literal[1], ram_literal[1] ? ram_literal[1] : '-', ram_corregida[1]);
    printf("RAM[0x02] (codigo)     : 0x%02X ('%c')          0x%02X\n", ram_literal[2], ram_literal[2] ? ram_literal[2] : '-', ram_corregida[2]);
    printf("\nResultado: la version literal corrompe la RAM de codigo (%s); la corregida no (%s).\n",
           (ram_literal[0] || ram_literal[1] || ram_literal[2]) ? "CONFIRMADO" : "no reproducido",
           (ram_corregida[0] || ram_corregida[1] || ram_corregida[2]) ? "FALLO" : "CONFIRMADO");
    return 0;
}
