# Estado del MEIGA del contenedor (octubre de 2026)

`src/` guarda el MEIGA de la tesis sin los cambios propios de cada campaña. Esos cambios se aplican en el contenedor
(`/opt/meiga/src`) con scripts reversibles que se guardan junto a cada campaña. Desde la v0.8.0 el contenedor tiene
aplicados **tres** parches, en este orden:

| Orden | Parche | Script (en el repositorio) | Archivos | Efecto |
|---|---|---|---|---|
| 1 | PMT de Sidelnik | [`simulations/replica-Sidelnik-500MeV/ajustar_pmt_sidelnik.py`](../simulations/replica-Sidelnik-500MeV/ajustar_pmt_sidelnik.py) | `G4Models/SaltyWCD.cc`, `Framework/Detector/OptDevice.cc` | semielipsoide de Pyrex de 10.16 × 10.16 × 5 cm (antes 10.1 × 10.1 × 6.5 cm) y PMT en la tapa |
| 2 | PMT bajado | [`simulations/AmBe-horizontal-PMT-bajo/bajar_pmt.py`](../simulations/AmBe-horizontal-PMT-bajo/bajar_pmt.py) | `G4Models/SaltyWCD.cc` | `zPMT = 0.3*fWaterHalfHeight`: cara plana a 86.45 cm del fondo del agua (46.55 cm bajo la tapa), la posición de las campañas 1 y 2; **se mantiene la forma de Sidelnik** |
| 3 | Suelo SoilBS | [`simulations/suelo-SoilBS/agregar_suelo.py`](../simulations/suelo-SoilBS/agregar_suelo.py) | `Applications/G4WCDSimulator/G4WCDConstruction.cc` | suelo seco o húmedo bajo el tanque, **solo si** se define `MEIGA_SUELO_W`; sin esa variable MEIGA se comporta como antes |

La posición del PMT bajado es la definitiva para las corridas siguientes. Los paquetes que necesitan el PMT en la
tapa (el montaje Am-Be lateral y los muones VEM del 21 de octubre de 2026) comprueban la posición y se niegan a correr
si no coincide.

## Cómo comprobar el contenedor

Los md5 esperados son los de `src/` con los tres parches aplicados, en el orden de la tabla y sobre el código de esta
versión:

| Archivo | md5 en `src/` (sin parches) | md5 en el contenedor (tres parches) |
|---|---|---|
| `G4Models/SaltyWCD.cc` | `3b4564c61e72fc7fd28ead8b2007398b` | `6315ad35898a914bef4f296a0d897ed7` |
| `Framework/Detector/OptDevice.cc` | `2bb5cd1c8ed7d61705dc977c2cc5cd56` | `f13ccd60e69a673c25046519cab867a6` |
| `Applications/G4WCDSimulator/G4WCDConstruction.cc` | `f1977b6296abd531fdfce8dbb469d82b` | `65e19d1f1eaa1a78916388015daffd67` |

```bash
sudo docker exec silly_roentgen bash -c 'cd /opt/meiga/src && md5sum G4Models/SaltyWCD.cc Framework/Detector/OptDevice.cc Applications/G4WCDSimulator/G4WCDConstruction.cc'
```

Si un md5 no coincide, el código del contenedor se aparta del que documenta el repositorio. Para ver la diferencia,
se copia el archivo fuera del contenedor y se compara con el diff del paso correspondiente.

Los cambios, paso por paso, están en
[`technical-reports/diffs/parches-contenedor-v0.8.0/`](technical-reports/diffs/parches-contenedor-v0.8.0/):
`1-pmt-sidelnik.diff`, `2-pmt-bajo.diff`, `3-suelo-SoilBS.diff` y `estado-final-vs-src.diff` (los tres juntos).

## Variables de entorno del suelo (parche 3)

| Variable | Qué fija | Valor por defecto |
|---|---|---|
| `MEIGA_SUELO_W` | fracción másica de agua del suelo (0 = seco); sin ella no hay suelo | sin suelo |
| `MEIGA_SUELO_XY` | lado del suelo [m] | 5 |
| `MEIGA_SUELO_Z` | profundidad [m] | 1 |
| `MEIGA_SIN_TANQUE` | `1`: no construye el tanque (estudios de albedo) | tanque |
| `MEIGA_SUELO_SEPARACION` | altura del fondo del tanque sobre el suelo [m]; 2 en los experimentos | 0 |

El registro de cada corrida lleva la línea
`[INFO] Suelo SoilBS: material = …, densidad = …, tamano = …, superficie en z = …`.

## Revertir

Para volver a `src/`, se revierte en orden inverso y se recompila:

```bash
cd /opt/Parche-suelo-SoilBS && ./preparar_suelo.sh revertir
python3 /opt/Corrida-AmBe-horizontal-PMT-bajo/bajar_pmt.py /opt/meiga/src --revertir
python3 ajustar_pmt_sidelnik.py /opt/meiga/src --revertir
```
