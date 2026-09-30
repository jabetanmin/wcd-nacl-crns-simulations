#!/bin/bash
# Extrae, de un archivo de datos crudos LAGO v5, la carga de cada pulso y el tiempo de adquisicion.
# Uso: ./extraer_eventos.sh <archivo.dat> <salida_eventos.tsv> <salida_resumen.tsv>
#
# Formato LAGO v5: cada pulso son 32 lineas "<ADC1> <ADC2>" seguidas de "# t <canal> <reloj>" y
# "# c <contador>"; cada segundo el equipo escribe "# x h <hh:mm:ss> <fecha> <segundos> 0".
# El numero de marcas "# x h" es el tiempo de adquisicion en segundos.
#
# Por pulso (canal 1) se calculan tres cargas, en ADC:
#   carga_ventana  notebook senales-detector-prototipo.ipynb, celda 1:
#                  linea base = media de las 20 primeras muestras; ventana alrededor del pico hasta que
#                  la senal cae bajo el 5 % del pico; se integra la parte positiva. -1 si el pico <= 0.
#   carga_figura   mismo notebook, celda 23 (figura Comparacion-3-configuraciones-bins9425 y
#                  Histograma-Comparado-*): linea base = mediana de las 20 primeras muestras; suma de
#                  la parte positiva de las 32 muestras.
#   carga_pretrig  como carga_ventana, pero con la linea base = media de las muestras 1-7, anteriores
#                  al pulso (el pico cae en las muestras 9-10, dentro de las 20 de la base original).
# Tambien: pico sobre la base pre-disparo y si alguna muestra alcanza la saturacion (>= 8160).
set -euo pipefail
IN=${1:?archivo .dat}; OUT=${2:?salida eventos}; RES=${3:?salida resumen}

LC_ALL=C awk -v out="$OUT" -v res="$RES" -v nombre="$(basename "$IN")" '
function carga(nb,    i, b, pk, pi, thr, s, e, q) {
  b = 0; for (i = 1; i <= nb; i++) b += v[i]; b /= nb
  pk = -1e9; pi = 1
  for (i = 1; i <= n; i++) { sg[i] = v[i] - b; if (sg[i] > pk) { pk = sg[i]; pi = i } }
  ultimo_pico = pk
  if (pk <= 0) return -1
  thr = 0.05 * pk
  s = 1; for (i = pi; i >= 1; i--) if (sg[i] < thr) { s = i + 1; break }
  e = n; for (i = pi; i <= n; i++) if (sg[i] < thr) { e = i; break }
  q = 0; for (i = s; i < e; i++) if (sg[i] > 0) q += sg[i]   # ventana [s, e), como en Python
  return q
}
function mediana(nb,    i, j, t, w) {
  for (i = 1; i <= nb; i++) w[i] = v[i]
  for (i = 2; i <= nb; i++) { t = w[i]; for (j = i - 1; j >= 1 && w[j] > t; j--) w[j + 1] = w[j]; w[j + 1] = t }
  return (nb % 2) ? w[(nb + 1) / 2] : (w[nb / 2] + w[nb / 2 + 1]) / 2
}
function cerrar_pulso(    qv, qp, pp, b, i, qf, nb) {
  if (n == 32) {
    qv = carga(20); qp = carga(7); pp = ultimo_pico
    b = mediana(20); qf = 0; for (i = 1; i <= n; i++) if (v[i] > b) qf += v[i] - b
    printf "%.2f\t%.2f\t%.2f\t%.2f\t%d\n", qv, qf, qp, pp, (maxv >= 8160) > out
    ev++; if (maxv >= 8160) nsat++
  } else if (n > 0) malos++
  n = 0; maxv = -1
}
BEGIN { print "carga_ventana\tcarga_figura\tcarga_pretrig\tpico_pretrig\tsaturado" > out }
/^# x h / { seg++; next }
/^# t / { cerrar_pulso(); next }
/^#/ { next }
NF >= 2 { n++; v[n] = $1 + 0; if (v[n] > maxv) maxv = v[n] }
END {
  cerrar_pulso()
  printf "archivo\teventos\teventos_malformados\tsaturados\ttiempo_s\n" > res
  printf "%s\t%d\t%d\t%d\t%d\n", nombre, ev, malos + 0, nsat + 0, seg > res
}' "$IN"
