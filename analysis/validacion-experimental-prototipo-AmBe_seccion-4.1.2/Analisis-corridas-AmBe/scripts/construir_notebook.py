#!/usr/bin/env python3
"""Construye Analisis-corridas-AmBe.ipynb (texto + ejecución de los scripts)."""
import os, nbformat as nbf
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
fig = lambda n: code(f"from IPython.display import Image\nImage('figuras/{n}.png', width=820)")
C = [
md("# Corridas MEIGA con la fuente $^{241}$Am-Be: comparación de medios y escalado al montaje blindado\n\n"
   "Corridas recuperadas del TOSHIBA y extraídas al ADATA (`ADATA HD330/Simulacion-fuente-241AmBe/`): agua pura, 2.5 % y 10 % NaCl, "
   "**1 637 458 neutrones cada una**, inyección `eCircle` (r = 0.2 m, z = 1.5 m) **vertical por la tapa**, QGSP_BERT_HP sin S(α,β). "
   "Archivo de entrada: `Espectro-completo-neutrones-fuente-AmBe241.txt` (437 energías, sesgado). Agua pura: solo `output.json` y archivos procesados.\n\n"
   "Informe: `informe/Informe-corridas-AmBe.pdf`."),
md("## 1. Extracción (requiere el ADATA conectado; ya hecha)\n`scripts/extraer_carga.py` (carga y E0 por evento desde `output.json`) y "
   "`scripts/procesar_pasos.sh` (resumen por evento, capturas, residuos, gammas de captura; solo NaCl). Las celdas se omiten si los resultados existen."),
code("import os, subprocess, sys, runpy, json\n"
     "if not os.path.exists('resultados/carga_nacl10.npz'):\n    runpy.run_path('scripts/extraer_carga.py', run_name='__main__')\n"
     "if not os.path.exists('resultados/eventos_nacl10.tsv.gz'):\n    subprocess.run(['bash', 'scripts/procesar_pasos.sh'], check=True)\n"
     "sorted(os.listdir('resultados'))"),
md("## 2. Análisis, reponderación al ISO 8529 y escalado\nCada evento se pondera con $w_j = P_{ISO}(\\text{celda}_j)/(n_j/N)$, lo que lleva la energía media de 4.064 a 4.211 MeV (ISO 4.211). "
   "Halo y fondo usan la respuesta de la Campaña 1 (misma inyección por la tapa) promediada con su espectro."),
code("runpy.run_path('scripts/analizar_corridas.py', run_name='__main__');"),
fig("fig06_reponderacion"),
md("### Comparación de medios\nLa reponderación cambia la eficiencia unos 0.3 puntos y la carga menos del 2 %. El NaCl aumenta la eficiencia $Q\\geq1$ por neutrón "
   "(36.4 → 42.2 → 49.4 %) y, sobre todo, las señales grandes ($Q\\geq20$: ×13 y ×27). "
   "En 2.5/10 % el ³⁵Cl concentra el 35.5/67.4 % de las capturas, como en las corridas de 500 MeV. ⟨Q|Q≥1⟩ (3.54/7.79/11.16 p.e.) es coherente con la Campaña 1."),
fig("fig01_respuesta_vs_energia"), fig("fig02_histograma_carga"), fig("fig03_nucleo_profundidad"), fig("fig04_gammas_captura"),
code("d = json.load(open('resultados/resumen_corridas.json'))\n"
     "{m: {k: d['corridas'][m][k] for k in ('eps_Q1', 'Q_media_senal', 'eta_cap')} for m in d['corridas']}"),
md("### Captura del haz en agua pura (estimada)\nSin archivos de pasos, $\\eta_{cap}$ se estima con dos métodos (eficiencia medida + probabilidades condicionales de 2.5 %; "
   "cociente agua pura/2.5 % de la Campaña 1): 59.4 % y 54.3 %, se adopta (56.9 ± 2.6) %."),
md("## 3. Escalado a los 373 272 neutrones del montaje blindado (5 min, 1 Ci)"),
code("import pandas as pd\npd.read_csv('resultados/escalado_373272.tsv', sep='\\t')"),
fig("fig05_escalado_componentes"),
md("**Resultado:** 88 287 / 107 258 / 136 065 eventos con señal en 5 min (agua pura / 2.5 % / 10 %), es decir 294 / 358 / 454 s⁻¹. "
   "Frente a agua pura, el NaCl multiplica las señales por 1.21 y 1.54, la carga total por 2.75 y 4.95 y los eventos con Q ≥ 20 p.e. por 20 y 44.\n\n"
   "> **Salvedad:** todas las corridas usadas inyectan por la tapa, mientras que el montaje real irradia por el costado (el PMT está en la tapa). Los absolutos son una estimación; "
   "los cocientes NaCl/agua pura son más robustos. Para la cifra definitiva hay que correr en MEIGA el archivo de 373 272 neutrones."),
md("## 4. Histograma de carga y comparación con el detector prototipo\n"
   "`datos/histogramas_comparados.txt` del notebook `analisis-datos-Flujo-Completo-Bga.ipynb` (TOSHIBA, `Detector-prototipo/Nuevo-analisis/`) "
   "es exactamente el histograma de carga de las corridas Am-Be. Aquí se construye además el histograma esperado del montaje en 5 min y se compara "
   "con las tomas LAGO del prototipo, con el mismo algoritmo de carga del notebook (ventana positiva alrededor de la muestra 8, pico > 1200 ADC) "
   "y la calibración 3.95 p.e./1000 ADC. Las tomas duran 300 s, salvo `10_neutrones`, que dura **240 s**: la resta fuente − fondo se normaliza por tiempo."),
code("if not os.path.exists('resultados/experimento_cargas.npz'):\n    runpy.run_path('scripts/procesar_experimento.py', run_name='__main__')\n"
     "json.load(open('resultados/experimento_tomas.json'))"),
code("runpy.run_path('scripts/comparar_exp_sim.py', run_name='__main__');"),
fig("fig07_histograma_carga_simulado"), fig("fig09_reproduccion_notebook"), fig("fig08_experimento_vs_simulacion"), fig("fig10_forma_exp_vs_sim"),
md("**Resultados:** (1) el pico de muones del fondo cae en 154–162 p.e. en los tres medios, así que la calibración vale aunque cambien el umbral (800/1000/1080) y la HV; "
   "(2) por encima de 10 p.e. el experimento tiene 28 / 21 / 39 veces más cuentas netas que el montaje modelado (373 272 n), lo que equivale a ~8–15 millones de neutrones incidentes en 5 min (1.2–2.2 % de 1 Ci); "
   "(3) la forma en NaCl coincide entre 20 y 60 p.e., pero en agua pura el experimento tiene una cola mucho más larga que la simulación (casi igual a la de NaCl): "
   "hay una componente de la señal que no depende del medio y que no está simulada (¿gammas de 4.44 MeV de la fuente, neutrones por el costado?); "
   "(4) el NaCl aumenta las cuentas con Q ≥ 20 p.e. ×5.4 y ×22 en el experimento, frente a ×20 y ×44 en la simulación."),
md("## 5. Histogramas sin fondo y neutrones por medio\n"
   "Se reproducen exactamente los `Diferencia-datos-A-*.dat` de `Detector-prototipo/Comparacion-robusta-fondo-neutrones-*` "
   "(carga = parte positiva de toda la traza, línea base = mediana de las 20 primeras muestras, todos los disparos). Luego se normalizan por tiempo a 300 s "
   "(la toma con fuente de 10 % dura 240 s). Detectados: Q ≥ 12 p.e.; incidentes = detectados / eficiencia simulada; capturados = incidentes × capturas por neutrón."),
code("runpy.run_path('scripts/histogramas_sin_fondo.py', run_name='__main__');\n"
     "pd.DataFrame(json.load(open('resultados/sin_fondo_resumen.json'))['medios']).T[['detectados_300s','neutrones_incidentes_300s','pct_de_emitidos_1Ci',"
     "'neutrones_capturados_300s','P_captura_dado_detectado','carga_media_detectados_pe','carga_media_sim_pe']]"),
fig("fig11_sin_fondo_reproduccion"), fig("fig12_sin_fondo_normalizado"),
md("**Resultado (5 min):** detectados 258 817 / 895 347 / 2 763 180; incidentes 36.6 / 14.8 / 21.9 M (5.5 / 2.2 / 3.3 % de 1 Ci); "
   "capturados 15.2 / 6.8 / 11.8 M (agua pura / 2.5 % / 10 %). La forma coincide con la simulación en los tres medios; "
   "el número de incidentes debería ser igual en los tres y no lo es (×2.5)."),
code("runpy.run_path('scripts/escribir_informe.py', run_name='__main__')"),
]
nb = nbf.v4.new_notebook(); nb.cells = C
nbf.write(nb, os.path.join(BASE, "Analisis-corridas-AmBe.ipynb"))
