# Campañas de simulación

Cada campaña tiene su propio directorio con la configuración, los scripts de corrida y un README
que registra el propósito, la geometría, la física, la fuente, el número de eventos, el entorno y
las fechas de ejecución. Las salidas de las corridas no se almacenan aquí (ver
[`docs/DATA_MANAGEMENT.md`](../docs/DATA_MANAGEMENT.md)).

| Campaña | Física | Estado en este directorio |
|---|---|---|
| Campaña 1 (febrero de 2025): neutrones monocromáticos de 1 meV a 1 keV (16 energías), cuatro medios | QGSP_BERT_HP, sin S(α,β) | Código en la etiqueta `campana-1-QGSP_BERT_HP`; configuraciones por corrida pendientes |
| Campaña 2 (septiembre de 2026): 25 meV, cuatro medios | QGSP_BERT_HP + S(α,β) | Código en la etiqueta `campana-2-QGSP_BERT_HP-SalphaBeta`; configuraciones pendientes |
| [`barrido-SalphaBeta_1meV-1keV/`](barrido-SalphaBeta_1meV-1keV/) (septiembre de 2026): agua pura y NaCl al 2.5, 5 y 10 %, 16 energías | ambas | Completo |
| [`replica-Sidelnik-500MeV/`](replica-Sidelnik-500MeV/) (octubre de 2026): réplica de Sidelnik et al. (2020), 150 000 neutrones de 500 MeV, cuatro medios (Sec. 4.1.1) | QGSP_BERT_HP, sin S(α,β) | Completo |
| Flujo atmosférico y suelo seco (Bucaramanga) | QGSP_BERT_HP | Flujos de entrada documentados en [`analysis/flujo-bucaramanga_secciones-4.3-4.5/`](../analysis/flujo-bucaramanga_secciones-4.3-4.5/) |
| [`montaje-AmBe-lateral/`](montaje-AmBe-lateral/) (octubre de 2026): fuente ²⁴¹AmBe por el costado (haz, halo y fondo), 10⁶ neutrones, tres medios, PMT en la tapa (Sec. 4.1.2) | QGSP_BERT_HP, sin S(α,β) | Completo |
| [`muones-VEM-agua-pura/`](muones-VEM-agua-pura/) (octubre de 2026): 2000 muones VEM, PMT en la tapa (calibración) | QGSP_BERT_HP, sin S(α,β) | Completo |
| [`AmBe-horizontal-PMT-bajo/`](AmBe-horizontal-PMT-bajo/) (octubre de 2026): Am-Be moderado, haz horizontal, 5×10⁵ neutrones, tres medios y muones VEM, PMT bajado | QGSP_BERT_HP, sin S(α,β) | Completo |
| [`suelo-SoilBS/`](suelo-SoilBS/) (octubre de 2026): parche de MEIGA con el suelo SoilBS seco o húmedo | — | Completo |
| [`albedo-suelo/`](albedo-suelo/) (octubre de 2026): albedo del suelo SoilBS con 5–30 % de agua, sin tanque | QGSP_BERT_HP, sin S(α,β) | Completo (seco y 5, 10, 15, 25 y 30 %) |
| [`barrido-rapidos-WCD/`](barrido-rapidos-WCD/) (octubre de 2026): neutrones monoenergéticos de 1 keV a 1 GeV (8 energías) por la tapa, cuatro medios (Sec. 4.7) | QGSP_BERT_HP_NoThermal | Completo |
| [`tanque-albedo/`](tanque-albedo/) (octubre de 2026): los neutrones que suben de cada suelo, inyectados en el WCD por la base y el costado, 10⁵ por suelo, cuatro medios, PMT a 0.3·H/2 (Sec. 4.7.8) | QGSP_BERT_HP_NoThermal | Completo |

La geometría y la física de cada campaña, medidas en sus propios datos, están en
[`docs/GEOMETRIA_Y_FISICA_CAMPANAS.md`](../docs/GEOMETRIA_Y_FISICA_CAMPANAS.md). La plantilla para
documentar una campaña nueva es [`CAMPAIGN_TEMPLATE.md`](CAMPAIGN_TEMPLATE.md).
