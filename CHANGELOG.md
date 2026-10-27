# Historial de cambios

Todas las modificaciones relevantes del repositorio se documentarán en este archivo.

## [Sin publicar]

## [0.9.1] - 2026-10-26

### Añadido

- `analysis/apendices-tesis/`: mapa de los apéndices A–K de la tesis (versión del 26 de octubre de 2026) a los archivos
  que los producen, y `scripts/apendice_B_atomos_hidrogeno.py`, que reproduce el cálculo del Apéndice B.

### Cambiado

- `docs/CONTRIBUTIONS.md`: contribuciones de octubre de 2026 (física seleccionable, PMT de Sidelnik bajado, suelo
  SoilBS con plano contador, fuentes de 1 keV a 1 GeV, Am-Be lateral e inyección por la base y el costado del tanque).
- README raíz: el apéndice de contribuciones es el K (antes H.0.5) y se agrega la fila de los apéndices.

## [0.9.0] - 2026-10-26

### Añadido

- `analysis/suelo-humedo-calibracion_seccion-4.7/`: análisis e informe técnico de la Sec. 4.7 (37 páginas).
  - Flujo que sube de suelos SoilBS con 0 a 30 % de agua, con las regiones de la Tabla 2.2 y su correspondencia con
    las de CRNS. Con 30 % de agua, los intermedios bajan a 0.550 del seco y los rápidos a 0.423; los térmicos suben
    un 42 %. La forma de Desilets se ajusta con parámetros propios; la banda más sensible es 0.1–3 MeV.
  - Coeficientes de captura, reflexión, transmisión y otros destinos de 1 meV a 1 GeV en los cuatro medios (Campaña 1
    hasta 1 keV y barrido rápido por encima), con su incertidumbre y la ganancia relativa del NaCl; cuatro
    definiciones de la captura, que explican el 25 % de Sidelnik et al. (2020) como capturas por traza.
  - Fotones Cherenkov aceptados y fotoelectrones por neutrón de 1 keV a 1 GeV.
  - Curva de calibración por plegado y por simulación directa en el tanque (cuatro medios): caída de seco a 30 % de
    agua de 10.0, 10.9, 11.3 y 11.6 % en la simulación directa (8.6–10.4 % por plegado), hasta 13.2 % con la ventana
    de carga 1 ≤ Q < 20 p.e.
  - Sensibilidad $S_j(\theta_v)$ (Ec. 4.130) y resolución estadística en humedad.
  - `scripts/actualizar_informe.sh` rehace resultados, figuras, tablas e informe a partir de las corridas.
- `simulations/barrido-rapidos-WCD/`: neutrones monoenergéticos de 1 keV a 1 GeV, cuatro medios.
- `simulations/tanque-albedo/`: los neutrones que suben de cada suelo inyectados en el WCD por la base y el costado.
- `analysis/flujo-bucaramanga_secciones-4.3-4.5/scripts/verificar_tiempo_exposicion.py`: fija en 12 h (12.09 h con
  E > 50 MeV) el tiempo del campo `all_bga_neutron_35.shw` con una corrida pública de ARTI de 300 s a 956 m.
- `data/manifiestos/corridas-v0.9.0.tsv` y `excluidos-v0.9.0.sha256`: manifiestos de las 79 corridas de la Sec. 4.7 y
  sha256 de los archivos que no se versionan.

### Cambiado

- `analysis/albedo-suelo-humedo_seccion-4.6/` (v0.8.0) pasa a `analysis/suelo-humedo-calibracion_seccion-4.7/`, con la
  numeración final de la tesis, y la normalización del albedo pasa de 3600 s a 12 h (las tasas absolutas se dividen
  entre 12; las razones $N/N_0$ no cambian).
- README de las Secs. 4.3–4.5: tiempo de exposición verificado y definición del albedo de la Sec. 4.5 como corriente
  que sube (44.5 % reflejado, 55.5 % creado en el suelo).
- README de la Sec. 4.6: la curva R_j(θ_v) y la sensibilidad S_j ya están simuladas (Sec. 4.7).
- `simulations/albedo-suelo/`: corridas completas (seco de validación y 5, 10, 15, 25 y 30 %).

## [0.8.0] - 2026-10-23

### Añadido

- `analysis/validacion-experimental-prototipo-AmBe_seccion-4.1.2/`: simulaciones MEIGA del montaje con la fuente de
  ²⁴¹AmBe (Sec. 4.1.2), en cuatro carpetas:
  - `Analisis-fuente-AmBe/`: revisión de la fuente usada hasta ahora (la digitalización sesga el número de neutrones
    por intervalo entre −46 % y +35 %; peine de 437 energías; archivo ordenado), espectro ISO 8529 digitalizado,
    fuente corregida (χ²/ndf = 218/214), modelo del montaje blindado (haz 35 %, halo 45 %, fondo 20 %) y espectro
    Am-Be moderado en agua (10 meV – 10 eV); informe `Informe-fuente-AmBe241.pdf`;
  - `Analisis-corridas-AmBe/`: corridas antiguas con la fuente inyectada por la tapa, reponderadas al espectro
    ISO 8529, y cargas de los pulsos de las seis tomas del prototipo; informe `Informe-corridas-AmBe.pdf`;
  - `Analisis-montaje-MEIGA/`: montaje con entrada lateral (10⁶ neutrones por medio, agua pura y 2.5 y 10 % NaCl,
    PMT de Sidelnik en la tapa), calibración p.e./ADC con 2000 muones VEM (7.9 p.e./kADC), modelo de la electrónica
    del prototipo (resolución de 1 p.e., cociente Q/A, recorte del ADC en 8040, disparo) y comparación por factores
    comunes a los tres medios (≈1000 ADC/p.e.); informe `Informe-montaje-MEIGA.pdf`;
  - `Analisis-PMT-bajo-horizontal/`: Am-Be moderado con haz horizontal a media altura y PMT bajado (5×10⁵
    neutrones por medio): eficiencia 16.3/21.2/29.3 %, factores comunes k = 625–650 ADC/p.e. y
    N = 6.1–7.6×10⁶ en 300 s. La calibración con muones del PMT bajado (68–70 ADC/p.e.) se probó con un criterio
    fijado de antemano y no se usa (k/k_μ = 9.4–9.8). Informe `Informe-PMT-bajo-horizontal.pdf` y cuaderno.
- `simulations/montaje-AmBe-lateral/`, `simulations/muones-VEM-agua-pura/` y `simulations/AmBe-horizontal-PMT-bajo/`:
  paquetes de corrida (configuración, scripts de ejecución y de verificación, pruebas). `bajar_pmt.py` deja el PMT
  en `zPMT = 0.3*fWaterHalfHeight` con la forma de Sidelnik.
- `simulations/suelo-SoilBS/`: parche reversible de `G4WCDConstruction.cc` con el suelo SoilBS de la tesis (2.7 g/cm³,
  14 elementos), seco o húmedo (volúmenes aditivos). Se activa con `MEIGA_SUELO_W`; `MEIGA_SIN_TANQUE` y
  `MEIGA_SUELO_SEPARACION` permiten estudiar el suelo sin tanque o con el tanque a 2 m, como en los experimentos.
- `simulations/albedo-suelo/` y `analysis/albedo-suelo-humedo_seccion-4.6/`: albedo del suelo según la humedad,
  con 200 000 neutrones que bajan en `all_bga_neutron_35.shw`, un plano contador a 5 cm y el origen de cada neutrón
  que sube; el modo `validacion` corre el suelo seco con los mismos 50 000 neutrones que la parte 1 de cada humedad,
  para validarlo frente a la curva "Sube" de la tesis. Las corridas están en curso.
- `docs/ESTADO_MEIGA_CONTENEDOR.md` y `docs/technical-reports/diffs/parches-contenedor-v0.8.0/`: parches aplicados
  en el contenedor, en orden, con los md5 esperados y los diffs.
- `data/manifiestos/`: manifiestos de las 12 corridas (archivos, bytes, md5 del listado), sha256 de los flujos
  regenerables y de los archivos que se dejan fuera de git. `tools/manifiesto.sh` y `tools/comprimir_carpeta.sh`
  (tar + zstd con verificación).

### Cambiado

- La posición del PMT del contenedor pasa a ser, de forma definitiva, `0.3*fWaterHalfHeight` (cara plana a 46.55 cm
  bajo la tapa), con la forma de Sidelnik.
- Los scripts de análisis toman las rutas de los discos y de los datos de variables de entorno (`ADATA`, `TOSHIBA`,
  `REPO_TESIS`, `ALL_BGA_SHW`, `FUENTE_AMBE_DATOS`, …) en lugar de rutas personales fijas.

### Notas

- Los archivos de flujo grandes (montaje: semilla 20261021; moderado: 20261025; albedo: 20261023) no se versionan:
  se regeneran byte a byte, comprobado con sha256.
- No se versionan las salidas de las corridas (23–150 GB cada una), las tablas por evento de más de 5 MB, la figura
  ISO 8529 del IAEA ni artículos de terceros.

## [0.7.0] - 2026-10-19

### Añadido

- `analysis/replica-Sidelnik-MEIGA_seccion-4.1.1/`: validación numérica de la Sección 4.1.1 con corridas nuevas de MEIGA
  en la configuración de Sidelnik et al. (2020): 1.5×10⁵ neutrones de 500 MeV por medio, agua pura y agua con 2.5, 5 y
  10 % de NaCl, `QGSP_BERT_HP_NoThermal` (sin S(α,β)), tanque de acero con Tyvek y PMT en la tapa. Incluye:
  - procesamiento de las corridas y 45 scripts de análisis (interacciones del primario, vértices elásticos, probabilidad,
    tiempo y distancia de captura, líneas γ por núcleo y esquemas de niveles de ¹⁷O y ³⁶Cl, cascadas del Cl, espectros
    γ y de electrones frente a las Figs. 3–5 del artículo, deuterones, Fig. 6 con y sin piones, curvas de razón
    NaCl/agua pura con métricas, destino de los fotones ópticos y sensibilidad al modelo del Tyvek);
  - figuras `fig00`–`fig24`, resultados reducidos (`resultados/`) y digitalizaciones de las Figs. 2–6 del artículo;
  - informe técnico `Informe-Sidelnik-500MeV.pdf` (49 páginas), con el mismo contenido que la Sec. 4.1.1 de la tesis
    (fuente común `informe/seccion_4_1_1.tex`), y notas técnicas `Informe-Sidelnik-500MeV-tecnico.pdf`;
  - notebook `Analisis-Sidelnik-500MeV.ipynb` generado a partir de los scripts y del informe.
- `simulations/replica-Sidelnik-500MeV/`: generador del flujo, configuraciones por medio, ajuste del PMT a la geometría
  de Sidelnik, scripts de corrida y de verificación, y la configuración exacta de cada corrida realizada.

### Cambiado

- README raíz: la Sec. 4.1.1 apunta al nuevo análisis; el estudio anterior
  (`analysis/validacion-numerica-Sidelnik_seccion-4.1.1/`, corrida conservada de 2×10⁵ neutrones) se mantiene como
  referencia. Se retira de los pendientes la falta de datos de deuterones y de líneas por núcleo, que el nuevo análisis
  regenera.

### Notas

- Las imágenes de las figuras del artículo de Sidelnik et al. (2020) no se versionan (derechos de la revista); se
  incluyen sus digitalizaciones y el informe en PDF.
- La escala absoluta de la carga en el PMT depende del modelo óptico del Tyvek (factor `scaleLinerRef` = 0.94 de
  `Materials.cc`); la comparación con el artículo y las diferencias entre medios no dependen de él.

## [0.6.1] - 2026-10-09

### Corregido

- Salvedad de la Sección 4.1.1 (README de la carpeta e informe): la corrida conservada de 2×10⁵ neutrones es anterior
  al estudio de validación (septiembre–octubre de 2024). La tesis la recoge en una nota al pie de la Sección 4.1.1.

## [0.6.0] - 2026-10-09

### Añadido

- `analysis/validacion-numerica-Sidelnik_seccion-4.1.1/`: validación numérica con neutrones de 500 MeV (Sec. 4.1.1).
  `procesar_500MeV.py` procesa la carga de seis medios (agua pura y 0.5–10 % NaCl) y los espectros de fotones y
  electrones; `analizar_validacion.py` recalcula la Tabla de métricas y la de ajustes de la tesis (coinciden
  exactamente) y prueba su robustez (grados de libertad reales, artefactos de la digitalización de la referencia,
  control de Pearson, ajustes de Poisson); notebook de figuras, tablas e informe técnico
  `Informe-tecnico-Validacion-numerica-500MeV-Seccion-4.1.1`. Conteos normalizados a 1.5×10⁵ neutrones incidentes.
- Salvedad sobre los datos: el estudio original usó 1.5×10⁵ neutrones por medio y sus datos se perdieron por un daño
  del disco; se analiza la corrida conservada de 2×10⁵ (anterior al estudio, septiembre–octubre de 2024), con la que se generaron las figuras y tablas de carga y el
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
