#!/bin/bash
# Diagnostico del factor ~0.70 entre fotones Cherenkov creados y fotones seguidos.
# 1) Busca filas repetidas en fotones-cherenkov.tsv (el mismo foton registrado dos veces).
# 2) Compara, por particula madre, los fotones creados con los seguidos.
# Uso: ./diagnostico_cherenkov.sh <carpeta de la corrida, la que contiene Datos-simulacion>
set -euo pipefail
export LC_ALL=C
D=${1:?Indique la carpeta de la corrida}/Datos-simulacion
awk -F'\t' '
  FNR == 1 { archivo++ }
  /^#/ { next }
  archivo == 1 {
    n++
    k1 = $1 SUBSEP $2 SUBSEP $5 SUBSEP $6 SUBSEP $7          # corrida, evento, madre, paso de la madre, indice
    k2 = $1 SUBSEP $2 SUBSEP $13 SUBSEP $14 SUBSEP $15 SUBSEP $16   # corrida, evento, posicion y energia
    if (k1 in v1) d1++; else v1[k1] = 1
    if (k2 in v2) d2++; else v2[k2] = 1
    pasos[$1 SUBSEP $2 SUBSEP $5 SUBSEP $6]++
    madre[$4]++
    next
  }
  archivo == 2 && $3 == "opticalphoton" && $6 == 1 { seg++ }
  archivo == 2 && ($3 == "e-" || $3 == "e+") { ppadre[$1 SUBSEP $2 SUBSEP $4 SUBSEP $6] = 1 }
  END {
    printf "Filas en fotones-cherenkov.tsv:           %d\n", n
    printf "Repetidas (madre, paso, indice):          %d  (%.1f %%)\n", d1, 100*d1/n
    printf "Repetidas (posicion y energia):           %d  (%.1f %%)\n", d2, 100*d2/n
    printf "Fotones seguidos (primer paso):           %d\n", seg
    for (m in madre) printf "  creados por %-8s %d\n", m, madre[m]
    # Pasos de la madre con fotones que NO aparecen como paso de e-/e+ en pasos-particulas.tsv
    for (p in pasos) { np++; if (!(p in ppadre)) { nsin++; fsin += pasos[p] } }
    printf "Pasos madre con fotones:                  %d\n", np
    printf "  sin paso e-/e+ en pasos-particulas:     %d  (fotones en ellos: %d, %.1f %%)\n", nsin, fsin, 100*fsin/n
  }' "$D/fotones-cherenkov.tsv" "$D/pasos-particulas.tsv"
