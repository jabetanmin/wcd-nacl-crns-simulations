# Sección 4.1.1 de la tesis: validación numérica con neutrones de 500 MeV

Reproducción de Sidelnik et al. (2020, *Adv. Space Res.* 65, 2216–2222): WCD de 1 m³ con agua pura y con NaCl,
irradiado con neutrones de 500 MeV. Esta carpeta procesa los datos de esa simulación, verifica las cifras de la
Sección 4.1.1 y prueba la robustez de la validación cuantitativa.

> **Salvedad sobre los datos.** El estudio de validación se realizó originalmente con una simulación de 1.5×10⁵ neutrones de 500 MeV por medio, cuyos datos se perdieron por un daño del disco. Se conserva una corrida anterior al estudio de validación (septiembre–octubre de 2024), de 2×10⁵ neutrones por medio, con la que se generaron las figuras y tablas de carga y el espectro gamma de la versión actual de la Sección 4.1.1 (verificado por comparación de archivos y por reproducción exacta de las cifras). No se conservan los datos de la figura de electrones, de la de deuterones ni de las líneas por núcleo; esas figuras corresponden al análisis original.

**Informe técnico:** [`informe/Informe-tecnico-Validacion-numerica-500MeV-Seccion-4.1.1.pdf`](informe/Informe-tecnico-Validacion-numerica-500MeV-Seccion-4.1.1.pdf)

## Datos de entrada

Se simularon **2×10⁵ neutrones de 500 MeV por medio**. Los conteos absolutos (tablas y ejes de las figuras) se presentan
normalizados a **1.5×10⁵ neutrones incidentes** para compararlos con Sidelnik et al. (columnas `*_norm` de los
resúmenes); los errores estadísticos se calculan con los conteos reales. Razones, métricas y pendientes no dependen de
la normalización.

Carpeta `Seccion-validacion-numerica/Espectros-gamma-500MeV/` del equipo del autor (3.3 GB, fuera del repositorio):

| Subcarpeta | Archivos | Contenido |
|---|---|---|
| `Histograma-total-carga/` | `Carga_Total_Agua_<medio>_Neutrones_500MeV.txt` | Un entero por evento con señal (fotoelectrones, Q ≥ 1); agua pura y 0.5, 1, 2.5, 5 y 10 % NaCl |
| `Espectro-gamma/` | `Espectro-energia-gamma(s)-<medio>.txt` | Una energía [MeV] por fila: la del **fotón al interactuar** creando un e± (no el espectro de emisión) |
| `Espectro-electrones/` | `Espectro-energia-electrones-agua-<medio>[...].txt` | Energía cinética del e± creado; fila a fila con el archivo de fotones de la misma corrida |

**Atención:** los nombres de los archivos de electrones no corresponden a su medio (ver `resultados/verificacion_archivos.tsv`):
`…-25NaCl.txt` es la corrida de 5 %, `…-5NaCl.txt` la de 10 %, `…-10NaCl-1.txt` es idéntico a `…-25NaCl.txt`, y
`…-10NaCl.txt` y los `-Meiga` no se emparejan con ningún archivo de fotones. No hay electrones de la corrida de 2.5 %. La figura de electrones de la tesis no se hizo con estos archivos (procede del análisis original).

## Contenido

| Archivo | Función |
|---|---|
| `procesar_500MeV.py` | Lee los datos crudos (~40 s) y escribe los resúmenes de `resultados/` |
| `analizar_validacion.py` | Recalcula la Tabla de métricas y la de ajustes de la tesis, y las variantes y controles de robustez |
| `construir_notebook.py` | Genera `figuras_seccion_4.1.1.ipynb` |
| `figuras_seccion_4.1.1.ipynb` | Ocho figuras (carga, razones, referencia, artefactos, control de Pearson, ajustes, espectros) |
| `tablas_informe.py` | Tablas LaTeX del informe (`informe/tablas/`) |
| `datos/digitalizacion_histograma_carga_referencia_700pts.csv` | Digitalización original de la Fig. 6 de Sidelnik et al. (notebook `Comparacion_Histogramas_Carga.ipynb`, celda 25) |
| `resultados/` | Resúmenes (ver abajo) |
| `figuras/` | Figuras en PDF (los PNG se crean al ejecutar el notebook) |

### `resultados/`

| Archivo | Contenido |
|---|---|
| `verificacion_archivos.tsv` | MD5, filas y emparejamiento fila a fila (fracción con E_e ≤ E_γ) de cada archivo de espectro |
| `resumen_carga.tsv`, `histograma_carga.tsv` | Eventos reales y normalizados, eficiencia, estadística de la carga e histograma por carga entera (conteos reales), seis medios |
| `espectro_gamma.tsv`, `espectro_electrones.tsv` | Histogramas de 5 keV (0–20 MeV) y logarítmicos (1 keV–600 MeV) |
| `lineas_gamma.tsv` | Energía tabulada y de Geant4 de cada línea de captura, cuentas en ±0.05 keV y fondo |
| `metricas_reproduccion.tsv` | Tabla de métricas de la tesis frente a la recalculada (coinciden) |
| `metricas_variantes.tsv` | Métricas con bins nativos, sin suavizar, a 25 pe y con la referencia sin artefactos |
| `control_pearson.tsv` | r y razón media de cada simulación (0.5–10 %) frente a cada referencia |
| `razon_25pe.tsv` | Razones NaCl/agua pura a 25 pe con error de Poisson y referencias cruda y limpia |
| `ajustes_tramos.tsv` | Tabla de ajustes de la tesis, origen de cada cifra (binnings A y B) y ajuste de Poisson |
| `referencia_limpia.tsv` | Razones de la referencia sin los picos de la leyenda |

## Resultados principales

- Las 15 métricas y los 40 parámetros de ajuste de la tesis se reproducen exactamente desde los datos crudos.
- Concordancia cualitativa confirmada: razón < 1 bajo ~100 pe, cruce hacia 100–110 pe, máximo hacia 290–310 pe,
  orden con la concentración (0.5 y 1 % encajan en la secuencia).
- Validación cuantitativa no robusta: p-valores calculados sobre 700 puntos interpolados (con los 36 bins reales,
  p = 10⁻⁹–10⁻⁴); la digitalización capturó la leyenda y sesga la referencia del 2.5 % (−23 %); Pearson no
  distingue concentraciones; la amplitud simulada es ~30 % menor que la de referencia para 2.5 y 5 %.
- La Tabla de ajustes combina dos binnings (valores de uno, errores de otro) y un ajuste no ponderado que descarta
  bins vacíos; con Poisson, la pendiente de 1500–3500 pe es −4.4 ± 0.08, no −5.5.
- Líneas de captura en Geant4: H a 2224.37 keV (NNDC 2223.25), ³⁵Cl a 8579.81 keV (NNDC 8578.6).
- El 79.8–80.8 % de los neutrones produce señal (119 702–121 254 eventos por 1.5×10⁵ neutrones), casi igual en
  todos los medios.
- Pendiente: deuterones (datos no localizados).

## Cómo reproducir

```bash
python3 procesar_500MeV.py <Espectros-gamma-500MeV> resultados
python3 analizar_validacion.py resultados datos
python3 construir_notebook.py
jupyter nbconvert --to notebook --execute figuras_seccion_4.1.1.ipynb
python3 tablas_informe.py resultados informe/tablas
```

Sin los datos crudos, todo salvo el primer paso funciona con `resultados/` y `datos/`.
