# Reproducibilidad

## Entorno principal de simulación

- Geant4: 10.07.p04 (10.7.4), instalado en `/opt/GEANT4/10.07.p04-install` dentro del contenedor Docker del autor; MEIGA en `/opt/meiga` (código en `src/`, compilación en `build/`).
- Lista de física: QGSP_BERT_HP. La clave `Simulation.PhysicsName` de la configuración elige `QGSP_BERT_HP` (con `G4ThermalNeutrons`, S(α,β) para el hidrógeno ligado en agua) o `QGSP_BERT_HP_NoThermal` (gas libre). Antes del commit `0fa4db1`, `G4WCDSimulator` ignoraba esta clave y usaba siempre QGSP_BERT_HP.
- Propiedades del detector: el simulador lee `build/Framework/ConfigManager/DetectorProperties.xml`, que CMake sobrescribe con la copia de `src/` al reconfigurar; ambas deben coincidir. Ver [`GEOMETRIA_Y_FISICA_CAMPANAS.md`](GEOMETRIA_Y_FISICA_CAMPANAS.md).
- `docker exec` requiere `bash -ic` (o cargar `geant4.sh`) para que el ejecutable encuentre las bibliotecas de Geant4.
- Procesos ópticos: Cherenkov, absorción, Rayleigh, Mie y procesos de frontera, según la configuración empleada.
- Parches en el contenedor: desde la v0.8.0, el MEIGA del contenedor tiene aplicados sobre `src/` los parches del PMT de Sidelnik, del PMT bajado (`zPMT = 0.3*fWaterHalfHeight`, posición definitiva) y del suelo SoilBS, este último activo solo con `MEIGA_SUELO_W`. Orden, md5 esperados y diffs en [`ESTADO_MEIGA_CONTENEDOR.md`](ESTADO_MEIGA_CONTENEDOR.md).
- Archivos de entrada: los flujos grandes no se versionan; se regeneran byte a byte con semilla fija ([`../data/manifiestos/flujos-regenerables.sha256`](../data/manifiestos/flujos-regenerables.sha256)).
- Copias de las corridas: se verifican con [`../tools/manifiesto.sh`](../tools/manifiesto.sh) (archivos, bytes y md5 del listado) frente a [`../data/manifiestos/corridas-v0.8.0.tsv`](../data/manifiestos/corridas-v0.8.0.tsv).
- Rutas de los datos: los scripts las toman de variables de entorno (`ADATA`, `TOSHIBA`, `REPO_TESIS`, `ALL_BGA_SHW`, `FUENTE_AMBE_DATOS`, `SIM_CUADERNO`, `CARGA_CAMPANA1`, `FLUJO_TERMICO_SHW`); por defecto, los discos externos en `/media/$USER/` y la carpeta personal.
- Semillas aleatorias: el simulador usa `time(NULL)` y no la registra; debe anotarse la hora de inicio de cada corrida y, a futuro, guardar la semilla en la salida.

## Información mínima por campaña

Cada directorio de simulación debe registrar:

1. propósito de la campaña;
2. geometría y versión del código;
3. medio detector;
4. fuente y distribución de partículas;
5. número de eventos incidentes;
6. lista de física y bibliotecas de datos;
7. semillas aleatorias;
8. comandos de compilación y ejecución;
9. archivos de salida esperados;
10. programa utilizado para analizar los resultados.

## Verificación prevista

La primera versión estable deberá incluir al menos un ejemplo pequeño que pueda ejecutarse de principio a fin y reproduzca una tabla o figura seleccionada de la tesis.
