# Campañas de simulación

Cada campaña tiene su propio directorio con la configuración, los scripts de corrida y un README
que registra el propósito, la geometría, la física, la fuente, el número de eventos, el entorno y
las fechas de ejecución. Las salidas de las corridas no se almacenan aquí (ver
[`docs/DATA_MANAGEMENT.md`](../docs/DATA_MANAGEMENT.md)).

| Campaña | Física | Estado en este directorio |
|---|---|---|
| Campaña 1 (febrero de 2025): neutrones monocromáticos de 1 meV a 10 keV, cuatro medios | QGSP_BERT_HP, sin S(α,β) | Código en la etiqueta `campana-1-QGSP_BERT_HP`; configuraciones por corrida pendientes |
| Campaña 2 (septiembre de 2026): 25 meV, cuatro medios | QGSP_BERT_HP + S(α,β) | Código en la etiqueta `campana-2-QGSP_BERT_HP-SalphaBeta`; configuraciones pendientes |
| [`barrido-SalphaBeta_1meV-1keV/`](barrido-SalphaBeta_1meV-1keV/) (septiembre de 2026): agua pura, 16 energías | ambas | Completo |
| Flujo atmosférico y suelo seco (Bucaramanga) | QGSP_BERT_HP | Flujos de entrada documentados en [`analysis/flujo-bucaramanga_secciones-4.3-4.5/`](../analysis/flujo-bucaramanga_secciones-4.3-4.5/) |
| Validación con AmBe | — | Pendiente |

La geometría y la física de cada campaña, medidas en sus propios datos, están en
[`docs/GEOMETRIA_Y_FISICA_CAMPANAS.md`](../docs/GEOMETRIA_Y_FISICA_CAMPANAS.md). La plantilla para
documentar una campaña nueva es [`CAMPAIGN_TEMPLATE.md`](CAMPAIGN_TEMPLATE.md).
