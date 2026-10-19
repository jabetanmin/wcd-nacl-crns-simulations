#!/usr/bin/env python3
"""Construye Analisis-Sidelnik-500MeV.ipynb a partir de los scripts de esta carpeta.

Las celdas de analisis contienen el codigo de cada script tal cual (con sys.argv y __file__ fijados antes),
asi que el notebook y los scripts tienen exactamente el mismo codigo. Los pasos de procesamiento, que leen
las corridas completas (~125 GB por medio en el disco ADATA), se ejecutan desde los scripts y se saltan si
sus resultados ya existen.
Uso: python3 scripts/construir_notebook.py
"""
import os, ast
import nbformat as nbf

H = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(H, ".."))
cells = []
md = lambda t: cells.append(nbf.v4.new_markdown_cell(t.strip("\n")))
code = lambda t: cells.append(nbf.v4.new_code_cell(t.strip("\n")))


def fuente(nombre):
    """Codigo del script sin shebang ni docstring (el docstring va como texto de la celda markdown)."""
    s = open(os.path.join(H, nombre)).read()
    t = ast.parse(s); doc = ast.get_docstring(t) or ""
    lineas = s.split("\n")
    desde = t.body[0].end_lineno if doc else (1 if lineas[0].startswith("#!") else 0)
    return doc, "\n".join(lineas[desde:]).lstrip("\n")


def paso(nombre, args, titulo, figuras=()):
    doc, cuerpo = fuente(nombre)
    md(f"### {titulo}\n\n`scripts/{nombre}` — " + doc.replace("\n", " "))
    argv = ", ".join([repr(nombre)] + list(args))
    code(f'sys.argv = [{argv}]\n__file__ = str(DIR_SCRIPTS / "{nombre}")\n# ---- código de scripts/{nombre} ----\n' + cuerpo)
    if figuras:
        code("\n".join(f'mostrar("{f}")' for f in figuras))


md(r"""
# Réplica de Sidelnik et al. (2020) con MEIGA: neutrones de 500 MeV en el WCD (Sección 4.1.1)

Corridas de MEIGA (Geant4 10.7.p04, `QGSP_BERT_HP_NoThermal`, sin $S(\alpha,\beta)$, modo óptico `eFast`) que reproducen la configuración de
Sidelnik et al., *Adv. Space Res.* **65** (2020) 2216: 150 000 neutrones de 500 MeV que entran horizontalmente a media altura del tanque
(radio 48 cm, altura 133 cm, Tyvek 0,12 mm + acero 0,5 mm, PMT de 10,16 × 10,16 × 5 cm en la tapa).

| Medio | Corrida (disco ADATA, `Corridas-Sidelnik-500MeV/`) | Neutrones |
|---|---|---|
| Agua pura | `150000N-500MeV-Sidelnik-H2O-pura-sinSab-20261012-061022` | 150 000 |
| Agua + 2,5 % NaCl | `42649N-parcial-...-20261013` (interrumpida) + `107351N-...-20261013-135213` (complemento), unidas con `unir_tramos.py` | 150 000 |

**Orden de ejecución.** Ejecute las celdas en orden.
1. *Procesamiento* (sección 1): lee los archivos crudos del disco; se salta para cada medio si su resultado ya está en `resultados/`
   (cambie `REPROCESAR = True` para rehacerlo).
2. *Referencias* (sección 2): digitalización por color de las Figs. 3 y 5 de Sidelnik (las imágenes están en `datos/`).
3. *Análisis y figuras* (secciones 3–6): trabajan con `resultados/` y tardan segundos. Cada celda contiene el código del script correspondiente.
4. *Informe* (sección 7): `informe/Informe-Sidelnik-500MeV.pdf`, con el mismo contenido que la Sec. 4.1.1 de la tesis en formato de informe (fuente común: `informe/seccion_4_1_1.tex` y `informe/apendice_procesos.tex`; `scripts/construir_informe.py` ajusta la jerarquía de títulos), y las notas técnicas `informe/Informe-Sidelnik-500MeV-tecnico.pdf` (corridas, procedimientos, diagnósticos y reproducibilidad).

Los archivos `resultados/<medio>_fotones.npz` (destino de cada fotón óptico, 345 MB y 113 MB) no están en el repositorio:
se regeneran con `destino_fotones.py` desde `pasos-particulas.tsv`; sin ellos se saltan solo los diagnósticos ópticos (Sec. 5).

Este notebook se genera con `scripts/construir_notebook.py` a partir de los scripts. Todas las figuras usan `scripts/estilo.py`
(dibujadas al ancho de la página, con leyendas de al menos 9 puntos impresos) y el informe tiene el mismo contenido que la Sec. 4.1.1 de la tesis.
""")
md("## 0. Configuración")
code(r'''
import os, sys, json, runpy, subprocess
from pathlib import Path
import numpy as np
from IPython.display import Image as ImagenNB, display   # (los scripts de digitalizacion importan Image de PIL)

BASE = Path.cwd()                                   # carpeta del notebook
DIR_SCRIPTS = BASE / "scripts"; DIR_RES = BASE / "resultados"; DIR_FIG = BASE / "figuras"   # (los scripts usan RES y FIG como texto)
# Carpeta con las corridas de MEIGA (cámbiela si el disco se monta en otra ruta)
CORRIDAS = Path(os.environ.get("CORRIDAS_SIDELNIK", "/ruta/a/Corridas-Sidelnik-500MeV"))   # <- escriba aquí la ruta de las corridas
os.environ["CORRIDAS_SIDELNIK"] = str(CORRIDAS)
CORRIDA = {"pura": CORRIDAS / "150000N-500MeV-Sidelnik-H2O-pura-sinSab-20261012-061022",
           "nacl25a": CORRIDAS / "42649N-parcial-500MeV-Sidelnik-H2O-2.5NaCl-sinSab-20261013",
           "nacl25b": CORRIDAS / "107351N-500MeV-Sidelnik-H2O-2.5NaCl-sinSab-20261013-135213",
           "nacl5": CORRIDAS / "150000N-500MeV-Sidelnik-H2O-5NaCl-sinSab-20261014-065724",
           "nacl10": CORRIDAS / "150000N-500MeV-Sidelnik-H2O-10NaCl-sinSab-20261015-081303"}
# medios de los analisis que leen las corridas por evento: lista de carpetas (tramos) de cada medio
FUENTES = {"pura": [CORRIDA["pura"]], "nacl25": [CORRIDA["nacl25a"], CORRIDA["nacl25b"]], "nacl5": [CORRIDA["nacl5"]], "nacl10": [CORRIDA["nacl10"]]}
TRAMOS = {"nacl25": ("nacl25a", "nacl25b")}      # corridas en dos tramos: se procesan por separado y se unen
MEDIOS = [m for m in ["pura", "nacl25", "nacl5", "nacl10"] if (DIR_RES / f"{m}.npz").exists() or (m in CORRIDA and CORRIDA[m].exists())
          or (m in TRAMOS and all(CORRIDA[t].exists() for t in TRAMOS[m]))]
REPROCESAR = False


def ejecutar(script, *args):
    """Ejecuta scripts/<script> con argumentos, como desde la terminal (mismo intérprete)."""
    argv0 = sys.argv[:]
    try:
        sys.argv = [script] + [str(a) for a in args]
        runpy.run_path(str(DIR_SCRIPTS / script), run_name="__main__")
    finally:
        sys.argv = argv0


def procesar(script, salida, *args):
    """Paso de procesamiento: se salta si la salida existe (salvo REPROCESAR) o si la corrida no está disponible."""
    if (DIR_RES / salida).exists() and not REPROCESAR:
        print(f"{salida}: ya existe, se omite")
    elif not Path(args[0]).exists():
        print(f"{salida}: no se encuentra la corrida {args[0]}")
    else:
        ejecutar(script, *args)


def mostrar(nombre):
    display(ImagenNB(filename=str(DIR_FIG / f"{nombre}.png")))


print("Medios:", MEDIOS); print("Corridas disponibles:", {m: c.exists() for m, c in CORRIDA.items()})
''')

md(r"""
## 1. Procesamiento de las corridas (lee el disco; se omite si los resultados existen)

| Script | Archivo crudo | Salida |
|---|---|---|
| `procesar_corrida.py` | todos salvo `pasos-particulas.tsv` (7,5 min por 150 000 n) | `<medio>.npz` |
| `distancias_alternativas.py` | `pasos-neutrones.tsv`, `capturas-neutrones.tsv` | `<medio>_distancias.npz` |
| `fraccion_captura_neutrones.py` | `pasos-neutrones.tsv` | `fraccion_captura_<medio>.json` |
| `espectro_gamma_pasos.py` | `pasos-gamma.tsv` (bines de 1 keV) | `<medio>_gamma_pasos.npz` |
| `gammas_acumulados.py` | `pasos-gamma.tsv` (hasta 600 MeV) | `<medio>_gammas_hasta600.npz` |
| `origen_electrones.py` | `secundarias-interaccion-gamma.tsv`, `pasos-gamma.tsv` | `<medio>_origen_electrones.npz` |
| `destino_fotones.py` | `pasos-particulas.tsv` (78 GB, 14 min) | `<medio>_fotones.npz` (no va al repositorio) |

Los scripts aceptan corridas interrumpidas: usan solo los neutrones terminados (líneas completas de `Carga-total.txt`).
""")
code(r'''
for m, c in CORRIDA.items():
    procesar("procesar_corrida.py", f"{m}.npz", c, DIR_RES / f"{m}.npz")
    procesar("distancias_alternativas.py", f"{m}_distancias.npz", c, DIR_RES / f"{m}_distancias.npz")
    procesar("fraccion_captura_neutrones.py", f"fraccion_captura_{m}.json", c, m)
    procesar("espectro_gamma_pasos.py", f"{m}_gamma_pasos.npz", c, DIR_RES / f"{m}_gamma_pasos.npz")
    procesar("gammas_acumulados.py", f"{m}_gammas_hasta600.npz", c, m)
    procesar("origen_electrones.py", f"{m}_origen_electrones.npz", c, m)
    if not (DIR_RES / f"{m}_aceptados_por_run.npy").exists():       # el destino de los fotones solo hace falta para los diagnósticos ópticos
        procesar("destino_fotones.py", f"{m}_fotones.npz", c, DIR_RES / f"{m}_fotones.npz")
for m, (ta, tb) in TRAMOS.items():
    if not (DIR_RES / f"{m}.npz").exists() or REPROCESAR:
        if (DIR_RES / f"{ta}.npz").exists() and (DIR_RES / f"{tb}.npz").exists():
            ejecutar("unir_tramos.py", ta, tb, m)
''')

paso("esquema_detector.py", ['"nacl25"', '"124"'], "Esquema del detector con un evento real con captura en Cl (lee el evento de la corrida si está disponible)", ["fig00_esquema_detector"])
code('ejecutar("esquema_detector.py", "pura", "142"); mostrar("fig00_esquema_detector_pura")')
md("## 2. Digitalización de las figuras de referencia")
paso("digitalizar_fig3.py", [], "Fig. 3 de Sidelnik (espectro gamma)")
paso("digitalizar_fig5.py", [], "Fig. 5 de Sidelnik (electrones producidos por gammas)")

md("## 3. Captura, distancia y resumen (Tabla 2 y Fig. 2 de Sidelnik)")
code(r'''
# Interacciones del neutron primario (lee las corridas; se omite si el resultado existe)
for m, cs in FUENTES.items():
    if (DIR_RES / f"inelasticas_primario_{m}.json").exists() and not REPROCESAR:
        print(f"inelasticas_primario_{m}.json: ya existe, se omite")
    elif all(c.exists() for c in cs):
        ejecutar("inelasticas_primario.py", m, *cs)
''')
paso("figura_inelasticas_primario.py", [], "Interacciones inelásticas del neutrón primario", ["fig20_inelasticas_primario"])
paso("primario_y_captura.py", [], "¿Desaparece el primario? Relación con las capturas y con la definición de Sidelnik")
code(r'''
# Dispersiones elasticas: reconstruccion de vertices (lee pasos-neutrones y pasos-particulas, ~15 min por corrida; se omite si existe)
for m, cs in FUENTES.items():
    if (DIR_RES / f"elasticas_{m}.json").exists() and not REPROCESAR:
        print(f"elasticas_{m}.json: ya existe, se omite")
    elif all(c.exists() for c in cs):
        ejecutar("elasticas_vertices.py", m, *cs)
''')
paso("figura_elasticas.py", [], "Dispersiones elásticas: blanco, energía, ángulo, ξ y leyes de conservación", ["fig21_elasticas"])
md("### Canales de reacción inelástica, valores Q y gammas de desexcitación\n\n`scripts/canales_reaccion.py` — " + "canal X(n,x)Y de cada inelástica, valor Q (AME2020), energía del neutrón y líneas gamma del núcleo residual; origen de los gammas de 4–7 MeV. Las tablas por medio están en el informe (Sec. ‘Ecuaciones, energías y porcentajes de todos los procesos’).")
code(r'''
for m, cs in FUENTES.items():
    if (DIR_RES / f"canales_{m}.json").exists() and not REPROCESAR:
        print(f"canales_{m}.json: ya existe, se omite")
    elif all(c.exists() for c in cs):
        ejecutar("canales_reaccion.py", m, *cs)
import pandas as pd
for m in FUENTES:
    if (DIR_RES / f"canales_{m}.json").exists():
        d = json.load(open(DIR_RES / f"canales_{m}.json"))
        t = pd.DataFrame(d["canales"])[["canal", "frac", "Q_MeV", "E_n_mediana_MeV", "gammas_por_reaccion", "lineas"]].head(20)
        t["frac"] = (100 * t.frac).round(2)
        print(m, "- inelásticas por neutrón incidente:", round(d["inelasticas_por_neutron_incidente"], 3)); display(t)
        print("gammas de 4-7 MeV por núcleo emisor:", {k: round(100 * v, 1) for k, v in d["gammas_4_7_MeV_por_residual"].items()})
''')
paso("analizar.py", [], "Resumen por medio y figuras 01–05",
     ["fig01_distancia_captura", "fig02_espectro_gamma", "fig03_espectro_electrones", "fig04_carga_y_tiempos", "fig05_tiempo_energia_captura"])

md("## 4. Espectros gamma y de electrones (Figs. 3–5 de Sidelnik)")
paso("espectro_gamma_tipo_sidelnik.py", ['"pura"'], "Espectro gamma en el formato de la Fig. 3 (agua pura)", ["fig11_espectro_gamma_tipo_sidelnik"])
code(r'''
# Mismo análisis para los medios con NaCl (código idéntico al de la celda anterior)
for m in MEDIOS[1:]:
    ejecutar("espectro_gamma_tipo_sidelnik.py", m); mostrar(f"fig11_espectro_gamma_tipo_sidelnik_{m}")
''')
paso("fig4_gammas_acumulados.py", [], "Gammas acumulados (Fig. 4 de Sidelnik)", ["fig17_gammas_acumulados"])
paso("espectro_electrones_tipo_sidelnik.py", [], "Electrones producidos por gammas (Fig. 5 de Sidelnik)", ["fig13_espectro_electrones_tipo_sidelnik"])
paso("interpretacion_electrones.py", [], "Interpretación física: origen del gamma de cada electrón", ["fig14_origen_electrones"])

md("## 5. Luz Cherenkov y carga (Fig. 6 de Sidelnik)")
paso("histograma_tipo_sidelnik.py", [], "Fotones aceptados por la eficiencia cuántica y carga en el PMT", ["fig09_histograma_tipo_sidelnik"])
paso("figura6_sidelnik_meiga.py", [], "Fig. 6 de Sidelnik reproducida, con la separación de eventos con piones", ["fig10_figura6_sidelnik_vs_meiga"])
md(r"""
### Diagnóstico óptico (requiere `resultados/<medio>_fotones.npz`)

`diagnostico_carga.py` (balance de luz, destino de los fotones) y `sensibilidad_tyvek.py` (modelo de rebotes en el Tyvek) usan el destino de cada
fotón óptico; si el archivo no está, se muestran las figuras ya guardadas.
""")
code(r'''
for m in MEDIOS:
    if (DIR_RES / f"{m}_fotones.npz").exists():
        ejecutar("diagnostico_carga.py", m)
        if m == "pura":
            ejecutar("sensibilidad_tyvek.py", m)
    if (DIR_RES / f"sensibilidad_tyvek_{m}.json").exists() and ((DIR_RES / f"tyvek_espectro_{m}.json").exists() or (DIR_RES / f"{m}_fotones.npz").exists()):
        ejecutar("tyvek_diagnostico.py", m)      # el estudio del Tyvek se hizo con agua pura
    else:
        print(f"{m}: falta {m}_fotones.npz; se usan los resultados guardados en resultados/diagnostico_{m}.json")
ejecutar("figura_destino_fotones_medios.py") if all((DIR_RES / f"{m}_fotones.npz").exists() for m in MEDIOS) else None
for f in ["fig06_balance_luz_y_fig6", "fig07_destino_fotones", "fig08_tyvek_diagnostico"]:
    if (DIR_FIG / f"{f}.png").exists():
        mostrar(f)
''')

md("## 6. Medios con NaCl: captura por núcleo, cascadas del cloro y deuterones")
paso("cascadas_cloro.py", ['"nacl25"'], "Cascadas de las capturas en ³⁵Cl, ²³Na y ¹H", ["fig12_cascadas_cloro_nacl25"])
paso("espectros_captura_nucleo.py", [], "Espectros de captura por núcleo (Fig. 4.1 de la tesis)", ["fig15_espectros_captura_nucleo"])
paso("deuterones_captura.py", [], "Deuterones de la captura en H (Fig. 4.6 de la tesis)", ["fig16_deuterones_captura"])
paso("tabla_parametros_nucleares.py", [], "Tabla 4.2 de la tesis: líneas de captura y su energía en MEIGA")
paso("esquema_niveles_O17.py", [], "Esquema de niveles de 16O(n,γ)17O (Fig. 4.2 de la tesis) e intensidades de MEIGA",
     ["fig18_esquema_niveles_O17", "fig18b_esquema_niveles_O17_MEIGA"])
paso("esquema_niveles_Cl36.py", [], "Esquema de niveles de 35Cl(n,γ)36Cl (ENSDF) e intensidades de MEIGA",
     ["fig19_esquema_niveles_Cl36", "fig19b_esquema_niveles_Cl36_MEIGA"])

md("## 7. Informe")
code(r'''
# Informe principal: copia fiel de la Sec. 4.1.1 de la tesis (seccion_4_1_1.tex + apendice_procesos.tex, preambulo de la tesis).
# Las notas tecnicas (Informe-Sidelnik-500MeV-tecnico) se generan con escribir_informe.py a partir de resultados/.
ejecutar("escribir_informe.py")
ejecutar("construir_informe.py")          # cuerpo del informe a partir de la fuente comun con la tesis
for doc in ("Informe-Sidelnik-500MeV", "Informe-Sidelnik-500MeV-tecnico"):
    r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", doc + ".tex"],
                       cwd=BASE / "informe", capture_output=True, text=True, errors="replace")
    print(doc, "->", "correcto" if r.returncode == 0 else r.stdout[-2000:])
subprocess.run(["latexmk", "-c"], cwd=BASE / "informe", capture_output=True)
''')

# ---- 8. Resultados y discusion: contenido completo del informe (texto, ecuaciones, tablas y figuras)
import sys as _sys
_sys.path.insert(0, H)
from informe_tesis_a_markdown import celdas as _celdas_informe
_ci = _celdas_informe()
if _ci:
    md(r"""
## 8. Resultados y discusión (contenido completo del informe)

Esta sección reproduce el texto, las ecuaciones, las tablas y las figuras de `informe/Informe-Sidelnik-500MeV.pdf`, con el mismo contenido que la Sec. 4.1.1 de la tesis, con la numeración del informe.
Se genera automáticamente desde el informe (`scripts/informe_tesis_a_markdown.py`) cada vez que se regenera el notebook, así que siempre coincide con el PDF.
Si se reprocesan los datos, ejecute la sección 7 y luego `python3 scripts/construir_notebook.py` para actualizar este texto.
""")
    for _t in _ci:
        md(_t.replace("\n#### ", "\n##### ").replace("\n### ", "\n#### ").replace("\n## ", "\n### ") if not _t.startswith("#") else
           ("#" + _t) if _t.startswith("#") else _t)

nb = nbf.v4.new_notebook(); nb.cells = cells
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbf.write(nb, os.path.join(R, "Analisis-Sidelnik-500MeV.ipynb"))
print("Analisis-Sidelnik-500MeV.ipynb:", len(cells), "celdas")
