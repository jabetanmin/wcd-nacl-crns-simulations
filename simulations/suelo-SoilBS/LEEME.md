# Parche MEIGA: suelo SoilBS (seco y húmedo) bajo el tanque

Agrega a `G4WCDSimulator` el suelo modelo de la tesis (cap. 3, Etapa III), con el tanque **apoyado sobre el suelo** o
**a 2 m sobre él, como en los experimentos** (`MEIGA_SUELO_SEPARACION=2`), o sin tanque (solo el suelo).

## El suelo

| Propiedad | Valor |
|---|---|
| Material seco | **SoilBS**, 2.7 g/cm³ (Ariza Gómez y Carrillo Moreno 2020, Tabla 3; Juárez Sanz et al. 2006; densidad de Köhli et al. 2015) |
| Composición (fracción másica) | O 0.4900 · Si 0.3300 · Al 0.0713 · Fe 0.0380 · C 0.0200 · Ca 0.0137 · K 0.0136 · Na 0.0063 · Mg 0.0060 · Ti 0.0046 · H 0.0038 · N 0.0010 · P 0.0009 · S 0.0008 (14 elementos, suma 1.0000) |
| Suelo húmedo | mezcla SoilBS (1 − w) + agua (w), ρ = (w/1.0 + (1 − w)/2.7)⁻¹ g/cm³ (volúmenes aditivos, ec. de la tesis) |
| Geometría | caja de 5 × 5 m y 1 m de profundidad (groundSizeX/Y/Z de MEIGA; como en la tesis, 1 m), centrada bajo el tanque, con la cara superior en z = −separación (0: tanque apoyado; 2 m en los experimentos) |
| Agua del suelo | su hidrógeno usa el elemento `TS_H_of_Water` de MEIGA (el mismo del agua del tanque) |

| w (agua) | 0 | 0.05 | 0.10 | 0.15 | 0.25 | 0.30 |
|---|---|---|---|---|---|---|
| ρ [g/cm³] | 2.700 | 2.488 | 2.308 | 2.151 | 1.895 | 1.788 |
| θ_w (agua en volumen) | 0 | 0.124 | 0.231 | 0.323 | 0.474 | 0.536 |

## Cómo se activa

El suelo solo aparece si se define la variable de entorno **`MEIGA_SUELO_W`** (fracción másica de agua). Sin ella,
MEIGA hace exactamente lo mismo que antes, así que **los demás paquetes siguen funcionando con el parche aplicado**.

| Variable | Qué fija |
|---|---|
| `MEIGA_SUELO_W=0` | suelo seco |
| `MEIGA_SUELO_W=0.10` | suelo con 10 % de agua en masa (0.05, 0.10, 0.15, 0.25, 0.30 como en la tesis) |
| `MEIGA_SUELO_XY=10` | (opcional) lado del suelo en m |
| `MEIGA_SUELO_Z=1` | (opcional) profundidad en m |
| `MEIGA_SIN_TANQUE=1` | (opcional) no construye el tanque: solo el suelo (estudios de albedo) |
| `MEIGA_SUELO_SEPARACION=2` | (opcional) altura del fondo del tanque sobre el suelo, en m; **2 en los experimentos**; 0 por defecto. El tanque no se mueve (su fondo sigue en z = 0): el suelo baja a z = −2 m |

Ejemplo con cualquier paquete de corrida:

```bash
sudo docker exec -d silly_roentgen bash -ic 'cd /opt/<paquete> && MEIGA_SUELO_W=0.10 MEIGA_SUELO_SEPARACION=2 ./ejecutar_corrida.sh agua-pura completa 4 > corrida.log 2>&1'
```

El registro de MEIGA de cada parte lleva la línea `[INFO] Suelo SoilBS: material = …, densidad = …` para
comprobar qué suelo se usó.

## Pasos (cuando termine la corrida de 10 %)

**0. Que no haya ninguna simulación corriendo:**

```bash
sudo docker exec silly_roentgen bash -c 'pgrep -c G4WCDSimulator'
```

Debe dar 0.

**1. Copiar el parche al contenedor** (portátil):

```bash
sudo docker cp "/media/jaime/TOSHIBA EXT/Parche-suelo-SoilBS.zip" silly_roentgen:/opt/
```

**2. Aplicar y recompilar** (dentro del contenedor, `sudo docker exec -it silly_roentgen bash`):

```bash
cd /opt && unzip -o Parche-suelo-SoilBS.zip && cd Parche-suelo-SoilBS && ./preparar_suelo.sh aplicar
```

Debe terminar con `== Listo: MEIGA compilado (Suelo SoilBS: APLICADO).` Si el código del contenedor no es el
esperado, el script no cambia nada y lo dice.

**3. Prueba** (dentro del contenedor; 30 neutrones térmicos que caen sobre el suelo, fuera del tanque, en cuatro casos:
sin suelo, seco, 10 % de agua, 25 % de agua sin tanque y 10 % de agua con el tanque a 2 m; con `CheckOverlaps` activado):

```bash
./probar_suelo.sh
```

Debe terminar con **TODO CORRECTO**: sin suelo no hay pasos en el suelo; seco, `material = SoilBS` y 2.7 g/cm³;
húmedo, `SoilBS_agua0.100` y 2.30769 g/cm³; sin tanque, la línea `SIN TANQUE`; a 2 m, `superficie en z = -2 m`; ninguna corrida con
solapamiento de volúmenes. Mande la captura.

**Para quitarlo** (vuelve el archivo original exacto y recompila):

```bash
cd /opt/Parche-suelo-SoilBS && ./preparar_suelo.sh revertir
```

## Archivos

| Archivo | Qué hace |
|---|---|
| `agregar_suelo.py` | cambia solo `Applications/G4WCDSimulator/G4WCDConstruction.cc` (guarda el original); `--revertir`, `--estado` |
| `preparar_suelo.sh aplicar\|revertir\|estado` | aplica o revierte y recompila (se niega si hay una simulación corriendo) |
| `probar_suelo.sh` | la prueba de 30 neutrones en tres casos |
| `prueba/30N-termicos-sobre-suelo.txt` | 30 neutrones de 25 meV, verticales hacia abajo desde z = 150 cm, 0.7–2 m al costado del tanque |
| `configuracion/` | DetectorList del montaje (agua pura) y plantilla con `CheckOverlaps` activado |

**Compatible con el PMT bajado:** este parche toca otro archivo (`G4WCDConstruction.cc`, no `SaltyWCD.cc`), así que
se puede usar con el PMT en la tapa o bajado.
