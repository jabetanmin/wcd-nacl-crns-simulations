#!/bin/bash
# Resume una corrida de prueba del WCD a partir de sus archivos TSV.
# Uso: ./resumen_prueba.sh <carpeta con neutrones-incidentes.tsv y pasos-neutrones.tsv> [--tsv]
# Con --tsv imprime una sola linea separada por tabuladores:
#   incidentes  capturados_total  pct_total  capturados_agua  pct_agua  error_pct_agua  N_medio
set -euo pipefail
D=${1:?Indique la carpeta que contiene los TSV}
MODO=${2:-texto}

# Columnas: 1 run_id, 4 track_id. Cada neutron primario es un run (BeamOn(1)).
awk -F'\t' -v modo="$MODO" '
FNR == 1 { archivo++ }
/^#/ { next }
archivo == 1 && $4 == 1 { inc[$1] = 1 }
# pasos-neutrones.tsv: 8 step_process, 9 material
archivo == 2 && $4 == 1 && $8 == "nCapture" {
    cap[$1] = 1
    if ($9 ~ /Water/) capagua[$1] = 1
}
archivo == 2 && $4 == 1 && $8 == "hadElastic" {
    nel[$1]++
    if ($9 ~ /Water/) nelagua[$1]++
}
END {
    n = length(inc); nc = length(cap); na = length(capagua)
    for (r in capagua) { s += nel[r]; sa += nelagua[r]; s2 += nel[r] * nel[r] }
    m = (na > 0) ? s / na : 0
    pa = 100 * na / n; ea = 100 * sqrt(na / n * (1 - na / n) / n)
    if (modo == "--tsv") {
        printf "%d\t%d\t%.2f\t%d\t%.2f\t%.2f\t%.1f\n", n, nc, 100 * nc / n, na, pa, ea, m
        exit
    }
    printf "Neutrones incidentes            : %d\n", n
    printf "Capturados (cualquier material) : %d  (%.2f %%)\n", nc, 100 * nc / n
    printf "Capturados en el agua           : %d  (%.2f %% +- %.2f)\n", na, pa, ea
    if (na > 0) {
        printf "<N> dispersiones elasticas antes de la captura en el agua\n"
        printf "   todas las regiones           : %.2f  (desv. est. %.2f)\n", m, sqrt(s2 / na - m * m)
        printf "   solo dentro del agua         : %.2f\n", sa / na
    }
}' "$D/neutrones-incidentes.tsv" "$D/pasos-neutrones.tsv"
