# Campaña 1: neutrones monoenergéticos (Sección 4.2 de la tesis)

Simulaciones de febrero de 2025 con `QGSP_BERT_HP` sin $S(\alpha,\beta)$ (código en la etiqueta
`campana-1-QGSP_BERT_HP`): 100 000 neutrones por corrida, incidencia vertical desde $z = 1.5$ m,
dieciséis energías entre 1 meV y la carpeta `1000000meV` (rotulada "1 keV" en la tesis) y cuatro medios
(agua pura y 2.5, 5 y 10 % de NaCl en masa).

## Procesamiento por corrida

`procesar_corrida.py <carpeta energía/medio> <salida>` lee solo las salidas crudas del simulador
(`interaccion-completa-neutrones.txt` y `Carga_Total_*.txt`) en una sola pasada y escribe:

- `historias.tsv.gz`: una fila por historia con los conteos de `Transportation`, `hadElastic`,
  `neutronInelastic` y `nCapture`, el destino final por cara del volumen activo, la posición y la energía
  de captura, `N_tesis`, `N_total` (verificación), `suma_ln_E` (suma de $\ln(E_\mathrm{pre}/E_\mathrm{post})$ en
  los `hadElastic`, para el $\xi$ de la tesis) y `xi_historia_inicial` (definición inicial, solo trazabilidad);
- `resumen.json`: medias por historia, coeficientes $\eta$ con incertidumbre binomial, $\langle N\rangle$,
  $\langle\xi\rangle$ de la tesis (`xi_colision_capturadas`) y estadística de la carga.

La definición de $N$ reproduce la del notebook original `Analisis-procesos-neutrones-*.ipynb`
(ver la cabecera del script). $N$ es el número de dispersiones elásticas de la cadena ininterrumpida dentro
del tanque que termina en la captura; $N_\mathrm{total}$ cuenta todos los `hadElastic` de la historia
capturada y se conserva solo como verificación.

`procesar_campana.py <carpeta Neutrones-termicos> resultados` procesa las 64 corridas en paralelo
(alrededor de 1 minuto) y escribe `resultados/resumen_campana.tsv`.

## Letargía $\xi$

- **Definición de la tesis:** $\xi = \ln(E_\mathrm{pre}/E_\mathrm{post})$ de cada dispersión elástica;
  $\langle\xi\rangle$ es su promedio sobre todas las dispersiones de las historias capturadas
  (`xi_colision_capturadas`). Con ella están calculados los resultados de la tesis (por ejemplo, 0.058 a
  1 eV y 0.165 a 1 keV en agua pura, Capítulo 5).
- **Definición inicial (reemplazada):** $\ln(E_0/E_\mathrm{cap})/N$ por historia, promediado sobre historias
  (`xi_historia_inicial`). Es la de los notebooks antiguos de las carpetas de datos; se conserva solo por
  trazabilidad y para verificar que el procesamiento reproduce esos archivos.

## Validación (1 meV, agua pura)

Comparado con los archivos derivados del notebook original:

| Magnitud | Script | Original / tesis |
|---|---|---|
| Historias / capturas | 100 000 / 17 418 | 17 418 (`neutrones-capturados.txt`) |
| $\eta_\mathrm{Cap}$ | (17.418 ± 0.120) % | (17.418 ± 0.120) %, Tabla 4.8 |
| Cadenas para $N$ (y $\xi$ inicial) | 17 213, todas idénticas en orden | 17 213 |
| $\langle N\rangle$ | 44.78 | 44.78 (Sec. 4.2.1) |
| Conteos por historia de los cuatro procesos | idénticos | `*-AP-1meV.txt` |
| $\langle N_\mathrm{total}\rangle$ | 44.62 | — |

## Validación de las 64 corridas

- Coeficientes de captura, reflexión, transmisión y otros destinos: idénticos (diferencia 0) a
  `analysis/revision-tesis_2026-10/resultados_balance/balance_caras_tanque.tsv` en las 64 corridas.
- Conteos de `hadElastic` por historia: idénticos a los archivos `hadElastic-*.txt` de las 15 corridas
  que los conservan.
- Cifras del Capítulo 5 (agua pura): $\langle N\rangle$ = 44.8, 52.2, 60.4 y 76.8 a 1 meV, 25 meV, 1 eV y
  1 keV; captura de 17.42, 35.88 y 33.77 % a 1 meV, 1 eV y 1 keV, y 51.38 % con 10 % de NaCl a 1 eV;
  reflexión de 76.6, 62.2 y 64.6 %; captura relativa a 1 meV de 1.61, 1.35 y 1.19. Todas se reproducen.
- Diferencias de redondeo en la tesis: $\langle\xi\rangle$ (definición de la tesis) a 1 eV es 0.0586 (la tesis escribe 0.058) y la
  captura relativa a 1 keV con 10 % de NaCl es 1.3447 (la tesis escribe 1.35).
