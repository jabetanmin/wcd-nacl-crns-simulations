# Corrida MEIGA de muones verticales (VEM) — calibración p.e./ADC

**Objetivo.** Comprobar la calibración del prototipo (hasta ahora 3.95 p.e. por 1000 ADC) con el pico de
muones de las tomas de fondo (≈ 35–40 mil ADC en los tres medios). Se simula la carga que deja un muón
vertical en el mismo detector y con el mismo PMT que las corridas del montaje Am-Be; el cociente
"pico medido en ADC / carga simulada en p.e." da los ADC por fotoelectrón.

| Parámetro | Valor |
|---|---|
| Partículas | **2000 μ⁻ de 4 GeV/c** (energía típica de los muones a nivel del mar), verticales hacia abajo |
| Entrada | puntos al azar en un disco de radio 45 cm sobre la tapa (z = 140 cm, en aire), atraviesan los 133 cm de agua |
| Detector | SaltyWCD, agua pura, R = 48 cm, H = 133 cm, Tyvek 0.12 mm + acero 0.5 mm, **PMT de Sidelnik** (el mismo del montaje) |
| Física | `QGSP_BERT_HP_NoThermal`, igual que las corridas del montaje |
| Inyección | `eFromFile` (archivo `6 0 0 4.0 x y 140 ...`, CORSIKA 6 = μ⁻; pz > 0 en el archivo = −z en Geant4) |

Cada muón produce unos 45 000 fotones Cherenkov; con la colección óptica de este modelo se esperan del orden
de cientos de p.e. por muón. La prueba de 5 muones lo muestra.

## Pasos

**0. Esperar a que termine la corrida de 2.5 % NaCl** (las dos competirían por los 4 núcleos; el script no
deja lanzar la completa mientras haya otra simulación):

```bash
sudo docker exec silly_roentgen tail -3 /opt/Corrida-AmBe-montaje-nacl-2.5/corrida-nacl-2.5.log
```

**1. Copiar el paquete al contenedor** (en el portátil; ajuste la ruta del disco):

```bash
sudo docker cp "/media/jaime/ADATA HD330/Corrida-muones-VEM-agua-pura.zip" silly_roentgen:/opt/
```

**2. Prueba de 5 muones** (dentro del contenedor, `sudo docker exec -it silly_roentgen bash`):

```bash
cd /opt && unzip -o Corrida-muones-VEM-agua-pura.zip && cd Corrida-muones-VEM-agua-pura && ./ejecutar_corrida.sh agua-pura prueba
```

Debe terminar con **TODO CORRECTO**: 5 eventos, partícula μ⁻ (PDG 13), todos verticales hacia abajo, **todos
con carga**, agua pura, sin S(α,β), tanque 48 × 133 cm. Imprime además la carga por muón (media, mediana) y
el tiempo y el tamaño estimados de los 2000. Salga con `exit`.

**3. Lanzar la corrida completa en 4 partes** (fuera del contenedor):

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-muones-VEM-agua-pura && ./ejecutar_corrida.sh agua-pura completa 4 > corrida-muones.log 2>&1'
```

**4. Avance** (cada parte tiene unos 500 muones):

```bash
sudo docker exec silly_roentgen bash -c 'for k in 1 2 3 4; do f=/opt/meiga/build/Applications/G4WCDSimulator-muones-agua-pura-parte$k/Flujo-parte$k-2000N-muones-VEM-H2O-pura.txt; echo "parte $k: $(grep -c "Run terminated" $f 2>/dev/null) de 500"; done; tail -2 /opt/Corrida-muones-VEM-agua-pura/corrida-muones.log'
```

**5. Al terminar, copiar los resultados al ADATA:**

```bash
sudo docker cp silly_roentgen:/opt/Corrida-muones-VEM-agua-pura/resultados "/media/jaime/ADATA HD330/Corrida-muones-VEM-agua-pura-resultados"
```

## Estimación

Cada muón genera unas 30 veces más fotones Cherenkov que un neutrón del montaje, y el seguimiento de los
fotones es lo que más cuesta. Estimación: **del orden de 10 s por muón → ≈ 5–8 h en un núcleo, ≈ 1.5–2 h en
4 partes, y ≈ 30–50 GB**. La prueba de 5 muones da la estimación real con este equipo.

## Análisis

Con los resultados en el ADATA, el script `Analisis-montaje-MEIGA/scripts/calibrar_vem.py` (en el PC de
análisis) calcula el pico de carga de los muones simulados y lo compara con el pico de muones de las tres
tomas de fondo, con los dos métodos de carga (ventana del disparo y carga positiva de toda la traza).
Resultado: ADC por p.e. y p.e. por 1000 ADC, para comparar con el 3.95 usado hasta ahora.

Nota: el fondo contiene muones de todas las direcciones; la simulación, solo verticales. La diferencia de
longitud media de traza introduce una incertidumbre de ~10 % en la calibración.
