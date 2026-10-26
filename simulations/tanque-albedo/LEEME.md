# El WCD iluminado por los neutrones que suben del suelo (curva de calibración, simulación directa)

**Para qué:** comprobar la curva de calibración obtenida por plegado. Aquí se inyectan en el tanque los mismos
neutrones que suben del suelo en cada humedad (seco, 5, 10, 15, 25 y 30 % de agua), con su energía y su dirección
reales. Así entran por el fondo y **por los costados** (≈ 70 %), que es lo que el plegado de incidencia vertical no
ve.

| Aspecto | Valor |
|---|---|
| Neutrones | los cruces hacia arriba del plano a 5 cm de las corridas `Corrida-suelo-albedo` (ADATA), con su energía y dirección |
| Geometría del experimento | tanque con el fondo 2 m sobre el suelo; en los 2 m de aire casi no interactúan (≈ 0.24 g/cm²) |
| Entrada | el campo que sube es uniforme, así que la tasa por la base es J·πR² y por el costado J·2RH·⟨tan θ⟩; los puntos de entrada se sortean sobre la base y el costado (1 mm fuera), con el peso de cada cruce. Corte de los más rasantes en 85° (vienen de 25–40 m) |
| Detector | SaltyWCD (R = 48 cm, H = 133 cm, Tyvek, acero), PMT del contenedor (Sidelnik, 0.3·H/2), **sin suelo** en la geometría (el script borra las variables `MEIGA_SUELO_*`) |
| Física | `QGSP_BERT_HP_NoThermal` (sin S(α,β)) |
| Neutrones por corrida | prueba: 2 000; completa: 100 000, en 4 partes paralelas |
| Archivos | `flujos/100000N-sube-<suelo>.txt`, `flujos/prueba/2000N-sube-<suelo>.txt`, `flujos/entrada_tanque.json` (tasas por la base y por el costado, con los cortes de 80°, 85° y sin corte) |
| Salida | `resultados/tanque.tsv`: ε con Q ≥ 1, 3, 5, 10 y 20 p.e., capturas en el agua, ⟨Q⟩ y tiempo. Se conservan la carga, las capturas y los incidentes |

El flujo que **baja** no se simula aquí: es igual para todas las humedades y se toma del plegado.

## Pasos (en el portátil, fuera del contenedor, sin ninguna otra simulación corriendo)

**1. Copiar y descomprimir:**

```bash
sudo docker cp "/media/jaime/ADATA HD330/Paquetes/Corrida-tanque-albedo.zip" silly_roentgen:/opt/ && sudo docker exec silly_roentgen bash -c 'cd /opt && unzip -o Corrida-tanque-albedo.zip > /dev/null && ls Corrida-tanque-albedo Corrida-tanque-albedo/flujos'
```

**2. Prueba con una humedad** (25 %, agua pura, 2 000 neutrones; mide el tiempo real):

```bash
sudo docker exec silly_roentgen bash -ic 'cd /opt/Corrida-tanque-albedo && ./ejecutar_tanque.sh agua25 AguaPura prueba 4'
```

Debe terminar con `OK agua25 AguaPura: eps(Q>=1) = …` y `== Listo`. Mande la captura.

**3. Barrido completo** (6 humedades; por defecto agua pura y 10 % NaCl; en segundo plano):

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-tanque-albedo && ./barrido_tanque.sh completa > barrido.log 2>&1'
```

Para los cuatro medios: `./barrido_tanque.sh completa AguaPura Agua25NaCl Agua5NaCl Agua10NaCl`.

Avance:

```bash
sudo docker exec silly_roentgen bash -c 'grep -c "OK " /opt/Corrida-tanque-albedo/barrido.log; tail -3 /opt/Corrida-tanque-albedo/barrido.log; pgrep -c G4WCDSimulator'
```

**4. Copiar los resultados al ADATA:**

```bash
sudo docker cp silly_roentgen:/opt/Corrida-tanque-albedo/resultados "/media/jaime/ADATA HD330/Corrida-tanque-albedo-resultados"
```

Con `resultados/tanque.tsv` se calcula en el PC de análisis la curva directa y se compara con la del plegado.
