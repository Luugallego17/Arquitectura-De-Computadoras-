# Clase 11 — Memoria virtual: llenar la RAM y forzar el uso de swap

**Fecha:** 21/09/2026
**Tarea:** Práctica de la diapositiva *16. Práctica*:

> Escribe un programa en C (o Python) para un sistema operativo Linux que
> asigna bloques de memoria de manera continua en un bucle hasta llenar la
> memoria RAM disponible y forzar al sistema a utilizar el espacio de
> intercambio (*Swap*).
>
> Registrar las evidencias. Documente el proceso y comandos utilizados.

## Contenido de la carpeta

| Archivo | Descripción |
|---------|-------------|
| [`llenar_memoria.c`](llenar_memoria.c) | El programa en C: pide bloques con `malloc`, los escribe completos con `memset` y después de cada bloque muestra la RAM disponible, la swap usada y el `VmRSS`/`VmSwap` del propio proceso. Avisa cuando el kernel empieza a mandar páginas a la swap. |
| [`llenar_memoria.py`](llenar_memoria.py) | La misma práctica en Python (`bytearray` lleno con un patrón), con la misma salida. |
| [`preparar_swap.sh`](preparar_swap.sh) | Muestra el estado de la swap (`swapon --show`, `free -h`, `swappiness`) y, con `--crear`, crea y activa un archivo de swap de 2 GiB si el sistema no tiene. |
| [`monitorear_memoria.sh`](monitorear_memoria.sh) | Registra `vmstat` cada segundo en `evidencias/` mientras corre el programa (en otra terminal). |

## Conceptos

- **Memoria virtual.** Cada proceso ve un espacio de direcciones propio,
  dividido en **páginas** de 4 KiB. El kernel decide qué páginas viven en
  un **marco** de la RAM física y cuáles no.
- **Swap (espacio de intercambio).** Una partición o archivo en disco
  donde el kernel guarda las páginas que saca de la RAM cuando se queda
  sin marcos libres (*page-out*). Si el proceso vuelve a tocar esa
  página, se produce un fallo de página mayor y se trae de vuelta
  (*page-in*). El disco es miles de veces más lento que la RAM, por eso
  el sistema se pone lento cuando empieza a usar swap.
- **`malloc` no es memoria física.** `malloc` solo reserva direcciones
  virtuales; el kernel asigna los marcos recién cuando se **escribe** en
  cada página (asignación perezosa / *overcommit*). Por eso el programa
  hace `memset` de todo el bloque con un valor distinto de cero: si solo
  hiciera `malloc`, la RAM no se llenaría nunca.
- **`vm.swappiness`** (0–200, 60 por defecto) indica qué tan pronto el
  kernel prefiere mandar páginas anónimas a la swap en vez de vaciar la
  caché de archivos.
- **OOM killer.** Si se acaban la RAM **y** la swap, el kernel mata al
  proceso que más memoria usa. Para no llegar a eso (ni congelar la
  laptop), el programa se detiene solo cuando la swap libre baja de un
  margen de seguridad.

## Cómo funciona `llenar_memoria.c`

```
mientras no se pida detener:
    si la swap libre < reserva (o, sin swap, la RAM disponible < reserva): parar
    p = malloc(bloque)              → solo direcciones virtuales
    memset(p, patrón, bloque)       → el kernel asigna marcos reales (RAM)
    guardar p en la lista           → nunca se libera dentro del bucle
    leer /proc/meminfo              → MemAvailable, SwapTotal, SwapFree
    leer /proc/self/status          → VmRSS (en RAM) y VmSwap (en swap) del proceso
    imprimir una fila de la tabla
    si VmSwap > 0 por primera vez:  avisar que la RAM se llenó y empezó el swapping
```

Al terminar muestra el resumen y **espera ENTER** antes de liberar la
memoria, para poder tomar las capturas con `free -h`, `swapon --show` y
`htop` mientras la swap está ocupada.

Opciones (en C y en Python):

| Opción | Por defecto | Qué hace |
|--------|-------------|----------|
| `--bloque-mb N` | 256 | Tamaño de cada bloque. |
| `--max-mb N` | 0 (sin tope) | Detenerse al asignar N MB en total. |
| `--reserva-ram MB` | 256 | Sin swap: RAM disponible mínima que se deja libre. |
| `--reserva-swap MB` | 512 | Con swap: swap libre mínima que se deja libre. |

## Proceso y comandos utilizados

Se usan **dos terminales**: en una corre el monitoreo y en la otra el
programa.

```bash
# 1. Estado inicial de la memoria y la swap
free -h                          # RAM y swap totales, usadas y disponibles
swapon --show                    # dispositivos/archivos de swap activos
cat /proc/sys/vm/swappiness      # tendencia del kernel a usar swap
bash preparar_swap.sh            # los tres comandos anteriores juntos

# 2. Si no hay swap, crear un archivo de swap de 2 GiB
sudo bash preparar_swap.sh --crear
#   equivale a:
#   sudo fallocate -l 2G /swapfile     # reservar el archivo
#   sudo chmod 600 /swapfile           # solo root puede leerlo
#   sudo mkswap /swapfile              # darle formato de swap
#   sudo swapon /swapfile              # activarlo

# 3. Compilar el programa
gcc -Wall -Wextra -O2 llenar_memoria.c -o llenar_memoria

# 4. Terminal 1: registrar la RAM y la swap cada segundo
bash monitorear_memoria.sh       # guarda evidencias/vmstat_<fecha>.log
#   (también sirven: watch -n 1 free -m   ·   htop   ·   vmstat -S M 1)

# 5. Terminal 2: llenar la RAM hasta usar la swap
./llenar_memoria                 # o: python3 llenar_memoria.py

# 6. Con el programa en pausa (antes de presionar ENTER), tomar las capturas
free -h
swapon --show
grep -E "VmRSS|VmSwap" /proc/$(pgrep llenar_memoria)/status
cat /proc/meminfo | grep -E "MemAvailable|SwapTotal|SwapFree"

# 7. Presionar ENTER en la terminal 2 y Ctrl+C en la terminal 1.
#    Opcional: devolver a la RAM lo que quedó en swap y quitar el archivo
sudo swapoff /swapfile && sudo swapon /swapfile   # vacía la swap
sudo swapoff /swapfile && sudo rm /swapfile       # la elimina
```

Qué observar en la tabla del programa y en `vmstat`:

1. Al principio cada bloque de 256 MB baja la **RAM disponible** en
   ~256 MB y sube el **VmRSS** del proceso en lo mismo; la swap queda en 0.
2. Cuando la RAM disponible llega casi a cero, el kernel empieza a sacar
   páginas: **Swap usada** y **VmSwap** crecen, y el `VmRSS` deja de subir
   (el proceso ya no cabe entero en RAM). El programa imprime
   `>>> La RAM se llenó: el kernel empezó a mover páginas ... a la swap`.
3. En `vmstat` la columna **`swpd`** crece y **`so`** (*swap out*) deja
   de ser 0: son las páginas que se escriben al disco. El `memset` de
   cada bloque tarda cada vez más porque ahora hay E/S de disco.
4. El bucle termina solo al llegar a la reserva de swap, sin que actúe
   el OOM killer.

## Compilación y verificación

```bash
gcc -Wall -Wextra -O2 llenar_memoria.c -o llenar_memoria
bash -n preparar_swap.sh && bash -n monitorear_memoria.sh
```

El programa compila **sin advertencias** con `-Wall -Wextra`, y los dos
scripts pasan `bash -n`.

Pruebas hechas en una máquina Linux de 4 núcleos y 15 GiB de RAM **sin
swap activa** (ahí no fue posible activar swap, así que se comprobó que
el bucle asigna y escribe la memoria de verdad y que se detiene a tiempo):

**Con tope `--max-mb 2048`** — cada bloque baja la RAM disponible y sube
el `VmRSS` en 256 MB, lo que demuestra que las páginas quedaron en RAM:

```
$ ./llenar_memoria --bloque-mb 256 --max-mb 2048
=== Llenar la RAM y forzar el uso de swap ===
PID del proceso      : 687
RAM total            : 16095 MB
RAM disponible       : 15590 MB
Swap total           : 0 MB (usada al inicio: 0 MB)
Tamaño de cada bloque: 256 MB
Tope de asignación   : 2048 MB
AVISO: el sistema no tiene swap activa; el programa se detendrá al quedar 256 MB de RAM disponible.

Bloque  Asignado MB     RAM disp. MB   Swap usada   VmRSS MB  VmSwap MB
     1          256            15331            0        257          0
     2          512            15074            0        513          0
     3          768            14829            0        769          0
     4         1024            14568            0       1025          0
     5         1280            14315            0       1281          0
     6         1536            14055            0       1537          0
     7         1792            13799            0       1793          0
     8         2048            13545            0       2049          0

=== Fin del bucle: se alcanzó el tope indicado con --max-mb ===
Memoria asignada y escrita : 2048 MB en 8 bloques (17.98 s)
RAM disponible             : 13545 MB (al inicio 15590 MB)
Swap usada por el sistema  : 0 MB (al inicio 0 MB)
VmRSS del proceso (en RAM) : 2049 MB
VmSwap del proceso (swap)  : 0 MB
El proceso no llegó a usar swap.
Memoria liberada.
```

**Margen de seguridad** — con `--reserva-ram 14800` el bucle se detiene
en cuanto el siguiente bloque dejaría menos RAM de la reserva:

```
$ ./llenar_memoria --bloque-mb 256 --reserva-ram 14800
...
=== Fin del bucle: la RAM disponible llegó al margen de seguridad (no hay swap) ===
Memoria asignada y escrita : 768 MB en 3 bloques (5.78 s)
RAM disponible             : 14799 MB (al inicio 15575 MB)
```

**Versión en Python** (`python3 llenar_memoria.py --max-mb 1024`): misma
tabla; el `VmRSS` arranca ~10 MB más alto por el propio intérprete.

## Evidencias en Ubuntu (con swap)

Las capturas donde se ve la swap llenándose se toman en la laptop con
Ubuntu siguiendo los pasos 1 a 6 de arriba, y se guardan en
`evidencias/` (la carpeta la crea `monitorear_memoria.sh` con sus `.log`):

- [x] `free -h` y `swapon --show` antes de empezar (swap en 0).
- [x] La tabla de `llenar_memoria` en el momento en que aparece el aviso
      `>>> La RAM se llenó...` y `VmSwap` empieza a crecer.
- [x] `free -h` / `swapon --show` con el programa en pausa (swap ocupada).
- [x] `htop` o `vmstat` mostrando `swpd` alto y `so` distinto de 0.
- [x] `evidencias/vmstat_<fecha>.log`.
