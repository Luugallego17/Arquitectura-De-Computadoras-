#!/bin/bash
# Compila los cuatro programas del laboratorio, los ejecuta y guarda las
# salidas originales en evidencias/ (sin editar).
#   bash ejecutar_pruebas.sh
cd "$(dirname "$0")" || exit 1
EV=evidencias
BIN=$(mktemp -d)
mkdir -p "$EV"
PROGS="exp1_puerto_teclado exp2_cola_teclado exp3_vram_monitor reto_integrador_terminal"
FLAGS="-std=c99 -Wall -Wextra -pedantic"

{
  echo "# Entorno de las pruebas"
  echo "fecha    : $(date '+%d/%m/%Y %H:%M:%S %Z')"
  echo "kernel   : $(uname -sr)"
  echo "gcc      : $(gcc --version | head -1)"
  echo "valgrind : $(valgrind --version 2>/dev/null || echo 'no disponible')"
  echo "gcov     : $(gcov --version 2>/dev/null | head -1)"
  echo "CPU      : $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | sed 's/^ //')"
  echo "git      : $(git rev-parse --short HEAD 2>/dev/null)"
} > $EV/00_entorno.txt

{
  echo "# Compilacion con $FLAGS (sin salida = sin advertencias)"
  for p in $PROGS; do
    echo "\$ gcc $FLAGS $p.c -o $p"
    gcc $FLAGS $p.c -o "$BIN/$p" 2>&1
  done
  echo "(fin)"
} > $EV/01_compilacion.txt

n=2
for p in exp1_puerto_teclado exp2_cola_teclado exp3_vram_monitor; do
  { echo "\$ ./${p}"; "$BIN/$p"; echo "codigo de salida: $?"; } > "$EV/0${n}_${p}.txt" 2>&1
  n=$((n+1))
done
{ echo "\$ ./terminal"; "$BIN/reto_integrador_terminal"; echo "codigo de salida: $?"; } > $EV/05_reto_integrador_terminal.txt 2>&1

# Terminal interactiva: '<' hace de Backspace. Se escribe HOLA, se borra la A,
# se reescribe "ANOS" (el texto salta de fila) y luego "XY" con dos borrados.
{
  echo "\$ printf 'HOLA<ANOS\\nXY<<\\n' | ./terminal -i"
  printf 'HOLA<ANOS\nXY<<\n' | "$BIN/reto_integrador_terminal" -i
} > $EV/06_terminal_interactiva.txt 2>&1

# Fallo del codigo literal del enunciado
{
  echo "\$ gcc $FLAGS demo_cursor_uint8.c -o demo_cursor_uint8"
  gcc $FLAGS demo_cursor_uint8.c -o "$BIN/demo" 2>&1
  echo "\$ ./demo_cursor_uint8"
  "$BIN/demo"
} > $EV/07_fallo_cursor_uint8.txt 2>&1

# Sanitizers y valgrind
{
  for p in $PROGS; do
    echo "\$ gcc -g -fsanitize=address,undefined -fno-omit-frame-pointer $p.c && ./a.out"
    gcc -g -std=c99 -fsanitize=address,undefined -fno-omit-frame-pointer $p.c -o "$BIN/san_$p" 2>&1
    "$BIN/san_$p" > "$BIN/san.out" 2>&1; rc=$?
    echo "  codigo de salida: $rc | errores ASan/UBSan: $(grep -c -E 'ERROR: AddressSanitizer|runtime error' "$BIN/san.out") | pruebas: $(grep -E '^Resultado' "$BIN/san.out")"
  done
  echo
  for p in $PROGS; do
    gcc -g -std=c99 $p.c -o "$BIN/vg_$p" 2>&1
    echo "\$ valgrind --leak-check=full --error-exitcode=9 ./$p"
    valgrind --leak-check=full --error-exitcode=9 "$BIN/vg_$p" > /dev/null 2> "$BIN/vg.err"; echo "  codigo de salida: $?"
    grep -E 'ERROR SUMMARY|All heap blocks|total heap usage' "$BIN/vg.err" | sed 's/^==[0-9]*== /  /'
  done
} > $EV/08_sanitizers_valgrind.txt 2>&1

# Cobertura de lineas con gcov
{
  for p in $PROGS; do
    mkdir -p "$BIN/cov_$p" && cp $p.c "$BIN/cov_$p/"
    ( cd "$BIN/cov_$p" && gcc -std=c99 --coverage -O0 $p.c -o t && ./t > /dev/null && gcov -b t-$p.gcda 2>/dev/null | grep -A3 "File '$p.c'" )
  done
} > $EV/09_cobertura_gcov.txt 2>&1

# Trazas CSV usadas para los graficos
{ for p in exp1_puerto_teclado exp2_cola_teclado exp3_vram_monitor reto_integrador_terminal; do echo "\$ ./$p -t"; "$BIN/$p" -t; echo; done; } > $EV/10_trazas.txt 2>&1

rm -rf "$BIN"
fallos=$(grep -l 'HAY FALLOS' $EV/0[2-5]_*.txt 2>/dev/null | wc -l)
echo "Evidencias escritas en $EV/ ($fallos programas con fallos)"
