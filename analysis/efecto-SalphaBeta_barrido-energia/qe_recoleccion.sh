#!/bin/bash
# Separa la conversion luz -> fotoelectrones en <QE> y eficiencia de recoleccion optica.
# En modo eFast, G4WCDStackingAction sortea la QE al crear cada foton Cherenkov, pero
# fotones-cherenkov.tsv registra TODOS los fotones (con su energia) antes del sorteo. Por eso:
#   <QE>    = suma_i QE(lambda_i) / N_Ch
#   eps_col = N_pe / suma_i QE(lambda_i)
# QE: respuesta R5912 de OptDevice.cc (interpolacion lineal 300-650 nm).
# Uso: ./qe_recoleccion.sh <carpeta de resultados-simulaciones> > qe_recoleccion.tsv
set -euo pipefail
R=${1:?Indique la carpeta Resultados-simulaciones}
echo -e "campana\trun\tN_ch\tsuma_QE\tN_pe\tQE_media\teps_col"
for c in Prueba-agua-pura Prueba-agua-25NaCl Prueba-agua-5NaCl Prueba-agua-10NaCl; do
  for d in "$R"/$c-1meV-1keV-dos-libreria/*N; do
    [ -d "$d" ] || continue
    npe=$(awk '{s+=$2} END{print s+0}' "$d/Datos-simulacion/Carga-total.txt")
    awk -F'\t' -v c="$c" -v r="$(basename "$d")" -v npe="$npe" '
      BEGIN{split("300 350 400 450 500 550 600 650",w," "); split("0.03 0.20 0.25 0.20 0.14 0.07 0.03 0.00",q," ")}
      /^#/{next}
      {l=1240/($16*1e6); n++; qe=0
       if(l>=300 && l<=650) for(i=2;i<=8;i++) if(l<=w[i]){qe=q[i-1]+(l-w[i-1])/(w[i]-w[i-1])*(q[i]-q[i-1]); break}
       s+=qe}
      END{printf "%s\t%s\t%d\t%.2f\t%d\t%.4f\t%.4f\n", c, r, n, s, npe, s/n, npe/s}' \
      "$d/Datos-simulacion/fotones-cherenkov.tsv"
  done
done
