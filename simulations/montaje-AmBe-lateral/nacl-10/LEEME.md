# Corrida MEIGA del montaje con la fuente ²⁴¹Am-Be — agua + 10 % NaCl

Misma corrida que las de agua pura y 2.5 % NaCl, con el medio cambiado: **1 000 000 de neutrones** que
entran por el costado del tanque, con **el mismo archivo de entrada** (mismos neutrones, misma mezcla):

| Componente | Neutrones | Energía | Origen y dirección |
|---|---|---|---|
| Haz directo | 350 000 | ISO 8529 (0.1–10.8 MeV) | desde la fuente (−88.062, 0, 66.562) cm, cono de 2.86° |
| Halo difuso | 450 000 | 0.5 eV – 100 keV, 1/E | cara del plomo (120 × 40 cm), 0–90°, ley del coseno |
| Fondo hemisférico | 200 000 | 10⁻⁴ – 0.5 eV, maxwelliano (kT = 25.3 meV) | plano frente al tanque (96 × 133 cm), hemisferio |

## Configuración

| Parámetro | Valor |
|---|---|
| Medio | agua + 10 % NaCl (`impuritiesFraction` 0.1, fracción másica final, Ec. 3.12) → material `SaltyWater_NaCl_10.0pct`, densidad 1.07051 g/cm³ (Tabla 3.6) |
| Tanque | SaltyWCD, agua R = 48 cm, H = 133 cm, Tyvek 0.12 mm + acero 0.5 mm |
| Inyección | `eFromFile` (pz invertido en el archivo, porque `ParticleFiller.cc` usa −pz) |
| Física | `QGSP_BERT_HP_NoThermal` (**sin** S(α,β)), igual que agua pura y 2.5 % |
| PMT | el de Sidelnik (en la tapa, 10.16 × 10.16 × 5 cm), el mismo de las otras corridas |

Carpeta propia `/opt/Corrida-AmBe-montaje-nacl-10`, carpetas de trabajo `G4WCDSimulator-ambe-nacl-10-parte<k>`
y archivos de entrada `…-nacl-10-parte<k>-de4.txt`: no toca nada de las otras corridas.

## Pasos

**0. Esperar a que termine la corrida de muones** (el script no deja lanzar la completa mientras haya otra
simulación) **y liberar espacio**: esta corrida necesita ~140 GB; el script pide al menos 180 GB libres.

```bash
sudo docker exec silly_roentgen tail -3 /opt/Corrida-muones-VEM-agua-pura/corrida-muones.log
```
```bash
sudo docker exec silly_roentgen df -h /opt
```

**1. Copiar el paquete al contenedor** (en el portátil; ajuste la ruta del disco):

```bash
sudo docker cp "/media/jaime/TOSHIBA EXT/Corrida-AmBe-montaje-nacl-10.zip" silly_roentgen:/opt/
```

**2. Prueba de 30 neutrones** (dentro del contenedor, `sudo docker exec -it silly_roentgen bash`):

```bash
cd /opt && unzip -o Corrida-AmBe-montaje-nacl-10.zip && cd Corrida-AmBe-montaje-nacl-10 && ./ejecutar_corrida.sh nacl-10 prueba
```

Debe terminar con **TODO CORRECTO**: material `SaltyWater_NaCl_10.0pct`, fracción 0.1, densidad
1.07051 g/cm³. La prueba se puede hacer mientras corren los muones (son 30 neutrones). Salga con `exit`.

**3. Lanzar la corrida completa en 4 partes** (fuera del contenedor, con los muones ya terminados):

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-AmBe-montaje-nacl-10 && ./ejecutar_corrida.sh nacl-10 completa 4 > corrida-nacl-10.log 2>&1'
```

**4. Avance:**

```bash
sudo docker exec silly_roentgen tail -5 /opt/Corrida-AmBe-montaje-nacl-10/corrida-nacl-10.log
```
```bash
sudo docker exec silly_roentgen bash -c 'for k in 1 2 3 4; do f=/opt/meiga/build/Applications/G4WCDSimulator-ambe-nacl-10-parte$k/Flujo-parte$k-1000000N-AmBe-montaje-haz-halo-fondo-H2O-10NaCl.txt; echo "parte $k: $(grep -c "Run terminated" $f 2>/dev/null) de 250000"; done'
```

**5. Al terminar, copiar los resultados** a un disco con al menos 150 GB libres:

```bash
sudo docker cp silly_roentgen:/opt/Corrida-AmBe-montaje-nacl-10/resultados "/media/jaime/ADATA HD330/Corrida-AmBe-montaje-nacl-10-resultados"
```

## Estimación

| | 4 partes en paralelo | Disco |
|---|---|---|
| agua pura (real) | 2.9 h | 59 GB |
| 2.5 % NaCl (real) | 3.6 h | 96 GB |
| **10 % NaCl (estimado)** | **≈ 4.5–5 h** | **≈ 130–140 GB** |

El NaCl produce más luz Cherenkov (cascadas del ³⁶Cl) y más capturas; la prueba de 30 neutrones imprime su
propia estimación.
