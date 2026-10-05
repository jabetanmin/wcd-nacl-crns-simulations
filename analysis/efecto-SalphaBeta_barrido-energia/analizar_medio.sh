#!/bin/bash
# Analisis completo del barrido de un medio detector.
# Uso: ./analizar_medio.sh <MEDIO> <carpeta del barrido>
#   MEDIO: AguaPura, Agua25NaCl, Agua5NaCl o Agua10NaCl
# Escribe todos los resultados (TSV y figuras) en salida/<MEDIO>/.
set -euo pipefail
MEDIO=${1:?Indique el medio: AguaPura, Agua25NaCl, Agua5NaCl o Agua10NaCl}
D=$(cd "${2:?Indique la carpeta del barrido}" && pwd)
BASE=$(cd "$(dirname "$0")" && pwd)
OUT="$BASE/salida/$MEDIO"
mkdir -p "$OUT"
cd "$OUT"

echo "[$(date '+%T')] $MEDIO: destinos"
"$BASE/balance_destinos.sh" "$D" "$MEDIO" > balance_destinos.tsv
echo "[$(date '+%T')] $MEDIO: capturas"
"$BASE/capturas_detalle.sh" "$D" "$MEDIO" > capturas_detalle.tsv
echo "[$(date '+%T')] $MEDIO: cadena EM (gammas y carga)"
"$BASE/em_detalle.sh" "$D" "$MEDIO"
echo "[$(date '+%T')] $MEDIO: cadena EM (procesos, electrones y luz)"
"$BASE/em_cadena.sh" "$D" "$MEDIO"
echo "[$(date '+%T')] $MEDIO: figuras"
for f in figuras_barrido figuras_capturas figuras_em figuras_em2; do
  MEDIO="$MEDIO" SALIDA="$OUT" python3 "$BASE/$f.py"
done
echo "[$(date '+%T')] $MEDIO: listo en $OUT"
