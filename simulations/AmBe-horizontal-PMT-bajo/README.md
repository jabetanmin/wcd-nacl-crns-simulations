# Am-Be moderado, haz horizontal, PMT bajado (octubre de 2026) — Sec. 4.1.2

500 000 neutrones por medio con el espectro Am-Be ya frenado en agua (10 meV – 10 eV: maxwelliano de kT = 25.3 meV
más una cola 1/E). El haz es horizontal (+x), en un disco de 2 cm de radio a media altura (z = 66.56 cm), a 1 mm de la
pared. Los medios son agua pura y 2.5 y 10 % NaCl. Incluye 2000 muones VEM con el mismo PMT. Análisis:
[`analysis/…_seccion-4.1.2/Analisis-PMT-bajo-horizontal/`](../../analysis/validacion-experimental-prototipo-AmBe_seccion-4.1.2/Analisis-PMT-bajo-horizontal/).

| | |
|---|---|
| Código | `src/` + parches 1 y 2 de [`docs/ESTADO_MEIGA_CONTENEDOR.md`](../../docs/ESTADO_MEIGA_CONTENEDOR.md): forma de Sidelnik y `zPMT = 0.3*fWaterHalfHeight` (`bajar_pmt.py`, reversible) |
| Física | `QGSP_BERT_HP_NoThermal` (sin S(α,β)), `eFast` |
| Orden | `preparar_meiga.sh bajar` (bajar el PMT y recompilar), `ejecutar_muones.sh`, y luego `ejecutar_corrida.sh <medio> completa`; `lanzar_neutrones_tras_muones.sh` encadena los neutrones al terminar los muones |
| Corridas | 2026-10-23; 23, 39 y 61 GB; muones 51 GB. Manifiestos en [`data/manifiestos/corridas-v0.8.0.tsv`](../../data/manifiestos/corridas-v0.8.0.tsv) |

Las instrucciones están en `LEEME.md`. El archivo de 500 000 neutrones (39 MB) y el de 50 000 no se versionan. Se
regeneran byte a byte desde `analysis/…_seccion-4.1.2/Analisis-fuente-AmBe/` con:

```bash
python3 scripts/generar_ambe_moderado.py resultados/AmBe-moderado-MEIGA/flujo_pura.tsv --N 500000 --semilla 20261025 \
    --horizontal --radio-haz 2 --salida <paquete>/flujos
```
