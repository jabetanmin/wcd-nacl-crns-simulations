#!/bin/bash
# Resumen por evento y lista de capturas para las corridas con datos crudos (2.5 % y 10 % NaCl).
set -e
BASE="${ADATA:-/media/$USER/ADATA HD330}/Simulacion-fuente-241AmBe/Tipos-medios"
AQUI="$(cd "$(dirname "$0")" && pwd)"; RES="$AQUI/../resultados"
for par in "nacl25|$BASE/Agua+2.5NaCl/Datos-simulacion" "nacl10|$BASE/Agua+10NaCl/Agua+10NaCl/Datos-simulacion"; do
  m="${par%%|*}"; d="${par#*|}"
  echo "[$(date +%T)] $m: eventos"
  LC_ALL=C mawk -f "$AQUI/resumen_eventos.awk" "$d/rastreo-neutron-completo.txt" | gzip -1 > "$RES/eventos_$m.tsv.gz"
  echo "[$(date +%T)] $m: capturas"
  LC_ALL=C mawk '{print $2"\t"$3"\t"$6"\t"$7"\t"$8"\t"$9}' "$d/neutrones-capturados.txt" | gzip -1 > "$RES/capturas_$m.tsv.gz"
  LC_ALL=C mawk '$1!="gamma"{print $1"\t"$6"\t"$7"\t"$8}' "$d/secondary-particles-neutron-capturado.txt" | gzip -1 > "$RES/residuos_$m.tsv.gz"
  LC_ALL=C mawk '$1=="gamma"{print $6"\t"$7"\t"$8"\t"$9}' "$d/secondary-particles-neutron-capturado.txt" | gzip -1 > "$RES/gammas_captura_$m.tsv.gz"
  LC_ALL=C mawk '{print $2"\t"$3"\t"$6"\t"$7"\t"$8}' "$d/neutron-inelastico-punto.txt" | gzip -1 > "$RES/inelasticos_$m.tsv.gz"
done
echo "[$(date +%T)] FIN"
