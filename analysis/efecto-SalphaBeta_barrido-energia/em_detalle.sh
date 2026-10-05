#!/bin/bash
# Cadena electromagnetica del barrido: gammas de captura y senal del PMT.
# Uso: ./em_detalle.sh <carpeta del barrido> [MEDIO, por defecto AguaPura]
# Escribe en la carpeta actual:
#   em_eventos.tsv  una fila por neutron incidente: destino del neutron, nucleo de captura,
#                   profundidad de la captura, numero de gammas de captura, cuantos interactuan en el agua,
#                   energia que transfieren al agua y carga del PMT (fotoelectrones)
#   em_gammas.tsv   una fila por gamma de captura: material de origen, nucleo de captura,
#                   profundidad de la captura,
#                   energia, si interactua en el agua, energia transferida al agua y destino
#
# Identificacion: los gammas de captura del neutron primario son las trazas de pasos-gamma.tsv
# con parent_id = 1 y creator_process = nCapture (en secundarias-captura-neutron.tsv el track_id
# aun no esta asignado y vale 0). La energia transferida al agua es la suma de (E_pre - E_post)
# de los pasos compt/phot/conv de ese gamma dentro del agua (energia entregada a electrones y
# positrones; no sigue a los gammas secundarios de aniquilacion o bremsstrahlung).
# Carga-total.txt contiene una linea por evento (= neutron = run), en el orden de los run_id.
# El nucleo de captura es el nucleo residual de secundarias-captura-neutron.tsv (deuteron -> H,
# Cl36 -> Cl35, Cl38 -> Cl37, Na24 -> Na23, O17 -> O16, isotopos de Fe, Cr y Ni -> acero).
set -euo pipefail
D=${1:?Indique la carpeta del barrido}
MEDIO=${2:-AguaPura}   # AguaPura, Agua25NaCl, Agua5NaCl o Agua10NaCl
Z_AGUA=133.062

printf "energia_eV\tetiqueta\tfisica\trun_id\tdestino\tnucleo\tprofundidad_captura_cm\tn_gammas\tn_gammas_interactuan_agua\tenergia_transferida_agua_MeV\tcarga_pe\n" > em_eventos.tsv
printf "energia_eV\tetiqueta\tfisica\trun_id\ttrack_id\torigen\tnucleo\tprofundidad_captura_cm\tenergia_MeV\tinteractua_agua\tenergia_transferida_agua_MeV\tsalida\n" > em_gammas.tsv

for d in "$D"/*-"$MEDIO"-*-*N; do
  nombre=$(basename "$d")
  etiq=${nombre%%-"$MEDIO"-*}
  fis=${nombre#*-"$MEDIO"-}; fis=${fis%-*N}
  e_ev=$(awk -v t="$etiq" 'BEGIN { if (t ~ /meV$/) { sub(/meV$/, "", t); print t / 1000 } else { sub(/eV$/, "", t); print t + 0 } }')
  S="$d/Datos-simulacion"
  LC_ALL=C awk -F'\t' -v e="$e_ev" -v et="$etiq" -v fis="$fis" -v zagua="$Z_AGUA" \
      -v fev=em_eventos.tsv -v fga=em_gammas.tsv '
  FNR == 1 { f++ }
  /^#/ { next }
  # 1) pasos-neutrones: destino del neutron primario (misma logica que balance_destinos.sh)
  f == 1 && $4 == 1 {
    r = $1; runs[r] = 1
    up[r] = $8; um[r] = $9; uz[r] = $15
    if ($9 ~ /Water|Tyvek|STEEL|Pyrex/) tz[r] = $15
    next
  }
  # 2) pasos-gamma: gammas de captura del neutron primario
  f == 2 && $5 == 1 && $7 == "nCapture" {
    k = $1 SUBSEP $4
    if (!(k in gorig)) {
      gorig[k] = ($9 ~ /Water/) ? "agua" : (($9 ~ /STEEL/) ? "acero" : "otro")
      ge[k] = $16; grun[k] = $1; gtrk[k] = $4
    }
    if (($8 == "compt" || $8 == "phot" || $8 == "conv") && $9 ~ /Water/) { gint[k] = 1; gdep[k] += $16 - $17 }
    if ($9 ~ /Water|Tyvek|STEEL|Pyrex/) gtz[k] = $15
    glp[k] = $8; glm[k] = $9
    next
  }
  # 3) Carga-total.txt: linea i -> run_id i
  f == 3 { carga[nq++] = $2; next }
  # 4) secundarias-captura-neutron: nucleo residual de la captura del neutron primario
  f == 4 && $3 == "nCapture" && $5 == 1 && $8 != "gamma" && $8 != "e-" && $8 != "e+" {
    p = $8
    if (p == "deuteron") n = ($12 ~ /Tyvek/) ? "H_Tyvek" : "H"
    else if (p == "Cl36") n = "Cl35"; else if (p == "Cl38") n = "Cl37"
    else if (p == "Na24") n = "Na23"; else if (p ~ /^O1[789]$/) n = "O"
    else if (p ~ /^(Fe|Cr|Ni|Mn)[0-9]+$/) n = "acero"; else n = p
    nuc[$1] = n
  }
  END {
    for (k in gorig) {
      r = grun[k]
      # Destino del gamma: absorbido (termina en phot o conv) o cara por la que sale del tanque
      if (glp[k] == "phot" || glp[k] == "conv") sal = (glm[k] ~ /Water/) ? "absorbido_agua" : "absorbido_estructura"
      else if (!(k in gtz)) sal = "sin_paso_en_tanque"
      else sal = (gtz[k] > 132) ? "sale_tapa" : ((gtz[k] < 1) ? "sale_fondo" : "sale_lateral")
      prof = (up[r] == "nCapture") ? zagua - uz[r] : -1
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%.4f\t%.6g\t%d\t%.6g\t%s\n", e, et, fis, r, gtrk[k], gorig[k], (r in nuc) ? nuc[r] : "NA", prof, ge[k], (k in gint), gdep[k] + 0, sal >> fga
      ng[r]++; if (k in gint) ngi[r]++; edep[r] += gdep[k]
    }
    for (r in runs) {
      if (up[r] == "nCapture" && um[r] ~ /Water/) des = "captura_agua"
      else if (up[r] == "nCapture" && um[r] ~ /Tyvek|STEEL|Pyrex/) des = "captura_estructura"
      else if (!(r in tz)) des = "desviado_en_aire"
      else if (tz[r] > 132) des = "reflexion_tapa"
      else if (tz[r] < 1) des = "transmision_fondo"
      else des = "escape_lateral"
      prof = (up[r] == "nCapture") ? zagua - uz[r] : -1
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%.4f\t%d\t%d\t%.6g\t%s\n", e, et, fis, r, des, (r in nuc) ? nuc[r] : "-", prof, ng[r] + 0, ngi[r] + 0, edep[r] + 0, (r in carga) ? carga[r] : "NA" >> fev
    }
    if (nq != length(runs)) printf "ATENCION %s %s: %d lineas de carga para %d neutrones\n", et, fis, nq, length(runs) > "/dev/stderr"
  }' "$S/pasos-neutrones.tsv" "$S/pasos-gamma.tsv" <(sed 's/^Carga:[[:space:]]*/x\t/' "$S/Carga-total.txt") "$S/secundarias-captura-neutron.tsv"
done
echo "Listo: $(($(wc -l < em_eventos.tsv) - 1)) eventos y $(($(wc -l < em_gammas.tsv) - 1)) gammas de captura"
