# Corrida MEIGA del montaje con la fuente ²⁴¹Am-Be — agua + 2.5 % NaCl

Misma corrida que la de agua pura (`Corrida-AmBe-montaje-agua-pura`), con el medio cambiado:
**1 000 000 de neutrones** que entran por el costado del tanque, con **el mismo archivo de entrada**
(mismos neutrones, misma mezcla), para que la comparación entre medios sea directa:

| Componente | Neutrones | Energía | Origen y dirección |
|---|---|---|---|
| Haz directo | 350 000 | ISO 8529 (0.1–10.8 MeV) | desde la fuente (−88.062, 0, 66.562) cm, cono de 2.86° |
| Halo difuso | 450 000 | 0.5 eV – 100 keV, 1/E | cara del plomo (120 × 40 cm), 0–90°, ley del coseno |
| Fondo hemisférico | 200 000 | 10⁻⁴ – 0.5 eV, maxwelliano (kT = 25.3 meV) | plano frente al tanque (96 × 133 cm), hemisferio |

## Configuración

| Parámetro | Valor |
|---|---|
| Medio | agua + 2.5 % NaCl (`impuritiesFraction` 0.025, fracción másica final, Ec. 3.12) → material `SaltyWater_NaCl_2.5pct`, densidad 1.01604 g/cm³ (Tabla 3.6) |
| Tanque | SaltyWCD, agua R = 48 cm, H = 133 cm, Tyvek 0.12 mm + acero 0.5 mm |
| Inyección | `eFromFile` (pz invertido en el archivo, porque `ParticleFiller.cc` usa −pz) |
| Física | `QGSP_BERT_HP_NoThermal` (**sin** S(α,β)), igual que agua pura |
| PMT | el de Sidelnik (en la tapa, 10.16 × 10.16 × 5 cm), el mismo de la corrida de agua pura |

Este paquete va en **su propia carpeta** (`/opt/Corrida-AmBe-montaje-nacl-2.5`), con carpetas de trabajo
`G4WCDSimulator-ambe-nacl-2.5-parte<k>` y archivos de entrada `…-nacl-2.5-parte<k>-de4.txt`: no toca nada
de la corrida de agua pura.

## Pasos

**0. Esperar a que termine la corrida de agua pura.** El script no deja lanzar otra simulación mientras
haya una en marcha, porque competirían por los 4 núcleos. Para comprobarlo, en el portátil:

```bash
sudo docker exec silly_roentgen tail -3 /opt/Corrida-AmBe-montaje-agua-pura/corrida-agua-pura.log
```

Debe decir `== Listo: ...`. Copie esos resultados al ADATA antes de seguir (ver el LEEME de agua pura).

**1. Copiar el paquete al contenedor** (en el portátil, fuera del contenedor; ajuste la ruta del disco
donde esté el zip):

```bash
sudo docker cp "/media/jaime/TOSHIBA EXT/Corrida-AmBe-montaje-nacl-2.5.zip" silly_roentgen:/opt/
```

**2. Prueba de 30 neutrones** (dentro del contenedor, `sudo docker exec -it silly_roentgen bash`):

```bash
cd /opt && unzip -o Corrida-AmBe-montaje-nacl-2.5.zip && cd Corrida-AmBe-montaje-nacl-2.5 && ./ejecutar_corrida.sh nacl-2.5 prueba
```

Debe terminar con **TODO CORRECTO**. El verificador comprueba además en el registro de MEIGA el material
(`SaltyWater_NaCl_2.5pct`), la fracción de NaCl (0.025) y la densidad (1.01604 g/cm³). Salga con `exit`.

**3. Lanzar la corrida completa en 4 partes** (desde fuera del contenedor):

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-AmBe-montaje-nacl-2.5 && ./ejecutar_corrida.sh nacl-2.5 completa 4 > corrida-nacl-2.5.log 2>&1'
```

**4. Avance** (cada parte tiene unos 250 000 neutrones):

```bash
sudo docker exec silly_roentgen tail -5 /opt/Corrida-AmBe-montaje-nacl-2.5/corrida-nacl-2.5.log
```
```bash
sudo docker exec silly_roentgen bash -c 'grep -c "Run terminated" /opt/meiga/build/Applications/G4WCDSimulator-ambe-nacl-2.5-parte1/Flujo-parte1-1000000N-AmBe-montaje-haz-halo-fondo-H2O-2.5NaCl.txt'
```

**5. Al terminar, copiar los resultados al ADATA:**

```bash
sudo docker cp silly_roentgen:/opt/Corrida-AmBe-montaje-nacl-2.5/resultados "/media/jaime/ADATA HD330/Corrida-AmBe-montaje-nacl-2.5-resultados"
```

## Estimación

| | 1 núcleo | 4 partes en paralelo | Disco |
|---|---|---|---|
| 1 000 000 n, 2.5 % NaCl | ≈ 14.5 h | **≈ 4 h** | **≈ 66 GB** |

Escalado desde la prueba de agua pura (0.038 s/neutrón, 51 GB por millón) con el cociente entre medios
que dan los tiempos reales de las corridas Am-Be: el NaCl produce más luz Cherenkov (cascadas del ³⁶Cl),
que es lo que más tiempo y disco consume. La prueba de 30 neutrones imprime su propia estimación.

## Archivos

`ejecutar_corrida.sh`, `verificar_prueba.py`, `revisar_espacio.sh` y `flujos/` funcionan igual que en el
paquete de agua pura (ver su LEEME para el detalle). La configuración del medio está en
`configuracion/nacl-2.5/DetectorList.xml`.
