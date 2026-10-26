# Flujo de neutrones emergentes de suelos húmedos y curva de calibración del WCD — sección 4.7 de la tesis

Esta carpeta respalda la Sección 4.7 del capítulo 4 y las partes de los capítulos 2, 3 y 5 y de los apéndices que
dependen de ella:

- Sec. 2.4.3: correspondencia entre la clasificación de energía de la tesis (Tabla 2.2) y la usada en CRNS;
- Secs. 3.4.1 y 3.5.5: corridas del suelo húmedo y barrido rápido en el tanque;
- Sec. 4.7.1–4.7.10: montaje, validación del suelo seco, espectros por humedad, efecto de la humedad y forma de
  Desilets, coeficientes de captura, reflexión, transmisión y otros de 1 meV a 1 GeV (con la comparación con Sidelnik
  et al. 2020), fotones Cherenkov y fotoelectrones de 1 keV a 1 GeV, curva por plegado, curva por simulación directa,
  sensibilidad $S_j$ y alcance;
- apéndices del balance de 1 meV a 1 GeV y de los procesos de los neutrones en el suelo húmedo;
- conclusiones y trabajo futuro (Cap. 5) sobre la calibración en humedad.

Informe técnico con todo el contenido: [`informe/Informe-albedo-suelo.pdf`](informe/Informe-albedo-suelo.pdf)
(37 páginas; fuente `informe/Informe-albedo-suelo.tex`, tablas en `informe/tablas/`, cifras en `informe/cifras*.tex`).

## Normalización

El campo de Bucaramanga (`all_bga_neutron_35.shw`) corresponde a **12 h sobre 1 m²**, verificado con una corrida de
ARTI de 300 s a 956 m (ver [`../flujo-bucaramanga_secciones-4.3-4.5/`](../flujo-bucaramanga_secciones-4.3-4.5/)).
La corriente que baja es J↓ = 25.7 n m⁻² s⁻¹ (`scripts/normalizacion.py`). Las razones $N/N_0$ no dependen de la
normalización; las tasas absolutas y la resolución en humedad sí.

## Corridas que usa

| Corridas | Paquete | Datos (fuera de git) |
|---|---|---|
| Suelo SoilBS seco (50 000 n) y con 5, 10, 15, 25 y 30 % de agua (200 000 n), sin tanque | [`simulations/albedo-suelo/`](../../simulations/albedo-suelo/) con el parche [`simulations/suelo-SoilBS/`](../../simulations/suelo-SoilBS/) | `Corrida-suelo-albedo-resultados/` (12–50 GB por corrida) |
| Barrido monoenergético de 1 keV a 1 GeV por la tapa, cuatro medios | [`simulations/barrido-rapidos-WCD/`](../../simulations/barrido-rapidos-WCD/) | `Barrido-rapidos-WCD-resultados/` y `…-2.5-5/` (≈7 GB) |
| Los neutrones que suben de cada suelo, inyectados en el WCD por la base y el costado, 10⁵ por suelo y medio | [`simulations/tanque-albedo/`](../../simulations/tanque-albedo/) | `Corrida-tanque-albedo-resultados-2.5-5/` (24 corridas, 17.8 GB) |
| Campaña 1 (1 meV–1 keV), cuatro medios | — | se leen las tablas ya versionadas en `analysis/revision-tesis_2026-10/` y `analysis/campana-1_respuesta-electromagnetica_seccion-4.2/` |

Los manifiestos (archivos, bytes y md5 del listado de cada carpeta) están en
[`data/manifiestos/corridas-v0.9.0.tsv`](../../data/manifiestos/corridas-v0.9.0.tsv).

## Scripts (`scripts/`)

| Script | Qué hace | Salidas principales |
|---|---|---|
| `actualizar_informe.sh [carpeta del suelo]` | Corre todo en orden y compila el informe | todo lo de abajo |
| `normalizacion.py` | Tiempo de exposición (12 h) y J↓ | — |
| `regiones.py` | Regiones de energía de la Tabla 2.2 y su correspondencia con CRNS | — |
| `generar_incidencia_suelo.py` | Muestrea los 200 000 neutrones que bajan sobre el suelo (semilla 20261023) | flujo del paquete `albedo-suelo` |
| `analizar_albedo.py` | Espectro que sube por humedad, albedo y origen (reflejado o creado) | `resultados/espectros_albedo*.tsv`, `albedo_suelo*.json`, fig01–04, fig11–12 |
| `curva_humedad.py` | Cocientes húmedo/seco por región y ajustes de Desilets | `resultados/curva_humedad.json`, tablas `regiones`, `ajustes`, `desilets`, `cifras.tex` |
| `procesos_neutrones.py` | Procesos, destino, creación y capturas de los neutrones en el suelo | `resultados/procesos_neutrones.json`, tablas `procesos`, `destino`, `creados`, `capturas`, `origen` |
| `graficas_espectros.py` | Espectros por humedad y su relación con θ | fig05–08 |
| `curva_calibracion_wcd.py` | Curva de calibración por plegado (Campaña 1 + barrido rápido) | `resultados/curva_calibracion_wcd.json`, fig09–10, tablas `calibracion_*`, `cuentas_banda` |
| `balance_rapidos.py <barrido…>` | Destino del neutrón incidente en el barrido (última frontera del volumen activo) | `resultados/balance_rapidos.tsv` |
| `captura_wcd.py` | Coeficientes η de captura, reflexión, transmisión y otros de 1 meV a 1 GeV y ganancia relativa | `resultados/captura_wcd.json`, fig15–18, tablas `captura_wcd`, `captura_relativa`, `balance_*`, `cifras_captura.tex` |
| `captura_definiciones.py <barrido…>` | Cuatro definiciones de la captura (comparación con Sidelnik et al. 2020) | `resultados/capturas_definiciones.tsv`, tabla `capturas_definiciones` |
| `luz_barrido.py <barrido…>` | Fotones Cherenkov aceptados y fotoelectrones por neutrón | `resultados/luz_barrido.json`, `resultados/luz_barrido/*.npz`, fig22–24, tabla `luz_barrido` |
| `generar_entrada_tanque.py` | Neutrones que suben, sorteados sobre la base y el costado del tanque (semilla 20261026) | flujos del paquete `tanque-albedo`, `entrada_tanque.json` |
| `curva_calibracion_tanque.py` | Curva de calibración por simulación directa | `resultados/curva_calibracion_tanque.json`, `eficiencia_base_costado.tsv`, fig13–14, tablas `calibracion_directa*` |
| `sensibilidad.py` | Sensibilidad $S_j(\theta_v)$ (Ec. 4.130) y resolución estadística σθ | `resultados/sensibilidad.json`, fig25, tabla `sensibilidad` |
| `esquemas.py` | Esquemas del montaje (suelo seco, suelo húmedo, WCD sobre el suelo) | fig19–21 |

### Datos de entrada (variables de entorno)

Los datos de las corridas no están en git. Los scripts los buscan con estas variables:

| Variable | Qué es |
|---|---|
| `ALL_BGA_SHW` | `all_bga_neutron_35.shw` (campo de Bucaramanga, 1 891 124 neutrones; sha256 en `data/manifiestos/`) |
| `SUELO_RES` | carpeta `Corrida-suelo-albedo-resultados` (argumento de `actualizar_informe.sh`) |
| `RAPIDOS_RES` | carpetas del barrido rápido, separadas por `:` |
| `TANQUE_RES` | carpeta `Corrida-tanque-albedo-resultados-2.5-5` |
| `FLUJO_BAJA` | `200000N-Bga-baja-sobre-suelo.txt` (se regenera con `generar_incidencia_suelo.py`) |
| `REPO_TESIS` | raíz de este repositorio (por defecto se deduce de la ubicación del script) |

Sin los datos crudos, los scripts que solo leen `resultados/` (por ejemplo `captura_wcd.py`, `sensibilidad.py`,
`curva_calibracion_wcd.py`) rehacen las figuras y las tablas con los resúmenes versionados.

## Resultados principales

| Medio | Caída de las cuentas, seco → 30 % de agua (Q ≥ 1 p.e.) | | Sensibilidad media $\bar S$ (plegado) |
|---|---|---|---|
| | plegado | simulación directa | |
| Agua pura | 8.6 % | 10.0 % | 0.167 |
| 2.5 % NaCl | 9.4 % | 10.9 % | 0.185 |
| 5 % NaCl | 9.9 % | 11.3 % | 0.193 |
| 10 % NaCl | 10.4 % | 11.6 % | 0.204 |

- Con 30 % de agua, el flujo que sube en los intermedios baja a 0.550 del seco y en los rápidos a 0.423; los térmicos
  suben un 42 %. La banda más sensible es 0.1–3 MeV.
- Cerca de dos tercios de las cuentas vienen del flujo que baja, que no depende del suelo; el NaCl y la ventana de
  carga 1 ≤ Q < 20 p.e. son las dos maneras de aumentar la sensibilidad (hasta 13.2 % de caída con 10 % NaCl).
- El coeficiente de captura del neutrón incidente va de 17.4 % (1 meV) a 62.8 % (5 MeV) en agua pura y de 28.1 a
  68.8 % con 10 % NaCl; desde 20 MeV domina la interacción inelástica.
- Son cotas superiores: solo se simulan neutrones; el fondo de muones y de la componente electromagnética no está
  incluido.

## Qué no se versiona

- `resultados/neutrones_que_suben/` (14 MB): caché de los cruces del plano, regenerable con `generar_entrada_tanque.py`
  a partir de las corridas del suelo.
- Los flujos de 200 000 y 100 000 neutrones de los paquetes (regenerables con semilla; sha256 en
  `data/manifiestos/excluidos-v0.9.0.sha256`).
- Las corridas crudas (decenas de GB; manifiestos en `data/manifiestos/corridas-v0.9.0.tsv`).
