# Campaña 2 (25 meV, con S(α,β)): notebooks de moderación y captura

Notebooks de la **Campaña 2** de simulación: neutrones de 25 meV, `QGSP_BERT_HP` con S(α,β), 10⁵ neutrones por medio,
inyectados verticalmente desde z = 200 cm. No mezclar sus cifras con las de la Campaña 1 sin leer antes
[`../../README.md`](../../README.md) (sección "Dos campañas de simulación").

Informes técnicos: [`docs/technical-reports/campana-2_con-S-alpha-beta_25meV/`](../../../docs/technical-reports/campana-2_con-S-alpha-beta_25meV/).

| Archivo | Contenido |
|---|---|
| `analisis_moderacion_captura_neutrones__agua-pura.ipynb` | Moderación y captura en agua pura |
| `analisis_moderacion_captura_neutrones__agua-2.5pct-nacl.ipynb` | Ídem, agua + 2.5 % NaCl |
| `analisis_moderacion_captura_neutrones__agua-5pct-nacl.ipynb` | Ídem, agua + 5 % NaCl |
| `build_notebook_moderacion_captura.py` | Genera los tres notebooks anteriores para un medio dado |
| `Estructura-archivos-simulacion.ipynb` | Estructura de los archivos de salida y comparación de colisiones elásticas; usa rutas absolutas del equipo del autor |

## Datos de entrada

Cada notebook se ejecuta desde la carpeta de la corrida (`Nuevas-simulaciones-2026/25meV/<medio>/`, fuera del
repositorio), que contiene `capturas-neutrones.tsv`, `neutrones-incidentes.tsv`, `pasos-neutrones.tsv` e
`interacciones-neutrones.tsv`. Las salidas se escriben en `Salidas/` dentro de esa carpeta.

## Cómo regenerar un notebook

```bash
python3 build_notebook_moderacion_captura.py "Agua + 5% NaCl" "1:H,8:O,11:Na,17:Cl" \
  analisis_moderacion_captura_neutrones__agua-5pct-nacl.ipynb
```

El segundo argumento lista los núcleos del medio (`"1:H,8:O"` para agua pura).
