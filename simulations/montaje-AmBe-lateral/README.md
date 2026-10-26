# Montaje Am-Be lateral (octubre de 2026) — Sec. 4.1.2

Un millón de neutrones de la fuente de ²⁴¹Am-Be que entran por el costado del tanque, según el modelo del blindaje:
haz directo 35 % (ISO 8529, cono de 2.86° desde la fuente), halo difuso 45 % (0.5 eV – 100 keV, 1/E, ley del coseno
desde la cara del plomo) y fondo hemisférico 20 % (maxwelliano de kT = 25.3 meV). Se usó el mismo archivo de entrada en
los tres medios. Análisis:
[`analysis/validacion-experimental-prototipo-AmBe_seccion-4.1.2/Analisis-montaje-MEIGA/`](../../analysis/validacion-experimental-prototipo-AmBe_seccion-4.1.2/Analisis-montaje-MEIGA/).

| | |
|---|---|
| Código | `src/` + parche 1 (PMT de Sidelnik en la tapa) de [`docs/ESTADO_MEIGA_CONTENEDOR.md`](../../docs/ESTADO_MEIGA_CONTENEDOR.md); `ejecutar_corrida.sh` se niega a correr con otro PMT |
| Geant4 / física | 10.7.4, `QGSP_BERT_HP_NoThermal` (sin S(α,β)), `eFast` |
| Detector | SaltyWCD: agua R = 48 cm, H = 133 cm; Tyvek 0.12 mm (reflectividad × 0.94); acero 0.5 mm |
| Medios | [`agua-pura/`](agua-pura/), [`nacl-2.5/`](nacl-2.5/), [`nacl-10/`](nacl-10/) (`impuritiesFraction` en `configuracion/<medio>/DetectorList.xml`) |
| Corridas | 2026-10-21; 10 463 s (pura), 12 918 s (2.5 %), ≈16 900 s (10 %); 62, 102 y 150 GB. Manifiestos en [`data/manifiestos/corridas-v0.8.0.tsv`](../../data/manifiestos/corridas-v0.8.0.tsv) |

Cada carpeta es el paquete que se copió al contenedor; las instrucciones están en su `LEEME.md`.

## Archivo de entrada (no versionado)

`flujos/1000000N-AmBe-montaje-haz-halo-fondo.txt` (78 MB) y su `-componentes.txt` se regeneran byte a byte. El comando,
desde `analysis/…_seccion-4.1.2/Analisis-fuente-AmBe/`, es:

```bash
python3 scripts/generar_irradiacion_compuesta.py --N-total 1000000 --semilla 20261021 --salida <paquete>/flujos
```

La salida debe coincidir con el sha256 de [`data/manifiestos/flujos-regenerables.sha256`](../../data/manifiestos/flujos-regenerables.sha256).
