#!/bin/bash
# El WCD iluminado por los neutrones que SUBEN del suelo con cada humedad (simulación directa de la curva de
# calibración). Los archivos de flujos/ traen, para cada suelo, neutrones con su energía y su dirección reales,
# inyectados 1 mm fuera de la base o del costado del tanque (generados con generar_entrada_tanque.py; ver LEEME).
# Sin suelo en la geometría (el suelo ya está en el espectro), sin S(alpha,beta), PMT del contenedor (Sidelnik, 0.3·H/2).
# Uso (dentro del contenedor, sin otra simulación corriendo):
#   ./ejecutar_tanque.sh <suelo> <medio> <prueba|completa> [PARTES]
#   suelo = seco | agua05 | agua10 | agua15 | agua25 | agua30
#   medio = AguaPura | Agua25NaCl | Agua5NaCl | Agua10NaCl
#   prueba: 2000 neutrones; completa: 100 000; PARTES corridas paralelas (1-4, por defecto 4)
# Agrega una línea a resultados/tanque.tsv:
#   suelo medio N incidentes eps_Q1 eps_Q3 eps_Q5 eps_Q10 eps_Q20 capturas_agua Q_media_pe segundos
set -euo pipefail
SUELO=${1:?suelo}; MEDIO=${2:?medio}; MODO=${3:?prueba o completa}; PARTES=${4:-4}
BASE=$(cd "$(dirname "$0")" && pwd)
EXE=${MEIGA_EXE:-/opt/meiga/build/Applications/G4WCDSimulator/G4WCDSimulator}
case "$MEDIO" in AguaPura) W=0 ;; Agua25NaCl) W=0.025 ;; Agua5NaCl) W=0.05 ;; Agua10NaCl) W=0.1 ;; *) echo "medio no reconocido: $MEDIO"; exit 1 ;; esac
case "$MODO" in prueba) N=2000; F="$BASE/flujos/prueba/2000N-sube-$SUELO.txt" ;; completa) N=100000; F="$BASE/flujos/100000N-sube-$SUELO.txt" ;;
  *) echo "modo: prueba o completa"; exit 1 ;; esac
[ -f "$F" ] || { echo "No existe $F"; exit 1; }
[[ "$PARTES" =~ ^[1-4]$ ]] || { echo "PARTES debe ser 1-4"; exit 1; }
[ -x "$EXE" ] || { echo "No se encuentra $EXE"; exit 1; }
if pgrep -x G4WCDSimulator > /dev/null; then echo "ERROR: ya hay una simulación G4WCDSimulator corriendo"; exit 1; fi
unset MEIGA_SUELO_W MEIGA_SUELO_XY MEIGA_SUELO_Z MEIGA_SIN_TANQUE MEIGA_SUELO_SEPARACION
NL=$(grep -c . "$F"); [ "$NL" -eq "$N" ] || { echo "ERROR: $F tiene $NL líneas (se esperaban $N)"; exit 1; }
D="$BASE/resultados/$SUELO-$MEDIO-${N}N"; [ -e "$D" ] && { echo "Ya existe $D (bórrela para repetir)"; exit 1; }
mkdir -p "$D"; split -n "l/$PARTES" -d -a 1 "$F" "$D/p"
echo "== $SUELO $MEDIO $MODO: $N neutrones en $PARTES partes, inicio $(date '+%F %T')"; INI=$(date +%s)
correr() {
  local k=$1 d="$D/parte$k"
  mkdir -p "$d/Datos-simulacion"; mv "$D/p$((k-1))" "$d/flujo.txt"
  cp "$BASE/configuracion/DetectorList-$MEDIO.xml" "$d/DetectorList.xml"; cp "$BASE/configuracion/G4WCDSimulator.json" "$d/config.json"
  ( cd "$d" && "$EXE" -c config.json > ejecucion.log 2>&1 ) || { echo "   ERROR en la parte $k (vea $d/ejecucion.log)"; return 1; }
  echo "   parte $k terminada ($(( $(date +%s) - INI )) s)"
}
for k in $(seq 1 "$PARTES"); do correr "$k" & sleep 3; done; wait
SEG=$(( $(date +%s) - INI ))
# comprobaciones: física, medio, sin suelo, una carga por neutrón
for k in $(seq 1 "$PARTES"); do L="$D/parte$k/ejecucion.log"
  grep -q "QGSP_BERT_HP without S(alpha,beta)" "$L" || { echo "ATENCION parte $k: la física no es NoThermal"; exit 1; }
  WL=$(grep -m1 "NaCl final mass fraction =" "$L" | awk -F'= ' '{ print $2 + 0 }')
  awk -v a="${WL:-x}" -v b="$W" 'BEGIN { exit !((a - b) ^ 2 < 1e-12) }' || { echo "ATENCION parte $k: NaCl = ${WL:-?}, se pidió $W"; exit 1; }
  grep -q "Suelo SoilBS" "$L" && { echo "ATENCION parte $k: hay suelo en la geometría"; exit 1; }
done
cat "$D"/parte[1-4]/Datos-simulacion/Carga-total.txt 2>/dev/null > "$D/Carga-total.txt"
NQ=$(grep -c . "$D/Carga-total.txt"); [ "$NQ" -eq "$N" ] || { echo "ATENCION: $NQ cargas para $N neutrones"; exit 1; }
CAP=0; for k in $(seq 1 "$PARTES"); do c=$(awk -F'\t' '!/^#/ && $8 == "nCapture" && $9 ~ /Water/ { c[$1] = 1 } END { print length(c) }' "$D/parte$k/Datos-simulacion/pasos-neutrones.tsv"); CAP=$((CAP + c)); done
[ -f "$BASE/resultados/tanque.tsv" ] || printf '# suelo\tmedio\tN\tincidentes\teps_Q1\teps_Q3\teps_Q5\teps_Q10\teps_Q20\tcapturas_agua\tQ_media_pe\tsegundos\n' > "$BASE/resultados/tanque.tsv"
LINEA=$(awk -v n="$N" -v s0="$SUELO" -v m="$MEDIO" -v cap="$CAP" -v seg="$SEG" '{ q = $2 + 0; s += q
  if (q >= 1) a++; if (q >= 3) b++; if (q >= 5) c++; if (q >= 10) d++; if (q >= 20) f++ }
  END { printf "%s\t%s\t%d\t%d\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.5f\t%.3f\t%d\n", s0, m, n, NR, a/n, b/n, c/n, d/n, f/n, cap/n, s/n, seg }' "$D/Carga-total.txt")
echo "$LINEA" >> "$BASE/resultados/tanque.tsv"
echo "OK $SUELO $MEDIO: $(echo "$LINEA" | awk -F'\t' '{ printf "eps(Q>=1) = %.4f, eps(Q>=5) = %.4f, capturas en agua = %.4f, <Q> = %.2f p.e., %d s", $5, $7, $10, $11, $12 }')"
# para no llenar el disco: quedan la carga, las capturas, los incidentes y los registros
for k in $(seq 1 "$PARTES"); do ( cd "$D/parte$k/Datos-simulacion" && rm -f pasos-particulas.tsv pasos-electrones.tsv pasos-gamma.tsv interacciones-gamma.tsv secundarias-interaccion-gamma.tsv fotones-cherenkov.tsv ); done
echo "== Listo: $D ($(du -sh "$D" | cut -f1), $SEG s)"
