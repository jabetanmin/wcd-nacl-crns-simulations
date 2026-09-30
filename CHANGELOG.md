# Historial de cambios

Todas las modificaciones relevantes del repositorio se documentarán en este archivo.

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
