# Barrido rápido de eficiencia del WCD: neutrones de 1 keV a 1 GeV

**Para qué:** la curva de calibración de humedad se obtiene plegando los espectros del suelo (seco, 5, 10, 15, 25 y
30 % de agua) con la eficiencia del WCD por energía, ε(E): cuentas = Σ flujo(E) · ε(E). La Campaña 1 ya da ε(E) de
1 meV a 1 keV. Pero la señal de humedad está sobre todo **por encima de 1 keV**: el flujo que sube del suelo por
encima de 1 keV cae de 116 a 53 n m⁻² s⁻¹ entre seco y 30 %. Este barrido mide ε(E) ahí, igual que el barrido de
S(α,β), sin tener que simular los seis espectros completos en el tanque.

| Aspecto | Valor |
|---|---|
| Geometría | la del barrido de S(α,β): agua R = 48 cm, H = 133 cm, Tyvek 0.12 mm, acero 0.5 mm; PMT del contenedor (Sidelnik, bajado a 0.3·H/2); **sin suelo** (el script borra las variables `MEIGA_SUELO_*`) |
| Inyección | neutrones monoenergéticos verticales desde z = 200 cm, uniformes en un círculo de 40 cm (`eCircle`) |
| Física | `QGSP_BERT_HP_NoThermal` (sin S(α,β)), la de las corridas del suelo |
| Energías y neutrones | 1 keV, 10 keV, 100 keV, 1 MeV y 5 MeV: 10 000 cada una; 20 MeV: 5 000; 100 MeV: 2 000; 1 GeV: 1 000. El punto de 1 keV coincide con la Campaña 1 y sirve para empalmar |
| Medios | por defecto agua pura y 10 % NaCl (lo mínimo); se pueden agregar `Agua25NaCl` y `Agua5NaCl` |
| Salida | `resultados/eficiencias.tsv`: ε con Q ≥ 1, 3, 5, 10 y 20 p.e., capturas en el agua, ⟨Q⟩ y tiempo. Se conservan la carga, las capturas y los incidentes; los archivos de pasos más pesados se borran |

## Pasos (dentro del contenedor, **sin ninguna otra simulación corriendo**)

**1. Copiar y descomprimir** (en el portátil):

```bash
sudo docker cp "/media/jaime/ADATA HD330/Paquetes/Barrido-rapidos-WCD.zip" silly_roentgen:/opt/ && sudo docker exec silly_roentgen bash -c 'cd /opt && unzip -o Barrido-rapidos-WCD.zip > /dev/null && ls Barrido-rapidos-WCD'
```

**2. Prueba** (20 neutrones por energía; unos minutos). Comprueba física, medio, que no haya suelo y que haya una
carga por neutrón, y estima el tiempo del barrido completo:

```bash
sudo docker exec silly_roentgen bash -ic 'cd /opt/Barrido-rapidos-WCD && ./barrido_rapidos.sh prueba'
```

Cada línea debe empezar por `OK`. La estimación de tiempo es un máximo: con 20 neutrones pesa mucho el arranque de
Geant4. Mande la captura.

**3. Barrido completo** (en segundo plano):

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Barrido-rapidos-WCD && ./barrido_rapidos.sh completa > barrido.log 2>&1'
```

Avance:

```bash
sudo docker exec silly_roentgen bash -c 'tail -5 /opt/Barrido-rapidos-WCD/barrido.log; pgrep -c G4WCDSimulator'
```

**4. Copiar la tabla al ADATA** (es un archivo pequeño):

```bash
sudo docker cp silly_roentgen:/opt/Barrido-rapidos-WCD/resultados/eficiencias.tsv "/media/jaime/ADATA HD330/Paquetes/eficiencias_rapidos.tsv"
```

Con esa tabla, `Albedo-suelo-humedo/scripts/curva_calibracion_wcd.py` (en el PC de análisis, copiándola a
`resultados/eficiencias_rapidos.tsv`) da la curva de calibración con todo el espectro.
