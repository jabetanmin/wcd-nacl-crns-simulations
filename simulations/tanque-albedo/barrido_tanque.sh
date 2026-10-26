#!/bin/bash
# Corre ejecutar_tanque.sh para todas las humedades y los medios indicados, una tras otra (cada una en 4 partes).
# Uso (dentro del contenedor): ./barrido_tanque.sh <prueba|completa> [MEDIO ...]   (por defecto: AguaPura Agua10NaCl)
# Las ya hechas no se repiten.
set -uo pipefail
MODO=${1:?prueba o completa}; shift; MEDIOS=("$@"); [ ${#MEDIOS[@]} -eq 0 ] && MEDIOS=(AguaPura Agua10NaCl)
BASE=$(cd "$(dirname "$0")" && pwd); cd "$BASE"; mkdir -p resultados
N=$([ "$MODO" = prueba ] && echo 2000 || echo 100000)
echo "== Barrido del tanque $MODO: ${MEDIOS[*]}; inicio $(date '+%F %T')"; INI=$(date +%s)
for m in "${MEDIOS[@]}"; do for s in seco agua05 agua10 agua15 agua25 agua30; do
  if [ -d "resultados/$s-$m-${N}N" ]; then echo "   $s $m: ya existe"; continue; fi
  ./ejecutar_tanque.sh "$s" "$m" "$MODO" 4 > "resultados/salida-$s-$m-${N}N.txt" 2>&1
  echo "   [$(date '+%T')] $(grep "^OK\|ERROR\|ATENCION" "resultados/salida-$s-$m-${N}N.txt" | tail -1)"
done; done
echo "== Fin: $(( $(date +%s) - INI )) s"
awk -F'\t' '{ printf "%-8s %-11s %7s %7s %8s %8s %8s %8s %8s %8s %8s %6s\n", $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12 }' resultados/tanque.tsv
