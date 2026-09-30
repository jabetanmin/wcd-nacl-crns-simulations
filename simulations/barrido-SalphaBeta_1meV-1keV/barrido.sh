#!/bin/bash
# Barrido en energia con y sin S(alpha,beta), agua pura, geometria de la Campana 2.
# Uso (dentro del contenedor, con el entorno de Geant4 cargado):
#   ./barrido.sh [energias en eV ...]      por defecto: 0.1 0.3 10
# Las corridas que ya existen (carpeta con "Fin" en su registro) no se repiten.
# Al final imprime la tabla comparativa de todas las pruebas terminadas.
set -uo pipefail
BASE=$(cd "$(dirname "$0")" && pwd)
N=10000
if [ $# -gt 0 ]; then ENERGIAS=("$@"); else ENERGIAS=(0.1 0.3 10); fi

cd "$BASE"
echo "Barrido: ${ENERGIAS[*]} eV, $N neutrones, inicio $(date '+%F %T')"
for e in "${ENERGIAS[@]}"; do
  etiq=$(awk -v e="$e" 'BEGIN { if (e < 1) printf "%gmeV", e * 1000; else printf "%geV", e }')
  for fis in QGSP_BERT_HP QGSP_BERT_HP_NoThermal; do
    d="$BASE/$etiq-AguaPura-$fis-${N}N"
    if [ -f "$d/ejecucion.log" ] && grep -q "^Fin" "$d/ejecucion.log"; then
      echo "[$(date '+%T')] $etiq $fis: ya existe, no se repite"
      continue
    fi
    echo "[$(date '+%T')] $etiq $fis: corriendo..."
    if ./correr_prueba.sh "$fis" "$e" "$N" > "salida-$etiq-$fis.txt" 2>&1; then
      if grep -q "^OK:" "salida-$etiq-$fis.txt"; then
        echo "[$(date '+%T')] $etiq $fis: terminada, fisica correcta"
      else
        echo "[$(date '+%T')] $etiq $fis: ATENCION, revise salida-$etiq-$fis.txt"
      fi
    else
      echo "[$(date '+%T')] $etiq $fis: ERROR, revise salida-$etiq-$fis.txt"
    fi
  done
done
echo "Barrido terminado: $(date '+%F %T')"
echo
./tabla_barrido.sh
