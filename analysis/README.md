# Análisis en Python

Este directorio contiene los programas y cuadernos utilizados para:

- leer y depurar las salidas de simulación;
- construir histogramas con intervalos lineales o logarítmicos;
- normalizar distribuciones por neutrón incidente y ancho de intervalo;
- calcular eficiencias e incertidumbres estadísticas;
- comparar agua pura con soluciones de NaCl;
- producir tablas y figuras de la tesis.

## Dos campañas de simulación: léase antes de comparar resultados

Los notebooks y los informes técnicos de este repositorio documentan **dos campañas de
simulación Geant4/MEIGA distintas** del mismo WCD (agua pura y NaCl al 2.5 %, 5 % y 10 % en
masa). Comparten geometría, materiales de estructura y framework, pero **difieren en si el
transporte de neutrones subtérmicos incluye o no el tratamiento térmico S(α,β)** para el
hidrógeno ligado en moléculas de agua — y eso hace que sus resultados, en particular la
fracción de captura, no coincidan a energías comparables. Quien llegue a este repositorio sin
haber seguido el desarrollo de la tesis debe tener esto presente antes de cruzar cifras entre
un notebook/informe y otro:

| | **Campaña 1 — base de la tesis** | **Campaña 2 — exploratoria** |
|---|---|---|
| Tratamiento térmico S(α,β) | **No** implementado (`QGSP_BERT_HP`) | **Sí** implementado |
| Energías de inyección | 16 energías entre 1 meV y 1 keV (16 × 4 medios = 64 corridas, febrero de 2025) | 25 meV únicamente (1 corrida × 4 medios), por ahora |
| Clasificación captura/reflexión/transmisión | Por geometría: última frontera del volumen activo atravesada (el archivo de trazabilidad no registra material) | Por material (el archivo de trazabilidad sí lo registra) |
| Rol en la tesis | **Es la campaña sobre la que se apoya la Sección 4.2 y el Capítulo 5** | Corrida de verificación/comparación, aún parcial |
| Informe técnico | [`docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Respuesta-WCD-flujos-monocromaticos-neutrones.pdf`](../docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Respuesta-WCD-flujos-monocromaticos-neutrones.pdf) | [`docs/technical-reports/campana-2_con-S-alpha-beta_25meV/Informe-tecnico-Estructura-Archivos-Simulacion.pdf`](../docs/technical-reports/campana-2_con-S-alpha-beta_25meV/Informe-tecnico-Estructura-Archivos-Simulacion.pdf) |
| Procesamiento y notebooks | [`campana-1_neutrones-monoenergeticos_seccion-4.2/`](campana-1_neutrones-monoenergeticos_seccion-4.2/): scripts que procesan los archivos crudos, resúmenes por corrida y notebook que regenera las figuras | [`analysis/notebooks/campana-2_con-S-alpha-beta_25meV/`](notebooks/campana-2_con-S-alpha-beta_25meV/) |
| Carpeta de datos crudos (fuera del repo) | `Neutrones-termicos/<energía>/<medio>/` (las carpetas `1000meV` … `1000000meV` se rotulan 1 eV … 1 keV en la tesis) | `Nuevas-simulaciones-2026/25meV/` (nombre correcto — 25 meV, verificado directamente en `neutrones-incidentes.tsv` de las 4 concentraciones) |

**Por qué importa esta distinción.** Ambas campañas comparten el punto de **25 meV** — elegido en
la Campaña 2 precisamente para poner a prueba el régimen térmico, en torno a la energía térmica
del medio, donde S(α,β) más debería notarse. S(α,β) modifica la sección eficaz de dispersión
elástica del hidrógeno ligado justo en ese rango de energías, así que **25 meV es el punto natural
de comparación directa entre las dos campañas** — no debe asumirse que el balance de
captura/reflexión/transmisión ni la letargía de una reproducen los de la otra ahí. Los primeros
resultados ya muestran una fracción de captura distinta entre campañas a esa misma energía; el
estudio [`efecto-SalphaBeta_barrido-energia/`](efecto-SalphaBeta_barrido-energia/) cuantifica el
efecto de S(α,β) entre 1 meV y 1 keV.

**Subconjunto anterior de cinco energías (retirado).** Antes del procesamiento de las 64 corridas,
la Campaña 1 se analizó con un subconjunto de cinco energías (1, 10, 25 y 100 meV y 1 keV; carpeta
`Nuevas-simulaciones-2026/Primeras-simulaciones/`). Ese análisis y su informe
(`Informe-tecnico-Analisis-Moderacion-Captura-Neutrones`) se retiraron del repositorio el 6 de octubre
de 2026 y se conservan en el historial de git; el informe de la Sección 4.2 los reemplaza. Lo que
estableció ese análisis sigue siendo válido en el procesamiento nuevo: la fracción de capturas fuera
del volumen activo es marginal (inferior al 0.4 % de los neutrones incidentes).



## Validación experimental (Sección 4.1.2)

[`validacion-experimental-prototipo-AmBe_seccion-4.1.2/`](validacion-experimental-prototipo-AmBe_seccion-4.1.2/)
contiene los notebooks, los histogramas de carga y las figuras de la validación con el prototipo
irradiado con ²⁴¹AmBe. Los datos crudos (1.9 GB, formato LAGO) están fuera del repositorio.

## Estudio del efecto de S(α,β) (septiembre de 2026)

[`efecto-SalphaBeta_barrido-energia/`](efecto-SalphaBeta_barrido-energia/) compara, con el mismo
ejecutable y la misma geometría, la física con y sin S(α,β) en agua pura de 1 meV a 1 keV. Muestra
que la diferencia de captura entre las campañas a 25 meV (factor ≈ 0.69) se debe a S(α,β) y no a la
tapa de acero, y analiza la cadena electromagnética hasta la carga del PMT. Incluye un informe
técnico de 21 páginas.

## Estructura de este directorio

```text
analysis/
├── <tema>_seccion-<n>/                      Una carpeta por sección de la tesis, con su README
├── figuras-tesis/                           Generadores de las figuras regeneradas de la tesis
├── revision-tesis_2026-10/                  Respaldo de las correcciones de la revisión final
└── notebooks/
    └── campana-2_con-S-alpha-beta_25meV/    Notebooks de la Campaña 2 (con S(α,β), 25 meV) y su generador
```

Los datos crudos de la Campaña 1 (cientos de MB a varios GB por corrida) y los notebooks originales
que los acompañan no se versionan en git. El procesamiento reproducible de las 64 corridas, sus
resúmenes y el notebook de figuras de la Sección 4.2 están en
[`campana-1_neutrones-monoenergeticos_seccion-4.2/`](campana-1_neutrones-monoenergeticos_seccion-4.2/),
cuyo README sirve de guía de lectura; las tablas por neutrón se publicarán en Zenodo.

Los programas definitivos deben aceptar rutas y parámetros por línea de comandos o archivos de
configuración; no deben contener rutas personales fijas.
