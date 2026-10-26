# Prueba MEIGA: Am-Be moderado, haz horizontal a media altura, PMT bajado 46.55 cm, con su calibración

Este paquete deja la simulación configurada **igual que el prototipo** en todo lo que MEIGA permite, y trae lo
necesario para calibrarla con muones en el mismo detector.

## Qué se simula

| Aspecto | Valor |
|---|---|
| Neutrones | **500 000 por medio** (archivo de 50 000 también incluido: `N_NEUTRONES=50000`), espectro Am-Be (ISO 8529) ya frenado en agua, 10 meV – 10 eV (maxwelliano kT = 25.3 meV + cola 1/E; 82.6 % entre 10 y 100 meV) |
| Haz | **horizontal (+x), a media altura del tanque**: disco de 2 cm de radio centrado en y = 0, z = 66.56 cm, 1 mm antes de la pared (el tamaño del haz colimado de la fuente al llegar al tanque) |
| Tanque | SaltyWCD, agua R = 48 cm, H = 133 cm; acero 0.5 mm + Tyvek 0.12 mm (reflectividad × 0.94) |
| **PMT** | el de Sidelnik (semielipsoide de Pyrex 10.16 × 10.16 × 5 cm), **bajado**: `zPMT = 0.3·fWaterHalfHeight`, cara superior a **46.55 cm bajo la tapa** (86.45 cm sobre el fondo del agua), como en las campañas anteriores |
| Medios | `agua-pura` (w = 0), `nacl-2.5` (w = 0.025), `nacl-10` (w = 0.1) |
| Física | `QGSP_BERT_HP_NoThermal` (sin S(α,β)), modo `eFast` |
| **Calibración** | 2000 μ⁻ verticales de 4 GeV/c con **el mismo PMT bajado** (la VEM cambia con la posición del PMT, así que hay que volver a simularla) |

## Orden de trabajo

**0. Sin otra simulación corriendo** (recompilar con una simulación en marcha la dañaría):

```bash
sudo docker exec silly_roentgen bash -c 'pgrep -a G4WCDSimulator; df -h /opt | tail -1'
```

**1. Copiar el paquete al contenedor** (en el portátil):

```bash
sudo docker cp "/media/jaime/ADATA HD330/Corrida-AmBe-horizontal-PMT-bajo.zip" silly_roentgen:/opt/
```

**2. Bajar el PMT y recompilar** (dentro del contenedor, `sudo docker exec -it silly_roentgen bash`):

```bash
cd /opt && unzip -o Corrida-AmBe-horizontal-PMT-bajo.zip && cd Corrida-AmBe-horizontal-PMT-bajo && ./preparar_meiga.sh bajar
```

Debe terminar con `== Listo: MEIGA compilado con el PMT BAJADO (0.3*fWaterHalfHeight).`

**3. Pruebas** (dentro del contenedor). Cada una debe terminar con **TODO CORRECTO**:

```bash
./ejecutar_corrida.sh agua-pura prueba
```
```bash
./ejecutar_muones.sh agua-pura prueba
```

La de neutrones comprueba además `haz horizontal: todos con dirección +x`; la de muones, que todos los muones
dejan carga (con el PMT bajado la carga por muón será distinta de los 305 p.e. de antes). Salga con `exit`.

**4. Calibración: 2000 muones** (fuera del contenedor; ≈ 1.6 h, ≈ 55 GB):

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-AmBe-horizontal-PMT-bajo && ./ejecutar_muones.sh agua-pura completa 4 > corrida-muones-pmtbajo.log 2>&1'
```

**5. Neutrones: lanzamiento automático tras los muones** (500 000 por medio; ≈ 40–70 min y 15–35 GB cada uno,
≈ 2.5–3 h en total). Este script espera a que terminen los muones, comprueba que su registro diga `== Listo` y
lanza agua pura, 2.5 % y 10 % NaCl uno tras otro. Se puede lanzar ya, mientras corren los muones:

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-AmBe-horizontal-PMT-bajo && ./lanzar_neutrones_tras_muones.sh > cadena-neutrones.log 2>&1'
```

Para ver en qué va la cadena:

```bash
sudo docker exec silly_roentgen bash -c 'cat /opt/Corrida-AmBe-horizontal-PMT-bajo/cadena-neutrones.log; pgrep -c G4WCDSimulator; df -h /opt | tail -1'
```

**5b. (alternativa manual) Neutrones, un medio tras otro:**

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-AmBe-horizontal-PMT-bajo && ./ejecutar_corrida.sh agua-pura completa 4 > corrida-horizontal-agua-pura.log 2>&1'
```
```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-AmBe-horizontal-PMT-bajo && ./ejecutar_corrida.sh nacl-2.5 completa 4 > corrida-horizontal-nacl-2.5.log 2>&1'
```
```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-AmBe-horizontal-PMT-bajo && ./ejecutar_corrida.sh nacl-10 completa 4 > corrida-horizontal-nacl-10.log 2>&1'
```

El script no deja lanzar una corrida mientras otra está en marcha. Para ver cómo va cualquiera:

```bash
sudo docker exec silly_roentgen bash -c 'tail -3 /opt/Corrida-AmBe-horizontal-PMT-bajo/corrida-muones-pmtbajo.log; pgrep -c G4WCDSimulator; df -h /opt | tail -1'
```

(cambie el nombre del log por el de la corrida que quiera ver).

**6. Copiar los resultados al ADATA:**

```bash
sudo docker cp silly_roentgen:/opt/Corrida-AmBe-horizontal-PMT-bajo/resultados "/media/jaime/ADATA HD330/Corrida-AmBe-horizontal-PMT-bajo-resultados"
```

**7. Devolver el PMT a la tapa** (dentro del contenedor). Sin esto, los demás paquetes se niegan a correr:

```bash
cd /opt/Corrida-AmBe-horizontal-PMT-bajo && ./preparar_meiga.sh revertir
```

## Análisis con las calibraciones (PC de análisis)

`Analisis-montaje-MEIGA/scripts/respuesta_prototipo.py` aplica a la simulación la respuesta medida del prototipo:

1. calibración ADC/p.e. con el pico de muones simulado (de esta misma corrida) frente al pico medido en las tomas de
   fondo, corregida por la saturación del ADC;
2. resolución de un fotoelectrón (40 %);
3. forma del pulso (cociente carga/amplitud medido) y recorte del ADC en 8040 cuentas;
4. disparo: pico mayor de 1200 ADC, como en los cuadernos del prototipo;
5. un factor vertical común (neutrones en 300 s) para los tres medios; opcionalmente (`--k-libre`), también el
   factor horizontal libre y común, como en los cuadernos.

```bash
python3 scripts/respuesta_prototipo.py --muones "<ADATA>/Corrida-AmBe-horizontal-PMT-bajo-resultados/2000N-muones-VEM-PMTbajo-H2O-pura-sinSab-<fecha>" --medio pura "<…>/50000N-AmBe-moderado-horizontal-PMTbajo-H2O-pura-sinSab-<fecha>" --medio 2.5 "<…2.5NaCl…>" --medio 10 "<…10NaCl…>" --etiqueta horizontal-pmtbajo --k-libre
```

## Archivos

| Archivo | Qué hace |
|---|---|
| `bajar_pmt.py`, `preparar_meiga.sh bajar\|revertir` | cambian `zPMT` en `SaltyWCD.cc` (guardando la línea original) y recompilan |
| `ejecutar_corrida.sh <medio> prueba\|completa [PARTES]` | neutrones; comprueba PMT bajado, forma de Sidelnik, medio, física, inyección |
| `ejecutar_muones.sh agua-pura prueba\|completa [PARTES]` | muones de calibración con el mismo PMT |
| `verificar_prueba.py`, `verificar_muones.py` | verificación de las pruebas (en el registro de MEIGA y en `output.json.gz`) |
| `flujos/50000N-…-horizontal-mitad-r2cm.txt` | neutrones (formato ARTI `13 px py pz x y z 4 0 0 0 0`), con sus energías en `…-componentes.txt` |
| `flujos/muones/2000N-muones-VEM.txt` | muones (`6 0 0 4.0 x y 140 …`, CORSIKA 6 = μ⁻) |
