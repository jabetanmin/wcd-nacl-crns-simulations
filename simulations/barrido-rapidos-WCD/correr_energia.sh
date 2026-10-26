#!/bin/bash
# Una corrida del barrido rápido: neutrones monoenergéticos verticales sobre el WCD (geometría del barrido de
# S(alpha,beta): agua R = 48 cm, H = 133 cm, inyección desde z = 200 cm en un círculo de 40 cm), sin S(alpha,beta).
# Uso (dentro del contenedor):  ./correr_energia.sh <MEDIO> <energía en eV> <neutrones>
#   MEDIO = AguaPura | Agua25NaCl | Agua5NaCl | Agua10NaCl
# Escribe en resultados/<energía>-<MEDIO>-<N>N/ y agrega una línea a resultados/eficiencias.tsv:
#   medio  E_eV  N  incidentes  eps_Q1  eps_Q3  eps_Q5  eps_Q10  eps_Q20  capturas_agua  Q_media_pe  segundos
set -euo pipefail
MEDIO=${1:?Indique el medio}; E_EV=${2:?Indique la energía en eV}; N=${3:?Indique el número de neutrones}
BASE=$(cd "$(dirname "$0")" && pwd)
EXE=${MEIGA_EXE:-/opt/meiga/build/Applications/G4WCDSimulator/G4WCDSimulator}
case "$MEDIO" in
  AguaPura) W=0 ;; Agua25NaCl) W=0.025 ;; Agua5NaCl) W=0.05 ;; Agua10NaCl) W=0.1 ;;
  *) echo "MEDIO no reconocido: $MEDIO"; exit 1 ;;
esac
XML="$BASE/configuracion/DetectorList-$MEDIO.xml"; [ -f "$XML" ] || { echo "No existe $XML"; exit 1; }
[ -x "$EXE" ] || { echo "No se encuentra el ejecutable $EXE"; exit 1; }
unset MEIGA_SUELO_W MEIGA_SUELO_XY MEIGA_SUELO_Z MEIGA_SIN_TANQUE MEIGA_SUELO_SEPARACION   # sin suelo

# p = sqrt(E^2 + 2 m E) en GeV/c (m = 939.565420 MeV); etiqueta legible 1keV, 5MeV, 1GeV...
PZ=$(awk -v e="$E_EV" 'BEGIN { m = 939565420.0; printf "%.8g", sqrt(e * e + 2 * m * e) / 1e9 }')
ETQ=$(awk -v e="$E_EV" 'BEGIN { if (e >= 1e9) printf "%gGeV", e / 1e9; else if (e >= 1e6) printf "%gMeV", e / 1e6;
                               else if (e >= 1e3) printf "%gkeV", e / 1e3; else printf "%geV", e }')
D="$BASE/resultados/$ETQ-$MEDIO-${N}N"
[ -e "$D" ] && { echo "Ya existe $D (bórrela o renómbrela para repetir)"; exit 1; }
mkdir -p "$D/Datos-simulacion"; cd "$D"
awk -v n="$N" -v p="$PZ" 'BEGIN { for (i = 0; i < n; i++) print "13 0 0 " p " 0 0 0 0 0 0 0 0" }' > flujo.txt
cp "$XML" DetectorList.xml; cp "$BASE/configuracion/G4WCDSimulator.json" config.json
INI=$(date +%s); echo "Inicio: $(date '+%F %T')  $MEDIO  $ETQ  $N neutrones" > ejecucion.log
"$EXE" -c config.json >> ejecucion.log 2>&1 || { echo "ERROR del simulador en $D (vea ejecucion.log)"; exit 1; }
SEG=$(( $(date +%s) - INI )); echo "Fin: $(date '+%F %T')  ($SEG s)" >> ejecucion.log

# comprobaciones: física, medio, que no haya suelo, número de cargas
grep -q "QGSP_BERT_HP without S(alpha,beta)" ejecucion.log || { echo "ATENCION $D: la física no es QGSP_BERT_HP_NoThermal"; exit 1; }
WL=$(grep -m1 "NaCl final mass fraction =" ejecucion.log | awk -F'= ' '{ print $2 + 0 }')
awk -v a="${WL:-x}" -v b="$W" 'BEGIN { exit !((a - b) ^ 2 < 1e-12) }' || { echo "ATENCION $D: NaCl = ${WL:-?}, se pidió $W"; exit 1; }
grep -q "Suelo SoilBS" ejecucion.log && { echo "ATENCION $D: la corrida tiene suelo"; exit 1; }
Q="Datos-simulacion/Carga-total.txt"; [ -f "$Q" ] || { echo "ATENCION $D: no hay $Q"; exit 1; }
NQ=$(grep -c . "$Q"); [ "$NQ" -eq "$N" ] || { echo "ATENCION $D: $NQ cargas para $N neutrones"; exit 1; }

# eficiencias con umbral de carga y capturas en el agua
CAP=$(awk -F'\t' '!/^#/ && $8 == "nCapture" && $9 ~ /Water/ { c[$1] = 1 } END { print length(c) }' Datos-simulacion/pasos-neutrones.tsv 2>/dev/null || echo 0)
LINEA=$(awk -v n="$N" -v medio="$MEDIO" -v e="$E_EV" -v cap="$CAP" -v seg="$SEG" '{ q = $2 + 0; s += q
          if (q >= 1) a++; if (q >= 3) b++; if (q >= 5) c++; if (q >= 10) d++; if (q >= 20) f++ }
        END { printf "%s\t%s\t%d\t%d\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.3f\t%d\n", medio, e, n, NR, a/n, b/n, c/n, d/n, f/n, cap/n, s/n, seg }' "$Q")
echo "$LINEA" >> "$BASE/resultados/eficiencias.tsv"
echo "OK $ETQ $MEDIO: $(echo "$LINEA" | awk -F'\t' '{ printf "eps(Q>=1) = %.4f, eps(Q>=5) = %.4f, capturas en agua = %.4f, <Q> = %.2f p.e., %d s", $5, $7, $10, $11, $12 }')"
# para no llenar el disco: se conservan la carga, las capturas y los incidentes; el resto se borra
cd Datos-simulacion && rm -f pasos-particulas.tsv pasos-electrones.tsv pasos-gamma.tsv interacciones-gamma.tsv secundarias-interaccion-gamma.tsv fotones-cherenkov.tsv
