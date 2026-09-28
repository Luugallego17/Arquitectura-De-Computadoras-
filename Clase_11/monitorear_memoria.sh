#!/usr/bin/env bash
# Registra la RAM y la swap cada segundo mientras corre llenar_memoria,
# para dejar evidencia en evidencias/. Se corre en OTRA terminal.
#
# Uso:  bash monitorear_memoria.sh [segundos]     (Ctrl+C para detener)

set -u
DURACION=${1:-0}            # 0 = hasta Ctrl+C
DIR="$(dirname "$0")/evidencias"
mkdir -p "$DIR"
MARCA=$(date +%Y%m%d_%H%M%S)

{
    echo "# $(date)  —  $(uname -srm)"
    echo "# swapon --show"
    swapon --show
    echo "# free -m (inicio)"
    free -m
} > "$DIR/estado_inicial_$MARCA.txt"

echo "Guardando vmstat en $DIR/vmstat_$MARCA.log  (si/so = memoria que entra/sale de la swap por segundo)"
if [ "$DURACION" -gt 0 ]; then
    vmstat -S M -t 1 "$DURACION" | tee "$DIR/vmstat_$MARCA.log"
else
    vmstat -S M -t 1 | tee "$DIR/vmstat_$MARCA.log"
fi
