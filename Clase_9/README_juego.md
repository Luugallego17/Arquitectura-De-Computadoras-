# Clase 9 — Juego: Monopoly en Google Sheets

**Fecha:** 09/09/2026
**Tarea:** [#18 — Juego de Monopoly en Google Sheets](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/18)

## De qué se trata

Un Monopoly que corre completo dentro de una hoja de cálculo de Google Sheets: el tablero, los dados, el dinero de cada jugador y las propiedades viven en celdas, y las reglas están hechas con fórmulas. No hay que instalar nada, se abre con el enlace y se juega desde el navegador.

La base es un tablero que encontré hecho en Sheets; sobre esa base voy a documentar cómo funciona por dentro y adaptarlo para que sirva como ejemplo de la clase.

> 🔗 Enlace al juego: *(pendiente — se agrega cuando esté la copia en mi Drive con permiso de solo lectura)*
> ✍️ Crédito del tablero original: *(pendiente)*

## Cómo funciona por dentro

| Pieza del juego | Cómo está resuelta en la hoja |
|-----------------|-------------------------------|
| Tablero | Las 40 casillas van en una tabla con nombre, tipo (propiedad, impuesto, suerte, cárcel…), precio y renta. El dibujo del tablero son celdas con formato. |
| Dados | Dos celdas con `RANDBETWEEN(1;6)`. Se vuelven a tirar al recalcular la hoja (o con una celda de "tirar" que cambia de valor). |
| Posición de cada jugador | Una celda por jugador con el número de casilla; avanza con `MOD(posición + dado1 + dado2; 40)`. |
| Dinero | Una celda de saldo por jugador; cada compra, renta o impuesto la actualiza. |
| Propiedades | Columna "dueño" en la tabla del tablero; la renta se cobra con un `BUSCARV`/`INDEX` sobre la casilla donde cayó el jugador. |
| Turno | Una celda que indica a quién le toca y rota con `MOD(turno; jugadores) + 1`. |
| Qué pasó en la jugada | Una celda de mensaje que explica la acción (compraste X, pagaste renta a Y, fuiste a la cárcel). |

## Cómo se juega

1. Hacer una copia de la hoja (Archivo → Hacer una copia) para no pisar la original.
2. Escribir los nombres de los jugadores en las celdas azules.
3. En cada turno, tirar los dados (cambiar la celda "tirar"), leer el mensaje de la jugada y decidir si se compra la propiedad.
4. La hoja actualiza sola la posición, el saldo y el dueño de la casilla. Gana el último que queda con dinero.

## Qué tiene que ver con la clase

Cada turno del juego se parece bastante al ciclo de instrucción que estamos simulando en [`Simulacion_ciclo_instruccion.xlsx`](Simulacion_ciclo_instruccion.xlsx):

| Ciclo de instrucción | Turno de Monopoly |
|----------------------|-------------------|
| Fetch: `RDM ← CP`, `RIM ← M(RDM)` | Mirar en qué casilla cayó el jugador y traer sus datos de la tabla del tablero. |
| Decode: `Sec ← Decod(RI)` | Ver qué tipo de casilla es (propiedad, impuesto, suerte) para saber qué regla aplica. |
| Execute | Cobrar la renta, comprar, pagar el impuesto. |
| Write-back | Guardar el nuevo saldo y el dueño de la propiedad. |
| `CP ← CP + 1` | Pasar el turno al siguiente jugador. |

O sea, la tabla del tablero es la memoria, la posición es el contador de programa y la celda de mensaje es lo que muestra el secuenciador. Esa comparación es la que quiero dejar clara en las capturas.

## Pendientes

- [ ] Subir la copia a Drive y poner el enlace de solo lectura arriba.
- [ ] Anotar el crédito del tablero original.
- [ ] Capturas de una partida de 3 turnos mostrando la tabla del tablero, los dados y el mensaje de la jugada.
- [ ] Cerrar la tarea #18 y moverla a Done en el tablero.
