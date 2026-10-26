#!/usr/bin/env python3
"""Construye Analisis-fuente-AmBe.ipynb: texto del análisis + ejecución de los scripts."""
import os, nbformat as nbf
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
fig = lambda n: code(f"from IPython.display import Image\nImage('figuras/{n}.png', width=780)")
C = [
md("# Análisis del espectro de la fuente de neutrones $^{241}$Am-Be (entrada de MEIGA)\n\n"
   "Revisión de la carpeta `Simulacion-fuente-241AmBe` (los archivos originales no se modifican). "
   "El informe completo está en `informe/Informe-fuente-AmBe241.pdf`.\n\n"
   "**Cadena original** (`simulacion-241-AmBe.ipynb`): puntos digitalizados $(E_i,y_i)$ → $n_i=\\mathrm{round}(|y_i|\\cdot2.5\\times10^6)$ "
   "→ cada $E_i$ repetida $n_i$ veces → $p_z=\\sqrt{(T+m_n)^2-m_n^2}$ en GeV/c → `13 0 0 pz 0 0 0 0 0 0 0 0` (1 637 458 neutrones)."),
md("## 1. Diagnóstico, espectro limpio y fuente original\n`scripts/analizar_fuente.py` escribe `resultados/resumen.json` y las figuras 1–7."),
code("import runpy, json\nrunpy.run_path('scripts/analizar_fuente.py', run_name='__main__');"),
md("### Digitalización principal\n667 puntos, no ordenados en $E$ (193 pasos hacia atrás, 437 energías distintas), "
   "28 puntos espurios (6.2 % de los neutrones de la fuente) y 3 valores negativos convertidos con `abs`."),
fig("fig01_digitalizacion_espurios"), fig("fig02_orden_digitalizacion"),
md("### Espectro limpio\n$\\langle E\\rangle = 4.15$ MeV (ISO 8529-1: 4.16 MeV), máximos en 3.03, 4.88, 6.33, 7.47 y 9.53 MeV. "
   "Archivo: `resultados/espectro_AmBe_limpio.txt`.\n\n> La procedencia de la figura digitalizada no está registrada en la carpeta: hay que citarla en la tesis."),
md("### Sesgo por densidad de puntos\nEl notebook asigna $n_i\\propto y_i$ a *cada punto*; el número correcto es $\\propto S(E)\\,\\Delta E$. "
   "La razón fuente/limpio (0.54–1.35 por bin de 0.25 MeV) sigue al número de puntos por bin (correlación 0.97); "
   "por encima de 8 MeV faltan un 17 % de neutrones y $\\langle E\\rangle$ queda en 4.06 MeV."),
fig("fig03_fuente_vs_limpio"),
md("### Espectro discreto\nLa fuente es un peine de 437 energías: los picos de las figuras *Geant4 (suavizado)* son este artefacto. "
   "Además, esa curva es el archivo de **entrada**, no una salida de Geant4."),
fig("fig04_fuente_discreta"),
md("### Orden del archivo\nLos neutrones están en el orden de la digitalización: el primer 1 % tiene $\\langle E\\rangle=0.12$ MeV, "
   "el primer 50 % llega solo a 4.17 MeV. **Verificar si alguna corrida usó solo parte del archivo.** "
   "Dirección: todos en $+z$ (haz pincel)."),
fig("fig07_sesgo_orden"),
md("## 2. Segunda digitalización (eje $y$ invertido)\nCorrelación con $S(E)$ = −0.997. Invertir el orden de la columna (`col2[::-1]`, "
   "`Funcion-espectro-AmBe-241-final.txt`) refleja el espectro en energía y **no** lo corrige (correlación 0.32); lo correcto es $y'=(a-y)/|b|$."),
fig("fig05_segunda_digitalizacion"),
md("## 3. Curvas de referencia\n`AmBe_IAEA.txt` es un triángulo de valores redondos (máximo único en 3.5 MeV), no un espectro IAEA/ISO; "
   "`AmBe_ISO8529_spectrum.txt` y `AmBe_neutron_spectrum.txt` son curvas analíticas con $\\langle E\\rangle$ = 3.47 y 2.22 MeV, tampoco ISO 8529-1."),
fig("fig06_referencias"),
md("## 4. Fuente corregida\n`scripts/generar_fuente.py` muestrea $S(E)$ (energías continuas, orden aleatorio, mismo formato). "
   "Opciones: `-n`, `--semilla`, `--direccion +z|-z|+x|iso`. Se omite si el archivo ya existe."),
code("import os, subprocess, sys\nf = 'resultados/Fuente-AmBe241-corregida-1637458n.txt'\n"
     "if not os.path.exists(f):\n    subprocess.run([sys.executable, 'scripts/generar_fuente.py'], check=True)\n"
     "runpy.run_path('scripts/validar_fuente.py', run_name='__main__');"),
fig("fig08_validacion_fuente_corregida"),
md("## 5. Espectro de referencia ISO 8529 digitalizado\n"
   "Figura ISO 8529 del espectro $^{241}$Am-Be ($B_E\\cdot E$ frente a $E$ en escala log) tomada de la lámina 26 de la presentación IAEA "
   "*Establishing neutron calibrations at SSDL using ISO 8529 radionuclide sources* (imagen en `referencia_ISO8529/`). "
   "`scripts/digitalizar_iso8529.py` la digitaliza por píxeles (47 grupos, 0.1–10.84 MeV): calibración $y$ lineal con las marcas del eje "
   "y $x$ interpolando $\\log_{10}E$ entre todas las marcas, porque las décadas del dibujo tienen anchos distintos. Los escalones más angostos que el trazo "
   "se recuperan intersectando los intervalos de las columnas vecinas.\n\n"
   "$\\langle E\\rangle$ = 4.21 MeV (ISO 8529-1:2021: 4.17 MeV para fuente pequeña). La digitalización previa de la carpeta coincide con este espectro "
   "(fracciones por banda iguales con diferencias de ≈1 punto porcentual): era el espectro ISO."),
code("runpy.run_path('scripts/digitalizar_iso8529.py', run_name='__main__');\n"
     "runpy.run_path('scripts/comparar_iso8529.py', run_name='__main__');"),
fig("fig09_digitalizacion_ISO8529"), fig("fig10_iso8529_vs_previa"),
md("## 6. Irradiación del tanque: 1 Ci durante 5 minutos, fuente a 10 cm\n"
   "`scripts/generar_irradiacion.py`: $Q = 3.7\\times10^{10}$ Bq × $6\\times10^{-5}$ n s$^{-1}$Bq$^{-1}$ = $2.22\\times10^6$ n/s (ISO 8529-1:2021, valor indicativo); "
   "$N\\sim$ Poisson($Q\\cdot300$ s). Fuente puntual isótropa en $(-58.062, 0, 66.562)$ cm: 10 cm fuera de la pared exterior ($R_{ext}$ = 48.062 cm) y a media altura del agua. "
   "Solo se escriben los neutrones cuya dirección corta el tanque, en archivos de $10^6$ líneas, formato `13 px py pz x y z 0 0 0 0 0` con **pz invertido** "
   "(MEIGA usa $-p_z$) y `injectionMode eFromFile` (ver `configuracion/DetectorList-AmBe-d10cm.xml`). Cada parte es una muestra aleatoria del total."),
code("import json\nr = json.load(open('resultados/Irradiacion-AmBe-1Ci-300s-d10cm/resumen.json'))\n"
     "{k: v for k, v in r.items() if not k.startswith('hist')}"),
code("runpy.run_path('scripts/validar_irradiacion.py', run_name='__main__');"),
fig("fig11_validacion_irradiacion"),
md("## 7. Montaje blindado: haz, halo y fondo\n"
   "Caja de polietileno con canal de 3 cm × 30 cm y 10 cm de plomo pegado al tanque (fuente a 40 cm de la pared). "
   "Haz del canal: semiángulo 2.86°, 0.062 % de la emisión, mancha de 4 cm (12.6 cm²). "
   "`scripts/blindaje_fuga.py` estima por atenuación entre 4×10⁴ y 7.5×10⁵ neutrones rápidos al tanque, en su mayoría fuga por el polietileno.\n\n"
   "Modelo adoptado por el autor (`scripts/generar_irradiacion_compuesta.py`), como fracción de lo que entra al tanque: "
   "**haz** 35 % (ISO 8529, cono de 2.86°), **halo** 45 % (0.5 eV–100 keV, 1/E, cara del plomo, 0–90° ley del coseno), "
   "**fondo** 20 % (1e-4–0.5 eV, maxwelliano kT = 25.3 meV, plano 96×133 cm, hemisferio isótropo). "
   "Normalización: haz = Q·Ω/4π·0.313·300 s = 1.30×10⁵, total = haz/0.35 = **373 272 neutrones** en 5 min."),
code("runpy.run_path('scripts/blindaje_fuga.py', run_name='__main__');"),
code("import json\nr = json.load(open('resultados/Irradiacion-AmBe-blindada-1Ci-300s/resumen.json'))\nr['componentes']"),
code("runpy.run_path('scripts/validar_irradiacion_compuesta.py', run_name='__main__');"),
fig("fig12_irradiacion_compuesta"),
md("## 8. Conclusiones\n1. Formato y conversión $T\\to p$ correctos.\n"
   "2. El espectro digitalizado limpio es un Am-Be realista ($\\langle E\\rangle$ 4.15 vs 4.16 MeV ISO).\n"
   "3. La fuente original lo distorsiona (densidad de puntos, 28 espurios, 437 líneas) y está ordenada.\n"
   "4. Las curvas IAEA/ISO de la carpeta no son referencias reales; la segunda digitalización tiene el eje $y$ invertido.\n"
   "5. Usar `resultados/Fuente-AmBe241-corregida-1637458n.txt` ($\\chi^2$/ndf = 218/214) y declarar procedencia y geometría de emisión.\\n"
   "6. Para irradiar el tanque: `resultados/Irradiacion-AmBe-1Ci-300s-d10cm/` (espectro ISO 8529, 1 Ci, 5 min, 10 cm). Simular una fracción de las partes y escalar por $N_{tanque}/N_{simulados}$.\\n"
   "7. Montaje blindado (haz/halo/fondo 35/45/20 %): `resultados/Irradiacion-AmBe-blindada-1Ci-300s/` con 373 272 neutrones, una sola corrida de MEIGA."),
]
nb.cells = C
nbf.write(nb, os.path.join(BASE, "Analisis-fuente-AmBe.ipynb"))
