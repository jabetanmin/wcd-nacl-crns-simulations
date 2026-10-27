# Apéndices de la tesis — dónde está cada uno en el repositorio

Mapa de los once apéndices de la tesis (A–K, numeración de la versión del 26 de octubre de 2026) a los archivos que
los producen o los respaldan. Los apéndices que dependen de una sección del Capítulo 4 se generan con el material de
esa sección; esta carpeta solo agrega lo que no tenía lugar en otra parte (el cálculo del Apéndice B).

| Apéndice | Título | Repositorio |
|---|---|---|
| A | Framework MEIGA | [`docs/MEIGA_UPSTREAM_README.md`](../../docs/MEIGA_UPSTREAM_README.md), [`docs/UPSTREAM.md`](../../docs/UPSTREAM.md); configuración de ejemplo en [`src/Applications/G4WCDSimulator/`](../../src/Applications/G4WCDSimulator/) |
| B | Número de átomos de hidrógeno en 1 m³ de agua al agregar sal | [`scripts/apendice_B_atomos_hidrogeno.py`](scripts/apendice_B_atomos_hidrogeno.py) → [`resultados/apendice_B_atomos_hidrogeno.txt`](resultados/apendice_B_atomos_hidrogeno.txt) |
| C | Síntesis de las incertidumbres del modelo Monte Carlo; coeficientes de captura, reflexión, transmisión y otros con incertidumbres (Tablas C.3–C.5) | [`analysis/revision-tesis_2026-10/`](../revision-tesis_2026-10/) (`balance_caras_tanque.py`, `resultados_balance/balance_caras_tanque.tsv`); informe de la Campaña 1 en [`analysis/campana-1_neutrones-monoenergeticos_seccion-4.2/`](../campana-1_neutrones-monoenergeticos_seccion-4.2/) |
| D | Distribuciones normalizadas del número de dispersiones elásticas en agua con NaCl (Figs. D.1–D.6) | [`analysis/campana-1_neutrones-monoenergeticos_seccion-4.2/`](../campana-1_neutrones-monoenergeticos_seccion-4.2/) (`figuras_seccion_4.2.ipynb`; figuras `fig_D_*`) |
| E | Procesos físicos inducidos por los electrones secundarios (Tabla E.1) | [`analysis/campana-1_respuesta-electromagnetica_seccion-4.2/`](../campana-1_respuesta-electromagnetica_seccion-4.2/) (`procesar_electrones.py`, `verificar_tesis_electrones.py`); líneas del Na en [`analysis/revision-tesis_2026-10/`](../revision-tesis_2026-10/) |
| F | Distribución espacial de la captura en el WCD con el flujo de neutrones rápidos y de alta energía | [`analysis/flujo-bucaramanga_secciones-4.3-4.5/notebooks/4.4_flujo-rapido-alta-energia/distribucion-espacial/`](../flujo-bucaramanga_secciones-4.3-4.5/notebooks/4.4_flujo-rapido-alta-energia/distribucion-espacial/) (un notebook por medio) |
| G | Distribución espacial de la captura en el WCD con el flujo de un suelo seco (ventana de 10 meV a 10 eV) | [`analysis/flujo-bucaramanga_secciones-4.3-4.5/notebooks/4.5_suelo-seco/`](../flujo-bucaramanga_secciones-4.3-4.5/notebooks/4.5_suelo-seco/) (`Histogramas-coordenada.ipynb`) |
| H | Ecuaciones, energías y porcentajes de los procesos de los neutrones de 500 MeV | [`analysis/replica-Sidelnik-MEIGA_seccion-4.1.1/`](../replica-Sidelnik-MEIGA_seccion-4.1.1/) (`informe/apendice_procesos.tex`, fuente común con la tesis, y los scripts que lo generan) |
| I | Coeficientes de captura, reflexión y transmisión de 1 meV a 1 GeV (cuatro medios) | [`analysis/suelo-humedo-calibracion_seccion-4.7/`](../suelo-humedo-calibracion_seccion-4.7/) (`scripts/balance_rapidos.py`, `scripts/captura_wcd.py` → `informe/tablas/balance_*.tex`) |
| J | Procesos de los neutrones en el suelo según la humedad | [`analysis/suelo-humedo-calibracion_seccion-4.7/`](../suelo-humedo-calibracion_seccion-4.7/) (`scripts/procesos_neutrones.py` → `informe/tablas/{procesos,destino,creados,capturas,origen}.tex`) |
| K | Actividades desarrolladas durante el doctorado y aportes de la investigación; contribuciones computacionales a MEIGA | [`docs/CONTRIBUTIONS.md`](../../docs/CONTRIBUTIONS.md); diferencias de código en [`docs/technical-reports/diffs/`](../../docs/technical-reports/diffs/) y parches del contenedor en [`docs/ESTADO_MEIGA_CONTENEDOR.md`](../../docs/ESTADO_MEIGA_CONTENEDOR.md) |

## Apéndice B

```bash
python3 analysis/apendices-tesis/scripts/apendice_B_atomos_hidrogeno.py
```

Como en la tesis, se toman 1000 kg de solución para los cuatro medios. Con una fracción en masa f de NaCl quedan
1000 (1 − f) kg de agua, y la reducción relativa de átomos de hidrógeno es exactamente f (2.50, 5.00 y 10.00 %). El
script reproduce las cifras del apéndice; la tesis redondea hacia arriba el último dígito de n_H₂O (5.55085×10⁴ mol
frente a 5.55084×10⁴). Por volumen, la solución salina es algo más densa que el agua, de modo que 1 m³ contiene un
poco más de 1000 kg; el apéndice no corrige por densidad.
