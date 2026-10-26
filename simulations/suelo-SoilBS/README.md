# Parche de MEIGA: suelo SoilBS seco o húmedo (octubre de 2026)

Agrega a `G4WCDSimulator` el suelo modelo de la tesis (cap. 3, Etapa III): SoilBS de 2.7 g/cm³ con 14 elementos y,
para el suelo húmedo, una mezcla con agua de densidad ρ = (w/1 + (1 − w)/2.7)⁻¹. Se puede usar con el tanque apoyado,
con el tanque a 2 m sobre el suelo, como en los experimentos (`MEIGA_SUELO_SEPARACION=2`), o sin tanque
(`MEIGA_SIN_TANQUE=1`).

Solo cambia `Applications/G4WCDSimulator/G4WCDConstruction.cc` y guarda el original. Sin la variable `MEIGA_SUELO_W`,
MEIGA se comporta exactamente como antes. Las variables, la tabla de densidades y los pasos (`preparar_suelo.sh
aplicar|revertir|estado`, `probar_suelo.sh`) están en `LEEME.md`. El diff y los md5 esperados están en
[`docs/ESTADO_MEIGA_CONTENEDOR.md`](../../docs/ESTADO_MEIGA_CONTENEDOR.md).

Se probó en el contenedor el 2026-10-23 (`probar_suelo.sh`: TODO CORRECTO, sin solapamientos de volúmenes).
