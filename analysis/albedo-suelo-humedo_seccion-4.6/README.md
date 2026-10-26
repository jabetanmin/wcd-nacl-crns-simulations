# Albedo de neutrones de un suelo SoilBS húmedo (Etapa III, Sec. 4.6) — en curso

El flujo de neutrones que baja sobre Bucaramanga (curva "Baja" de la tesis, `all_bga_neutron_35.shw`) incide sobre
un suelo SoilBS húmedo. Se mide el espectro que sube (el albedo) y el origen de cada neutrón que sube: si es el
incidente reflejado o uno creado en el suelo. La referencia del suelo seco es la curva "Sube" de la tesis.

| Aspecto | Valor |
|---|---|
| Neutrones | 200 000 de los 1 111 010 que bajan en `all_bga_neutron_35.shw` (semilla 20261023), con su energía y dirección originales |
| Distribución | uniforme en x, y ∈ [−8.5, 8.5] m, a 6 cm sobre el suelo |
| Suelo | SoilBS de 20 × 20 × 1 m, w = 0.05, 0.10, 0.15, 0.25 y 0.30 (parche [`simulations/suelo-SoilBS/`](../../simulations/suelo-SoilBS/)), sin tanque |
| Contador | plano virtual a 5 cm sobre el suelo |
| Física | `QGSP_BERT_HP_NoThermal` (sin S(α,β)) |

Corridas: [`simulations/albedo-suelo/`](../../simulations/albedo-suelo/). Cada humedad tarda unas 5 h y ocupa unos
35 GB.

## Scripts

| Script | Qué hace |
|---|---|
| `generar_incidencia_suelo.py <all_bga_neutron_35.shw>` | archivo de 200 000 neutrones y la prueba de 30 (los 10 de menor energía, 10 intermedios y los 10 de mayor) |
| `analizar_albedo.py --corrida <etiqueta>=<carpeta> …` | cruces del plano, espectro letárgico que sube (normalizado como la figura de la tesis, J_baja = 308.6 n m⁻² s⁻¹), origen de los neutrones que suben y tabla por región; la ruta del `.shw` se da con `--shw` o `ALL_BGA_SHW` |

## Estado

El paquete y el análisis están listos. Las corridas de las cinco humedades están en marcha; el informe y la curva de
calibración del tanque (los espectros de albedo inyectados en el WCD a 2 m sobre el suelo) vendrán en versiones
siguientes.
