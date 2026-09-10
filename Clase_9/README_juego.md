# Clase 9 — Juego: Monopoly en Excel (con macros VBA)

**Fecha:** 09/09/2026
**Tarea:** [#18 — Juego de Monopoly en hoja de cálculo](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/18)

## De qué se trata

Un Monopoly que corre completo dentro de una hoja de cálculo: el tablero, los dados, el dinero de cada jugador, las propiedades y las cartas viven en celdas, y las reglas están programadas en un módulo de macros VBA. Al final quedó en **Excel de escritorio** en vez de Google Sheets por la misma razón que la simulación del ciclo de instrucción: los botones y las macros funcionan al abrir el archivo, sin autorizar scripts.

La base es un tablero que encontré ya hecho; sobre esa base lo adapté (jugadoras: Luna, Inge, Karen y Belén) y lo documento aquí para que sirva como ejemplo de la clase.

> 📎 Archivo del juego: [`Monopoly.xlsm`](Monopoly.xlsm)
> ✍️ Crédito del tablero original: *(pendiente)*

## Cómo funciona por dentro

El archivo tiene dos hojas y un módulo de VBA llamado `Monopoly`:

| Pieza del juego | Cómo está resuelta en el archivo |
|-----------------|----------------------------------|
| Tablero (hoja `Board`) | Las 40 casillas clásicas (de Mediterranean Avenue a Boardwalk) dibujadas con celdas con formato, con las fichas (carrito, perro, sombrero y plancha) moviéndose encima. |
| Datos del juego (hoja `Pieces`) | La tabla de propiedades con nombre, costo, costo de casa/hotel, renta, dueño, construcciones, hipoteca y color de grupo. Es la "memoria" del juego. |
| Cartas | Dos tablas con los mazos de **Chance** y **Community Chest**: cada carta tiene su mensaje y su efecto en columnas (cuánto ganas o pagas, a dónde te mueves, cuánto pagas por casa/hotel). |
| Jugadores | Una tabla por jugadora con su ficha, su dinero, su posición y su tipo: **Person** (juega una persona) o **Computer** (la macro juega sola). |
| Turnos y reglas | El módulo VBA `Monopoly` tira los dados, mueve la ficha, aplica la casilla donde caes (comprar, pagar renta, carta, cárcel) y muestra mensajes como `Rent Owed: $8`. |

## Cómo se juega

1. Descargar [`Monopoly.xlsm`](Monopoly.xlsm) y abrirlo en Excel de escritorio.
2. Aceptar **"Habilitar contenido"** para que corran las macros (sin eso el tablero se ve, pero no se puede jugar).
3. En la hoja `Pieces` poner el nombre de cada jugadora y elegir si la lleva una persona (`Person`) o la computadora (`Computer`).
4. Jugar por turnos desde el tablero: la macro tira los dados, mueve la ficha y va actualizando dinero, propiedades y construcciones. Gana la última que queda con dinero.

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

- [x] Subir el archivo del juego al repo ([`Monopoly.xlsm`](Monopoly.xlsm)) y anexarlo a la tarea #18.
- [ ] Anotar el crédito del tablero original.
- [ ] Capturas de una partida de 3 turnos mostrando el tablero, los dados y el mensaje de la jugada.
- [ ] Cerrar la tarea #18 y moverla a Done en el tablero.
