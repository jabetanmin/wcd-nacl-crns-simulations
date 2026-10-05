#!/bin/bash
# Tabla comparativa con y sin S(alpha,beta) para todas las pruebas terminadas del medio de medio.conf.
# Uso: ./tabla_barrido.sh [carpeta ...]   (por defecto: esta carpeta)
# Tambien guarda la tabla en tabla_barrido.tsv.
set -uo pipefail
BASE=$(cd "$(dirname "$0")" && pwd)
[ -f "$BASE/medio.conf" ] && . "$BASE/medio.conf"
MEDIO=${MEDIO:-AguaPura}
if [ $# -gt 0 ]; then DIRS=("$@"); else DIRS=("$BASE"); fi

TMP=$(mktemp)
for dir in "${DIRS[@]}"; do
  [ -d "$dir" ] || continue
  for d in "$dir"/*-"$MEDIO"-*-*N; do
    [ -f "$d/ejecucion.log" ] || continue
    grep -q "^Fin" "$d/ejecucion.log" || continue            # solo corridas terminadas
    nombre=$(basename "$d")
    etiq=${nombre%%-"$MEDIO"-*}                               # 25meV, 0.1eV...
    fis=${nombre#*-"$MEDIO"-}; fis=${fis%-*N}                 # QGSP_BERT_HP o QGSP_BERT_HP_NoThermal
    e_ev=$(awk -v t="$etiq" 'BEGIN { if (t ~ /meV$/) { sub(/meV$/, "", t); print t / 1000 } else { sub(/eV$/, "", t); print t + 0 } }')
    linea=$("$BASE/resumen_prueba.sh" "$d/Datos-simulacion" --tsv) || continue
    printf "%s\t%s\t%s\t%s\n" "$e_ev" "$etiq" "$fis" "$linea" >> "$TMP"
  done
done

sort -t$'\t' -k1,1g -k3,3 "$TMP" | awk -F'\t' '
{
    e = $1; lab[e] = $2
    if ($3 == "QGSP_BERT_HP") { conP[e] = $8; conE[e] = $9; conN[e] = $10 }
    else                      { sinP[e] = $8; sinE[e] = $9; sinN[e] = $10 }
    if (!(e in visto)) { visto[e] = 1; orden[++k] = e }
}
END {
    printf "%-8s | %-24s | %-24s | %-24s | %-16s\n", "Energia", "Captura agua CON S(a,b)", "Captura agua SIN S(a,b)", "Efecto S(a,b)", "<N> con / sin"
    printf "%s\n", "---------+--------------------------+--------------------------+--------------------------+-----------------"
    for (i = 1; i <= k; i++) {
        e = orden[i]
        c = (e in conP) ? sprintf("%6.2f +- %.2f %%", conP[e], conE[e]) : "      (falta)"
        s = (e in sinP) ? sprintf("%6.2f +- %.2f %%", sinP[e], sinE[e]) : "      (falta)"
        if ((e in conP) && (e in sinP)) {
            d = conP[e] - sinP[e]; err = sqrt(conE[e]^2 + sinE[e]^2)
            ef = sprintf("%+6.2f pts (%.1f sigma)", d, (err > 0 ? d / err : 0))
            nn = sprintf("%6.1f / %6.1f", conN[e], sinN[e])
        } else { ef = "-"; nn = "-" }
        printf "%-8s | %-24s | %-24s | %-24s | %-16s\n", lab[e], c, s, ef, nn
    }
}' | tee "$BASE/tabla_barrido.tsv"
rm -f "$TMP"
