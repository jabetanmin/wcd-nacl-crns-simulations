# Geometría y física de las campañas de simulación

Este documento fija qué geometría y qué física tiene cada conjunto de datos del WCD. Los valores
se **midieron en los propios datos de simulación** (límites entre volúmenes en los archivos de
pasos), no se tomaron de los archivos de configuración, porque el simulador lee el XML de la
carpeta de compilación y no el de `src/` (ver más abajo).

Referencia experimental: Sidelnik et al. (2020b), *Advances in Space Research* 65(9), 2216–2222,
Sec. 2, p. 2217 (tanque de 133 cm × 96 cm, acero de 0.5 mm, Tyvek de 0.12 mm).

| | Referencia (Sidelnik 2020b) | Campaña 1 original (feb. 2025) | Campaña 2 (sep. 2026) y Campaña 1 repetida |
|---|---|---|---|
| Física | — | QGSP_BERT_HP (sin S(α,β)) | QGSP_BERT_HP + S(α,β) / `QGSP_BERT_HP_NoThermal` |
| `PhysicsName` | — | (ignorado por el código de entonces) | `QGSP_BERT_HP` / `QGSP_BERT_HP_NoThermal` |
| Altura del agua | 133 cm | 133 cm | 133 cm |
| Radio del agua | 48 cm | 48 cm | 48 cm |
| Acero (tapa y pared) | 0.5 mm | **0.05 mm** | 0.50 mm |
| Revestimiento de Tyvek | 0.12 mm | 0.05 mm | 0.12 mm |
| PMT (cara plana, desde el fondo) | parte superior central | ≈ 120 cm (90 %)¹ | **86.5 cm (65 %)** |
| Código | — | commit `25093f8` | `main` |

¹ Del código (`0.8 * fTankHalfHeight` sobre el centro del tanque); los archivos de la
Campaña 1 no registran el material, así que la posición del PMT no puede medirse en ellos.

## Cómo se midió

- **Campaña 2** (`Nuevas-simulaciones-2026/25meV/<medio>/pasos-neutrones.tsv` y
  `pasos-gamma.tsv`, columna `material`): el agua llega a z = 133.062 cm y r = 48.000 cm; el
  Tyvek, a 133.074 cm y 48.012 cm; el acero, a 133.124 cm y 48.062 cm. El Pyrex del PMT ocupa
  z = 80.0–86.5 cm en los cuatro medios, incluida la corrida de agua pura del 14-09-2026, que es
  anterior a la recompilación del 15-09-2026.
- **Campaña 1** (`Neutrones-termicos/<E>/Agua-pura/interaccion-completa-neutrones.txt`): los
  pasos `Transportation` terminan en z = 1330.00, 1330.05 y 1330.10 mm y en r = 480.00 y
  480.05 mm, es decir, capas de 0.05 mm, en todas las energías revisadas.

## Qué XML usa el simulador

`DefaultProperties.h` fija la ruta
`/opt/meiga/build/Framework/ConfigManager/DetectorProperties.xml`, es decir, la **copia de la
carpeta de compilación**. CMake la sobrescribe con la de `src/` solo cuando se reconfigura el
proyecto (`file(COPY ...)` en `src/Framework/ConfigManager/CMakeLists.txt`), lo que ocurre, por
ejemplo, al modificar cualquier `CMakeLists.txt`. Por eso `src/` y `build/` deben mantener los
mismos valores. Antes de cada campaña conviene comprobar:

```bash
grep tank /opt/meiga/build/Framework/ConfigManager/DetectorProperties.xml
```

Valores esperados: `tankHeight` 133 cm, `tankRadius` 48 cm, `tankThickness` 0.5 mm.

## Decisión sobre el PMT

Se mantiene el PMT al 65 % de la altura (cara plana a 86.5 cm) para la Campaña 1 repetida, de modo
que la única diferencia con los datos existentes de la Campaña 2 sea el tratamiento térmico
S(α,β). La descripción del Capítulo 3 de la tesis se ajustó a este valor.
