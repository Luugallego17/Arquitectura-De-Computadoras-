#!/bin/bash
# Crea (si falta) el entorno virtual, ejecuta los cuatro laboratorios y
# guarda las salidas originales en evidencias/. El .venv no se versiona.
#   bash ejecutar_pruebas.sh
cd "$(dirname "$0")" || exit 1
EV=evidencias
mkdir -p "$EV"
PY=".venv/bin/python3"

if [ ! -x "$PY" ]; then
  echo "No está el .venv. Créalo así y vuelve a lanzar este script:" >&2
  echo "  python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

export MPLBACKEND=Agg

{
  echo "# Entorno de las pruebas"
  echo "fecha      : $(date '+%d/%m/%Y %H:%M:%S %Z')"
  echo "kernel     : $(uname -sr)"
  echo "python     : $($PY --version 2>&1)"
  echo "venv       : $(pwd)/.venv"
  echo "CPU        : $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | sed 's/^ //')"
  echo "git        : $(git rev-parse --short HEAD 2>/dev/null || echo 'sin commit')"
  echo
  echo "\$ python3 -c \"import qiskit, qiskit_aer; print('Qiskit Core:', qiskit.__version__); print('Aer Simulator OK')\""
  $PY -c "import qiskit, qiskit_aer; print('Qiskit Core:', qiskit.__version__); print('Aer Simulator OK')"
  echo
  echo "\$ python3 -c \"import qiskit_aer, matplotlib, pylatexenc; print('qiskit-aer', qiskit_aer.__version__); print('matplotlib', matplotlib.__version__); print('pylatexenc', pylatexenc.__version__)\""
  $PY -c "import qiskit_aer, matplotlib, pylatexenc; print('qiskit-aer', qiskit_aer.__version__); print('matplotlib', matplotlib.__version__); print('pylatexenc', pylatexenc.__version__)"
} > "$EV/00_entorno.txt"

correr() {
  local salida="$1"
  shift
  {
    echo "\$ python3 $*"
    "$PY" "$@"
    echo "codigo de salida: $?"
  } > "$salida" 2>&1
}

correr "$EV/01_lab1_bell.txt" lab1_hola_mundo.py
{
  echo
  echo "\$ python3 lab1_hola_mundo.py --psi-plus"
  "$PY" lab1_hola_mundo.py --psi-plus
  echo "codigo de salida: $?"
} >> "$EV/01_lab1_bell.txt" 2>&1

correr "$EV/02_lab2_bloch.txt" lab2_rotaciones_bloch.py
correr "$EV/03_lab3_deutsch.txt" lab3_algoritmo_deutsch.py
correr "$EV/04_lab4_teletransportacion.txt" lab4_teletransportacion.py

fallos=$(grep -h '\[FALLO\]' "$EV"/0[1-4]_*.txt | wc -l)
codigos=$(grep -h 'codigo de salida: 0' "$EV"/0[1-4]_*.txt | wc -l)
echo "Evidencias escritas en $EV/ (lineas [FALLO]: $fallos, codigos de salida 0: $codigos)"
if [ "$fallos" -ne 0 ]; then
  exit 1
fi
