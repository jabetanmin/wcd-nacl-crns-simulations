# Sección 4.2 de la tesis: respuesta electromagnética del WCD a la captura de neutrones (Campaña 1)

Esta carpeta reproduce la parte electromagnética de la **Sección 4.2** de la tesis: lo que ocurre después de que el
neutrón es capturado. El estudio avanza en tres etapas, siguiendo la cadena de la señal,

> captura → **fotones gamma** → electrones y positrones → luz Cherenkov → fotomultiplicador (PMT)

y contiene las dos primeras: los **fotones gamma** de captura (producción, interacciones en el tanque y destino) y los
**electrones y positrones** que producen. La luz Cherenkov, la carga y la eficiencia quedan para la etapa siguiente.
La parte neutrónica (transporte, moderación y captura) está en
[`../campana-1_neutrones-monoenergeticos_seccion-4.2/`](../campana-1_neutrones-monoenergeticos_seccion-4.2/).

**Informes técnicos:**

- [*Respuesta electromagnética del WCD a la captura de neutrones: fotones gamma*](../../docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Respuesta-electromagnetica-WCD-captura-neutrones.pdf).
  Integra y actualiza los tres informes previos sobre los gamma (procesos y destino, espectros por proceso y líneas de
  captura de H, O, Na y Cl).
- [*Respuesta electromagnética del WCD a la captura de neutrones: electrones y positrones secundarios*](../../docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Respuesta-electromagnetica-WCD-electrones-secundarios.pdf).
  Ver la sección [Electrones y positrones](#electrones-y-positrones).

## Cómo leer esta carpeta

| Si quiere… | Empiece por… |
|---|---|
| Entender los resultados | El informe técnico |
| Consultar una cifra por corrida | `resultados_gammas/resumen_gammas_campana.tsv` (ver [Diccionario de datos](#diccionario-de-datos)) |
| Ver o rehacer una figura gamma de la tesis | `figuras_gammas_seccion_4.2.ipynb` y `figuras-gammas/` |
| Saber cómo se calculó una cifra de la tesis y si es correcta | `resultados_gammas/verificacion_tesis_gamma.tsv` |
| Reprocesar desde los datos crudos | [Cómo reproducir](#cómo-reproducir) |

## Datos de entrada

Carpeta `Gammas-contenido-completo/<energía>/<medio>/` del equipo del autor (6.8 GB con los notebooks y archivos
intermedios del análisis original; no está en el repositorio). Son las mismas 64 corridas de la Campaña 1 (16 energías
× 4 medios, $10^5$ neutrones, `QGSP_BERT_HP` sin $S(\alpha,\beta)$); la carpeta de 2.5 meV se llama `2-5meV`.

| Archivo | Contenido |
|---|---|
| `gamma-completo-*.txt` | Una fila por paso de cada fotón: `gamma trackID parentID paso proceso x y z E`, con la posición [mm] y la energía cinética [MeV] **posteriores** al paso (`G4WCDSteppingAction.cc`, etiqueta `campana-1-QGSP_BERT_HP`). Sin identificador de evento: una traza empieza cuando el paso vuelve a 1. En `phot` y `conv`, E = 0; la energía de llegada es la del paso anterior de la misma traza |
| `gamma-primario-*.txt` | Solo 1–10 meV: un fotón de captura (`nCapture`) por fila, con la energía exacta de emisión y la posición de la captura. Los fotones de una misma captura comparten la posición: cada grupo es una cascada |

## Convenciones

- **Tanque:** $|x|,|y|\le480$ mm y $0\le z\le1330.05$ mm (criterio de la tesis, incluye la cara interior de la tapa).
  **Tanque estricto:** $z\le1330$ mm (archivos `gamma-limpio` del análisis original).
- **Fotón del neutrón:** traza con `parentID` = 1 (captura e inelásticas). **Secundario:** el resto (aniquilación,
  bremsstrahlung, fluorescencia, desintegración del 24Na).
- **Destino:** `phot`/`conv` (absorbido, dentro o fuera del tanque) o salida del tanque (escapa).
- Energías y medios como en la carpeta de neutrones (`1000000meV` se rotula "1 keV"); colores de las figuras: agua pura
  rojo, 2.5 % verde, 5 % violeta, 10 % naranja.

## Contenido

| Archivo | Función |
|---|---|
| `procesar_gammas.py` | Procesa los 64 `gamma-completo` (y los `gamma-primario` disponibles) en una pasada; ~11 s con 8 procesos; cuarto argumento opcional `caja` (por defecto, criterio de la tesis) o `cilindro` (r ≤ 480 mm) |
| `comparar_cilindro_gammas.py` | Compara caja y cilindro (`resultados_gammas_cilindro/comparacion_caja_cilindro_gammas.tsv`): las interacciones físicas cambian menos del 0.12 %; solo cambian los conteos que incluyen pasos de transporte |
| `verificar_tesis_gamma.py` | Recalcula las cifras gamma de la tesis con las definiciones de los notebooks originales y las compara |
| `construir_notebook_gammas.py` | Genera `figuras_gammas_seccion_4.2.ipynb` |
| `figuras_gammas_seccion_4.2.ipynb` | Regenera las Figs. 4.30–4.37, 4.39–4.42 de la tesis y dos figuras nuevas |
| `tablas_informe_gammas.py` | Tablas LaTeX del informe técnico |
| `resultados_gammas/` | `resumen_gammas_campana.tsv`, un `resumen_gammas.json` por corrida y `verificacion_tesis_gamma.tsv` |
| `figuras-gammas/` | Figuras en PDF (los PNG se crean al ejecutar el notebook) |

## Diccionario de datos

### `resultados_gammas/resumen_gammas_campana.tsv` (una fila por corrida)

| Columna | Significado |
|---|---|
| `filas_total`, `filas_tanque`, `filas_exterior`, `filas_tanque_estricto` | Pasos de los fotones, en total y por zona |
| `trazas_total`, `trazas_neutron`, `trazas_secundarias` | Fotones (trazas), del neutrón y secundarios |
| `<proceso>_total`, `_tanque`, `_exterior` | Pasos por proceso (`compt`, `phot`, `Rayl`, `conv`, `Transportation`) y zona |
| `compt_E_menor_3MeV_total` | Pasos `compt` con E < 3 MeV en cualquier posición (definición de la tesis para el agua pura) |
| `compt_por_foton_neutron_media` | Dispersiones Compton en el tanque por fotón del neutrón |
| `absorbidos_phot_tanque`, `absorbidos_conv_tanque`, `escapan` | Destino de los fotones |
| `emision_H_2.224`, `emision_N_10.83`, `emision_B_0.478`, `emision_otras` | Fotones del neutrón con energía de emisión conocida (primer paso sin pérdida), por línea |
| `z_fotoabs_media_mm`, `r_fotoabs_media_mm`, `E_phot_entrada_media` | Posición media de la fotoabsorción en el tanque y energía media de llegada |
| `cascadas`, `cascadas_H`, `cascadas_Cl`, `E_cascada_Cl_media_MeV`, `fraccion_Cl_conserva_Q` | Cascadas de captura (solo 1–10 meV) |
| `tesis_phot_n`, `tesis_phot_media_0.01-0.1`, `tesis_phot_std_0.01-0.1` | Fotoabsorciones con la definición de la tesis (tabla de fotoabsorción, Fig. 4.40) |

### `resumen_gammas.json` (por corrida)

Las mismas magnitudes y, además: `procesos` y `otros_procesos` por zona; `primer_paso_trazas_neutron`; `destino`
separado para fotones del neutrón y secundarios; `histogramas` de 5 keV (energía de todos los pasos en el tanque, de
emisión, tras Compton, Rayleigh, de llegada a `phot` y `conv`, y de los fotones que escapan); `histogramas_baja_energia`
(0.5 keV hasta 0.3 MeV); `fotoabsorcion_tanque` (histogramas de z y r); `histogramas_tesis` con la binning de las
figuras de la tesis; `tesis_fotoabsorcion_previa_compt` con momentos en varias ventanas; y `cascadas_captura`
(espectro exacto de emisión y, por tipo de núcleo, capturas, fotones por captura, energía media de la cascada,
fracción que conserva $Q$ e histograma de la energía de la cascada).

### `verificacion_tesis_gamma.tsv`

Una fila por cifra de la tesis: `magnitud`, `energia`, `medio`, `tesis`, `reproducido`, `definicion` (la reconstruida)
y `estado` (`igual`, `difiere`, `sin valor en la tesis`).

## Resultados principales

- 239 de 252 cifras gamma de la tesis se reproducen exactamente. Tres errores de transcripción de la Tabla 4.10
  (636 187, 40 064, 140 659) y nueve puntos mal copiados en las Figs. 4.31, 4.32, 4.35, 4.37 y 4.40 se corrigieron
  en la tesis (2026-10-06).
- La tesis mezcla definiciones: $N(\gamma_\mathrm{Cap})$ son los fotones de captura exactos a 1 y 10 meV pero todas
  las trazas a ≥ 100 meV; la columna Compton es "E < 3 MeV en cualquier posición" en agua pura y "en el tanque" con NaCl;
  la distribución espacial usa un cilindro de 46 cm (el tanque tiene 48 cm).
- Compton es el 88–90 % de las interacciones físicas en el tanque; solo el 28–37 % de los fotones se absorbe en el agua.
- El NaCl pasa de 1.02 a 2.3 fotones por captura; el aumento de las interacciones con la salinidad se debe a la fuente,
  no a una mayor probabilidad de interacción por fotón.
- **Limitación del modelo:** las cascadas de captura del 35Cl no conservan la energía (10.1–10.3 MeV de media frente a
  $Q$ = 8.58 MeV; solo el 26–27 % suma $Q$), lo que aumenta la energía gamma por captura un 12–17 % en los medios con
  NaCl. Debe verificarse con una corrida con emisión correlacionada.

## Cómo reproducir

```bash
python3 procesar_gammas.py <Gammas-contenido-completo> resultados_gammas 8
python3 verificar_tesis_gamma.py <Gammas-contenido-completo> \
  ../campana-1_neutrones-monoenergeticos_seccion-4.2/resultados/resumen_campana.tsv \
  resultados_gammas/verificacion_tesis_gamma.tsv
python3 construir_notebook_gammas.py
jupyter nbconvert --to notebook --execute figuras_gammas_seccion_4.2.ipynb
python3 tablas_informe_gammas.py resultados_gammas \
  ../campana-1_neutrones-monoenergeticos_seccion-4.2/resultados/resumen_campana.tsv \
  ../../docs/technical-reports/campana-1_sin-S-alpha-beta/figuras-respuesta-electromagnetica
```

Sin los datos crudos, el notebook y `tablas_informe_gammas.py` funcionan con los resúmenes de `resultados_gammas/`.

## Electrones y positrones

### Datos de entrada

Carpeta `Electrones/<energía>/` del equipo del autor (4.2 GB, no está en el repositorio):
`rastreo-electron-{AP,A-25NaCl,A-5NaCl,A-10NaCl}-<energía>.txt`, las mismas 64 corridas (el número de trazas de
positrones coincide, ±4, con el de conversiones del archivo gamma). El de 300 meV en agua pura se copió de
`Imagenes-radiacion-EM/imagenes-resultados/Cherenkov/300meV/Agua-pura/rastreo-electron.txt` (MD5 idéntico).

Una fila por paso de cada e- o e+: `partícula proceso trackID parentID paso x y z E`, con el proceso que **limitó** el
paso (`GetProcessDefinedStep`), la posición [mm] y la energía cinética [MeV] posteriores. Particularidades:

- contar filas por proceso es contar pasos, no interacciones: la ionización continua actúa en todos los pasos;
- `Scintillation` es un paso de longitud cero con E = 0 que Geant4 añade cuando el electrón se detiene (≈ una por
  traza); no hay luz de centelleo;
- `G4Cerenkov` acorta el paso para que el electrón termine sobre el umbral del material: la energía tras los pasos
  `Cerenkov` se acumula en 264.06 keV (agua, n = 1.33 constante, tabla `waterPT1`, **igual en los cuatro medios**) y en
  186.2 keV (Pyrex del PMT, n = 1.47);
- las trazas se intercalan (G4Cerenkov suspende el electrón para seguir sus fotones): se siguen por `trackID`;
- falta el punto inicial de cada traza: la energía tras el paso 1 es una cota inferior de la de producción.

### Contenido

| Archivo | Función |
|---|---|
| `procesar_electrones.py` | Procesa los 64 `rastreo-electron` en una pasada (~35 s con 12 procesos); mismo cuarto argumento `caja`/`cilindro` |
| `verificar_tesis_electrones.py` | Recalcula las cifras de electrones de la tesis (Figs. 4.45–4.47, Tablas 4.17–4.19 y E.1) |
| `construir_notebook_electrones.py` | Genera `figuras_electrones_seccion_4.2.ipynb` |
| `figuras_electrones_seccion_4.2.ipynb` | Regenera las Figs. 4.45–4.47, E.3–E.4 y seis figuras nuevas |
| `tablas_informe_electrones.py` | Tablas LaTeX del informe de electrones |
| `resultados_electrones/` | `resumen_electrones_campana.tsv`, un `resumen_electrones.json` por corrida y `verificacion_tesis_electrones.tsv` |
| `figuras-electrones/` | Figuras en PDF |

### `resultados_electrones/resumen_electrones_campana.tsv` (una fila por corrida)

| Columna | Significado |
|---|---|
| `filas_*` | Pasos en total, en el tanque (z ≤ 1330.05 mm), en el tanque estricto (z ≤ 1330 mm, criterio de la tesis) y fuera |
| `trazas_e-`, `trazas_e+`, `trazas_tanque_*` | Trazas, en total y nacidas en el tanque |
| `trazas_sobre_umbral_*` | Trazas nacidas en el tanque con E > 264.06 keV tras el paso 1 |
| `trazas_emisoras_*` | Trazas con al menos un paso `Cerenkov` en el tanque |
| `<proceso>_{total,tanque,tanque_estricto,exterior}` | Pasos por proceso y zona |
| `longitud_tanque_mm`, `longitud_sobre_umbral_mm` | Longitud registrada en el tanque (sin el primer paso), total y con E sobre el umbral |
| `Cerenkov_ventana_tesis`, `Cerenkov_ventana_pyrex`, `Cerenkov_bajo_umbral_agua` | Pasos `Cerenkov` (tanque estricto) en 259.6–268.6 keV (Tabla 4.19), en 180–190 keV y bajo el umbral |
| `Cerenkov_pico_MeV`, `eIoni_E_no_nula_media` | Intervalo más poblado (0.04 keV) y media de la energía tras los pasos `eIoni` con E ≠ 0 |

### Resultados principales

- 118 de 152 cifras se reproducen exactamente y 20 (ajuste del máximo Cherenkov, Tabla 4.18) a menos de un intervalo.
  Ocho celdas de la Tabla E.1 estaban mal transcritas (msc/eBrem intercambiados a 1 meV con 2.5 y 5 %; valores de 1 meV
  repetidos a 100 meV); se corrigieron en la tesis (2026-10-06), junto con las Figs. 4.45 y 4.46, la nota de la
  Tabla 4.19 y la interpretación del máximo Cherenkov.
- La Fig. 4.46 ("espectro de ionización") es la ventana de 0.4–1.3 MeV en la que `eIoni` limita el paso; fuera de ella
  lo limita `Cerenkov`. Su máximo (0.48–0.50 MeV) no se desplaza con el NaCl; sí cambia la media (0.71 → 0.87 MeV).
- El máximo Cherenkov ajustado es 264.085–264.088 keV en las 20 combinaciones: el umbral de n = 1.33. El acuerdo del
  0.87 % con la Tabla 4.17 refleja n = 1.333 frente a 1.33, no una validación.
- El análisis original restó a las energías Cherenkov de los medios con NaCl una constante (5.6, 9.4 y 15.4 keV) sin
  base física; las ventanas de la nota de la Tabla 4.19 son esas ventanas desplazadas (equivalen a la de agua pura).
- Por captura, los rendimientos casi no dependen de E_n; con 10 % de NaCl, 2.3–2.4 veces más trazas emisoras y una
  longitud sobre el umbral 5.3–5.7 veces mayor que en agua pura.

### Cómo reproducir

```bash
python3 procesar_electrones.py <Electrones> resultados_electrones 12
python3 verificar_tesis_electrones.py <Electrones> resultados_electrones \
  resultados_electrones/verificacion_tesis_electrones.tsv
python3 construir_notebook_electrones.py
jupyter nbconvert --to notebook --execute figuras_electrones_seccion_4.2.ipynb
python3 tablas_informe_electrones.py resultados_electrones \
  ../campana-1_neutrones-monoenergeticos_seccion-4.2/resultados/resumen_campana.tsv \
  ../../docs/technical-reports/campana-1_sin-S-alpha-beta/tablas-electrones-secundarios
```
