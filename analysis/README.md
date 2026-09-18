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

| | **Campaña 1 — "primeras simulaciones"** | **Campaña 2 — exploratoria** |
|---|---|---|
| Tratamiento térmico S(α,β) | **No** implementado | **Sí** implementado |
| Energías de inyección | 1 meV, 10 meV, 25 meV, 100 meV, 10 keV (5 corridas × 4 medios = 20 corridas) | 2 meV únicamente (1 corrida × 4 medios), por ahora |
| Clasificación captura/reflexión/transmisión | Por geometría (posición final del neutrón); el archivo de trazabilidad no registra material | Por material (el archivo de trazabilidad sí lo registra) |
| Rol en la tesis | **Es la campaña sobre la que se apoya el análisis completo de la tesis** | Corrida de verificación/comparación, aún parcial |
| Informe técnico | [`docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Analisis-Moderacion-Captura-Neutrones.pdf`](../docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Analisis-Moderacion-Captura-Neutrones.pdf) | [`docs/technical-reports/campana-2_con-S-alpha-beta_2meV/Informe-tecnico-Estructura-Archivos-Simulacion.pdf`](../docs/technical-reports/campana-2_con-S-alpha-beta_2meV/Informe-tecnico-Estructura-Archivos-Simulacion.pdf) |
| Notebooks | Viven junto a los datos crudos, fuera de este repositorio (no replicados aquí por su tamaño) | [`analysis/notebooks/campana-2_con-S-alpha-beta_2meV/`](notebooks/campana-2_con-S-alpha-beta_2meV/) |
| Carpeta de datos crudos (fuera del repo) | `Nuevas-simulaciones-2026/Primeras-simulaciones/` (~113 GB; incluye la subcarpeta mal etiquetada `1keV/`, que en realidad es 10 keV) | `Nuevas-simulaciones-2026/25meV/` (~82 GB; el nombre de la carpeta es un error heredado — la energía real es **2 meV**, no 25 meV) |

**Por qué importa esta distinción.** S(α,β) modifica la sección eficaz de dispersión elástica
del hidrógeno ligado justo en el rango de energías donde ambas campañas se solapan, alrededor
del equilibrio térmico del agua. No debe asumirse que el balance de captura/reflexión/transmisión
ni la letargía de una campaña reproducen los de la otra a una energía comparable: los primeros
resultados de la Campaña 2 (a 2 meV) ya muestran una fracción de captura distinta de la que
obtiene la Campaña 1 a energías cercanas. Cuantificar sistemáticamente esa diferencia — y
extender la Campaña 2 a las otras cuatro energías de la Campaña 1 — queda como trabajo futuro;
ver la sección de conclusiones del informe técnico de la Campaña 1 para más detalle.

**Nombres de carpeta mal etiquetados.** Dos carpetas de datos crudos tienen nombres que no
corresponden a la energía real de la corrida (probablemente arrastrados de una etapa anterior de
generación de los archivos de flujo de entrada). Se documentan aquí, y en los informes técnicos
correspondientes, para que no se propague el error, pero **las carpetas no se renombraron en
disco** — los notebooks existentes leen rutas relativas a ese nombre:

- `1keV/` (dentro de la Campaña 1) contiene en realidad la corrida de **10 keV**.
- `25meV/` (la Campaña 2 completa) contiene en realidad la corrida de **2 meV**.

## Estructura de este directorio

```text
analysis/
├── notebooks/
│   └── campana-2_con-S-alpha-beta_2meV/   Notebooks de la Campaña 2 (con S(α,β), 2 meV)
├── scripts/                                Programas reproducibles
├── wcd_analysis/                           Funciones reutilizables (pendiente)
└── tests/                                  Pruebas de las funciones de análisis (pendiente)
```

Los notebooks de la Campaña 1 (cinco energías, sin S(α,β)) no están replicados en este
repositorio: viven junto a sus datos crudos, cuyo tamaño (cientos de MB a varios GB por corrida)
los hace poco prácticos para versionar en git. El informe técnico de la Campaña 1 describe su
convención de nombres y su flujo de trabajo en la sección "Reproducibilidad".

Los programas definitivos deben aceptar rutas y parámetros por línea de comandos o archivos de
configuración; no deben contener rutas personales fijas.
