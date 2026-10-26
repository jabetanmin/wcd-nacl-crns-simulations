# Am-Be moderado con haz horizontal y PMT bajado: respuesta y comparación con el prototipo por factores comunes

Tres corridas de 500 000 neutrones Am-Be ya frenados (10 meV – 10 eV), en un haz horizontal (r = 2 cm) que entra a
media altura, con el PMT de Sidelnik bajado a 0.3·H/2 (cara a 46.55 cm bajo la tapa), en agua pura y con 2.5 y 10 %
NaCl. Incluye 2000 muones VEM con el mismo PMT. Las corridas están en
[`simulations/AmBe-horizontal-PMT-bajo/`](../../../simulations/AmBe-horizontal-PMT-bajo/). Informe:
[`informe/Informe-PMT-bajo-horizontal.pdf`](informe/Informe-PMT-bajo-horizontal.pdf) (7 páginas); cuaderno:
`Analisis-PMT-bajo-horizontal.ipynb`.

## Resultados principales

| | Agua pura | 2.5 % NaCl | 10 % NaCl |
|---|---|---|---|
| Eficiencia Q ≥ 1 p.e. | 16.3 % | 21.2 % | 29.3 % |
| Sobre el disparo del prototipo | 1.3 % | 6.9 % | 14.6 % |
| Capturas en ³⁵Cl | 0 | 35.8 % | 67.8 % |
| τ de captura | 134 μs | 105 μs | 61 μs |

- **Factores comunes** (un k horizontal y un N vertical para los tres medios): k = 625–650 ADC/p.e. y
  N = 6.1–7.6 × 10⁶ neutrones en 300 s, con el mismo residuo que con el PMT en la tapa. El agua pura se reproduce;
  con sal la simulación es más ancha que los datos.
- **Calibración con muones**: la VEM del PMT bajado da 68–70 ADC/p.e. Se fijó de antemano que entraría al informe
  solo si mejoraba el acuerdo con los datos: k/k_μ entre 0.67 y 1.5, rms no mayor que 1.25 veces el del ajuste libre
  y al menos el 80 % de los bins con simulación. **No pasa** (k/k_μ = 9.4–9.8) y el informe no la usa. La decisión
  queda en `resultados/decision_calibracion_muones.json`.

## Reproducción

Desde esta carpeta, con `M=../Analisis-montaje-MEIGA/scripts` y las corridas en el disco (`ADATA`):

```bash
python3 $M/procesar_montaje.py <corrida pura> pura_horiz resultados        # y nacl25_horiz, nacl10_horiz
python3 $M/ajuste_factor_comun.py --eventos pura_horiz nacl25_horiz nacl10_horiz \
    --calibracion calibracion_vem_pmtbajo.json --etiqueta horizontal-PMTbajo --salida .
python3 $M/respuesta_prototipo.py --muones <muones PMT bajado> --medio pura resultados/eventos_pura_horiz.npz \
    --medio 2.5 resultados/eventos_nacl25_horiz.npz --medio 10 resultados/eventos_nacl10_horiz.npz \
    --etiqueta horizontal-PMTbajo --k-libre --sin-panel-muones --salida .
python3 scripts/decidir_calibracion_muones.py
python3 scripts/analizar_horizontal_pmtbajo.py
```

El cuaderno hace lo mismo. `eventos_*_horiz.npz` (9–10 MB) no se versionan.
