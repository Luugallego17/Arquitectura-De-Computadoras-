#!/usr/bin/env bash
# Verificación previa del hardware (sección 2 de la guía de laboratorio).
# Ejecuta los tres comandos de la guía y comprueba cuántos float caben
# en una línea de caché.
#
# Uso:  bash verificar_hardware.sh

set -u

echo "=== 1. Jerarquía y tamaños de memoria caché L1, L2 y L3 ==="
echo '$ lscpu | grep -E "L1|L2|L3|Model name"'
lscpu | grep -E "L1|L2|L3|Model name"
echo

echo "=== 2. Tamaño de la línea de caché de datos L1 (getconf) ==="
echo '$ getconf LEVEL1_DCACHE_LINESIZE'
linea_getconf=$(getconf LEVEL1_DCACHE_LINESIZE)
echo "$linea_getconf"
echo

echo "=== 3. Tamaño del bloque de coherencia según el sysfs del kernel ==="
echo '$ cat /sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size'
linea_sysfs=$(cat /sys/devices/system/cpu/cpu0/cache/index0/coherency_line_size)
echo "$linea_sysfs"
echo

echo "=== Detalle de cada nivel de caché del cpu0 (sysfs) ==="
for d in /sys/devices/system/cpu/cpu0/cache/index*; do
    printf "%s: L%s %-11s tamaño=%-7s línea=%s bytes\n" \
        "$(basename "$d")" "$(cat "$d/level")" "$(cat "$d/type")" \
        "$(cat "$d/size")" "$(cat "$d/coherency_line_size")"
done
echo

echo "=== Principio físico ==="
if [ "$linea_getconf" = "$linea_sysfs" ]; then
    echo "getconf y sysfs coinciden: la línea de caché mide $linea_sysfs bytes."
else
    echo "Atención: getconf ($linea_getconf) y sysfs ($linea_sysfs) no coinciden."
fi
bytes_float=4
echo "Un float ocupa $bytes_float bytes, así que una línea guarda $((linea_sysfs / bytes_float)) float contiguos."
echo "Al pedir un solo float, el bus trae la línea completa: 1 fallo de caché por cada $((linea_sysfs / bytes_float)) lecturas."
