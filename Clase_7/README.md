# Clase 7 — Transferencia de bloques de memoria con `memcpy`/`memmove`

**Fecha:** 02/09/2026
**Tareas:**

- [#9 — Generar el archivo de datos en memoria secundaria](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/9)
- [#10 — Lectura del arreglo desde memoria secundaria](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/10)
- [#11 — Transferencia de bloque de memoria con memcpy/memmove](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/11)
- [#12 — Salidas por consola y validación](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/12)
- [#13 — Compilación, pruebas y entrega](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/13)

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`generador.cpp`](generador.cpp) | Programa auxiliar (tarea #9): crea `datos.txt` con 1000 enteros **secuenciales** (0 a 999), uno por línea. Con valores secuenciales el valor de cada elemento coincide con su índice, así que es facilísimo verificar qué se transfirió. |
| [`transferencia.cpp`](transferencia.cpp) | Programa principal (tareas #10–#12): lee el archivo, transfiere el bloque de los índices 500–599 con `memcpy`, limpia ese rango con `memset` y valida el resultado. |

El archivo `datos.txt` no se sube al repo (está en el `.gitignore`)
porque se genera con el programa auxiliar.

## Idea de la práctica

Es el recorrido completo de los datos por la jerarquía de memoria:

1. **Memoria secundaria → memoria principal:** los 1000 enteros viven
   en un archivo (`datos.txt`) y se cargan a un arreglo en RAM,
   controlando errores de apertura y verificando que se lean exactamente
   1000 elementos.
2. **RAM → RAM en bloque:** los índices 500 a 599 se copian a un segundo
   arreglo de 100 elementos con `memcpy`, que copia el bloque completo
   de una vez (100 × 4 bytes). Se usa `memcpy` porque los dos arreglos
   **no se traslapan**; si fueran regiones que se encimaran habría que
   usar `memmove`, que sí tolera el traslape.
3. **Limpieza:** el rango original queda en cero con `memset`.
4. **Validación automática:** se recorre el rango 500–599 del arreglo
   original confirmando que todo sea cero, y de pilón se verifica que el
   resto del arreglo no se haya tocado.

## Cómo compilar y ejecutar

Probado en Ubuntu con `g++`, compila sin advertencias con `-Wall -Wextra`:

```bash
g++ -Wall -Wextra generador.cpp -o generador
g++ -Wall -Wextra transferencia.cpp -o transferencia

./generador        # crea datos.txt
./transferencia
```

## Salida del programa

```
Se cargaron 1000 enteros en el arreglo en memoria principal.

Primeros cinco elementos: 0 1 2 3 4
Ultimos cinco elementos : 995 996 997 998 999

Elementos transferidos al segundo arreglo (indices 500 a 599):
500 501 502 503 504 505 506 507 508 509
510 511 512 513 514 515 516 517 518 519
520 521 522 523 524 525 526 527 528 529
530 531 532 533 534 535 536 537 538 539
540 541 542 543 544 545 546 547 548 549
550 551 552 553 554 555 556 557 558 559
560 561 562 563 564 565 566 567 568 569
570 571 572 573 574 575 576 577 578 579
580 581 582 583 584 585 586 587 588 589
590 591 592 593 594 595 596 597 598 599

Validacion EXITOSA: los indices 500 a 599 del arreglo original contienen cero.
El resto del arreglo original no fue afectado.
```

También se probó el manejo de errores: si `datos.txt` no existe o tiene
menos de 1000 enteros, el programa lo reporta y termina con código de
error en lugar de trabajar con datos incompletos.
