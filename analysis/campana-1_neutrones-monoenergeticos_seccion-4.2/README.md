# Sección 4.2 de la tesis: respuesta del WCD a flujos monocromáticos de neutrones (Campaña 1)

Esta carpeta contiene todo lo necesario para reproducir y entender los resultados de la **Sección 4.2** de la
tesis, en la que se irradia el detector Cherenkov de agua (WCD) con haces de neutrones de una sola energía para
estudiar qué les ocurre dentro del detector: cómo se transportan, cómo se moderan, cuántos se capturan, cuántos
escapan y a qué distancia de la tapa se capturan. Se comparan agua pura y agua con 2.5, 5 y 10 % de NaCl.

Desde los archivos crudos del simulador, dos scripts reconstruyen todas las magnitudes por neutrón y por corrida;
un notebook regenera las figuras y tablas de la tesis solo con los resúmenes guardados aquí, y comprueba
automáticamente que las cifras coinciden con las publicadas.

**Informe técnico:** [*Respuesta del WCD a flujos monocromáticos de neutrones*](../../docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Respuesta-WCD-flujos-monocromaticos-neutrones.pdf)
(`docs/technical-reports/campana-1_sin-S-alpha-beta/`). Cubre la parte neutrónica de la Sección 4.2: transporte,
moderación, balance de destinos, ganancia relativa y longitud de captura (Figs. 4.17–4.29, D.1–D.6, Tablas 4.6–4.9 y
Apéndice C). La carga y la eficiencia de detección (Figs. 4.48–4.51) se documentarán en el informe de la respuesta
electromagnética.

## Índice

1. [Cómo leer esta carpeta](#cómo-leer-esta-carpeta)
2. [Contexto físico y de la simulación](#contexto-físico-y-de-la-simulación)
3. [Convenciones](#convenciones)
4. [Glosario de magnitudes](#glosario-de-magnitudes)
5. [Contenido de la carpeta](#contenido-de-la-carpeta)
6. [Diccionario de datos](#diccionario-de-datos)
7. [Índice de figuras](#índice-de-figuras)
8. [Definiciones (las de la tesis)](#definiciones-las-de-la-tesis)
9. [Validación](#validación)
10. [Longitud de captura (Tabla 4.9 y Figuras 4.28 y 4.29)](#longitud-de-captura-tabla-49-y-figuras-428-y-429)
11. [Carga y eficiencia (Figuras 4.48, 4.50 y 4.51)](#carga-y-eficiencia-figuras-448-450-y-451)
12. [Advertencias para el lector](#advertencias-para-el-lector)
13. [Cómo reproducir](#cómo-reproducir)

## Cómo leer esta carpeta

| Si quiere… | Empiece por… |
|---|---|
| Entender los resultados físicos | El informe técnico (enlace arriba): sigue el orden de la Sección 4.2 de la tesis |
| Consultar una cifra concreta (captura, $\langle N\rangle$, $\langle\xi\rangle$, $\lambda_\mathrm{cap}$…) | [`resultados/resumen_campana.tsv`](resultados/resumen_campana.tsv): una fila por corrida (ver [Diccionario de datos](#diccionario-de-datos)) |
| Ver o rehacer una figura de la tesis | [`figuras_seccion_4.2.ipynb`](figuras_seccion_4.2.ipynb) y [`figuras-seccion-4.2/`](figuras-seccion-4.2/) (ver [Índice de figuras](#índice-de-figuras)) |
| Entender cómo se calcula cada magnitud | [Definiciones](#definiciones-las-de-la-tesis) y `procesar_corrida.py` |
| Comprobar que el procesamiento reproduce la tesis | [Validación](#validación) y la última celda del notebook |
| Reprocesar desde los datos crudos | [Cómo reproducir](#cómo-reproducir) |

## Contexto físico y de la simulación

El WCD no detecta los neutrones directamente, porque son eléctricamente neutros. La señal resulta de la cadena

> neutrón → moderación y captura → fotones gamma de captura → electrones y positrones → luz Cherenkov → fotomultiplicador (PMT)

Esta carpeta se ocupa del primer eslabón, el único en el que interviene el neutrón: entra por la tapa, pierde energía
por dispersiones elásticas (sobre todo con hidrógeno) y termina **capturado** (por H, O, Na o Cl), **reflejado** (sale
por la tapa), **transmitido** (sale por el fondo o las paredes) o en **otros destinos** (no llega al agua o sufre una
interacción inelástica). El NaCl se añade porque el $^{35}$Cl absorbe neutrones térmicos unas 132 veces más que el
hidrógeno, lo que aumenta la captura y, con ella, la señal.

| Parámetro | Valor |
|---|---|
| Simulador | Geant4/MEIGA, aplicación `G4WCDSimulator`; código en la etiqueta `campana-1-QGSP_BERT_HP` |
| Física hadrónica | `QGSP_BERT_HP` **sin** el tratamiento térmico $S(\alpha,\beta)$ del hidrógeno ligado |
| Fecha de las simulaciones | febrero de 2025 |
| Neutrones por corrida | $N_\mathrm{inc}=100\,000$ |
| Fuente | haz vertical descendente desde $z_0=1500$ mm, dentro de un disco de 25 cm de radio centrado en el eje |
| Volumen activo | cilindro de agua de 480 mm de radio y 1330 mm de altura ($0\le z\le1330$ mm; $V=0.962694$ m³) |
| Cara interior de la tapa | $z=1330$ mm (17 cm por debajo del punto de inyección) |
| Temperatura del medio | 20 °C (293.15 K), $k_BT\simeq25.3$ meV |
| Corridas | 16 energías × 4 medios = 64 |

Hay una segunda campaña de simulación, **con** $S(\alpha,\beta)$, solo a 25 meV; sus resultados no coinciden con estos
(ver [`../README.md`](../README.md) y [`../efecto-SalphaBeta_barrido-energia/`](../efecto-SalphaBeta_barrido-energia/)).

## Convenciones

**Energías.** Las carpetas se nombran por la energía en meV; la tesis y las figuras usan el rótulo de la segunda
columna. Los regímenes son los de la Tabla 2.2 de la tesis.

| Carpeta | Rótulo | Régimen |
|---|---|---|
| `1meV`, `2.5meV`, `5meV`, `7meV` | 1, 2.5, 5, 7 meV | frío (1–10 meV) |
| `10meV` | 10 meV | frontera frío/térmico |
| `25meV`, `50meV`, `80meV` | 25, 50, 80 meV | térmico (10–100 meV) |
| `100meV` | 100 meV | frontera térmico/epitérmico |
| `300meV`, `500meV`, `700meV` | 300, 500, 700 meV | epitérmico (100 meV–1 eV) |
| `1000meV` | 1 eV | frontera epitérmico/intermedio |
| `10000meV`, `100000meV` | 10 eV, 100 eV | intermedio (1 eV–1 keV) |
| `1000000meV` | 1 keV | intermedio (rótulo de la tesis) |

Las figuras de $\xi$ de cada régimen incluyen las dos energías de frontera, como en la tesis.

**Medios.**

| Carpeta | Concentración de NaCl (en masa) | Abreviatura en nombres de figuras | Color en las figuras |
|---|---|---|---|
| `Agua-pura` | 0 % | `AP` | rojo |
| `Agua+2.5NaCl` | 2.5 % | `A25NaCl`, `2.5NaCl` | verde |
| `Agua+5NaCl` | 5 % | `A5NaCl`, `5NaCl` | violeta |
| `Agua+10NaCl` | 10 % | `A10NaCl`, `10NaCl` | naranja |

**Unidades.** En los archivos crudos, la energía está en MeV y las posiciones en mm. En `resumen_campana.tsv`, los
coeficientes $\eta$ son **fracciones** (0–1, no porcentajes) y las longitudes llevan la unidad en el nombre de la
columna (`_cm`). En `resumen.json`, la longitud de captura está en mm (campo `unidad`).

**Coordenadas.** $z=0$ es el fondo del volumen activo y $z=1330$ mm la cara interior de la tapa; el neutrón viaja
hacia $z$ decreciente. La profundidad de captura es $1330\,\mathrm{mm}-z_\mathrm{cap}$.

## Glosario de magnitudes

| Símbolo | Nombre | Definición | Dónde está |
|---|---|---|---|
| $\overline{N}_\mathrm{Trans}$ | Pasos de transporte por neutrón | Media de pasos `Transportation` por neutrón incidente. Es un diagnóstico de la segmentación de las trayectorias en Geant4, no una interacción física | `media_Transportation` |
| $\overline{N}_\mathrm{hadElastic}$ | Dispersiones elásticas por neutrón | Media de pasos `hadElastic` por neutrón incidente (todas las historias, con cualquier destino) | `media_hadElastic` |
| $\eta_\mathrm{Cap}$ | Eficiencia de captura | Fracción de neutrones incidentes cuya historia termina en `nCapture` (dentro o fuera del volumen activo) | `eta_cap` |
| $\eta_\mathrm{Refle}$ | Coeficiente de reflexión | Fracción que entra al agua y sale por la tapa | `eta_refle` |
| $\eta_\mathrm{Trans}$ | Coeficiente de transmisión | Fracción que sale por el fondo o las paredes laterales | `eta_trans` |
| $\eta_\mathrm{Otros}$ | Otros destinos | Fracción que no llega al agua o termina en una interacción inelástica | `eta_otros` |
| $u(\eta)$ | Incertidumbre estadística | $\sqrt{\eta(1-\eta)/N_\mathrm{inc}}$ ($1\sigma$); las cuatro $\eta$ están correlacionadas negativamente | `u_eta_*` |
| Captura relativa | Ganancia de captura | $\eta_\mathrm{Cap}(\mathrm{NaCl})/\eta_\mathrm{Cap}(\mathrm{agua\ pura})$ a la misma energía | se calcula de `eta_cap` |
| $N$ | Dispersiones antes de la captura | Número de dispersiones elásticas de la cadena ininterrumpida que termina en captura (definición de la tesis) | `N_tesis_media`; histograma en `resumen.json` |
| $P(N\mid\text{captura})$ | Distribución de $N$ | Histograma normalizado de $N$; se caracteriza por $x_\mathrm{max}$, FWHM, $\langle N\rangle$ y $\sigma$ | `N_tesis.histograma` |
| $\xi$ | Letargía por colisión | $\ln(E_\mathrm{pre}/E_\mathrm{post})$ de cada dispersión elástica de las cadenas; negativa si el neutrón gana energía | `xi_media`, `xi_sigma`; histograma en `resumen.json` |
| $\xi_\mathrm{ini}$ | Definición inicial (reemplazada) | $\ln(E_0/E_\mathrm{cap})/N$ por historia; se conserva solo por trazabilidad | `xi_historia_inicial_media` |
| $\lambda_\mathrm{cap}$ | Longitud de captura | Distancia en línea recta desde la primera dispersión en la cara interior de la tapa hasta la captura; valor representativo: la mediana | `lambda_mediana_cm` y siguientes |
| $\langle k\rangle$ | Fotoelectrones por evento | Media de fotoelectrones de los eventos con señal | `carga_media_pe` |
| $\varepsilon$ | Eficiencia de detección | Eventos con al menos un fotoelectrón / $N_\mathrm{inc}$ | `carga_eventos` / 100 000 |

## Contenido de la carpeta

```text
campana-1_neutrones-monoenergeticos_seccion-4.2/
├── README.md                            esta guía
├── procesar_corrida.py                  procesa una corrida desde los archivos crudos
├── procesar_campana.py                  procesa las 64 corridas en paralelo
├── comparar_cilindro.py                 repite el procesamiento con un cilindro y compara
├── construir_notebook.py                genera figuras_seccion_4.2.ipynb
├── figuras_seccion_4.2.ipynb            regenera las figuras y tablas de la tesis
├── figuras_informe.py                   figuras y tablas propias del informe técnico
├── tablas_seccion_4_2.py                tablas del informe por régimen y medio
├── verificar_tabla_4_9_original.py      revisión de la Tabla 4.9 anterior
├── verificacion_tabla_4_9_original.txt  salida de esa revisión
├── datos/
│   └── eficiencia_CRS1000_Kohli2018.tsv curvas de referencia de la Figura 4.51
├── figuras-seccion-4.2/                 figuras regeneradas (PDF en git; PNG al ejecutar el notebook)
├── resultados/
│   ├── resumen_campana.tsv              una fila por corrida
│   └── <energía>/<medio>/
│       ├── resumen.json                 resumen de la corrida
│       └── historias.tsv.gz             una fila por neutrón (no está en git; se publicará en Zenodo)
└── resultados-cilindro/                 comparación caja/cilindro (en git solo comparacion_caja_cilindro.tsv)
```

| Archivo | Función |
|---|---|
| `procesar_corrida.py` | Procesa una corrida desde los archivos crudos (`interaccion-completa-neutrones.txt`, `Carga_Total_*.txt`) en una sola pasada |
| `procesar_campana.py` | Procesa las 64 corridas en paralelo (alrededor de 1 minuto) y escribe `resultados/resumen_campana.tsv` |
| `comparar_cilindro.py` | Repite el procesamiento con un cilindro de 480 mm de radio en lugar de la caja cuadrada y compara |
| `figuras_seccion_4.2.ipynb` | Regenera las Figuras 4.17–4.29, 4.48, 4.50, 4.51 y D.1–D.6 y la Tabla 4.9 de la tesis solo con los resúmenes (generado por `construir_notebook.py`) |
| `datos/eficiencia_CRS1000_Kohli2018.tsv` | Funciones de respuesta del CRS1000 (Köhli et al., 2018) usadas como referencia en la Figura 4.51 |
| `verificar_tabla_4_9_original.py` | Repite los ajustes gaussianos de la Tabla 4.9 de la versión anterior y documenta sus problemas (`verificacion_tabla_4_9_original.txt`) |
| `figuras_informe.py` | Figuras y tablas propias del informe técnico ($\langle N\rangle$, $\langle\xi\rangle$, profundidad de captura, tablas por medio, caja/cilindro) |
| `tablas_seccion_4_2.py` | Tablas del informe técnico por régimen y medio: pasos por neutrón, $\langle\xi\rangle$ y $\sigma(\xi)$, eficiencia de detección y señal por captura |
| `resultados/` | `resumen_campana.tsv` y un `resumen.json` por corrida |
| `figuras-seccion-4.2/` | Figuras regeneradas en PDF |

## Diccionario de datos

### `resultados/resumen_campana.tsv`

Una fila por corrida (64 filas), separada por tabuladores.

| Columna | Unidad | Significado |
|---|---|---|
| `energia`, `medio` | — | Carpeta de energía y de medio (ver [Convenciones](#convenciones)) |
| `historias` | — | Neutrones incidentes (100 000) |
| `capturas` | — | Neutrones capturados |
| `eta_cap`, `eta_refle`, `eta_trans`, `eta_otros` | fracción | Coeficientes de destino; suman 1 |
| `u_eta_*` | fracción | Incertidumbre estadística marginal de cada coeficiente ($1\sigma$) |
| `media_Transportation`, `std_Transportation` | pasos | Media y desviación de pasos `Transportation` por neutrón incidente |
| `media_hadElastic`, `std_hadElastic` | pasos | Media y desviación de dispersiones elásticas por neutrón incidente |
| `media_neutronInelastic` | pasos | Media de interacciones inelásticas por neutrón incidente |
| `cadenas_N` | — | Capturas con cadena válida (aportan un valor de $N$) |
| `N_tesis_media` | — | $\langle N\rangle$ con la definición de la tesis |
| `N_total_media` | — | Media de todas las dispersiones elásticas de las historias capturadas (verificación) |
| `xi_colisiones` | — | Número de colisiones que entran en la estadística de $\xi$ |
| `xi_media`, `xi_sigma`, `xi_mediana` | — | $\langle\xi\rangle$, $\sigma(\xi)$ y mediana de $\xi$ |
| `xi_historia_inicial_n`, `xi_historia_inicial_media` | — | Historias y media de $\xi_\mathrm{ini}$ (solo trazabilidad) |
| `carga_eventos` | — | Eventos con al menos un fotoelectrón |
| `carga_media_pe` | fotoelectrones | Fotoelectrones medios por evento con señal |
| `lambda_n` | — | Capturas que entran en la estadística de $\lambda_\mathrm{cap}$ |
| `lambda_mediana_cm`, `u_lambda_mediana_cm` | cm | Mediana de $\lambda_\mathrm{cap}$ y su incertidumbre por remuestreo (valor de la Tabla 4.9) |
| `lambda_p25_cm`, `lambda_p75_cm` | cm | Percentiles 25 y 75 |
| `lambda_moda_cm`, `u_lambda_moda_cm` | cm | Moda (intervalos de 0.5 cm y ajuste parabólico); inestable a baja energía, solo como referencia |
| `lambda_media_cm`, `u_lambda_media_cm` | cm | Media y su incertidumbre (sensible a la cola larga) |

### `resultados/<energía>/<medio>/resumen.json`

| Clave | Contenido |
|---|---|
| `corrida`, `geometria`, `historias` | Identificación, selección usada (`caja`) y neutrones incidentes |
| `pasos_por_historia` | `media` y `std` de `Transportation`, `hadElastic`, `neutronInelastic` y `nCapture` por neutrón |
| `destinos` | Conteos por destino detallado (tabla siguiente) |
| `eta_cap`, `eta_refle`, `eta_trans`, `eta_otros` | `valor` e `incertidumbre` de cada coeficiente |
| `capturas` | Número de capturas |
| `N_tesis` | `cadenas`, `media` e `histograma` de $N$ (el índice $i$ es el número de dispersiones; conteos sin normalizar) |
| `N_total_media` | Verificación de $\langle N\rangle$ |
| `xi_tesis` | `colisiones`, `media`, `sigma`, `mediana` e `histograma` (`bins` = 300 en `rango` [−2, 2], `conteos`, y colisiones `debajo` y `encima` del rango) |
| `xi_historia_inicial` | `n` y `media` de $\xi_\mathrm{ini}$ |
| `lambda_cap` | Estadística de $\lambda_\mathrm{cap}$ en mm (`unidad`): `n`, `mediana`, `u_mediana`, `p25`, `p75`, `moda`, `u_moda`, `media`, `u_media`, `std` e `histograma` (`ancho` 2 mm en `rango` [0, 1000] mm, `conteos`, `encima`) |
| `carga` | `archivo` de origen, `eventos`, `media_pe`, `std_pe` e `histograma_pe` (el índice es el número de fotoelectrones) |

Destinos detallados y su agrupación en coeficientes:

| Destino (`destinos`, columna `destino`) | Significado | Coeficiente |
|---|---|---|
| `cap_dentro` | Captura dentro del volumen activo | $\eta_\mathrm{Cap}$ |
| `cap_fuera` | Captura fuera del volumen activo (tapa, aire) | $\eta_\mathrm{Cap}$ |
| `arriba` | Sale del volumen activo por la tapa | $\eta_\mathrm{Refle}$ |
| `abajo` | Sale por el fondo | $\eta_\mathrm{Trans}$ |
| `lateral` | Sale por la pared lateral | $\eta_\mathrm{Trans}$ |
| `no_entra` | No llega al volumen activo | $\eta_\mathrm{Otros}$ |
| `inel_dentro`, `inel_fuera` | Termina en una interacción inelástica, dentro o fuera del volumen activo | $\eta_\mathrm{Otros}$ |

### `resultados/<energía>/<medio>/historias.tsv.gz`

Una fila por neutrón (100 000 por corrida). No se versiona en git por su tamaño (unos 120 MB en total); se regenera
con `procesar_campana.py` y se publicará en Zenodo. Las celdas vacías indican que la magnitud no aplica (por
ejemplo, la posición de captura de un neutrón reflejado).

| Columna | Unidad | Significado |
|---|---|---|
| `historia` | — | Número de la historia en la corrida |
| `n_pasos` | — | Pasos del neutrón primario |
| `n_Transportation`, `n_hadElastic`, `n_neutronInelastic`, `n_nCapture` | — | Pasos de cada proceso |
| `ultimo_proceso` | — | Proceso del último paso |
| `destino` | — | Destino detallado (tabla anterior) |
| `x_cap`, `y_cap`, `z_cap` | mm | Posición de captura |
| `E_cap` | MeV | Energía del neutrón en el paso de captura |
| `N_total` | — | Todas las dispersiones elásticas de la historia capturada |
| `N_tesis` | — | $N$ de la tesis (vacío si la cadena se interrumpe) |
| `suma_xi_cadena` | — | Suma de $\xi$ en las dispersiones de la cadena |
| `xi_historia_inicial` | — | $\xi_\mathrm{ini}$ (solo trazabilidad) |
| `lambda_cap` | mm | Longitud de captura (vacío si la primera interacción en el agua no es la dispersión en la cara interior de la tapa) |

## Índice de figuras

Todas en [`figuras-seccion-4.2/`](figuras-seccion-4.2/), en PDF (y PNG tras ejecutar el notebook).

| Archivo | Tesis | Contenido |
|---|---|---|
| `fig_4_17_transportation` | Fig. 4.17 | Pasos `Transportation` por neutrón incidente frente a la energía |
| `fig_4_18_hadElastic` | Fig. 4.18 | Dispersiones elásticas por neutrón incidente frente a la energía |
| `fig_4_19_N_agua_pura` | Fig. 4.19 | $P(N\mid\text{captura})$ en agua pura, siete energías, con tabla de $x_\mathrm{max}$, FWHM, $\langle N\rangle$, $\sigma$ y capturas |
| `fig_D_1_N_2.5NaCl`, `fig_D_2_N_5NaCl`, `fig_D_3_N_10NaCl` | Figs. D.1–D.3 | Lo mismo para 2.5, 5 y 10 % de NaCl |
| `fig_4_20_xi_AP_fria` | Fig. 4.20 | $\rho(\xi)$ en agua pura, régimen frío (1–10 meV) |
| `fig_4_21_xi_AP_termica` | Fig. 4.21 | $\rho(\xi)$ en agua pura, régimen térmico (10–100 meV) |
| `fig_4_22_xi_AP_epitermica` | Fig. 4.22 | $\rho(\xi)$ en agua pura, régimen epitérmico (100 meV–1 eV) |
| `fig_4_23_xi_AP_intermedia` | Fig. 4.23 | $\rho(\xi)$ en agua pura, régimen intermedio (1 eV–1 keV) |
| `fig_D_4_xi_A25NaCl_fria`, `fig_D_5_xi_A5NaCl_fria`, `fig_D_6_xi_A10NaCl_fria` | Figs. D.4–D.6 | $\rho(\xi)$ en el régimen frío con NaCl |
| `fig_complementaria_xi_<medio>_<régimen>` (9 figuras) | — | $\rho(\xi)$ con NaCl en los regímenes térmico, epitérmico e intermedio (no están en la tesis; Apéndice B del informe) |
| `fig_4_24_captura` | Fig. 4.24 | $\eta_\mathrm{Cap}$ frente a la energía |
| `fig_4_25_reflexion` | Fig. 4.25 | $\eta_\mathrm{Refle}$ frente a la energía |
| `fig_4_26_transmision_otros` | Fig. 4.26 | $\eta_\mathrm{Trans}$ y $\eta_\mathrm{Otros}$ frente a la energía |
| `fig_4_27_captura_relativa` | Fig. 4.27 | Ganancia relativa de captura con NaCl |
| `fig_4_28_lambda_cap_1keV` | Fig. 4.28 | Distribución de $\lambda_\mathrm{cap}$ a 1 keV, con medianas |
| `fig_4_29_lambda_cap_vs_energia` | Fig. 4.29 | Mediana de $\lambda_\mathrm{cap}$, banda de percentiles 25–75 y ajuste en $\log_{10}E$ |
| `tabla_4_9_lambda_cap.tex` | Tabla 4.9 | Mediana de $\lambda_\mathrm{cap}$ por energía y medio (filas LaTeX) |
| `fig_4_48_histogramas_carga` | Fig. 4.48 | Histogramas de fotoelectrones por evento detectado |
| `fig_4_50_fotoelectrones_medios` | Fig. 4.50 | Fotoelectrones medios por evento detectado |
| `fig_4_51_eficiencia_deteccion` | Fig. 4.51 | Eficiencia de detección, con las curvas del CRS1000 como referencia |

## Definiciones (las de la tesis)

- **Cadena de dispersión:** pasos con la posición previa o posterior dentro de la caja $|x|,|y|\le478$ mm,
  $0\le z\le1330$ mm, que empiezan en una dispersión elástica, continúan solo con dispersiones elásticas en
  pasos consecutivos y terminan en la captura (notebook `Analisis-procesos-neutrones-*.ipynb`).
- **$N$:** número de dispersiones elásticas de la cadena. Una captura sin dispersiones previas dentro de la caja
  cuenta como $N=0$; una historia cuya cadena se interrumpe (sale de la caja y vuelve a entrar) no aporta $N$.
  $N_\mathrm{total}$ (todas las del neutrón capturado) se conserva solo como verificación.
- **$\xi$:** $\ln(E_\mathrm{pre}/E_\mathrm{post})$ de cada dispersión elástica de las cadenas; $\langle\xi\rangle$ y
  $\sigma(\xi)$ sobre todas esas colisiones; histograma de 300 intervalos entre $-2$ y $2$ (notebooks
  `Histogramas_cita_*.ipynb`). La definición inicial del estudio, $\ln(E_0/E_\mathrm{cap})/N$ por historia, fue
  reemplazada y se conserva solo por trazabilidad (`xi_historia_inicial`).
- **Destino final:** la captura se identifica por el proceso `nCapture`; para los demás neutrones, por la última
  frontera del volumen activo ($|x|,|y|\le480$ mm, $0\le z\le1330$ mm) atravesada, como en
  `analysis/revision-tesis_2026-10/` (`balance_caras_tanque.py`).
- **$\lambda_\mathrm{cap}$:** distancia en línea recta entre el punto de la primera dispersión elástica en la cara interior
  de la tapa ($z=1330.05$ mm, sin pérdida previa de energía) y el punto de captura, para las capturas cuya primera
  interacción en el agua es esa dispersión (83–99 % de las capturas). Valor representativo: la mediana, con
  incertidumbre por remuestreo (200 réplicas, semilla fija), y los percentiles 25–75 como dispersión.
- **Eficiencia de detección:** número de eventos con al menos un fotoelectrón aceptado dividido entre $10^5$; el
  umbral de un fotoelectrón es ideal (sin ruido electrónico) y da una cota superior de la eficiencia instrumental.

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
- Caja frente a cilindro: seleccionar los pasos con un cilindro de 480 mm en lugar de la caja cuadrada cambia los
  coeficientes como máximo en 0.031 puntos porcentuales y $\langle N\rangle$ en menos del 0.005 %
  (`resultados-cilindro/comparacion_caja_cilindro.tsv`).

## Longitud de captura (Tabla 4.9 y Figuras 4.28 y 4.29)

La versión anterior de la tesis daba, para once energías, la posición y el ancho de ajustes gaussianos al pico de la
distribución de $\lambda_\mathrm{cap}$, con intervalos de ajuste introducidos a mano. `verificar_tabla_4_9_original.py`
reproduce 33 de los 44 valores con los intervalos registrados en los notebooks y muestra que el archivo de 100 eV en
agua pura era una copia del de 1 keV y que los de 700 meV con 2.5 y 5 % de NaCl no provienen de los datos de la
Campaña 1. La versión final de la tesis usa la mediana, calculada con un procedimiento fijo para las 64 corridas.

## Carga y eficiencia (Figuras 4.48, 4.50 y 4.51)

Estas figuras pertenecen a la respuesta electromagnética del detector y se analizarán en su propio informe técnico;
los datos ya están procesados aquí. Los archivos `Carga_Total_*.txt` contienen el número de fotoelectrones de cada
evento con señal (no hay eventos con 0). La eficiencia de detección es el número de eventos con señal dividido entre
$10^5$ neutrones; los valores que usaba la figura de la tesis coinciden con estos archivos en las 64 corridas. La
versión anterior de la Figura 4.50 graficaba ese mismo número de eventos con el rótulo "número medio de fotones"
(con un valor mal transcrito, 21 399 en lugar de 21 349); la versión final muestra el número medio de fotoelectrones
por evento detectado (3.2 en agua pura y 10.5 con 10 % de NaCl, casi sin dependencia con la energía).

## Advertencias para el lector

- **$\eta$ en fracción.** En los archivos, los coeficientes están entre 0 y 1; la tesis y el informe los dan en %.
- **Promedios con distinta población.** $\overline{N}_\mathrm{hadElastic}$ promedia sobre todos los neutrones incidentes;
  $\langle N\rangle$, solo sobre las capturas con cadena válida. Por eso $\langle N\rangle$ (44.8 a 1 meV en agua pura)
  es mucho mayor que $\overline{N}_\mathrm{hadElastic}$ (17.1).
- **Resultados condicionados a la captura.** $P(N\mid\text{captura})$ y $\xi$ describen solo las historias que
  terminan capturadas. Que el NaCl reduzca $N$ o aumente $\langle\xi\rangle$ no significa que modere mejor: acorta
  las historias porque el cloro captura antes. Por colisión, el hidrógeno sigue siendo el mejor moderador.
- **Incertidumbres correlacionadas.** Las cuatro $\eta$ suman 1; sus incertidumbres no deben combinarse como
  independientes (covarianza $-\eta_i\eta_j/N_\mathrm{inc}$).
- **Captura no es detección.** $\eta_\mathrm{Cap}$ es una cota superior de la eficiencia de detección: solo una parte
  de las capturas produce fotoelectrones en el PMT.
- **Sin $S(\alpha,\beta)$.** Por debajo de ~1 eV, el tratamiento del hidrógeno ligado cambia el transporte; estos
  resultados no deben mezclarse con los de la Campaña 2 sin tenerlo en cuenta.
- **Moda de $\lambda_\mathrm{cap}$.** Es inestable (a baja energía queda junto a la tapa); use la mediana.

## Cómo reproducir

Requisitos: Python 3 con NumPy y Matplotlib (y Jupyter para el notebook). Los datos crudos (`Neutrones-termicos/`)
no están en el repositorio. Desde esta carpeta:

```bash
python3 procesar_campana.py <carpeta Neutrones-termicos> resultados 8      # ~1 min, 119 MB
python3 comparar_cilindro.py <carpeta Neutrones-termicos> resultados resultados-cilindro 8   # opcional
python3 construir_notebook.py
jupyter nbconvert --to notebook --execute figuras_seccion_4.2.ipynb        # figuras y verificación de 25 cifras
python3 figuras_informe.py resultados ../../docs/technical-reports/campana-1_sin-S-alpha-beta/figuras-procesamiento-64-corridas
python3 tablas_seccion_4_2.py resultados ../../docs/technical-reports/campana-1_sin-S-alpha-beta/figuras-procesamiento-64-corridas
```

Sin los datos crudos, el notebook y `tablas_seccion_4_2.py` funcionan igual con los resúmenes incluidos en
`resultados/`. Para recompilar el informe técnico, ejecute `latexmk -pdf` en
`docs/technical-reports/campana-1_sin-S-alpha-beta/`.
