#!/bin/bash
# Barrido rápido de eficiencia del WCD para neutrones de 1 keV a 1 GeV (completa la respuesta de 1 meV a 1 keV de
# la Campaña 1), para plegar con los espectros del suelo y obtener la curva de calibración por humedad.
# Uso (dentro del contenedor, sin otra simulación corriendo):
#   ./barrido_rapidos.sh prueba   [MEDIO ...]   # 20 neutrones por energía: comprueba todo y mide el tiempo
#   ./barrido_rapidos.sh completa [MEDIO ...]   # la estadística de la tabla N_COMPLETA
#   MEDIO = AguaPura Agua25NaCl Agua5NaCl Agua10NaCl   (por defecto: AguaPura Agua10NaCl)
# Corre hasta PARALELO corridas a la vez (por defecto 4). Las ya hechas no se repiten.
set -uo pipefail
MODO=${1:?Indique prueba o completa}; shift
MEDIOS=("$@"); [ ${#MEDIOS[@]} -eq 0 ] && MEDIOS=(AguaPura Agua10NaCl)
PARALELO=${PARALELO:-4}
BASE=$(cd "$(dirname "$0")" && pwd); cd "$BASE"; mkdir -p resultados
#           energía [eV]  neutrones
N_COMPLETA=("1e3 10000" "1e4 10000" "1e5 10000" "1e6 10000" "5e6 10000" "2e7 5000" "1e8 2000" "1e9 1000")
case "$MODO" in prueba|completa) ;; *) echo "Uso: $0 prueba|completa [MEDIO ...]"; exit 1 ;; esac

if pgrep -x G4WCDSimulator > /dev/null; then echo "ERROR: ya hay una simulación G4WCDSimulator corriendo"; exit 1; fi
LIBRE=$(df -BG --output=avail "$BASE" | tail -1 | tr -dc '0-9'); MIN=$([ "$MODO" = prueba ] && echo 5 || echo 60)
(( LIBRE >= MIN )) || { echo "ERROR: hay $LIBRE GB libres; se piden $MIN GB"; exit 1; }
[ -f resultados/eficiencias.tsv ] || printf '# medio\tE_eV\tN\tincidentes\teps_Q1\teps_Q3\teps_Q5\teps_Q10\teps_Q20\tcapturas_agua\tQ_media_pe\tsegundos\n' > resultados/eficiencias.tsv
echo "== Barrido $MODO: ${MEDIOS[*]}; $PARALELO en paralelo; $LIBRE GB libres; inicio $(date '+%F %T')"
INI=$(date +%s)
for medio in "${MEDIOS[@]}"; do
  for par in "${N_COMPLETA[@]}"; do
    set -- $par; e=$1; n=$2; [ "$MODO" = prueba ] && n=20
    etq=$(awk -v e="$e" 'BEGIN { if (e >= 1e9) printf "%gGeV", e / 1e9; else if (e >= 1e6) printf "%gMeV", e / 1e6; else printf "%gkeV", e / 1e3 }')
    if [ -d "resultados/$etq-$medio-${n}N" ]; then echo "   $etq $medio: ya existe"; continue; fi
    while (( $(jobs -rp | wc -l) >= PARALELO )); do wait -n; done
    ( ./correr_energia.sh "$medio" "$e" "$n" > "resultados/salida-$etq-$medio-${n}N.txt" 2>&1
      echo "   [$(date '+%T')] $(tail -1 "resultados/salida-$etq-$medio-${n}N.txt")" ) &
    sleep 2
  done
done
wait
echo "== Fin: $(( $(date +%s) - INI )) s"
awk -F'\t' '{ printf "%-11s %6s %6s %6s %8s %8s %8s %8s %8s %8s %8s %6s\n", $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12 }' resultados/eficiencias.tsv
if [ "$MODO" = prueba ]; then
  # el arranque de Geant4 (tablas HP) es el mínimo de los tiempos de la prueba; se resta antes de repartir por neutrón
  echo "== Tiempo estimado del barrido completo (arranque de Geant4 restado):"
  awk -F'\t' -v par="$PARALELO" 'BEGIN { split("1e3 10000 1e4 10000 1e5 10000 1e6 10000 5e6 10000 2e7 5000 1e8 2000 1e9 1000", t, " ")
         for (i = 1; i <= 16; i += 2) full[t[i] + 0] = t[i + 1] }
       !/^#/ && $3 == 20 { k++; m[k] = $1; e[k] = $2 + 0; s[k] = $12; if (min == "" || $12 < min) min = $12 }
       END { for (i = 1; i <= k; i++) { pn = (s[i] - min) / 20; if (pn < 0.04) pn = 0.04
                                          t_i = min + pn * full[e[i]]; tot[m[i]] += t_i; if (t_i > mx) mx = t_i }
             printf "   arranque de Geant4: %d s por corrida\n", min
             for (x in tot) { printf "   %-11s ~ %.1f h en un proceso\n", x, tot[x] / 3600; all += tot[x] }
             printf "   total con %d en paralelo: ~ %.1f h (la corrida más larga: ~ %.1f h)\n", par, (all / par > mx ? all / par : mx) / 3600, mx / 3600 }' resultados/eficiencias.tsv
fi
