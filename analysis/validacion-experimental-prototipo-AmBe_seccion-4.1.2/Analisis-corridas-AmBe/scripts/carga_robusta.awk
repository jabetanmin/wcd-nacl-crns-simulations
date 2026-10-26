# Carga "robusta" por disparo (método de Comparacion-robusta-fondo-neutrones-*):
# línea base = mediana de las primeras min(20, n) muestras del canal 1; carga = suma de (x - base) > 0.
# Solo líneas con dos columnas numéricas (como el parser del notebook); un disparo termina en '# t'.
function cerrar(   i, j, k, t, m, b, q) {
  if (n == 0) return
  m = (n < 20) ? n : 20
  for (i = 1; i <= m; i++) s[i] = x[i]
  for (i = 2; i <= m; i++) { t = s[i]; for (j = i - 1; j >= 1 && s[j] > t; j--) s[j + 1] = s[j]; s[j + 1] = t }
  b = (m % 2) ? s[(m + 1) / 2] : (s[m / 2] + s[m / 2 + 1]) / 2
  q = 0; for (k = 1; k <= n; k++) if (x[k] > b) q += x[k] - b
  printf "%.1f\n", q; n = 0
}
/^# t / { cerrar(); next }
/^#/ { next }
NF >= 2 && $1 ~ /^-?[0-9.]+$/ && $2 ~ /^-?[0-9.]+$/ { x[++n] = $1 + 0 }
END { cerrar() }
