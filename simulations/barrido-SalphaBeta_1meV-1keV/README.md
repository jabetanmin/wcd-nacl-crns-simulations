# Barrido en energía con y sin S(α,β) (agua pura, 1 meV – 1 keV)

Kit de simulación que produjo los datos del estudio
[`analysis/efecto-SalphaBeta_barrido-energia/`](../../analysis/efecto-SalphaBeta_barrido-energia/).
Para cada energía corre el mismo ejecutable dos veces, cambiando solo la física:

| `PhysicsName` | Física |
|---|---|
| `QGSP_BERT_HP` | QGSP_BERT_HP + `G4ThermalNeutrons` (S(α,β) del hidrógeno ligado en agua, E < 4 eV) |
| `QGSP_BERT_HP_NoThermal` | QGSP_BERT_HP sin tratamiento térmico (hidrógeno como gas libre) |

## Configuración

| Parámetro | Valor |
|---|---|
| Medio | agua pura (`impuritiesFraction` = 0) |
| Geometría | agua de 48 cm de radio y 133 cm de altura; Tyvek 0.12 mm; acero 0.5 mm; PMT con la cara plana a 86.5 cm del fondo (fijada en `DetectorList-AguaPura.xml`, no depende de `DetectorProperties.xml`) |
| Inyección | vertical hacia abajo desde z = 200 cm, uniforme en un círculo de 40 cm |
| Neutrones | 10 000 por corrida |
| Energías (eV) | 0.001 0.0025 0.005 0.007 0.01 0.025 0.05 0.08 0.1 0.3 0.5 0.7 1 10 100 1000 |
| Código | rama `main` desde el commit `0fa4db1` (lectura de `PhysicsName` desde la configuración) |
| Entorno | Geant4 10.7.4 en el contenedor Docker del autor, ejecutable recompilado el 2026-09-28 |
| Fecha de las corridas | 2026-09-29, 16:54–20:12 UTC (32 corridas) |

El momento del neutrón se calcula como p = √(E² + 2mE); para 25 meV da 6.85407·10⁻⁶ GeV/c, igual
que el archivo de flujo de la Campaña 2.

## Archivos

| Archivo | Función |
|---|---|
| `correr_prueba.sh` | Una corrida: `./correr_prueba.sh <PhysicsName> <energía en eV> [neutrones]`. Crea su propia carpeta, genera el flujo, ejecuta el simulador y comprueba la física registrada, la energía inyectada y la geometría leída. |
| `barrido.sh` | Recorre una lista de energías con ambas físicas; salta las corridas ya terminadas. |
| `resumen_prueba.sh` | Captura en el agua y ⟨N⟩ de una corrida. |
| `tabla_barrido.sh` | Tabla comparativa con y sin S(α,β) de todas las corridas terminadas. |
| `DetectorList-AguaPura.xml`, `G4WCDSimulator-prueba.json` | Geometría, inyección y configuración (la física se inserta en `@FISICA@`). |
| `tabla_barrido_resultado.tsv` | Tabla producida por el barrido del 2026-09-29. |

## Uso (dentro del contenedor, con el entorno de Geant4 cargado)

```bash
./barrido.sh 0.001 0.0025 0.005 0.007 0.01 0.025 0.05 0.08 0.1 0.3 0.5 0.7 1 10 100 1000 > salida-barrido.txt 2>&1
```

Desde fuera del contenedor, `docker exec` necesita `bash -ic` (o cargar `geant4.sh`) para que el
simulador encuentre las bibliotecas de Geant4.

## Datos producidos

Cada corrida escribe sus TSV en `<energía>-AguaPura-<física>-10000N/Datos-simulacion/`
(7.5 GB en total sin `pasos-particulas.tsv`). No se versionan en git: la copia comprimida
(`barrido-1meV-1keV.tar.gz`, 1.6 GB) se conserva fuera del repositorio y debe publicarse en un
repositorio de datos con identificador persistente (ver [`docs/DATA_MANAGEMENT.md`](../../docs/DATA_MANAGEMENT.md)).

## Advertencias

- La semilla aleatoria se inicializa con `time(NULL)` y no se registra.
- El simulador escribe en `Datos-simulacion/` con modo *append*: cada corrida debe ejecutarse en una
  carpeta nueva, como hace `correr_prueba.sh`.
- Las órdenes con asteriscos pueden perderlos al copiarse desde algunos visores de texto; los scripts
  evitan necesitarlos.
