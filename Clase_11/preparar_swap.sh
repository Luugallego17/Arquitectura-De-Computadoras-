#!/usr/bin/env bash
# Revisa la swap del sistema y, si no hay, ofrece crear un archivo de
# swap de 2 GiB. Se corre ANTES de llenar_memoria.
#
# Uso:  sudo bash preparar_swap.sh          # solo muestra el estado
#       sudo bash preparar_swap.sh --crear  # crea y activa /swapfile si no hay swap

set -u
TAM=2G
ARCHIVO=/swapfile

echo "=== Swap activa (swapon --show) ==="
swapon --show
echo

echo "=== RAM y swap (free -h) ==="
free -h
echo

echo "=== Tendencia a usar swap (vm.swappiness, 0-200) ==="
cat /proc/sys/vm/swappiness
echo

if [ -n "$(swapon --show --noheadings)" ]; then
    echo "El sistema ya tiene swap activa: no hace falta crear nada."
    exit 0
fi

if [ "${1:-}" != "--crear" ]; then
    echo "No hay swap activa. Para crear $ARCHIVO de $TAM ejecute:"
    echo "  sudo bash $0 --crear"
    exit 0
fi

if [ "$(id -u)" -ne 0 ]; then
    echo "Hay que ejecutarlo con sudo para crear la swap." >&2
    exit 1
fi

echo "=== Creando $ARCHIVO de $TAM ==="
set -x
fallocate -l "$TAM" "$ARCHIVO"
chmod 600 "$ARCHIVO"
mkswap "$ARCHIVO"
swapon "$ARCHIVO"
set +x
echo
swapon --show
free -h
echo
echo "Para quitarla al terminar la práctica:  sudo swapoff $ARCHIVO && sudo rm $ARCHIVO"
