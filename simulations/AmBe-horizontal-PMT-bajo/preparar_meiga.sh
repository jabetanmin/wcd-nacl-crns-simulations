#!/usr/bin/env bash
# Baja el PMT (o lo devuelve a la tapa) y recompila MEIGA.
#   ./preparar_meiga.sh bajar      # zPMT = 0.3*fWaterHalfHeight, recompila
#   ./preparar_meiga.sh revertir   # PMT de Sidelnik en la tapa otra vez, recompila
# No hace nada si hay una simulacion G4WCDSimulator corriendo (recompilar la dañaria).
# Variables opcionales: MEIGA_SRC (/opt/meiga/src), MEIGA_BUILD (/opt/meiga/build)
set -euo pipefail
ACCION="${1:-}"
[[ "$ACCION" == "bajar" || "$ACCION" == "revertir" ]] || { echo "Uso: $0 bajar|revertir"; exit 1; }
AQUI="$(cd "$(dirname "$0")" && pwd)"
SRC="${MEIGA_SRC:-/opt/meiga/src}"; BUILD="${MEIGA_BUILD:-/opt/meiga/build}"
EXE="$BUILD/Applications/G4WCDSimulator/G4WCDSimulator"
if pgrep -x G4WCDSimulator > /dev/null; then
    echo "ERROR: hay una simulacion G4WCDSimulator corriendo. Espere a que termine antes de recompilar."; exit 1
fi
if [[ "$ACCION" == "bajar" ]]; then python3 "$AQUI/bajar_pmt.py" "$SRC"; else python3 "$AQUI/bajar_pmt.py" "$SRC" --revertir; fi
echo "== Linea zPMT activa:"; grep -n "const G4double zPMT =" "$SRC/G4Models/SaltyWCD.cc" | grep -v "^\s*[0-9]*:\s*//"
echo "== Compilando MEIGA ($(date))"
cd "$BUILD"
if ! make -j4 > "$AQUI/compilacion-$ACCION.log" 2>&1; then
    echo "ERROR: fallo la compilacion. Ultimas lineas de $AQUI/compilacion-$ACCION.log:"; tail -20 "$AQUI/compilacion-$ACCION.log"; exit 1
fi
tail -3 "$AQUI/compilacion-$ACCION.log"
[[ "$EXE" -nt "$SRC/G4Models/SaltyWCD.cc" ]] || { echo "ERROR: el ejecutable no es mas reciente que SaltyWCD.cc."; exit 1; }
echo "== Listo: MEIGA compilado con el PMT $( [[ $ACCION == bajar ]] && echo 'BAJADO (0.3*fWaterHalfHeight)' || echo 'en la TAPA (Sidelnik)' )."
