#!/usr/bin/env bash
# Aplica (o revierte) el parche del suelo SoilBS en MEIGA y recompila.
#   ./preparar_suelo.sh aplicar | revertir | estado
# No recompila si hay una simulacion G4WCDSimulator corriendo.
set -euo pipefail
ACCION="${1:-}"; AQUI="$(cd "$(dirname "$0")" && pwd)"
SRC="${MEIGA_SRC:-/opt/meiga/src}"; BUILD="${MEIGA_BUILD:-/opt/meiga/build}"
EXE="$BUILD/Applications/G4WCDSimulator/G4WCDSimulator"
CC="$SRC/Applications/G4WCDSimulator/G4WCDConstruction.cc"
case "$ACCION" in
  estado) python3 "$AQUI/agregar_suelo.py" "$SRC" --estado; exit 0 ;;
  aplicar) OPC="" ;;
  revertir) OPC="--revertir" ;;
  *) echo "Uso: $0 aplicar|revertir|estado"; exit 1 ;;
esac
if pgrep -x G4WCDSimulator > /dev/null; then
    echo "ERROR: hay una simulacion G4WCDSimulator corriendo. Espere a que termine antes de recompilar."; exit 1
fi
python3 "$AQUI/agregar_suelo.py" "$SRC" $OPC
echo "== Compilando MEIGA ($(date))"
cd "$BUILD"
if ! make -j4 > "$AQUI/compilacion-suelo-$ACCION.log" 2>&1; then
    echo "ERROR: fallo la compilacion. Ultimas lineas de $AQUI/compilacion-suelo-$ACCION.log:"; grep -n -i "error" "$AQUI/compilacion-suelo-$ACCION.log" | head -20; exit 1
fi
tail -2 "$AQUI/compilacion-suelo-$ACCION.log"
[[ "$EXE" -nt "$CC" ]] || { echo "ERROR: el ejecutable no es mas reciente que G4WCDConstruction.cc."; exit 1; }
echo "== Listo: MEIGA compilado ($(python3 "$AQUI/agregar_suelo.py" "$SRC" --estado))."
