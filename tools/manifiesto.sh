#!/usr/bin/env bash
# Manifiesto de una carpeta de corrida: número de archivos, bytes y md5 del listado ordenado (tamaño y ruta).
# Sirve para comparar una copia (docker cp, disco externo) con el original sin leer el contenido de los archivos.
# Uso: tools/manifiesto.sh <carpeta> [<carpeta> ...]
set -euo pipefail
for d in "$@"; do
  [ -d "$d" ] || { echo "no es una carpeta: $d" >&2; exit 1; }
  ( cd "$d"
    n=$(find . -type f | wc -l)
    b=$(find . -type f -printf '%s\n' | awk '{s += $1} END {print s + 0}')
    m=$(find . -type f -printf '%s %p\n' | LC_ALL=C sort -k2 | md5sum | cut -c1-32)
    printf '%s\t%s\t%s\t%s\n' "$(basename "$d")" "$n" "$b" "$m" )
done
