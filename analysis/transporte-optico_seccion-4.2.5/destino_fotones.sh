#!/bin/bash
# Destino de los fotones Cherenkov seguidos por el simulador (modo eFast).
# Lee pasos-particulas.tsv (todos los pasos de todas las particulas) y, para cada foton optico,
# clasifica su ultimo paso:
#   detectado            ultimo paso dentro del Pyrex (el PMT es un detector sensible y mata al foton)
#   absorbido_agua       OpAbsorption en el medio activo
#   absorbido_tyvek_*    ultimo paso termina en una frontera del agua (Transportation u OpBoundary) o dentro del Tyvek:
#                        absorcion en la superficie del Tyvek (tapa, fondo o pared lateral). En Geant4 el paso que
#                        llega a una frontera se atribuye a Transportation; OpBoundary actua despues sobre el foton.
#                        (tapa, fondo o pared lateral, segun la posicion final)
#   otro                 cualquier otro final (se lista aparte)
# rebotes = pasos que terminan en una frontera, sin contar el ultimo (aprox. reflexiones en el Tyvek).
# En modo eFast la QE ya se sorteo al crear el foton, asi que detectados / seguidos = eps_col.
# Uso: ./destino_fotones.sh <ruta a pasos-particulas.tsv> [archivo de salida, por defecto destino_fotones.tsv]
set -euo pipefail
export LC_ALL=C   # punto decimal en awk y printf, sin importar el idioma del sistema
F=${1:?Indique la ruta a pasos-particulas.tsv}
SAL=${2:-destino_fotones.tsv}
[ -r "$F" ] || { echo "No se puede leer $F"; exit 1; }
echo "Leyendo $F ($(du -h "$F" | cut -f1)); puede tardar varios minutos..." >&2

awk -F'\t' -v sal="$SAL" '
  /^#/ { next }
  $3 != "opticalphoton" { next }
  {
    k = $1 SUBSEP $2 SUBSEP $4
    if (!(k in nst)) { orden[++nt] = k; mat0[k] = $9 }
    nst[k]++
    dx = $13 - $10; dy = $14 - $11; dz = $15 - $12
    largo[k] += sqrt(dx*dx + dy*dy + dz*dz)
    if ($8 == "OpBoundary" || $8 == "Transportation") nbound[k]++
    if ($8 == "OpMieHG" || $8 == "OpRayleigh") nscat[k]++
    if ($6 + 0 >= ult[k] + 0) {
      ult[k] = $6; proc[k] = $8; mat[k] = $9
      px[k] = $10; py[k] = $11; pz[k] = $12
      qx[k] = $13; qy[k] = $14; qz[k] = $15
    }
  }
  END {
    if (nt == 0) { print "No hay fotones opticos en el archivo." > "/dev/stderr"; exit 1 }
    # Extremos geometricos tomados de los propios datos
    zbmax = -1e30; zbmin = 1e30; zpmax = -1e30; zpmin = 1e30; rbmax = 0
    for (i = 1; i <= nt; i++) {
      k = orden[i]
      if (mat[k] == "Pyrex") { if (pz[k] > zpmax) zpmax = pz[k]; if (pz[k] < zpmin) zpmin = pz[k] }
      else if (mat[k] ~ /Tyvek/ || proc[k] == "OpBoundary" || proc[k] == "Transportation") {
        if (qz[k] > zbmax) zbmax = qz[k]; if (qz[k] < zbmin) zbmin = qz[k]
        r = sqrt(qx[k]^2 + qy[k]^2); if (r > rbmax) rbmax = r
      }
    }
    zmed = 0.5 * (zbmin + zbmax)
    for (i = 1; i <= nt; i++) {
      k = orden[i]
      if (mat[k] == "Pyrex") {
        d = "detectado"
        if (pz[k] > zpmax - 0.01) cara["plana (z maxima)"]++
        else cara["superficie curva"]++
      } else if (proc[k] == "OpAbsorption" && mat[k] !~ /Tyvek/) d = "absorbido_agua"
      else if (mat[k] ~ /Tyvek/ || proc[k] == "OpBoundary" || proc[k] == "Transportation") {
        if (mat[k] !~ /Tyvek/) nbound[k]--   # el ultimo paso de frontera es la absorcion, no un rebote
        if (sqrt(qx[k]^2 + qy[k]^2) > rbmax - 0.05) d = "absorbido_tyvek_lateral"
        else if (qz[k] > zmed) d = "absorbido_tyvek_tapa"
        else d = "absorbido_tyvek_fondo"
      } else { d = "otro"; otro[proc[k] " en " mat[k]]++ }
      n[d]++; L[d] += largo[k]; B[d] += nbound[k]; S[d] += nscat[k]
    }
    printf "destino\tfotones\tporcentaje\tlongitud_media_cm\trebotes_frontera_medios\tdispersiones_medias\n" > sal
    split("detectado absorbido_agua absorbido_tyvek_tapa absorbido_tyvek_fondo absorbido_tyvek_lateral otro", lista, " ")
    printf "Fotones seguidos: %d\n\n", nt
    printf "%-26s %9s %8s %12s %12s %12s\n", "destino", "fotones", "%", "longitud_cm", "rebotes", "dispersiones"
    for (j = 1; j <= 6; j++) {
      d = lista[j]; if (!(d in n)) continue
      printf "%-26s %9d %7.2f%% %12.1f %12.2f %12.2f\n", d, n[d], 100*n[d]/nt, L[d]/n[d], B[d]/n[d], S[d]/n[d]
      printf "%s\t%d\t%.3f\t%.2f\t%.3f\t%.3f\n", d, n[d], 100*n[d]/nt, L[d]/n[d], B[d]/n[d], S[d]/n[d] > sal
    }
    if ("detectado" in n) {
      printf "\nEntrada al PMT (detectados):\n"
      for (c in cara) printf "  %-22s %8d  %6.2f%%\n", c, cara[c], 100*cara[c]/n["detectado"]
      printf "  (z de la cara plana del PMT: %.3f cm)\n", zpmax
    }
    if (length(otro) > 0) { printf "\nOtros finales:\n"; for (o in otro) printf "  %-40s %d\n", o, otro[o] }
    printf "\nTabla escrita en %s\n", sal
  }' "$F"
