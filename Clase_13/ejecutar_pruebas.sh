#!/usr/bin/env bash
# Compila y ejecuta las dos pruebas del práctico (FIFO vs memoria compartida).
# Uso: bash ejecutar_pruebas.sh [repeticiones]     (por defecto 3)
set -u
cd "$(dirname "$0")"
REPS="${1:-3}"

echo "== Compilación =="
gcc -Wall -Wextra -O3 Prod_NO.c  -o Prod_NO  || exit 1
gcc -Wall -Wextra -O3 Cons_NO.c  -o Cons_NO  || exit 1
gcc -Wall -Wextra -O3 Prod_OPT.c -o Prod_OPT -lrt -lpthread || exit 1
gcc -Wall -Wextra -O3 Cons_OPT.c -o Cons_OPT -lrt -lpthread || exit 1
echo "OK (4 programas, sin advertencias)"

for r in $(seq 1 "$REPS"); do
    echo
    echo "################ Repetición $r de $REPS ################"

    echo "---- Prueba 1: NO optimizada (FIFO) ----"
    ./Cons_NO & cons=$!
    sleep 0.3                       # el consumidor crea el FIFO
    ./Prod_NO
    wait "$cons"

    echo
    echo "---- Prueba 2: OPTIMIZADA (memoria compartida + batching) ----"
    ./Prod_OPT & prod=$!
    # el consumidor falla si la memoria compartida todavía no existe: esperarla
    while [ ! -e /dev/shm/bus_shm_opt ]; do sleep 0.01; done
    sleep 0.05                      # deja que el productor termine sem_init
    ./Cons_OPT
    wait "$prod"
done
