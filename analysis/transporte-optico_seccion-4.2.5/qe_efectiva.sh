#!/bin/bash
# QE efectiva aplicada por el ejecutable en modo eFast.
# Compara, por longitud de onda, los fotones Cherenkov creados (fotones-cherenkov.tsv) con los
# fotones que el simulador realmente siguio (primer paso de cada opticalphoton en pasos-particulas.tsv).
# El cociente seguidos/creados es la probabilidad de supervivencia al sorteo de la QE en
# G4WCDStackingAction. Se compara con la QE interpolada del R5912 (OptDevice.cc) y con la tabla
# por escalones de 50 nm de la tesis (Cap. 3).
# Uso: ./qe_efectiva.sh <carpeta de la corrida, la que contiene Datos-simulacion>
set -euo pipefail
export LC_ALL=C
D=${1:?Indique la carpeta de la corrida}/Datos-simulacion
awk -F'\t' '
  BEGIN { split("300 350 400 450 500 550 600 650", w, " "); split("0.03 0.20 0.25 0.20 0.14 0.07 0.03 0.00", q, " ")
          split("0.01 0.03 0.20 0.25 0.20 0.14 0.07 0.03 0.01", e, " ") }
  function qlin(l,   i) { if (l < 300 || l > 650) return 0
                         for (i = 2; i <= 8; i++) if (l <= w[i]) return q[i-1] + (l-w[i-1])/(w[i]-w[i-1])*(q[i]-q[i-1]) }
  function qesc(l) { if (l < 250 || l >= 700) return 0; return e[int((l-250)/50)+1] }
  FNR == 1 { archivo++ }
  /^#/ { next }
  $16 + 0 <= 0 { next }
  archivo == 1 { l = 1240/($16*1e6); b = int(l/25)*25; cre[b]++; ncre++; slin[b] += qlin(l); sesc[b] += qesc(l); next }
  archivo == 2 && $3 == "opticalphoton" && $6 == 1 { l = 1240/($16*1e6); b = int(l/25)*25; seg[b]++; nseg++ }
  END {
    printf "%-10s %10s %10s %10s %10s %10s\n", "lambda_nm", "creados", "seguidos", "QE_efect", "QE_tabla", "QE_escal"
    for (b = 275; b <= 650; b += 25) if (cre[b] > 0)
      printf "%3d-%3d    %10d %10d %10.4f %10.4f %10.4f\n", b, b+25, cre[b], seg[b], seg[b]/cre[b], slin[b]/cre[b], sesc[b]/cre[b]
    for (b in cre) { tl += slin[b]; te += sesc[b] }
    printf "\nTotal: creados %d, seguidos %d, QE efectiva %.4f, QE tabla interpolada %.4f, QE escalones %.4f\n", ncre, nseg, nseg/ncre, tl/ncre, te/ncre
  }' "$D/fotones-cherenkov.tsv" "$D/pasos-particulas.tsv"
