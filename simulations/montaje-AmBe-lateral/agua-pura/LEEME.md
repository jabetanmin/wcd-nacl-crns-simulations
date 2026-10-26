# Corrida MEIGA del montaje con la fuente ²⁴¹Am-Be — agua pura

Simulación del detector prototipo irradiado por el costado con la fuente ²⁴¹Am-Be blindada (caja de
polietileno con canal de 3 cm × 30 cm y 10 cm de plomo). Se lanzan **1 000 000 de neutrones** que
entran al tanque, con la mezcla acordada:

| Componente | Neutrones | Energía | Origen y dirección |
|---|---|---|---|
| Haz directo | 350 000 | ISO 8529 (0.1–10.8 MeV) | desde la fuente (−88.062, 0, 66.562) cm, cono de 2.86° |
| Halo difuso | 450 000 | 0.5 eV – 100 keV, 1/E | cara del plomo (120 × 40 cm), 0–90°, ley del coseno |
| Fondo hemisférico | 200 000 | 10⁻⁴ – 0.5 eV, maxwelliano (kT = 25.3 meV) | plano frente al tanque (96 × 133 cm), hemisferio |

Neutrones por intervalo de energía: ver `flujos/resumen.json` y la tabla del informe
(`analysis/validacion-experimental-prototipo-AmBe_seccion-4.1.2/Analisis-corridas-AmBe/resultados/neutrones_por_intervalo.tsv`).

## Configuración

| Parámetro | Valor |
|---|---|
| Tanque | SaltyWCD, agua R = 48 cm, H = 133 cm, Tyvek 0.12 mm + acero 0.5 mm (`DetectorList.xml`) |
| Medio | agua pura (`impuritiesFraction` 0) |
| Inyección | `eFromFile`: posición y dirección de cada neutrón desde el archivo |
| Física | `QGSP_BERT_HP_NoThermal` (**sin** S(α,β), igual que las corridas Am-Be y la Campaña 1) |
| PMT | el de Sidelnik (en la tapa, 10.16 × 10.16 × 5 cm), como quedó compilado en el contenedor |

El archivo de neutrones (`flujos/1000000N-AmBe-montaje-haz-halo-fondo.txt`, formato ARTI
`13 px py pz x y z C 0 0 0 0`, p en GeV/c, x en cm) se escribió con **pz invertido**, porque
`ParticleFiller.cc` guarda el momento como (px, py, −pz). La columna 8 (C) marca la componente
(1 haz, 2 halo, 3 fondo); MEIGA la lee pero no la usa. `...-componentes.txt` da componente y energía
por línea (línea k = `run_id` k).

## Pasos

**0. Revisar el espacio y liberar lo que ya está respaldado** (en el portátil, fuera del contenedor, con
el ADATA conectado; ajuste la ruta del ADATA):

```bash
unzip -o Corrida-AmBe-montaje-agua-pura.zip && cd Corrida-AmBe-montaje-agua-pura
```
```bash
./revisar_espacio.sh "/media/jaime/ADATA HD330"
```

Muestra el espacio del portátil, del ADATA y del contenedor, y para cada carpeta de resultados del
contenedor dice si tiene **copia idéntica** en el ADATA (mismo número de archivos y mismos bytes).
**No borra nada**: imprime los comandos `sudo docker exec silly_roentgen rm -rf ...` solo para las
carpetas verificadas, para que usted los revise y los ejecute. Las carpetas `[SIN COPIA]` o
`[DIFERENTE]` no deben borrarse. Se necesitan ≥ 100 GB libres en `/opt` del contenedor.

**1. Copiar el paquete al contenedor** (en el portátil, fuera del contenedor):

```bash
sudo docker cp Corrida-AmBe-montaje-agua-pura.zip silly_roentgen:/opt/
```

**2. Entrar, descomprimir y hacer la prueba de 30 neutrones** (unos segundos):

```bash
sudo docker exec -it silly_roentgen bash
```
```bash
cd /opt && unzip -o Corrida-AmBe-montaje-agua-pura.zip && cd Corrida-AmBe-montaje-agua-pura
```
```bash
./ejecutar_corrida.sh agua-pura prueba
```

Debe terminar con **TODO CORRECTO**. La prueba también imprime una estimación del tiempo y del
tamaño de la corrida completa. Salga del contenedor con `exit` (no lo detenga).

**3. Lanzar la corrida completa en segundo plano, en 4 partes paralelas** (desde fuera del contenedor):

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-AmBe-montaje-agua-pura && ./ejecutar_corrida.sh agua-pura completa 4 > corrida-agua-pura.log 2>&1'
```

`bash -ic` carga el `.bashrc` del contenedor (rutas de Geant4); con `bash -c` falla con
`libG4zlib.so not found`. Con `-d` la corrida sigue aunque cierre la terminal.

**4. Seguir el avance:**

```bash
sudo docker exec silly_roentgen tail -3 /opt/Corrida-AmBe-montaje-agua-pura/corrida-agua-pura.log
```
```bash
sudo docker exec silly_roentgen bash -c 'grep -c "Run terminated" /opt/meiga/build/Applications/G4WCDSimulator-ambe-agua-pura-parte1/Flujo-parte1-1000000N-AmBe-montaje-haz-halo-fondo-H2O-pura.txt'
```

(cada parte tiene unos 250 000 neutrones).

**5. Al terminar, copiar los resultados al ADATA:**

```bash
sudo docker cp silly_roentgen:/opt/Corrida-AmBe-montaje-agua-pura/resultados "/media/jaime/ADATA HD330/Corrida-AmBe-montaje-agua-pura-resultados"
```

(ajuste la ruta del ADATA en su portátil).

## Estimación

| | 1 núcleo | 4 partes en paralelo | Disco |
|---|---|---|---|
| 1 000 000 n, agua pura | ≈ 11.5 h (+10–30 % de arranque) | **≈ 3–4 h** | **≈ 75 GB** |

Estimado a partir de los tiempos reales por neutrón de las corridas Am-Be (0.073 s en 2.5 % NaCl) y
≈ 1.8 MB por segundo simulado. El script exige ≥ 100 GB libres (`MIN_GB=...` para cambiarlo) y que
no haya otra simulación corriendo (`PERMITIR_PARALELO=1`).

## Qué hace `ejecutar_corrida.sh <medio> prueba|completa [PARTES]`

1. Comprueba: opción `QGSP_BERT_HP_NoThermal`, soporte de `eFromFile`, inversión de pz en
   `ParticleFiller.cc`, `impuritiesFraction` del medio, PMT de Sidelnik, ejecutable más reciente que
   el código, número de líneas del archivo y, en la completa, espacio libre y que no haya otra corrida.
2. Divide el archivo en PARTES bloques contiguos (parte 1 = primeras líneas…) y lanza cada parte en
   su carpeta `/opt/meiga/build/Applications/G4WCDSimulator-ambe-<medio>-parte<k>`, con 3 s de
   separación para que MEIGA use semillas distintas.
3. Guarda todo en `resultados/<N>N-AmBe-montaje-<medio>-sinSab-<fecha>/parte<k>/` (Datos-simulacion,
   output.json.gz, registro, DetectorList, JSON y el bloque de neutrones de esa parte), más el
   archivo completo y su archivo de componentes. Para unir las partes: el evento i de la parte k es la
   línea (suma de las líneas de las partes anteriores) + i del archivo completo.
4. En la prueba ejecuta `verificar_prueba.py`: eventos, posición y momento de inyección iguales al
   archivo, todos hacia el tanque, medio, física sin S(α,β), tanque, tiempo y tamaño estimados.

Si el PMT del contenedor ya se revirtió al original, el script se detiene y dice cómo volver a
aplicar el de Sidelnik (`ajustar_pmt_sidelnik.py` y recompilar).
