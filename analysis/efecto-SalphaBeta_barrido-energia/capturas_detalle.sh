#!/bin/bash
# Detalle de cada neutron primario capturado en el agua, para todas las corridas del barrido.
# Uso: ./capturas_detalle.sh <carpeta del barrido> [MEDIO, por defecto AguaPura] > capturas_detalle.tsv
#
# Columnas de salida:
#   energia_eV, etiqueta, fisica
#   profundidad_cm   distancia de la captura bajo la superficie del agua (z = 133.062 cm)
#   radio_cm         distancia radial de la captura al eje del tanque
#   tiempo_us        tiempo desde que el neutron toca la tapa hasta la captura (sin el vuelo por el aire)
#   energia_previa_eV  energia cinetica del neutron al comenzar el paso en que se captura
set -euo pipefail
D=${1:?Indique la carpeta del barrido}
MEDIO=${2:-AguaPura}   # AguaPura, Agua25NaCl, Agua5NaCl o Agua10NaCl
Z_AGUA=133.062

printf "energia_eV\tetiqueta\tfisica\tprofundidad_cm\tradio_cm\ttiempo_us\tenergia_previa_eV\n"
for d in "$D"/*-"$MEDIO"-*-*N; do
  nombre=$(basename "$d")
  etiq=${nombre%%-"$MEDIO"-*}
  fis=${nombre#*-"$MEDIO"-}; fis=${fis%-*N}
  e_ev=$(awk -v t="$etiq" 'BEGIN { if (t ~ /meV$/) { sub(/meV$/, "", t); print t / 1000 } else { sub(/eV$/, "", t); print t + 0 } }')
  # pasos-neutrones.tsv: 1 run_id, 4 track_id, 8 step_process, 9 material,
  # 13-15 post x,y,z (cm), 16 pre_energy_MeV, 18 global_time_ns (al final del paso).
  # Los pasos de cada neutron aparecen consecutivos y en orden.
  LC_ALL=C awk -F'\t' -v e="$e_ev" -v et="$etiq" -v fis="$fis" -v zagua="$Z_AGUA" '
  /^#/ { next }
  $4 != 1 { next }
  {
    if ($1 != run) { run = $1; dentro = 0; t_prev = 0; t_entrada = -1 }
    if (!dentro && $9 ~ /Water|Tyvek|STEEL|Pyrex/) { dentro = 1; t_entrada = t_prev }
    if ($8 == "nCapture" && $9 ~ /Water/ && t_entrada >= 0) {
      printf "%s\t%s\t%s\t%.4f\t%.4f\t%.4f\t%.6g\n", e, et, fis, zagua - $15,
             sqrt($13 * $13 + $14 * $14), ($18 - t_entrada) / 1000, $16 * 1e6
    }
    t_prev = $18
  }' "$d/Datos-simulacion/pasos-neutrones.tsv"
done
