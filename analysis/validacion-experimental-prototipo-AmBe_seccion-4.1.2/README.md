# Sección 4.1.2 — Validación experimental con un prototipo de WCD y una fuente de ²⁴¹AmBe

Análisis de las medidas del Centro Atómico Bariloche con un prototipo de detector Cherenkov de agua
irradiado con una fuente de ²⁴¹AmBe, con agua pura y soluciones de NaCl al 2.5 % y al 10 % en masa,
y su comparación con la simulación.

## Correspondencia con la tesis

| Elemento de la tesis (Sección 4.1.2) | Archivo | Producido por |
|---|---|---|
| Figura `Muestra-pulsos-fondo-AP` (pulsos de fondo, agua pura) | `figuras/Muestra-pulsos-fondo-AP.png` | `notebooks/señales-detector-prototipo.ipynb` |
| Figura `Comparacion-3-configuraciones-bins9425` | `figuras/Comparacion-3-configuraciones-bins9425.pdf` | `notebooks/señales-detector-prototipo.ipynb` |
| Figuras `Histograma-Comparado-*-mejorado` (neutrones frente a fondo, tres medios) | `figuras/Histograma-Comparado-Agua-{pura,25NaCl,10NaCl}-mejorado.pdf` | `notebooks/señales-detector-prototipo.ipynb` |
| Figura `compara-sim-exp` (espectros experimentales y simulados) | `figuras/Comparacion-Exp-vs-Sim-Termicos.pdf` | `notebooks/comparacion-experimento-simulacion.ipynb` |
| Tabla `tab:signal_comparison` (razones de mejora 11.2 y 35.6; simulación 13.2 y 31.8) | — | **No trazable todavía** (ver más abajo) |
| Figura `Espectro-AmBe-Geant4-vs-IAEA` | — | No está en esta carpeta de origen |

Las figuras de la tesis que muestran el montaje (`tanque-exp`, `blindaje-plomo`, esquema experimental)
son fotografías o diagramas, no productos de análisis.

## Contenido

| Carpeta | Contenido |
|---|---|
| `notebooks/` | `señales-detector-prototipo.ipynb`: lectura de los datos crudos, pulsos, histogramas de carga y comparación neutrones–fondo para los tres medios. `comparacion-experimento-simulacion.ipynb` (originalmente `Nuevo-analisis/analisis-datos-termicos-Bga.ipynb`): comparación de los espectros experimentales con los simulados. Ambos se conservan con sus salidas, porque los datos crudos no están en el repositorio. |
| `datos-derivados/histogramas-carga/` | Histogramas de carga (ADU) de las seis tomas: `{pura,2.5,10}_{neutrones,fondo}_charge_hist.csv`. |
| `datos-derivados/simulacion/` | Fotones Cherenkov simulados por evento (`counts-number-photons*.txt`), histogramas comparados y los archivos de la comparación preliminar (`sim_phot_*`, `exp_adc_*`). |
| `figuras/` | Figuras de la tesis producidas por los notebooks. |
| `datos-crudos.sha256` | Sumas SHA-256 de los seis archivos de datos crudos. |

## Datos crudos (no incluidos en git)

Seis archivos en el formato de datos crudos de LAGO, versión 5 (una línea por pulso con los dos
canales ADC, y marcas de disparo, reloj de 125 MHz y registros del equipo):

| Archivo | Tamaño | Toma |
|---|---|---|
| `pura_neutrones.dat` / `pura_fondo.dat` | 231 MB / 51 MB | agua pura, con y sin fuente |
| `2.5_neutrones.dat` / `2.5_fondo.dat` | 451 MB / 47 MB | 2.5 % de NaCl |
| `10_neutrones.dat` / `10_fondo.dat` | 1022 MB / 76 MB | 10 % de NaCl |

Registros del equipo en la cabecera: umbral de disparo T1 = 800, alta tensión del canal 1
1492.7 mV; sin GPS (la hora local registrada no es válida). Copia de trabajo en el disco externo
del autor, `Archivos-tramites/Detector-prototipo-PC/`. Deben publicarse en un repositorio de datos
con identificador persistente (ver [`docs/DATA_MANAGEMENT.md`](../../docs/DATA_MANAGEMENT.md));
`datos-crudos.sha256` permite verificar la copia publicada.

Para ejecutar `señales-detector-prototipo.ipynb`, los archivos `.dat` deben estar en la misma carpeta
que el notebook. `comparacion-experimento-simulacion.ipynb` usa los histogramas de carga y los
archivos de `datos-derivados/`, que deben copiarse junto a él.

## Pendiente de trazabilidad

- **Razones de la Tabla `tab:signal_comparison`.** Ningún notebook de la carpeta de origen calcula
  11.2 ± 0.1 y 35.6 ± 0.2 (experimento) ni 13.2 y 31.8 (simulación). No se reproducen con la suma de
  fotones simulados (2.80 y 5.51), ni con las cuentas o la carga netas sin normalizar por el tiempo de
  adquisición. Debe identificarse su origen (cálculo propio, grupo de Bariloche) y añadirse aquí el
  programa que las produce. Además, los errores relativos de la tabla (17.6 % y 10.6 %) no coinciden
  exactamente con los valores redondeados (17.9 % y 10.7 %).
- **Tiempos de adquisición.** No se encontraron registrados; son necesarios para normalizar las tomas
  con y sin fuente.

## Notebooks de la carpeta de origen no incluidos

Son versiones anteriores o derivadas de los dos notebooks incluidos:
`process/results/analisis-datos.ipynb` (diciembre de 2025),
`Comparacion-experimento-simulacion/Comparacion-datos-simulacion.ipynb` (diciembre de 2025),
`Comparacion-tres-configuraciones/Extraccion-pendientes.ipynb` (julio de 2026) y
`Nuevo-analisis/analisis-datos-Flujo-Completo-Bga.ipynb` (comparación con el flujo atmosférico, julio
de 2026).
