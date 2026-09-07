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

**Versión de trabajo (`v0.2.0`).** Los 18 archivos versionados modificados en la carpeta recibida ya fueron aplicados sobre una copia limpia de la rama `dev_meiga`, commit `39b950e`, y organizados en cinco commits funcionales. Permanecen pendientes los programas finales de análisis, las configuraciones adicionales y una selección documentada de los archivos de flujo.

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
├── analysis/             Programas Python y cuadernos de análisis
├── simulations/          Configuraciones de las campañas de simulación
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

- Rama de desarrollo: `thesis-wcd-nacl`.
- Punto de partida: etiqueta `meiga-base-39b950e`.
- Repositorio original: <https://github.com/ataboadanunez/meiga>.
- README original preservado en [`docs/MEIGA_UPSTREAM_README.md`](docs/MEIGA_UPSTREAM_README.md).
- Auditoría de la carpeta recibida: [`docs/IMPORT_AUDIT.md`](docs/IMPORT_AUDIT.md).

## Datos

El repositorio no debe contener resultados masivos, archivos de compilación ni datos que puedan regenerarse fácilmente. Se incluirán datos pequeños de ejemplo y productos procesados esenciales. Los conjuntos grandes deberán publicarse por separado y enlazarse mediante un identificador persistente.

Consulte [`docs/DATA_MANAGEMENT.md`](docs/DATA_MANAGEMENT.md).

## Citación

Cuando utilice este repositorio, emplee la información de [`CITATION.cff`](CITATION.cff). La referencia definitiva se completará al publicar la primera versión estable.

## Licencia

Este repositorio conserva la licencia MIT de MEIGA y reconoce el copyright de su autor original. Las modificaciones y materiales propios incorporados en esta versión también se distribuyen bajo MIT. Consulte [`LICENSE`](LICENSE) y [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## Autor

**Jaime A. Betancourt**
Investigación doctoral en Física, Universidad Industrial de Santander, Colombia.
