# WCD–NaCl CRNS Simulations

Repositorio de investigación de la tesis doctoral de **Jaime A. Betancourt** sobre la evaluación Monte Carlo de un detector Cherenkov de agua (WCD) dopado con NaCl para la detección de neutrones cósmicos y su aplicación al monitoreo de humedad del suelo mediante CRNS.

## Alcance

Este repositorio reúne y continuará incorporando:

- las extensiones y adaptaciones realizadas sobre el framework MEIGA/Geant4;
- la implementación geométrica, física y óptica del WCD;
- los medios detectores de agua pura y soluciones con 2.5 %, 5.0 % y 10.0 % de NaCl en fracción másica;
- las configuraciones para fuentes monocromáticas, flujo atmosférico, neutrones de albedo y validación con \(^{241}\mathrm{AmBe}\);
- los programas Python utilizados para procesar, normalizar, analizar y representar los resultados;
- datos de ejemplo y resultados seleccionados necesarios para reproducir las principales conclusiones.

## Estado

**Versión 0.4.0 (4 de octubre de 2026).** La rama `main` reúne el código de las dos campañas de simulación de la tesis, los análisis por sección, los informes técnicos y los scripts que respaldan las correcciones de la revisión final de la tesis.

| Componente | Dónde |
|---|---|
| Código actual (`src/`) | Campaña 2 y estudio de S(α,β): QGSP_BERT_HP con o sin `G4ThermalNeutrons`, elegido en la configuración (`PhysicsName`) |
| Código de la Campaña 1 | etiqueta `campana-1-QGSP_BERT_HP` (ejecutable del 13-02-2025) |
| Código de la Campaña 2 | etiqueta `campana-2-QGSP_BERT_HP-SalphaBeta` |
| Geometría y física medidas en los datos | [`docs/GEOMETRIA_Y_FISICA_CAMPANAS.md`](docs/GEOMETRIA_Y_FISICA_CAMPANAS.md) |
| Entorno | Geant4 10.7.4 (10.07.p04) en un contenedor Docker; ver [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) |

Pendientes para la versión 1.0.0 (ver [`CHANGELOG.md`](CHANGELOG.md)): figuras de carga de la Campaña 1 (Sección 4.2), notebooks de la validación numérica (Sección 4.1.1), trazabilidad de la Tabla de razones de la Sección 4.1.2, configuraciones por corrida de las campañas 1 y 2, y publicación de los datos crudos con identificador persistente.

## Mapa entre la tesis y el repositorio

| Tesis | Contenido | Repositorio |
|---|---|---|
| Cap. 3, Etapa IV | Modelo del WCD: geometría, materiales, física, óptica y QE | [`src/G4Models/`](src/G4Models/) (`SaltyWCD.cc`, `Materials.cc`, `G4MPhysicsList.cc`, `G4MPMTAction.cc`), [`src/Applications/G4WCDSimulator/`](src/Applications/G4WCDSimulator/); informes de PMT, Tyvek, densidades e integración en [`docs/technical-reports/`](docs/technical-reports/) |
| Sec. 4.1.1 | Validación numérica (Sidelnik et al. 2020b) | pendiente |
| Sec. 4.1.2 | Validación experimental con un prototipo y ²⁴¹AmBe | [`analysis/validacion-experimental-prototipo-AmBe_seccion-4.1.2/`](analysis/validacion-experimental-prototipo-AmBe_seccion-4.1.2/) |
| Sec. 4.2 | Respuesta a neutrones monocromáticos (Campaña 1): procesamiento de las 64 corridas, validación frente a la tesis y comparación caja/cilindro y notebook que regenera las Figuras 4.17–4.29, D.1–D.6 y la Tabla 4.9 | [`analysis/campana-1_neutrones-monoenergeticos_seccion-4.2/`](analysis/campana-1_neutrones-monoenergeticos_seccion-4.2/), [`docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Procesamiento-Campana-1-64-corridas.pdf`](docs/technical-reports/campana-1_sin-S-alpha-beta/Informe-tecnico-Procesamiento-Campana-1-64-corridas.pdf); figuras de carga pendientes |
| Secs. 4.3–4.5 | Flujo atmosférico (ARTI, 3600 s en el nivel de inyección; flujo completo de 12 h en la superficie) y de suelo seco en Bucaramanga | [`analysis/flujo-bucaramanga_secciones-4.3-4.5/`](analysis/flujo-bucaramanga_secciones-4.3-4.5/) |
| Sec. 4.6 | Respuesta de referencia del WCD a un suelo seco | [`analysis/caracterizacion-respuesta-referencia-wcd_seccion-4.6/`](analysis/caracterizacion-respuesta-referencia-wcd_seccion-4.6/) |
| Sec. 4.2.4 | Efecto de S(α,β): barrido de 1 meV a 1 keV en agua pura y con 2.5, 5 y 10 % de NaCl, transporte y respuesta electromagnética | [`simulations/barrido-SalphaBeta_1meV-1keV/`](simulations/barrido-SalphaBeta_1meV-1keV/), [`analysis/efecto-SalphaBeta_barrido-energia/`](analysis/efecto-SalphaBeta_barrido-energia/) |
| Sec. 4.2.5 | Transporte óptico y conversión de la luz en fotoelectrones (Tablas 4.26 y 4.27) | [`analysis/transporte-optico_seccion-4.2.5/`](analysis/transporte-optico_seccion-4.2.5/) |
| Revisión final (Tablas 3.2, 4.8, 4.13, 4.16, 4.18, 4.19, C.3–C.5; Secs. 4.3–4.4; Ap. E) | Scripts que respaldan las correcciones numéricas de octubre de 2026 | [`analysis/revision-tesis_2026-10/`](analysis/revision-tesis_2026-10/) |
| Figuras regeneradas | Generadores de las figuras de `Figuras-corregidas/` | [`analysis/figuras-tesis/`](analysis/figuras-tesis/) |
| Campaña 2 (25 meV) | Moderación y captura con S(α,β), cuatro medios | [`analysis/notebooks/campana-2_con-S-alpha-beta_25meV/`](analysis/notebooks/campana-2_con-S-alpha-beta_25meV/), [`docs/technical-reports/campana-2_con-S-alpha-beta_25meV/`](docs/technical-reports/campana-2_con-S-alpha-beta_25meV/) |
| Apéndice A | Framework MEIGA | [`docs/MEIGA_UPSTREAM_README.md`](docs/MEIGA_UPSTREAM_README.md) |
| Apéndice H.0.5 | Contribuciones computacionales a MEIGA | [`docs/CONTRIBUTIONS.md`](docs/CONTRIBUTIONS.md), diferencias de código en [`docs/technical-reports/diffs/`](docs/technical-reports/diffs/) |

## Relación con MEIGA

MEIGA es un framework desarrollado con anterioridad a esta tesis. Su arquitectura general, sus clases base y sus mecanismos fundamentales de ejecución no constituyen contribuciones originales de este trabajo.

Las contribuciones de la tesis corresponden a extensiones, configuraciones y rutinas específicas para:

- modelar el WCD y sus componentes;
- definir agua pura y soluciones acuosas de NaCl;
- incorporar propiedades físicas y ópticas dependientes del medio;
- seleccionar y registrar información de capturas neutrónicas, fotones secundarios y respuesta fotoelectrónica;
- organizar las salidas necesarias para el análisis científico;
- procesar los resultados mediante programas desarrollados en Python.

La descripción detallada se encuentra en [`docs/CONTRIBUTIONS.md`](docs/CONTRIBUTIONS.md).

## Estructura

```text
wcd-nacl-crns-simulations/
├── src/                  Código de MEIGA y modificaciones de la tesis
├── simulations/          Configuraciones y scripts de corrida de cada campaña
├── analysis/             Análisis por sección de la tesis (scripts, tablas, figuras, informes)
├── data/                 Datos pequeños de entrada y datos procesados
├── results/              Figuras y tablas seleccionadas
├── docs/                 Metodología, atribución y reproducibilidad
├── CITATION.cff          Metadatos para citar el repositorio
├── CHANGELOG.md          Historial de versiones
└── environment.yml       Entorno reproducible de análisis
```

## Requisitos

- Geant4 10.07.p04 para reproducir el entorno principal de la tesis;
- datos de física neutrónica compatibles con la instalación de Geant4;
- compilador C++ compatible con la versión de Geant4;
- CMake;
- Python 3 y las dependencias indicadas en `environment.yml`.

## Compilación

Desde la raíz del repositorio:

```bash
mkdir -p build
cd build
cmake -DCMAKE_INSTALL_PREFIX=../install ../src
make -j4
make install
```

La compilación requiere que Geant4 y sus paquetes de datos estén configurados previamente. El ejemplo anterior conserva el procedimiento general del proyecto MEIGA original; deberá verificarse en el entorno empleado para reproducir la tesis.

## Trazabilidad

- Rama principal: `main` (consolida las antiguas ramas `thesis-wcd-nacl` e `integracion-meiga-2026`).
- Punto de partida: etiqueta `meiga-base-39b950e`.
- Repositorio original: <https://github.com/ataboadanunez/meiga>.
- README original preservado en [`docs/MEIGA_UPSTREAM_README.md`](docs/MEIGA_UPSTREAM_README.md).
- Auditoría de la carpeta recibida: [`docs/IMPORT_AUDIT.md`](docs/IMPORT_AUDIT.md).

## Datos

El repositorio no debe contener resultados masivos, archivos de compilación ni datos que puedan regenerarse fácilmente. Se incluirán datos pequeños de ejemplo y productos procesados esenciales. Los conjuntos grandes deberán publicarse por separado y enlazarse mediante un identificador persistente.

Consulte [`docs/DATA_MANAGEMENT.md`](docs/DATA_MANAGEMENT.md).

## Citación

Cuando utilice este repositorio, emplee la información de [`CITATION.cff`](CITATION.cff) (GitHub la muestra en "Cite this repository"). Al publicar la versión 1.0.0 se archivará en Zenodo, que asignará un DOI permanente; la tesis debe citar esa versión por su DOI.

## Licencia

Este repositorio conserva la licencia MIT de MEIGA y reconoce el copyright de su autor original. Las modificaciones y materiales propios incorporados en esta versión también se distribuyen bajo MIT. Consulte [`LICENSE`](LICENSE) y [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Autor

**Jaime A. Betancourt**
Investigación doctoral en Física, Universidad Industrial de Santander, Colombia.
