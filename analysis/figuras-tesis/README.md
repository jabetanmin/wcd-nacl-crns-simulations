# Generadores de las figuras regeneradas de la tesis

Scripts que producen las figuras de la carpeta `Figuras-corregidas/` de la tesis a partir de fórmulas,
datos de simulación o del código del simulador, en sustitución de figuras antiguas o redibujadas.

| Script | Figuras |
|---|---|
| `regenerar_figuras.py` | líneas gamma de captura, niveles del ¹⁷O, deuterones, captura relativa (Fig. 4.27) |
| `regenerar_figuras_2.py` | umbral Cherenkov, Klein–Nishina, fotones Cherenkov por electrón (Fig. 2.16), dispersiones elásticas, QE del PMT |
| `regenerar_esquemas.py` | esquemas (ARTI, contador de ³He, suelo, procesos) y trayectorias de neutrones en el WCD |
| `regenerar_flujo_ARTI_seccion_4_4.py` | flujo por unidad de letargía de ARTI de la Sec. 4.4 (Fig. 4.62), normalizado a 1 m² y 3600 s |

Las figuras del balance por caras del tanque (Figs. 4.25 y 4.26) las genera
[`../revision-tesis_2026-10/balance_caras_tanque.py`](../revision-tesis_2026-10/balance_caras_tanque.py).

Las carpetas de datos se indican con variables de entorno (`DATOS_NEUTRONES_TERMICOS`,
`DATOS_NEUTRONES_BGA`, `DATOS_ESPECTROS_500MEV`); los `.tsv` de esta carpeta son datos auxiliares
pequeños (tablas digitalizadas y resúmenes). Uso: `python3 <script> <carpeta de salida>`.
