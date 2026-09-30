#!/bin/bash
# Cadena electromagnetica completa: interacciones gamma, electrones secundarios y luz Cherenkov.
# Uso: ./em_cadena.sh <carpeta del barrido>
# Escribe en la carpeta actual:
#   em_procesos.tsv    interacciones de todos los gammas, por proceso y material, para cada corrida
#   em_electrones.tsv  una fila por electron o positron: proceso creador, material, energia cinetica
#                      inicial y numero de fotones Cherenkov que emite
#   em_luz.tsv         fotones Cherenkov creados en cada evento (neutron), por material de emision
#
# Los fotones Cherenkov se asignan a su electron con (run_id, parent_track_id) de
# fotones-cherenkov.tsv; se registran al crearse, antes de aplicar la eficiencia cuantica del PMT.
set -euo pipefail
D=${1:?Indique la carpeta del barrido}

printf "energia_eV\tetiqueta\tfisica\tproceso\tmaterial\tinteracciones\n" > em_procesos.tsv
printf "energia_eV\tetiqueta\tfisica\trun_id\ttrack_id\tparticula\tcreador\tmaterial\tenergia_inicial_MeV\tfotones_cherenkov\n" > em_electrones.tsv
printf "energia_eV\tetiqueta\tfisica\trun_id\tfotones_agua\tfotones_otros\n" > em_luz.tsv

for d in "$D"/*-AguaPura-*-*N; do
  nombre=$(basename "$d")
  etiq=${nombre%%-AguaPura-*}
  fis=${nombre#*-AguaPura-}; fis=${fis%-*N}
  e_ev=$(awk -v t="$etiq" 'BEGIN { if (t ~ /meV$/) { sub(/meV$/, "", t); print t / 1000 } else { sub(/eV$/, "", t); print t + 0 } }')
  S="$d/Datos-simulacion"
  LC_ALL=C awk -F'\t' -v e="$e_ev" -v et="$etiq" -v fis="$fis" \
      -v fpr=em_procesos.tsv -v fel=em_electrones.tsv -v flu=em_luz.tsv '
  FNR == 1 { f++ }
  /^#/ { next }
  # 1) interacciones-gamma: proceso ($8) y material ($9)
  f == 1 { pm[$8 SUBSEP $9]++; next }
  # 2) pasos-electrones: primer paso de cada traza (step_number = 1)
  f == 2 && $6 == 1 {
    k = $1 SUBSEP $4
    ep[k] = $3; ec[k] = $7; em[k] = $9; et0[k] = $16
    next
  }
  # 3) fotones-cherenkov: run_id ($1), parent_track_id ($5), material de emision ($12)
  f == 3 {
    nf[$1 SUBSEP $5]++
    if ($12 ~ /Water/) la[$1]++; else lo[$1]++
    ev[$1] = 1
    next
  }
  END {
    for (k in pm) { split(k, a, SUBSEP); printf "%s\t%s\t%s\t%s\t%s\t%d\n", e, et, fis, a[1], a[2], pm[k] >> fpr }
    for (k in ep) {
      split(k, a, SUBSEP)
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%.6g\t%d\n", e, et, fis, a[1], a[2], ep[k], ec[k], em[k], et0[k], nf[k] + 0 >> fel
    }
    for (r in ev) printf "%s\t%s\t%s\t%s\t%d\t%d\n", e, et, fis, r, la[r] + 0, lo[r] + 0 >> flu
  }' "$S/interacciones-gamma.tsv" "$S/pasos-electrones.tsv" "$S/fotones-cherenkov.tsv"
done
echo "Listo: $(($(wc -l < em_electrones.tsv) - 1)) electrones/positrones y $(($(wc -l < em_luz.tsv) - 1)) eventos con luz"
