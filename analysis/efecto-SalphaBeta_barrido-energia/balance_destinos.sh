#!/bin/bash
# Balance de destinos del neutron primario para cada corrida del barrido.
# Uso: ./balance_destinos.sh <carpeta del barrido> [MEDIO, por defecto AguaPura] > balance_destinos.tsv
#
# Cada neutron primario (track_id 1; un run por neutron) se clasifica en:
#   captura_agua        ultimo paso nCapture en el agua
#   captura_estructura  ultimo paso nCapture en acero, Tyvek o Pyrex
#   reflexion_tapa      salio del tanque por la tapa (z > 132 cm)
#   escape_lateral      salio por la pared lateral
#   transmision_fondo   salio por el fondo (z < 1 cm)
#   desviado_en_aire    se desvio en el aire antes de llegar al tanque (nunca entro)
# La cara de salida se toma del ultimo paso dentro de un material del tanque, no de la
# posicion final en el borde del mundo; las capturas o reacciones (n,p) en el aire,
# ocurridas despues de salir, cuentan como escapes por esa cara.
set -euo pipefail
D=${1:?Indique la carpeta del barrido}
MEDIO=${2:-AguaPura}   # AguaPura, Agua25NaCl, Agua5NaCl o Agua10NaCl

printf "energia_eV\tetiqueta\tfisica\tincidentes\tcaptura_agua\tcaptura_estructura\treflexion_tapa\tescape_lateral\ttransmision_fondo\tdesviado_en_aire\tN_medio_captura_agua\tN_error_medio\tz_medio_captura_agua_cm\n"

for d in "$D"/*-"$MEDIO"-*-*N; do
  nombre=$(basename "$d")
  etiq=${nombre%%-"$MEDIO"-*}
  fis=${nombre#*-"$MEDIO"-}; fis=${fis%-*N}
  e_ev=$(awk -v t="$etiq" 'BEGIN { if (t ~ /meV$/) { sub(/meV$/, "", t); print t / 1000 } else { sub(/eV$/, "", t); print t + 0 } }')
  # pasos-neutrones.tsv: 1 run_id, 4 track_id, 8 step_process, 9 material, 13-15 post x,y,z (cm)
  awk -F'\t' -v e="$e_ev" -v et="$etiq" -v fis="$fis" '
  /^#/ { next }
  $4 != 1 { next }
  {
    r = $1
    seen[r] = 1
    ult_proc[r] = $8; ult_mat[r] = $9; ult_z[r] = $15
    if ($9 ~ /Water|Tyvek|STEEL|Pyrex/) { tz[r] = $15; trr[r] = sqrt($13 * $13 + $14 * $14) }
    if ($8 == "hadElastic") nel[r]++
  }
  END {
    for (r in seen) {
      n++
      if (ult_proc[r] == "nCapture" && ult_mat[r] ~ /Water/) { ca++; sN += nel[r]; sN2 += nel[r] * nel[r]; sZ += ult_z[r]; continue }
      if (ult_proc[r] == "nCapture" && ult_mat[r] ~ /Tyvek|STEEL|Pyrex/) { ce++; continue }
      if (!(r in tz)) { sc++; continue }
      if (tz[r] > 132) rt++
      else if (tz[r] < 1) tf++
      else el++
    }
    m = (ca ? sN / ca : 0); sem = (ca > 1 ? sqrt((sN2 / ca - m * m) / ca) : 0)
    printf "%s\t%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%.2f\t%.2f\t%.2f\n", e, et, fis, n, ca, ce, rt, el, tf, sc, m, sem, (ca ? sZ / ca : 0)
  }' "$d/Datos-simulacion/pasos-neutrones.tsv"
done | LC_ALL=C sort -t$'\t' -k1,1g -k3,3
