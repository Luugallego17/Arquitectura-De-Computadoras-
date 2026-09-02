# Clase 2 — Sistemas numéricos y aritmética binaria

**Fecha:** 10/08/2026
**Tarea:** [#2 — Sistemas Numéricos y Aritmética Binaria](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/2)

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`practicaSistemas_numericos.md`](practicaSistemas_numericos.md) | Resolución de los 6 niveles de la práctica: conversión de bases, aritmética binaria, complemento a dos, overflow y banderas, punto flotante IEEE 754 y script de verificación. |
| [`overflow.c`](overflow.c) | Programa en C del nivel 4.3: demuestra el overflow de un `int8_t` (120 + 20 da −116 en lugar de 140). |
| [`convertidor.py`](convertidor.py) | Script del nivel 6: convierte un entero a binario, octal y hexadecimal, calcula su complemento a dos en 8/16/32 bits e indica si hay overflow en 8 bits con signo. |

## Cómo ejecutar

```bash
# Programa de overflow en C
gcc overflow.c -o overflow
./overflow
# Salida esperada: a + b = -116

# Convertidor de bases
python3 convertidor.py 127
python3 convertidor.py -128
```

Las salidas de prueba (casos límite 127, 128, −128, −129 y 0) están
documentadas dentro de la práctica.
