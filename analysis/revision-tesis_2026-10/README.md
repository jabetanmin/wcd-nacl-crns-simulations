# Revisión de contenido de la tesis (octubre de 2026)

Scripts que respaldan las correcciones numéricas hechas en la tesis durante la revisión del 2 al 4 de
octubre de 2026. Cada script recibe las carpetas de datos como argumentos; las salidas de verificación
están en [`salidas_verificacion/`](salidas_verificacion/) y los productos del balance en
[`resultados_balance/`](resultados_balance/).

| Tesis | Corrección | Script |
|---|---|---|
| Tabla 3.2 | θw recalculado con las Ecs. 3.7–3.8 (0.1244, 0.2308, 0.3227, 0.4737, 0.5364) | `calculos_tablas_3_2_4_13_4_18.py` |
| Tabla 4.8, Figs. 4.25–4.26, Tablas C.3–C.5 | Balance de destinos por caras del volumen activo, con cuatro categorías: captura, reflexión (tapa), transmisión (fondo y laterales) y otros (no ingreso y reacción inelástica). La versión anterior clasificaba por la cara de la caja del mundo de Geant4. | `balance_caras_tanque.py` |
| Tabla 4.13 | μ/ρ con coeficientes de NIST, concentración como fracción en masa de la solución (como en `SaltyWCD.cc`) y masas de la Tabla 4.7 | `calculos_tablas_3_2_4_13_4_18.py` |
| Tabla 4.16 | Porcentaje de conversión de pares: el denominador es N_Int(γ_Tanque); seis celdas estaban truncadas | `conversion_pares.py` |
| Cap. 4 (líneas del Na), Apéndice E | 1.37 y 2.75 MeV proceden del decaimiento β⁻ del ²⁴Na; las líneas de captura del Na son 472 keV y 3.98 MeV. Entre 6 y 7 MeV dominan las líneas de captura del ³⁵Cl | `origen_lineas_gamma.py` |
| Tablas 4.18 y 4.19 | El máximo del espectro Cherenkov está en 0.2641 MeV en los cuatro medios (los archivos de NaCl del notebook original estaban desplazados); fila de 10 meV de la Tabla 4.19 corregida | `umbral_cherenkov.py`, `calculos_tablas_3_2_4_13_4_18.py` |
| Secs. 4.3 y 4.4 | Normalización de ARTI: el archivo de la Sec. 4.4 es de 3600 s en el nivel de inyección; el flujo completo de 12 h en la superficie es coherente con la atenuación en el bloque atmosférico de 2000 m | `normalizacion_ARTI.py` |

## Datos de entrada

| Script | Datos |
|---|---|
| `balance_caras_tanque.py` | `Neutrones-termicos/<energía>/<medio>/interaccion-completa-neutrones.txt` (Campaña 1, malla de 16 energías) |
| `origen_lineas_gamma.py`, `conversion_pares.py` | `Gammas/<energía>/<medio>/gamma-completo-*.txt` (Campaña 1) |
| `umbral_cherenkov.py` | `Cherenkov/<energía>/<medio>/procesos_filtrados/Cerenkov/Cerenkov.txt` (Campaña 1) |
| `normalizacion_ARTI.py` | `S3_bga_003600_neutrons.shw` (ARTI), `all_bga_neutron_35.shw` (flujo completo), `salida_bga_30.shw` (muestra de MEIGA, opcional) |

Los datos no se incluyen en git por su tamaño (véase [`docs/DATA_MANAGEMENT.md`](../../docs/DATA_MANAGEMENT.md)).

## Notas

- La carpeta `1000000meV` de la Campaña 1 se rotula «1 keV» en la tesis por decisión del autor.
- En la columna de agua pura de la Tabla 4.19, `umbral_cherenkov.py` difiere de la tesis en 1 a 6
  electrones de 40 000–90 000 (≤ 0.01 %) por el tratamiento de los bordes de la ventana en el notebook
  original; las columnas con NaCl coinciden exactamente.
- La reconstrucción del balance de la Tabla 4.8 reproduce las 64 filas de la tesis.
