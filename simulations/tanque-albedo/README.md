# El WCD iluminado por los neutrones que suben del suelo (octubre de 2026)

Simulación directa de la curva de calibración (Sec. 4.7.8). Los neutrones que suben de cada suelo (seco y 5, 10, 15, 25
y 30 % de agua), con su energía y dirección, se inyectan en el WCD por la base y por el costado: la tasa por la base es
J↑·πR² y por el costado J↑·2RH·⟨tan θ⟩, con un corte de los cruces más rasantes en 85°. Cerca del 71 % entra por el
costado, que el plegado de incidencia vertical no ve.

| Aspecto | Valor |
|---|---|
| Detector | SaltyWCD (R = 48 cm, H = 133 cm), PMT de Sidelnik a 0.3·H/2, sin suelo en la geometría |
| Física | `QGSP_BERT_HP_NoThermal` (sin S(α,β)) |
| Neutrones | 100 000 por suelo y medio, en 4 partes; prueba de 2 000 |
| Medios | agua pura y 2.5, 5 y 10 % de NaCl (24 corridas) |
| Salida | `resultados/tanque.tsv` (ε con Q ≥ 1, 3, 5, 10 y 20 p.e., capturas, ⟨Q⟩, tiempo) y la carga por evento |

`ejecutar_tanque.sh <suelo> <medio> <prueba|completa> [partes]` y `barrido_tanque.sh <prueba|completa>`; pasos en
`LEEME.md`. Las tasas de entrada están en `flujos/entrada_tanque.json`: se calcularon con la normalización anterior de
3600 s, y `curva_calibracion_tanque.py` las reescala a 12 h. Los seis flujos de 100 000 neutrones no se versionan; se
regeneran con `analysis/suelo-humedo-calibracion_seccion-4.7/scripts/generar_entrada_tanque.py` (semilla 20261026) a
partir de las corridas del suelo, y sus sha256 están en `data/manifiestos/excluidos-v0.9.0.sha256`.
