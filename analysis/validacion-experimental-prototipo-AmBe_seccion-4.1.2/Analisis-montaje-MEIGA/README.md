# Simulación MEIGA del montaje con la fuente de ²⁴¹Am-Be: entrada lateral, calibración y comparación con el prototipo

Un millón de neutrones que entran **por el costado** según el modelo del blindaje (haz 35 %, halo 45 %, fondo 20 %),
en agua pura y con 2.5 y 10 % NaCl. Usa el PMT de Sidelnik en la tapa y física sin S(α,β). Las corridas están en
[`simulations/montaje-AmBe-lateral/`](../../../simulations/montaje-AmBe-lateral/) y los muones de calibración en
[`simulations/muones-VEM-agua-pura/`](../../../simulations/muones-VEM-agua-pura/). Informe:
[`informe/Informe-montaje-MEIGA.pdf`](informe/Informe-montaje-MEIGA.pdf); cuaderno: `Analisis-montaje-MEIGA.ipynb`.

## Resultados principales

- Eficiencia de señal por neutrón incidente: 17.5 % (pura), 22.7 % (2.5 %) y 29.8 % (10 %).
- Calibración con 2000 muones VEM en el mismo detector: 7.9 p.e. por cada 1000 ADC (7.0–7.2 con la corrección por
  el recorte del ADC).
- El exceso medido con la fuente es 10³–10⁴ veces lo que predice la simulación para 1 Ci, y la discrepancia no se
  resuelve con la calibración.
- Con el método de los cuadernos del prototipo (un factor horizontal y uno vertical, comunes a los tres medios), el
  montaje reproduce los tres medios dentro de un factor 2, con ≈1000 ADC/p.e. y 4.7–6.6 × 10⁶ neutrones en 300 s.
  Con la Campaña 1 (por la tapa) el factor global es 450 ADC/p.e.

## Scripts (en orden)

| Script | Qué hace |
|---|---|
| `procesar_montaje.py <corrida> <medio> [salida]` | resumen por evento (`eventos_<medio>.npz`) y verificación |
| `analizar_montaje.py`, `tablas_informe.py` | respuesta por componente y tablas del informe |
| `calibrar_vem.py <muones> [etiqueta]` | calibración p.e./ADC con muones (`calibracion_vem[_<etiqueta>].json`) |
| `calibracion_por_consistencia.py`, `comparar_con_calibracion_vem.py` | calibración por consistencia entre medios; exceso frente a la predicción absoluta |
| `ajuste_factor_comun.py` | factores horizontal y vertical comunes; con `--eventos`, `--calibracion`, `--etiqueta` y `--salida` se aplica a otras corridas |
| `ajuste_factor_comun_campana1.py` | lo mismo con la Campaña 1 (carpeta de cargas en `CARGA_CAMPANA1`) |
| `comparacion_metodo_cuaderno.py` | reproducción del cuaderno del prototipo (`SIM_CUADERNO`) |
| `respuesta_prototipo.py` | electrónica del prototipo (resolución, Q/A, recorte del ADC en 8040, disparo) y ajuste con `--k-libre` |
| `comparar_pmt_bajo.py` | prueba de 200 000 n con el PMT bajado frente al PMT en la tapa |

`eventos_{pura,nacl25,nacl10}.npz` (17–19 MB) no se versionan; se regeneran con `procesar_montaje.py` desde las corridas.
