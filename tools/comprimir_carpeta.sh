#!/usr/bin/env bash
# Comprime una carpeta de resultados en <carpeta>.tar.zst junto a ella y verifica el archivo.
# NO borra nada: al final dice si la verificacion paso y que orden usar para borrar la carpeta original.
#
# Uso:  ./comprimir_carpeta.sh "<ruta de la carpeta>"
#
# Verificaciones antes de declarar OK:
#   1. zstd -t: el archivo comprimido se lee completo y su suma de control (xxhash) es correcta;
#   2. la lista del .tar.zst (ruta y tamano de cada archivo) es identica a la de la carpeta original.
# Se escribe <carpeta>.tar.zst.verificacion.txt con el resultado.
set -euo pipefail
D="${1:-}"; D="${D%/}"
[[ -n "$D" && -d "$D" ]] || { echo "Uso: $0 <carpeta>"; exit 1; }
command -v zstd > /dev/null || { echo "ERROR: falta zstd (en Ubuntu: sudo apt install zstd)"; exit 1; }
PADRE="$(cd "$(dirname "$D")" && pwd)"; NOM="$(basename "$D")"
SAL="$PADRE/$NOM.tar.zst"; TMP="$SAL.part"; VER="$SAL.verificacion.txt"
[[ -e "$SAL" ]] && { echo "ERROR: ya existe $SAL"; exit 1; }
cd "$PADRE"

TAM=$(find "$NOM" -type f -printf "%s\n" | awk '{s+=$1} END{printf "%.0f", s}')
LIBRE=$(df -B1 --output=avail "$PADRE" | tail -1 | tr -dc '0-9')
echo "== $NOM: $(find "$NOM" -type f | wc -l) archivos, $(( TAM / 1000000000 )) GB; libres $(( LIBRE / 1000000000 )) GB"
(( LIBRE > TAM / 3 )) || { echo "ERROR: poco espacio libre (se necesita ~1/3 del tamano de la carpeta)."; exit 1; }

echo "== Comprimiendo ($(date +%H:%M:%S))"
INI=$(date +%s)
tar -cf - "$NOM" | zstd -T0 -10 -q -o "$TMP"
echo "   listo en $(( $(date +%s) - INI )) s: $(du -h "$TMP" | cut -f1)"

echo "== Verificando ($(date +%H:%M:%S))"
zstd -t -q "$TMP" || { echo "ERROR: zstd -t fallo; NO borre la carpeta."; exit 1; }
LISTA_ORIG="$(mktemp)"; LISTA_ARCH="$(mktemp)"
find "$NOM" -type f -printf "%s %p\n" | LC_ALL=C sort -k2 > "$LISTA_ORIG"
zstd -dc -q "$TMP" | tar -tvf - | awk '$1 !~ /^d/ {n=$3; $1=$2=$3=$4=$5=""; sub(/^ +/, ""); print n, $0}' | LC_ALL=C sort -k2 > "$LISTA_ARCH"
if ! cmp -s "$LISTA_ORIG" "$LISTA_ARCH"; then
    echo "ERROR: la lista del archivo no coincide con la carpeta; NO borre la carpeta."; diff "$LISTA_ORIG" "$LISTA_ARCH" | head; exit 1
fi
mv "$TMP" "$SAL"
{
  echo "Carpeta:     $NOM"
  echo "Archivo:     $NOM.tar.zst ($(stat -c %s "$SAL") bytes)"
  echo "Fecha:       $(date)"
  echo "Archivos:    $(wc -l < "$LISTA_ORIG")"
  echo "Bytes orig.: $TAM"
  echo "md5 lista:   $(md5sum < "$LISTA_ORIG" | cut -d' ' -f1)"
  echo "zstd -t:     OK"
  echo "Lista tar = lista carpeta: OK"
  echo; cat "$LISTA_ORIG"
} > "$VER"
rm -f "$LISTA_ORIG" "$LISTA_ARCH"
echo "== VERIFICACION CORRECTA: $(( TAM / 1000000000 )) GB -> $(( $(stat -c %s "$SAL") / 1000000000 )) GB  (detalle en $(basename "$VER"))"
echo "   Para liberar el espacio, borre la carpeta original con:"
echo "   rm -rf \"$PADRE/$NOM\""
echo "   Para recuperarla mas adelante:  tar -I zstd -xf \"$SAL\""
