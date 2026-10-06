# Campaña 1: neutrones monoenergéticos (Sección 4.2 de la tesis)

Simulaciones de febrero de 2025 con `QGSP_BERT_HP` sin $S(\alpha,\beta)$ (código en la etiqueta
`campana-1-QGSP_BERT_HP`): 100 000 neutrones por corrida, incidencia vertical desde $z = 1.5$ m,
dieciséis energías entre 1 meV y la carpeta `1000000meV` (rotulada "1 keV" en la tesis) y cuatro medios
(agua pura y 2.5, 5 y 10 % de NaCl en masa).

Informe técnico: [`docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Procesamiento-Campana-1-64-corridas.pdf`](../../docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Procesamiento-Campana-1-64-corridas.pdf).

## Contenido

| Archivo | Función |
|---|---|
| `procesar_corrida.py` | Procesa una corrida desde los archivos crudos (`interaccion-completa-neutrones.txt`, `Carga_Total_*.txt`) en una sola pasada |
| `procesar_campana.py` | Procesa las 64 corridas en paralelo (alrededor de 1 minuto) y escribe `resultados/resumen_campana.tsv` |
| `comparar_cilindro.py` | Repite el procesamiento con un cilindro de 480 mm de radio en lugar de la caja cuadrada y compara |
| `figuras_seccion_4.2.ipynb` | Regenera las Figuras 4.17–4.29, 4.48, 4.50, 4.51 y D.1–D.6 y la Tabla 4.9 de la tesis solo con los resúmenes (generado por `construir_notebook.py`) |
| `datos/eficiencia_CRS1000_Kohli2018.tsv` | Funciones de respuesta del CRS1000 (Köhli et al., 2018) usadas como referencia en la Figura 4.51 |
| `verificar_tabla_4_9_original.py` | Repite los ajustes gaussianos de la Tabla 4.9 de la versión anterior y documenta sus problemas (`verificacion_tabla_4_9_original.txt`) |
| `figuras_informe.py` | Figuras y tablas del informe técnico |
| `resultados/` | `resumen_campana.tsv` y un `resumen.json` por corrida (las tablas por neutrón `historias.tsv.gz` se publican en Zenodo) |
| `figuras-seccion-4.2/` | Figuras regeneradas en PDF (los PNG se crean al ejecutar el notebook) |

Cada `resumen.json` contiene las medias y desviaciones de pasos por historia, los destinos y los coeficientes
$\eta$ con incertidumbre binomial, $\langle N\rangle$ y el histograma de $N$, $\langle\xi\rangle$, $\sigma(\xi)$ y
el histograma de $\xi$, la estadística de la longitud de captura $\lambda_\mathrm{cap}$ (mediana, cuartiles, moda y media
con incertidumbres por remuestreo, e histograma), y la estadística y el histograma de la carga.

## Definiciones (las de la tesis)

- **Cadena de dispersión:** pasos con la posición previa o posterior dentro de la caja $|x|,|y|\le478$ mm,
  $0\le z\le1330$ mm, que empiezan en una dispersión elástica, continúan solo con dispersiones elásticas en
  pasos consecutivos y terminan en la captura (notebook `Analisis-procesos-neutrones-*.ipynb`).
- **$N$:** número de dispersiones elásticas de la cadena. $N_\mathrm{total}$ (todas las del neutrón capturado)
  se conserva solo como verificación.
- **$\xi$:** $\ln(E_\mathrm{pre}/E_\mathrm{post})$ de cada dispersión elástica de las cadenas; $\langle\xi\rangle$ y
  $\sigma(\xi)$ sobre todas esas colisiones; histograma de 300 intervalos entre $-2$ y $2$ (notebooks
  `Histogramas_cita_*.ipynb`). La definición inicial del estudio, $\ln(E_0/E_\mathrm{cap})/N$ por historia, fue
  reemplazada y se conserva solo por trazabilidad (`xi_historia_inicial`).
- **Destino final:** última frontera del volumen activo ($|x|,|y|\le480$ mm, $0\le z\le1330$ mm) atravesada.
- **$\lambda_\mathrm{cap}$:** distancia en línea recta entre el punto de la primera dispersión elástica en la cara interior
  de la tapa ($z=1330.05$ mm, sin pérdida previa de energía) y el punto de captura. Valor representativo: la mediana,
  con incertidumbre por remuestreo (200 réplicas, semilla fija), y los percentiles 25–75 como dispersión.

## Validación

- Balance de captura, reflexión, transmisión y otros destinos: idéntico a
  `analysis/revision-tesis_2026-10/resultados_balance/balance_caras_tanque.tsv` (Tabla 4.8 y Apéndice C) en
  las 64 corridas.
- $\xi$: número de colisiones, $\langle\xi\rangle$ y $\sigma(\xi)$ idénticos a los impresos por los notebooks
  `Histogramas_cita_*.ipynb` en las 64 corridas (por ejemplo, 770 803 colisiones, $-0.0611$ y 1.0863 a 1 meV en
  agua pura; $\langle\xi\rangle$ = 0.0583 y 0.1651 a 1 eV y 1 keV).
- Figura 4.19: $x_\mathrm{max}$, FWHM y $\langle N\rangle$ de las siete energías idénticos.
- 1 meV en agua pura: las 17 213 cadenas, los conteos por historia de los cuatro procesos y las posiciones de
  captura son idénticos a los archivos del notebook original.
- Cifras del Capítulo 5: $\langle N\rangle$ = 44.8, 52.2, 60.4 y 76.8; captura de 17.42, 35.88 y 33.77 %, y
  51.38 % con 10 % de NaCl; reflexión de 76.6, 62.2 y 64.6 %; captura relativa a 1 meV de 1.61, 1.35 y 1.19.
- Diferencias encontradas en la tesis:
  - la captura relativa a 1 keV con 10 % de NaCl es 1.3447; la tesis escribía 1.35 (corregido a 1.34);
  - en las Figuras 4.17 y 4.18, tres puntos (700 meV con 2.5 y 5 % de NaCl y 10 eV con 2.5 %) provienen de
    un archivo de promedios que difiere de los datos crudos hasta en 0.7 %.

## Longitud de captura (Tabla 4.9 y Figuras 4.28 y 4.29)

La versión anterior de la tesis daba, para once energías, la posición y el ancho de ajustes gaussianos al pico de la
distribución de $\lambda_\mathrm{cap}$, con intervalos de ajuste introducidos a mano. `verificar_tabla_4_9_original.py`
reproduce 33 de los 44 valores con los intervalos registrados en los notebooks y muestra que el archivo de 100 eV en
agua pura era una copia del de 1 keV y que los de 700 meV con 2.5 y 5 % de NaCl no provienen de los datos de la
Campaña 1. La versión final de la tesis usa la mediana, calculada con un procedimiento fijo para las 64 corridas.

## Carga y eficiencia (Figuras 4.48, 4.50 y 4.51)

Los archivos `Carga_Total_*.txt` contienen el número de fotoelectrones de cada evento con señal (no hay eventos con 0).
La eficiencia de detección es el número de eventos con señal dividido entre $10^5$ neutrones; los valores que usaba la
figura de la tesis coinciden con estos archivos en las 64 corridas. La versión anterior de la Figura 4.50 graficaba
ese mismo número de eventos con el rótulo "número medio de fotones" (con un valor mal transcrito, 21 399 en lugar de
21 349); la versión final muestra el número medio de fotoelectrones por evento detectado (3.2 en agua pura y 10.5 con
10 % de NaCl, casi sin dependencia con la energía).
