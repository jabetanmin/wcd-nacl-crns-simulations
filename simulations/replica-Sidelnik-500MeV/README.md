# Réplica de Sidelnik et al. (2020) con MEIGA — neutrones de 500 MeV, cuatro medios (Sección 4.1.1)

Configuración y scripts de las corridas de MEIGA de octubre de 2026 con las que se hizo la validación numérica
de la Sección 4.1.1 de la tesis (reproducción de Sidelnik et al., *Adv. Space Res.* **65** (2020) 2216).
El análisis y el informe están en
[`analysis/replica-Sidelnik-MEIGA_seccion-4.1.1/`](../../analysis/replica-Sidelnik-MEIGA_seccion-4.1.1/).
Las salidas de las corridas (124–166 GB por medio) no se guardan en el repositorio.

## Configuración común

| Parámetro | Valor | Dónde se fija |
|---|---|---|
| Tanque | agua R = 48 cm, H = 133 cm; Tyvek 0.12 mm; acero inoxidable 0.5 mm (lados, tapa y fondo) | `DetectorList.xml` + `SaltyWCD.cc` |
| Neutrones | 150 000 de 500 MeV, horizontales (+x), a media altura z = 66.562 cm, desde x = −49.062 cm (1 cm fuera de la pared) | `generar_flujo.py` + `DetectorList.xml` |
| PMT | en la tapa (cara plana 0.1 mm bajo el agua), semielipsoide 10.16 × 10.16 × 5 cm, eficiencia cuántica del R5912 | `ajustar_pmt_sidelnik.py` (reversible con `--revertir`) |
| Física | Geant4 10.7.p04, `QGSP_BERT_HP_NoThermal`: sin S(α,β), H como gas libre (física de la Campaña 1); G4NDL 4.6 | `PhysicsName` en el JSON |
| Óptica | modo `eFast`: la eficiencia cuántica se aplica al crearse cada fotón; Tyvek con el modelo de MEIGA sin cambios | `SimulationMode` en el JSON |

Solo cambia `impuritiesFraction` en `DetectorList.xml`. La fracción másica es la de la solución final (Ec. 3.12 de
la tesis); la densidad y el índice de refracción son los de la Tabla 3.6, ya definidos en `Materials.cc`.

| Medio | w_NaCl | Material MEIGA | Densidad (g/cm³) | n a 589.3 nm |
|---|---|---|---|---|
| `agua-pura` | 0 | `Water_TS_H_of_Water` | 0.99820 | 1.3330 |
| `nacl-2.5` | 0.025 | `SaltyWater_NaCl_2.5pct` | 1.01604 | 1.3397 |
| `nacl-5` | 0.050 | `SaltyWater_NaCl_5.0pct` | 1.03401 | 1.3436 |
| `nacl-10` | 0.100 | `SaltyWater_NaCl_10.0pct` | 1.07051 | 1.3594 |

## Corridas realizadas

Ejecutadas en el contenedor Docker de MEIGA (código en `/opt/meiga/src`). La configuración exacta de cada corrida,
copiada de su carpeta de salida, está en [`corridas-realizadas/`](corridas-realizadas/).

| Medio | Carpeta de salida | Neutrones | Tamaño | Tiempo |
|---|---|---|---|---|
| Agua pura | `150000N-500MeV-Sidelnik-H2O-pura-sinSab-20261012-061022` | 150 000 | 124 GB | 20.2 h |
| Agua + 2.5 % NaCl | `42649N-parcial-500MeV-Sidelnik-H2O-2.5NaCl-sinSab-20261013` (interrumpida al detenerse el contenedor; se usan los 42 649 neutrones terminados) + `107351N-500MeV-Sidelnik-H2O-2.5NaCl-sinSab-20261013-135213` (complemento con otra semilla y un archivo de flujo de 107 351 neutrones) | 150 000 | 43 + 108 GB | 16.6 h (complemento) |
| Agua + 5 % NaCl | `150000N-500MeV-Sidelnik-H2O-5NaCl-sinSab-20261014-065724` | 150 000 | 162 GB | 24.4 h |
| Agua + 10 % NaCl | `150000N-500MeV-Sidelnik-H2O-10NaCl-sinSab-20261015-081303` | 150 000 | 166 GB | 26.8 h |

Los dos tramos de 2.5 % se unen en el análisis con `unir_tramos.py` (los números de evento del complemento se
desplazan en 42 649). MEIGA lanza cada neutrón como una corrida aparte (`run_id` = 0…N−1, `event_id` = 0): en el
análisis el neutrón se identifica por `run_id`.

## Uso

```bash
python3 generar_flujo.py                      # 150000N-500MeV-Sidelnik.txt y 10N-500MeV-Sidelnik.txt (formato ARTI)
python3 ajustar_pmt_sidelnik.py /opt/meiga/src   # PMT de Sidelnik; recompilar MEIGA
./ejecutar_corrida.sh agua-pura prueba        # 10 neutrones + verificar_prueba.py (física, material, geometría, fuente, PMT)
./ejecutar_corrida.sh agua-pura completa      # 150 000 neutrones (necesita ≥ 250 GB libres)
python3 ajustar_pmt_sidelnik.py /opt/meiga/src --revertir   # al terminar
```

`desactivar_termico.py` no fue necesario: el MEIGA del contenedor ya ofrece `QGSP_BERT_HP_NoThermal`.
Para el complemento de 2.5 % se generó un flujo de 107 351 neutrones con las primeras líneas del archivo de 150 000.
El archivo de flujo de 150 000 neutrones (6.3 MB) se regenera con `generar_flujo.py` y no se versiona.
