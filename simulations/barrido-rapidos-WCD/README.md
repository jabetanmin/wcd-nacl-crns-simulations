# Barrido monoenergético del WCD de 1 keV a 1 GeV (octubre de 2026)

Neutrones monoenergéticos verticales por la tapa del WCD (agua R = 48 cm, H = 133 cm, Tyvek 0.12 mm, acero 0.5 mm,
PMT de Sidelnik a 0.3·H/2, sin suelo), uniformes en un círculo de 40 cm desde z = 200 cm. Extienden de 1 keV a 1 GeV la
eficiencia y el balance de la Campaña 1 (1 meV–1 keV) para la curva de calibración de la Sec. 4.7.

| Aspecto | Valor |
|---|---|
| Física | `QGSP_BERT_HP_NoThermal` (sin S(α,β)) |
| Energías y neutrones | 1, 10 y 100 keV, 1 y 5 MeV: 10 000; 20 MeV: 5 000; 100 MeV: 2 000; 1 GeV: 1 000 |
| Medios | agua pura y 2.5, 5 y 10 % de NaCl (`configuracion/DetectorList-<medio>.xml`) |
| Salida | `resultados/eficiencias.tsv` y, por corrida, `Carga-total.txt`, `pasos-neutrones.tsv`, capturas e incidentes |

`barrido_rapidos.sh <prueba|completa> [medios]` corre todas las energías; `correr_energia.sh` una sola. Los pasos
detallados están en `LEEME.md`. El análisis está en
[`analysis/suelo-humedo-calibracion_seccion-4.7/`](../../analysis/suelo-humedo-calibracion_seccion-4.7/)
(`balance_rapidos.py`, `captura_wcd.py`, `captura_definiciones.py`, `luz_barrido.py`, `curva_calibracion_wcd.py`).
Manifiestos de las 32 corridas: [`data/manifiestos/corridas-v0.9.0.tsv`](../../data/manifiestos/corridas-v0.9.0.tsv).
