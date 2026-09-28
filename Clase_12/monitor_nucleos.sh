#!/usr/bin/env bash
# Muestra cada segundo el porcentaje de uso de cada núcleo lógico,
# calculado a partir de /proc/stat (no necesita instalar sysstat ni htop).
# Se corre en otra terminal mientras afinidad_cpu está en ejecución.
#
# Uso:  bash monitor_nucleos.sh [segundos]     (Ctrl+C para detener)

set -u
DURACION=${1:-0}     # 0 = hasta Ctrl+C

leer() { grep -E '^cpu[0-9]+ ' /proc/stat; }

declare -A total_ant ocioso_ant
while read -r cpu u n s i w irq sirq st _; do
    total_ant[$cpu]=$((u + n + s + i + w + irq + sirq + st))
    ocioso_ant[$cpu]=$((i + w))
done < <(leer)

cuenta=0
while [ "$DURACION" -eq 0 ] || [ "$cuenta" -lt "$DURACION" ]; do
    sleep 1
    linea="$(date +%T)"
    while read -r cpu u n s i w irq sirq st _; do
        total=$((u + n + s + i + w + irq + sirq + st))
        ocioso=$((i + w))
        dt=$((total - total_ant[$cpu]))
        di=$((ocioso - ocioso_ant[$cpu]))
        uso=0
        [ "$dt" -gt 0 ] && uso=$(( (100 * (dt - di)) / dt ))
        linea+=$(printf "  %s:%3d%%" "$cpu" "$uso")
        total_ant[$cpu]=$total
        ocioso_ant[$cpu]=$ocioso
    done < <(leer)
    echo "$linea"
    cuenta=$((cuenta + 1))
done
