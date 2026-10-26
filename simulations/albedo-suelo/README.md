# Albedo del suelo SoilBS con distintas humedades (octubre de 2026)

200 000 neutrones de los que bajan en Bucaramanga (`all_bga_neutron_35.shw`) inciden sobre un suelo SoilBS de
20 × 20 × 1 m, sin tanque. Las humedades son 5, 10, 15, 25 y 30 % en masa, y se usa el
[parche del suelo](../suelo-SoilBS/). Un plano virtual a 5 cm sobre el suelo cuenta los neutrones que lo cruzan y se
sigue cada paso de cada neutrón. Análisis:
[`analysis/suelo-humedo-calibracion_seccion-4.7/`](../../analysis/suelo-humedo-calibracion_seccion-4.7/).

`ejecutar_suelo.sh <seco|humedo-5|humedo-10|humedo-15|humedo-25|humedo-30> <prueba|completa> [PARTES]`. Las pruebas
de 30 neutrones y las corridas completas (≈5 h y 40–50 GB cada una) se describen en `LEEME.md`. El suelo seco se corrió
en modo `validacion` (los mismos 50 000 neutrones que la parte 1 de cada humedad): coincide con la curva "Sube" de la
tesis por debajo de 10 MeV y es la referencia de los cocientes húmedo/seco. Las seis corridas están completas;
manifiestos en [`data/manifiestos/corridas-v0.9.0.tsv`](../../data/manifiestos/corridas-v0.9.0.tsv).

El archivo de 200 000 neutrones no se versiona. Se regenera byte a byte con `generar_incidencia_suelo.py` (semilla
20261023); ver [`data/manifiestos/flujos-regenerables.sha256`](../../data/manifiestos/flujos-regenerables.sha256).
