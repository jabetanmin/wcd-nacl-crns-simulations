# Auditoría inicial de `Meiga-Jaime-Betancourt.zip`

## Identificación

- Rama activa: `dev_meiga`.
- Commit base: `39b950ee4ceeb1164bd8fa6d58d0f57ddcf0dbbc`.
- Archivos versionados modificados: 18.
- Balance preliminar del diff: 1077 líneas añadidas y 152 eliminadas.

## Material identificado

La carpeta contiene:

- el repositorio Git de MEIGA;
- cambios locales sobre archivos C++, cabeceras, XML y un script de generación;
- numerosos archivos de flujo neutrónico sin seguimiento por Git;
- un directorio de compilación completo;
- un archivo `src.zip` interno;
- una copia adicional denominada `src (1)`;
- archivos con nombres accidentales que deben revisarse.

## Criterio de importación

Se incorporarán gradualmente:

1. cambios versionados cuya función pueda documentarse;
2. archivos nuevos necesarios para compilar o reproducir el estudio;
3. configuraciones y muestras pequeñas de flujo con procedencia conocida;
4. programas Python empleados en los análisis finales.

No se incorporarán directamente:

- `build/` ni ejecutables compilados;
- objetos `.o`, cachés de CMake o archivos temporales;
- copias redundantes como `src (1)` y `src.zip`;
- todos los flujos de producción sin una selección y descripción previa;
- archivos con nombres aparentemente accidentales.

## Incorporaciones posteriores

Es válido añadir nuevos archivos en etapas posteriores. Cada grupo deberá registrarse mediante un commit separado y actualizar `docs/CONTRIBUTIONS.md` y `CHANGELOG.md`.
