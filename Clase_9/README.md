# Clase 9 — Simulación del ciclo de instrucción (fase de búsqueda)

**Fecha:** 09/09/2026
**Tareas:** [#19 — Simulación del ciclo de instrucción (fase de búsqueda)](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/19) · [#18 — Juego en Google Sheets](https://github.com/Luugallego17/Arquitectura-De-Computadoras-/issues/18)

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`Simulacion_ciclo_instruccion.xlsx`](Simulacion_ciclo_instruccion.xlsx) | Las tablas de la simulación (registros, memoria central, fase de búsqueda y traza por paso) y la hoja `Plan` con las etapas que faltan. Cuando tenga los botones pasa a ser `.xlsm`. |
| [`README_juego.md`](README_juego.md) | El juego de Monopoly en Google Sheets (tarea #18): cómo funciona por dentro, cómo se juega y su relación con el ciclo de instrucción. |

## Qué se simula

El esquema de la clase tiene tres bloques: la **Unidad de Control** (Reloj, Secuenciador, Decodificador, RI y CP), la **Unidad Aritmético Lógica** (Acumulador, R. Estado, REN1, REN2 y el operador) y la **Memoria Central** (RDM, RIM, Selector y las celdas de memoria). La fase de búsqueda es lo que hace la CPU para traer la siguiente instrucción antes de ejecutarla, y son cinco microoperaciones:

| Paso | Microoperación | Qué pasa en el esquema |
|------|----------------|------------------------|
| 1 | `RDM ← CP` | El CP (que vale 6) manda su contenido al Registro de Dirección de Memoria. |
| 2 | `RIM ← M(RDM)` | El Selector busca la dirección 6 en la memoria y deja su contenido (1123) en el Registro de Intercambio de Memoria. |
| 3 | `RI ← RIM` | La instrucción 1123 sube al Registro de Instrucción. |
| 4 | `Sec ← Decod(RI)` | El Decodificador interpreta el código de operación y el Secuenciador genera las microórdenes. |
| 5 | `CP ← CP + 1` | La UAL suma 1 al CP (REN1 = 1, REN2 = 6) y el CP queda apuntando a la 7. |

Con el ejemplo de la diapositiva, después de los cinco pasos los registros quedan así: `CP = 7`, `RDM = 6`, `RIM = 1123`, `RI = 1123`.

## Cómo lo voy a hacer

La idea es que la hoja se vea como el esquema del pizarrón y que uno pueda avanzar el ciclo de a un paso, viendo qué registro cambia y por qué camino viaja el dato.

1. **Tablas base** (ya están en el archivo). Cada bloque tiene su tabla `Registro | Valor | Qué guarda`, la memoria central es una tabla `Dirección | Contenido` con el 1123 en la dirección 6, y hay una tabla de traza con una fila por paso.
2. **Traza con fórmulas.** La fila 0 es el estado inicial. En cada fila siguiente todos los registros copian el valor de arriba, salvo el que cambia en ese paso: `RDM = CP`, `RIM = INDEX(memoria; RDM)`, `RI = RIM`, `Secuenciador = decodificación de RI`, `CP = CP + 1`. Así la lógica queda en fórmulas, no escondida en el código.
3. **Celda de control `Paso actual`** (0 a 5). Las celdas "Valor" de cada bloque leen de la traza la fila que indica esa celda, así que cambiar el número ya mueve toda la simulación.
4. **Botones en VBA.** `Siguiente paso` suma 1 a la celda de control (hasta 5), `Paso anterior` resta 1 y `Reiniciar` la deja en 0. Son macros de tres líneas; el trabajo pesado lo siguen haciendo las fórmulas.
5. **Resaltado del flujo.** Formato condicional que pinta el registro que cambia en el paso actual, la fila de memoria que se está leyendo y la microoperación activa en la tabla de la fase de búsqueda. Con eso se ve el mismo camino que marcan las flechas numeradas de la diapositiva.
6. **Decodificador.** Una tabla `código de operación → microorden` para que el paso 4 muestre algo real (por ejemplo, de 1123 sacar la operación y el operando).
7. **Probar con otra memoria.** Validación de datos en el CP inicial y en la tabla de memoria para cargar otra instrucción y comprobar que la traza sigue dando bien.

## Por qué en Excel y no en Google Sheets

Quería la versión más interactiva: botones que avancen el ciclo, no una celda donde escribir el número del paso. Eso en Google Sheets se hace con Apps Script y necesita que quien abra la hoja autorice el script, y en Excel web los botones directamente no corren. En Excel de escritorio los botones con VBA funcionan al abrir el archivo (habilitando macros) y el resaltado con formato condicional se comporta igual que en la clase.

Lo que se pierde es compartir por enlace. Para eso el archivo se sube al repo y en las capturas del README se ven los cinco pasos, así se puede revisar sin abrir Excel. Las fórmulas están hechas con funciones básicas (`INDEX`, `IF`), así que si hace falta también abre en Google Sheets, solo sin los botones.

## Cómo abrirlo

1. Descargar `Simulacion_ciclo_instruccion.xlsm` (cuando estén los botones; por ahora es `.xlsx`).
2. Abrir en Excel de escritorio y aceptar "Habilitar contenido" para que funcionen las macros.
3. Poner el CP inicial y la memoria en las celdas azules, y usar `Siguiente paso` para recorrer el ciclo.

## Salidas

*(pendiente: capturas de los pasos 0 a 5 cuando esté la traza con fórmulas)*
