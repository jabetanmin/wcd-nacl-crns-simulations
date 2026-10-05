#!/bin/bash
# Diagnostico 2 del factor ~0.70: compara, para cada electron (o positron) que emitio luz Cherenkov,
# los fotones esperados tras la QE (suma de QE de sus fotones creados) con los fotones seguidos.
# Si la perdida es por foton, todas las madres tienen seguidos/esperados ~0.70.
# Si es por madre, una fraccion de madres tiene 0 seguidos y el resto ~1.0.
# Uso: ./diagnostico_madres.sh <carpeta de la corrida, la que contiene Datos-simulacion>
set -euo pipefail
export LC_ALL=C
D=${1:?Indique la carpeta de la corrida}/Datos-simulacion
awk -F'\t' '
  BEGIN { split("300 350 400 450 500 550 600 650", w, " "); split("0.03 0.20 0.25 0.20 0.14 0.07 0.03 0.00", q, " ") }
  function qlin(l,   i) { if (l < 300 || l > 650) return 0
                         for (i = 2; i <= 8; i++) if (l <= w[i]) return q[i-1] + (l-w[i-1])/(w[i]-w[i-1])*(q[i]-q[i-1]) }
  FNR == 1 { archivo++ }
  /^#/ { next }
  archivo == 1 { k = $1 SUBSEP $2 SUBSEP $5; esp[k] += qlin(1240/($16*1e6)); ncre[k]++; next }
  archivo == 2 && $3 == "opticalphoton" && $6 == 1 { seg[$1 SUBSEP $2 SUBSEP $5]++; next }
  archivo == 2 && ($3 == "e-" || $3 == "e+") && $6 == 1 { ini[$1 SUBSEP $2 SUBSEP $4] = $16 }
  END {
    for (k in esp) {
      m++; E += esp[k]; S += seg[k]
      if (esp[k] >= 5) {
        g++; Eg += esp[k]; Sg += seg[k]
        if (seg[k] == 0) { cero++; Ecero += esp[k] }
        r = seg[k] / esp[k]; b = int(r * 5); if (b > 5) b = 5; hist[b]++
      }
    }
    printf "Madres con luz: %d   esperados %.0f   seguidos %d   cociente %.3f\n", m, E, S, S/E
    printf "Madres con >=5 fotones esperados: %d  (esperados %.0f, seguidos %d, cociente %.3f)\n", g, Eg, Sg, Sg/Eg
    printf "  de ellas con 0 seguidos: %d (%.1f %%), que suman el %.1f %% de los esperados\n", cero, 100*cero/g, 100*Ecero/Eg
    printf "  (si la perdida fuera por foton, P(0 seguidos | 5 esperados) seria ~ %.1f %%)\n", 100*exp(-5*0.70)
    printf "Distribucion de seguidos/esperados (madres con >=5 esperados):\n"
    split("0.0-0.2 0.2-0.4 0.4-0.6 0.6-0.8 0.8-1.0 >=1.0", et, " ")
    for (b = 0; b <= 5; b++) printf "  %-8s %6d  (%.1f %%)\n", et[b+1], hist[b], 100*hist[b]/g
  }' "$D/fotones-cherenkov.tsv" "$D/pasos-particulas.tsv"
