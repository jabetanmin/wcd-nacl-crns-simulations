#!/usr/bin/env bash
# Rehace el análisis del albedo y el informe con todas las corridas que haya en la carpeta de resultados:
# el seco (50000N-...-seco-...) y cada humedad (200000N-...-aguaWW-...). Si aparece una humedad nueva (p. ej. 15 %),
# entra sola en las tablas, las figuras y las cifras.
#   scripts/actualizar_informe.sh <Corrida-suelo-albedo-resultados>   (o la variable SUELO_RES)
#   RAPIDOS_RES = carpetas del barrido rápido separadas por ":"; TANQUE_RES = resultados del tanque; ALL_BGA_SHW = campo
set -euo pipefail
AQUI="$(cd "$(dirname "$0")/.." && pwd)"; cd "$AQUI"
R="${1:-${SUELO_RES:-}}"; [[ -n "$R" ]] || { echo "Uso: $0 <Corrida-suelo-albedo-resultados> (o SUELO_RES)"; exit 1; }
[[ -d "$R" ]] || { echo "ERROR: no existe $R (¿está conectado el disco?)"; exit 1; }
SECO=$(ls "$R" | grep "^50000N-Bga-sobre-SoilBS-seco-" | tail -1)
[[ -n "$SECO" ]] || { echo "ERROR: no está la corrida del suelo seco en $R"; exit 1; }
COMPLETAS=(--corrida "seco (5e4)=$R/$SECO"); MISMOS=(--corrida "seco=$R/$SECO")
for d in $(ls "$R" | grep "^200000N-Bga-sobre-SoilBS-agua[0-9][0-9]-" | sort); do
    ww=$(echo "$d" | sed 's/.*-agua\([0-9][0-9]\)-.*/\1/'); w=$((10#$ww))
    n=$(for k in 1 2 3 4; do f=$(ls "$R/$d/parte$k" 2>/dev/null | grep "^Flujo-parte"); [[ -n "$f" ]] && grep -c "Run terminated" "$R/$d/parte$k/$f"; done | paste -sd+ | bc)
    if [[ "$n" != "200000" ]]; then echo "   se omite $d: $n de 200000 neutrones"; continue; fi
    echo "   humedad $w %: $d"
    COMPLETAS+=(--corrida "humedo-$w=$R/$d"); MISMOS+=(--corrida "humedo-$w (parte 1)=$R/$d@1")
done
echo "== Corridas completas"; python3 scripts/analizar_albedo.py "${COMPLETAS[@]}" > resultados/log_analizar_albedo.txt
echo "== Mismos neutrones (parte 1)"; python3 scripts/analizar_albedo.py --sufijo _validacion "${MISMOS[@]}" > resultados/log_analizar_albedo_validacion.txt
echo "== Curva de humedad"; python3 scripts/curva_humedad.py --carpetas > resultados/log_curva_humedad.txt
echo "== Procesos de los neutrones en el suelo"; python3 scripts/procesos_neutrones.py > resultados/log_procesos_neutrones.txt
echo "== Graficas de espectros y humedad"; python3 scripts/graficas_espectros.py > resultados/log_graficas_espectros.txt
echo "== Curva de calibracion del WCD (plegado)"; python3 scripts/curva_calibracion_wcd.py > resultados/log_curva_calibracion_wcd.txt
RAPD=(); IFS=: read -ra _RAP <<< "${RAPIDOS_RES:-}"; for D in "${_RAP[@]}"; do [[ -d "$D" ]] && RAPD+=("$D"); done
if (( ${#RAPD[@]} )); then echo "== Balance del barrido rapido: ${RAPD[*]}"; python3 scripts/balance_rapidos.py "${RAPD[@]}" > resultados/log_balance_rapidos.txt
else echo "   (sin el barrido rapido en el disco; se conserva resultados/balance_rapidos.tsv si existe)"; fi
if (( ${#RAPD[@]} )); then python3 scripts/captura_definiciones.py "${RAPD[@]}" > resultados/log_captura_definiciones.txt; else python3 scripts/captura_definiciones.py > resultados/log_captura_definiciones.txt; fi
if (( ${#RAPD[@]} )); then python3 scripts/luz_barrido.py "${RAPD[@]}" > resultados/log_luz_barrido.txt; else python3 scripts/luz_barrido.py > resultados/log_luz_barrido.txt; fi
echo "== Coeficientes de captura del WCD"; python3 scripts/captura_wcd.py > resultados/log_captura_wcd.txt
TANQ=${TANQUE_RES:-}
if [[ -n "$TANQ" ]]; then echo "== Curva de calibracion del WCD (simulacion directa): $TANQ"; python3 scripts/curva_calibracion_tanque.py --tanque "$TANQ" > resultados/log_curva_calibracion_tanque.txt
else echo "   (sin resultados del tanque; se conservan las tablas de la simulacion directa)"; fi
echo "== Sensibilidad a la humedad"; python3 scripts/sensibilidad.py > resultados/log_sensibilidad.txt
echo "== Esquemas del montaje"; python3 scripts/esquemas.py > resultados/log_esquemas.txt
echo "== Informe"; cd informe; for i in 1 2; do pdflatex -interaction=nonstopmode -halt-on-error Informe-albedo-suelo.tex > /dev/null; done
grep -q "quincetrue" cifras.tex && echo "   15 % incluido" || echo "   (todavía sin 15 %)"
echo "== Listo: informe/Informe-albedo-suelo.pdf ($(pdfinfo Informe-albedo-suelo.pdf | awk '/Pages/ {print $2}') páginas)"
