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
| Energías de inyección | 1 meV, 10 meV, 25 meV, 100 meV, 10 keV (5 corridas × 4 medios = 20 corridas) | 25 meV únicamente (1 corrida × 4 medios), por ahora |
| Clasificación captura/reflexión/transmisión | Por geometría (posición del neutrón); el archivo de trazabilidad no registra material — ver nota sobre volumen del tanque más abajo | Por material (el archivo de trazabilidad sí lo registra) |
| Rol en la tesis | **Es la campaña sobre la que se apoya el análisis completo de la tesis** | Corrida de verificación/comparación, aún parcial |
| Informe técnico | [`docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Analisis-Moderacion-Captura-Neutrones.pdf`](../docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Analisis-Moderacion-Captura-Neutrones.pdf) | [`docs/technical-reports/campana-2_con-S-alpha-beta_25meV/Informe-tecnico-Estructura-Archivos-Simulacion.pdf`](../docs/technical-reports/campana-2_con-S-alpha-beta_25meV/Informe-tecnico-Estructura-Archivos-Simulacion.pdf) |
| Notebooks | Viven junto a los datos crudos, fuera de este repositorio (no replicados aquí por su tamaño) | [`analysis/notebooks/campana-2_con-S-alpha-beta_25meV/`](notebooks/campana-2_con-S-alpha-beta_25meV/) |
| Carpeta de datos crudos (fuera del repo) | `Nuevas-simulaciones-2026/Primeras-simulaciones/` (incluye la subcarpeta mal etiquetada `1keV/`, que en realidad es 10 keV) | `Nuevas-simulaciones-2026/25meV/` (nombre correcto — 25 meV, verificado directamente en `neutrones-incidentes.tsv` de las 4 concentraciones) |

**Por qué importa esta distinción.** Ambas campañas comparten el punto de **25 meV** — elegido en
la Campaña 2 precisamente para poner a prueba el régimen térmico, en torno a la energía térmica
del medio, donde S(α,β) más debería notarse. S(α,β) modifica la sección eficaz de dispersión
elástica del hidrógeno ligado justo en ese rango de energías, así que **25 meV es el punto natural
de comparación directa entre las dos campañas** — no debe asumirse que el balance de
captura/reflexión/transmisión ni la letargía de una reproducen los de la otra ahí. Los primeros
resultados ya muestran una fracción de captura distinta entre campañas a esa misma energía.
Cuantificar sistemáticamente esa diferencia a partir de este punto — y extender la Campaña 2 a las
otras cuatro energías de la Campaña 1 — queda como trabajo futuro; ver la sección de conclusiones
del informe técnico de la Campaña 1 para más detalle.

**Nombre de carpeta mal etiquetado.** Solo una de las dos carpetas de datos crudos tiene un nombre
que no corresponde a la energía real de la corrida (probablemente arrastrado de una etapa anterior
de generación de los archivos de flujo de entrada): `1keV/` (dentro de la Campaña 1) contiene en
realidad la corrida de **10 keV**. La carpeta `25meV/` de la Campaña 2 **sí** está correctamente
nombrada (verificado: 25 meV). Se documenta aquí y en el informe técnico correspondiente para que
no se propague el error; **la carpeta `1keV/` no se renombró en disco** — los notebooks existentes
leen rutas relativas a ese nombre.

**Volumen activo del tanque (actualización del 18 de septiembre de 2026).** Los 20 notebooks de la
Campaña 1 ahora subdividen "Capturado" según si la posición de la captura cae dentro o fuera de la
caja del volumen activo del tanque (z∈[0,1330] mm, |x|,|y|≤480 mm, dada explícitamente). La fracción
fuera del tanque resultó marginal (0.03 %–0.4 % de los neutrones incidentes) en las 20 corridas, así
que no cambia ninguna cifra de captura total ya reportada — ver el informe técnico de la Campaña 1
para el detalle completo.



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
├── notebooks/
│   └── campana-2_con-S-alpha-beta_25meV/  Notebooks de la Campaña 2 (con S(α,β), 25 meV)
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
