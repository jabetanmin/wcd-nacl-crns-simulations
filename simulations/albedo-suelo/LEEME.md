# Albedo de neutrones del suelo SoilBS: seco y con distintas humedades (sin tanque)

**Objetivo:** hacer incidir el flujo de neutrones que baja sobre Bucaramanga (la curva "Baja" de la tesis) sobre un
suelo SoilBS húmedo, con 25 % de agua en masa, y obtener el espectro que emerge (el albedo). Se compara con el suelo
seco: el de la tesis y uno simulado aquí con el mismo montaje. Además se sigue a cada neutrón, para saber si el que
sube es el incidente reflejado o uno creado en el suelo (por ejemplo por dispersión inelástica).

| Aspecto | Valor |
|---|---|
| Neutrones incidentes | 200 000, tomados al azar de los 1 111 010 que **bajan** en `all_bga_neutron_35.shw` (tesis), con su energía y su dirección originales (de 0.09 meV a 123 GeV; 58 % por encima de 20 MeV; cos θ medio 0.81) |
| Distribución espacial | **uniforme** en x e y de −8.5 a 8.5 m, a 6 cm sobre el suelo (a 1.5 m de los bordes) |
| Suelo | SoilBS (tesis), 20 × 20 × 1 m, superficie en z = 0: `seco` (2.700 g/cm³) o `humedo-5`, `humedo-10`, `humedo-15`, `humedo-25` (1.895 g/cm³, 47 % de agua en volumen), `humedo-30` |
| Contador | plano virtual a **5 cm sobre el suelo**: se cuentan los neutrones que lo cruzan bajando y subiendo, como el plano de la tesis |
| Seguimiento | cada paso de cada neutrón (`pasos-neutrones.tsv`): traza, traza madre, proceso que lo creó, energía, posición |
| Física | `QGSP_BERT_HP_NoThermal` (sin S(α,β)), igual que las demás corridas |
| Tanque | **no se construye** (`MEIGA_SIN_TANQUE=1`): solo suelo y aire, hasta tener los espectros de varias humedades. El tanque a 2 m sobre el suelo (como en los experimentos) ya está en el parche (`MEIGA_SUELO_SEPARACION=2`) para la etapa siguiente |

## Requisito: el parche del suelo

Primero hay que aplicar `Parche-suelo-SoilBS` (`./preparar_suelo.sh aplicar` y `./probar_suelo.sh`), **cuando no
haya ninguna simulación corriendo**. Este paquete se niega a correr si el parche no está aplicado y compilado.

## Pasos

**1. Copiar el paquete al contenedor** (portátil):

```bash
sudo docker cp "/media/jaime/TOSHIBA EXT/Corrida-suelo-albedo.zip" silly_roentgen:/opt/
```

**2. Pruebas de 30 neutrones** (dentro del contenedor). Incluyen los 10 de menor energía, 10 intermedios y los 10 de
mayor energía, para estimar bien el tiempo:

```bash
cd /opt && unzip -o Corrida-suelo-albedo.zip && cd Corrida-suelo-albedo && ./ejecutar_suelo.sh seco prueba
```
```bash
./ejecutar_suelo.sh humedo-25 prueba
```

(los otros: `humedo-5`, `humedo-10`, `humedo-15`, `humedo-30`). Las pruebas comprueban también la línea `SIN TANQUE`.

Cada una debe terminar con **TODO CORRECTO**: material y densidad del suelo, suelo de 20 × 20 × 1 m, 30 corridas,
pasos dentro del suelo y cruces del plano. Imprimen el tiempo y el disco estimados para 200 000 neutrones. Mande las
capturas **antes** de lanzar las completas: los neutrones de muy alta energía (hasta 123 GeV) pueden hacer las corridas
largas y pesadas.

**3. Corridas completas** (fuera del contenedor; una tras otra; primero húmedo 25 % y seco, después las demás humedades):

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-suelo-albedo && ./ejecutar_suelo.sh humedo-25 completa 4 > corrida-suelo-humedo-25.log 2>&1'
```
```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-suelo-albedo && ./ejecutar_suelo.sh seco completa 4 > corrida-suelo-seco.log 2>&1'
```

**3b. Validación del suelo seco** (después de las húmedas, o entre dos de ellas; nunca a la vez que otra corrida):

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-suelo-albedo && ./ejecutar_suelo.sh seco validacion 4 > corrida-suelo-seco-validacion.log 2>&1'
```

Corre los primeros 50 000 de los 200 000 neutrones: son exactamente los de la **parte 1** de cada corrida completa,
así que el seco se compara con cada humedad usando los mismos neutrones. Se reparte en 4 partes de 12 500, tarda
≈1.2 h, ocupa ≈10 GB y pide al menos 20 GB libres. Al final verifica cada parte (debe terminar con cuatro
**TODO CORRECTO**). Su salida es `resultados/50000N-Bga-sobre-SoilBS-seco-sinSab-<fecha>`.

El análisis compara el seco de MEIGA con la curva "Sube" de la tesis (validación) y con la parte 1 de cada humedad
(`--corrida humedo-25=<carpeta>@1`).

**4. Avance:**

```bash
sudo docker exec silly_roentgen bash -c 'for s in seco humedo-5 humedo-10 humedo-15 humedo-25 humedo-30; do for k in 1 2 3 4; do f=$(ls /opt/meiga/build/Applications/G4WCDSimulator-suelo-$s-parte$k/ 2>/dev/null | grep "^Flujo-parte"); [ -n "$f" ] && echo "$s parte $k: $(grep -c "Run terminated" /opt/meiga/build/Applications/G4WCDSimulator-suelo-$s-parte$k/$f) de 50000"; done; done; df -h /opt | tail -1'
```

**5. Copiar los resultados al disco:**

```bash
sudo docker cp silly_roentgen:/opt/Corrida-suelo-albedo/resultados "/media/jaime/ADATA HD330/Corrida-suelo-albedo-resultados"
```

## Análisis (PC de análisis)

`analysis/suelo-humedo-calibracion_seccion-4.7/scripts/analizar_albedo.py`:

```bash
python3 scripts/analizar_albedo.py --corrida seco=<…>/200000N-Bga-sobre-SoilBS-seco-… --corrida humedo-25=<…>/200000N-Bga-sobre-SoilBS-agua25-… [--corrida humedo-10=<…> …]
```

Produce:
- el espectro letárgico que sube en seco y en húmedo, junto a "Baja" y "Sube" de la tesis, con la misma
  normalización (n m⁻² s⁻¹);
- el origen de los neutrones que suben (incidente reflejado o creado en el suelo, con el proceso que lo creó), por
  energía;
- una tabla por región (térmica, epitérmica, de evaporación y de cascada) con el cociente húmedo/seco.
