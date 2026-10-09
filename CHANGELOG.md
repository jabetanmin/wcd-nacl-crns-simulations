# Historial de cambios

Todas las modificaciones relevantes del repositorio se documentarán en este archivo.

## [Sin publicar]

## [0.6.0] - 2026-10-09

### Añadido

- `analysis/validacion-numerica-Sidelnik_seccion-4.1.1/`: validación numérica con neutrones de 500 MeV (Sec. 4.1.1).
  `procesar_500MeV.py` procesa la carga de seis medios (agua pura y 0.5–10 % NaCl) y los espectros de fotones y
  electrones; `analizar_validacion.py` recalcula la Tabla de métricas y la de ajustes de la tesis (coinciden
  exactamente) y prueba su robustez (grados de libertad reales, artefactos de la digitalización de la referencia,
  control de Pearson, ajustes de Poisson); notebook de figuras, tablas e informe técnico
  `Informe-tecnico-Validacion-numerica-500MeV-Seccion-4.1.1`. Conteos normalizados a 1.5×10⁵ neutrones incidentes.
- Salvedad sobre los datos: el estudio original usó 1.5×10⁵ neutrones por medio y sus datos se perdieron por un daño
  del disco; se analiza la corrida conservada de 2×10⁵, con la que se generaron las figuras y tablas de carga y el
  espectro gamma de la versión actual de la sección. No se conservan los datos de las figuras de electrones,
  deuterones y líneas por núcleo.

## [0.5.0] - 2026-10-09

### Añadido

- `analysis/campana-1_neutrones-monoenergeticos_seccion-4.2/`: procesamiento reproducible de las 64 corridas
  de la Campaña 1 (16 energías × 4 medios) desde los archivos crudos del simulador (`procesar_corrida.py`,
  `procesar_campana.py`), con resúmenes por corrida (`resultados/`), comparación entre la selección por caja
  y por cilindro (`comparar_cilindro.py`) y generador de figuras (`figuras_informe.py`). Reproduce el balance
  de la Tabla 4.8 y el Apéndice C, los conteos por proceso y las cifras del Capítulo 5. La letargía se calcula
  con la definición de la tesis (por colisión); la definición inicial por historia se conserva solo por
  trazabilidad. Las tablas por neutrón (`historias.tsv.gz`) se publicarán en Zenodo.
- Informe técnico `docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Respuesta-WCD-flujos-monocromaticos-neutrones`
  (*Respuesta del WCD a flujos monocromáticos de neutrones*; antes `Informe-tecnico-Procesamiento-Campana-1-64-corridas`):
  sigue la parte neutrónica de la Sección 4.2 (transporte, moderación, balance de destinos con su tratamiento
  multinomial, ganancia relativa y longitud de captura; Figs. 4.17–4.29, D.1–D.6, Tablas 4.6–4.9 y Apéndice C),
  además del método, la validación y la comparación caja/cilindro. La carga y la eficiencia de detección
  (Figs. 4.48–4.51) se dejan para el informe de la respuesta electromagnética.
- `tablas_seccion_4_2.py`: tablas por régimen y medio (pasos por neutrón, $\langle\xi\rangle$ y $\sigma(\xi)$,
  eficiencia de detección y señal por captura).
- Guía de lectura de la carpeta de la Sección 4.2 en su `README.md`: contexto, convenciones, glosario, diccionario
  de datos de `resumen_campana.tsv`, `resumen.json` e `historias.tsv.gz`, e índice de figuras.
- `figuras_seccion_4.2.ipynb` (y `construir_notebook.py`): regenera las Figuras 4.17–4.27 y D.1–D.6 de la tesis
  solo con los resúmenes del repositorio; verifica automáticamente 25 cifras de la tesis.

- Carga y eficiencia (Figuras 4.48, 4.50 y 4.51): `resumen.json` guarda el histograma de fotoelectrones por evento; el
  notebook regenera las tres figuras (la 4.50 pasa a mostrar los fotoelectrones medios por evento detectado) con las
  curvas del CRS1000 de Köhli et al. (2018) en `datos/`.
- Longitud de captura $\lambda_\mathrm{cap}$ (Tabla 4.9 y Figuras 4.28 y 4.29): `procesar_corrida.py` la calcula con la
  definición de la tesis y una estadística fija (mediana con incertidumbre por remuestreo y percentiles 25–75); el
  notebook regenera la tabla y las figuras; `verificar_tabla_4_9_original.py` documenta la tabla anterior.

- `analysis/campana-1_respuesta-electromagnetica_seccion-4.2/` (fotones gamma): `procesar_gammas.py` procesa
  los 64 archivos `gamma-completo` (y las cascadas de `gamma-primario`, 1–10 meV); `verificar_tesis_gamma.py`
  reproduce 239 de 252 cifras gamma de la tesis y documenta sus definiciones; notebook de figuras (Figs. 4.30–4.42 y
  dos nuevas) y tablas del informe técnico `Informe-tecnico-Respuesta-electromagnetica-WCD-captura-neutrones`, que
  integra los tres informes previos sobre los gamma. Documenta que las cascadas de captura del 35Cl de `G4NeutronHP`
  no conservan la energía (10.1–10.3 MeV frente a Q = 8.58 MeV).
- Comparación caja/cilindro de los fotones gamma (`comparar_cilindro_gammas.py`), incluida como sección del informe:
  las interacciones físicas cambian menos del 0.12 %; solo cambian los conteos con pasos de transporte.
- Respuesta electromagnética, etapa de la carga y la eficiencia (`procesar_carga.py`, `construir_notebook_carga.py`,
  `tablas_informe_carga.py`, `resultados_carga/`, `figuras-carga/`) e informe técnico
  `Informe-tecnico-Respuesta-electromagnetica-WCD-carga-eficiencia`: distribución de carga en las 64 corridas,
  pruebas de su independencia de la energía, factorización ε = η_Cap × P(señal | captura), profundidad de captura y
  ganancia de eficiencia del NaCl por umbral de carga.

### Eliminado

- Informe técnico `Informe-tecnico-Analisis-Moderacion-Captura-Neutrones` (subconjunto anterior de cinco energías de la
  Campaña 1) y su carpeta `figuras-analisis-energia/`; queda en el historial de git. Las referencias en
  `analysis/README.md` y en el informe de estructura de archivos de la Campaña 2 se actualizaron.
- `analysis/notebooks/analisis_moderacion_captura_neutrones__agua-{pura,2.5pct-nacl}.ipynb`: copias anteriores de los
  notebooks de la Campaña 2 (sin la nota de campaña); quedan los de `campana-2_con-S-alpha-beta_25meV/`.

### Cambiado

- `analysis/scripts/build_notebook_moderacion_captura.py` se mueve junto a los notebooks que genera
  (`analysis/notebooks/campana-2_con-S-alpha-beta_25meV/`), que ahora tienen un `README.md`.

### Corregido

- La letargía $\xi$ de la tesis se calcula sobre las dispersiones elásticas de las cadenas que terminan en
  captura (como en las figuras de la tesis), no sobre todas las colisiones del neutrón capturado; con ello
  $\langle\xi\rangle$ = 0.0583 a 1 eV en agua pura y el valor 0.058 de la tesis es correcto (la versión anterior
  del informe señalaba erróneamente un redondeo a 0.059).
- `resumen.json` incluye los histogramas de $N$, $\xi$ y carga; la columna `suma_ln_E` se reemplaza por
  `suma_xi_cadena`.
- Tabla 4.9: los valores anteriores (ajustes gaussianos con intervalos elegidos a mano) se sustituyen por la mediana
  de $\lambda_\mathrm{cap}$; el valor anterior de 100 eV en agua pura se había calculado con los datos de 1 keV.
- Documentación: la Campaña 1 se rotula de 1 meV a 1 keV en todo el repositorio (`simulations/README.md`,
  `analysis/README.md`, `analysis/figuras-tesis/regenerar_figuras.py`); la fila del barrido S(α,β) en
  `simulations/README.md` incluye los cuatro medios; `THIRD_PARTY_NOTICES.md` identifica la base de MEIGA (commit
  `39b950e`, etiqueta `meiga-base-39b950e`); el árbol de `analysis/README.md` refleja la estructura real (se quitan
  `wcd_analysis/` y `tests/`, que no existían); el informe de electrones remite al informe de carga y eficiencia.

## [0.4.0] - 2026-10-04

### Añadido

- `analysis/revision-tesis_2026-10/`: scripts y salidas que respaldan las correcciones de la revisión
  final de la tesis: balance de destinos por caras del volumen activo (Tabla 4.8 y Apéndice C),
  Tablas 3.2, 4.13, 4.16, 4.18 y 4.19, origen de las líneas gamma del Na y de 6–7 MeV, y normalización
  temporal de los flujos de ARTI.
- `analysis/transporte-optico_seccion-4.2.5/`: kit de destino de los fotones ópticos y resultados de
  los cuatro medios (Tablas 4.26 y 4.27).
- `analysis/figuras-tesis/`: generadores de las figuras regeneradas de la tesis, incluido el flujo de
  ARTI normalizado a 3600 s (Fig. 4.62).
- Barrido de S(α,β) para soluciones con 2.5, 5 y 10 % de NaCl: configuración por medio
  (`medio.conf`, `DetectorList-<MEDIO>.xml`), tablas de resultados y análisis por medio y comparado.
- `analysis/validacion-experimental-prototipo-AmBe_seccion-4.1.2/`: notebooks, histogramas de carga,
  datos simulados de comparación, figuras y sumas SHA-256 de los datos crudos de la validación
  experimental con ²⁴¹AmBe, con la reconstrucción de las razones de mejora desde los datos crudos y
  la documentación de su origen (Sarmiento-Cano et al. 2026, arXiv:2601.17595).

### Cambiado

- Los scripts del barrido y de su análisis se generalizan a los cuatro medios.
- Mapa entre la tesis y el repositorio actualizado con la numeración final de la tesis.

## [0.3.0] - 2026-09-29

### Añadido

- Consolidación de las ramas `thesis-wcd-nacl` e `integracion-meiga-2026` en `main`; las ramas
  antiguas se conservan como etiquetas `archivo/...`.
- Etiquetas `campana-1-QGSP_BERT_HP` (código de febrero de 2025, verificado contra el binario) y
  `campana-2-QGSP_BERT_HP-SalphaBeta`.
- Selección de la física desde la configuración: `QGSP_BERT_HP` (con S(α,β)) o
  `QGSP_BERT_HP_NoThermal` (gas libre).
- `docs/GEOMETRIA_Y_FISICA_CAMPANAS.md`: geometría y física de cada campaña medidas en los datos.
- `simulations/barrido-SalphaBeta_1meV-1keV/`: kit del barrido en energía con ambas físicas.
- `analysis/efecto-SalphaBeta_barrido-energia/`: análisis, figuras e informe técnico del efecto de
  S(α,β) sobre el transporte de neutrones y la respuesta electromagnética.
- Mapa entre las secciones de la tesis y el repositorio en `README.md`.

### Corregido

- `Materials.h` sobrescrito con el contenido de `SaltyWCD.cc` (commit `103e01b`).
- `G4WCDSimulator` ignoraba `Simulation.PhysicsName`.
- `DetectorProperties.xml`: altura del tanque 133 cm (no 1.33 cm), acero de 0.5 mm y fracción de
  NaCl por defecto válida.

## [0.2.0] - 2026-09-07

### Añadido

- Código fuente limpio de MEIGA en el commit base `39b950e`.
- Rama `thesis-wcd-nacl` y etiqueta `meiga-base-39b950e`.
- Cinco commits funcionales que incorporan los 18 archivos modificados.
- Copia del README original de MEIGA para trazabilidad.
- Estructura científica para análisis, simulaciones, datos y resultados.

### Excluido

- Directorios de compilación y ejecutables.
- Copias redundantes `src (1)` y `src.zip`.
- Archivos de flujo todavía no seleccionados ni documentados.

## [0.1.0] - 2026-09-07

### Añadido

- Estructura inicial del repositorio.
- Documentación del alcance científico y de la relación con MEIGA.
- Plan de reproducibilidad y gestión de datos.
- Metadatos iniciales de citación.
- Entorno base para los programas de análisis en Python.
- Registro del repositorio original de MEIGA, sus ramas conocidas y la licencia MIT.
- Copia del aviso de licencia de MEIGA para preservar la atribución requerida.
- Identificación del commit `39b950e` como base de la carpeta modificada recibida.
- Auditoría preliminar de 18 archivos versionados con modificaciones locales.
- Registro de duplicados, productos de compilación y datos pendientes de depuración.
