#!/usr/bin/env python3
"""Genera el notebook figuras_carga_seccion_4.2.ipynb (sin salidas).

Uso: python3 construir_notebook_carga.py
"""
import nbformat as nbf

celdas = []


def md(texto):
    celdas.append(nbf.v4.new_markdown_cell(texto.strip("\n")))


def code(texto):
    celdas.append(nbf.v4.new_code_cell(texto.strip("\n")))


md(r"""
# Carga total y eficiencia de detección: figuras (Campaña 1, Sección 4.2)

Este notebook dibuja la carga total por evento (fotoelectrones, pe) y la eficiencia de detección del WCD para las
16 energías × 4 medios de la Campaña 1 ($10^5$ neutrones por corrida, `QGSP_BERT_HP` sin $S(\alpha,\beta)$). Solo
lee los resúmenes que produce `procesar_carga.py` (`resultados_carga/`).

| Figura | Contenido |
|---|---|
| `histograma_carga_matriz` | Histogramas de carga, un panel por medio, una curva por energía (cuentas absolutas) |
| `histograma_carga_matriz_normalizada` | Las mismas distribuciones normalizadas: la forma no depende de la energía |
| `eficiencia_captura_vs_energia` | Fracción de captura, $\varepsilon(Q\ge1)$ y $P(\text{señal}\mid\text{captura})$ |
| `profundidad_captura` | Profundidad media de captura y su relación con $P(\text{señal}\mid\text{captura})$ |
| `carga_vs_energia` | Carga media y fracción con $Q\ge20$ pe frente a la energía |
| `eficiencia_umbral` | $\varepsilon(Q\ge q)$ para $q$ = 1, 5, 10 y 20 pe |

$\varepsilon = N(Q\ge1)/10^5$, porque los archivos `Carga_Total_*.txt` solo contienen eventos con señal.
La carpeta `1000000meV` se rotula "1 keV", como en la tesis.
""")

code(r"""
import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, LogNorm

RES = Path("resultados_carga")
SALIDA = Path("figuras-carga")
SALIDA.mkdir(exist_ok=True)

ENERGIAS = ["1meV", "2.5meV", "5meV", "7meV", "10meV", "25meV", "50meV", "80meV", "100meV",
            "300meV", "500meV", "700meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
E_MEV = {e: float(e[:-3]) for e in ENERGIAS}
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
ROTULO_MEDIO = dict(zip(MEDIOS, ["Agua pura", "Agua + 2.5 % NaCl", "Agua + 5 % NaCl", "Agua + 10 % NaCl"]))
COLOR = dict(zip(MEDIOS, ["red", "green", "purple", "darkorange"]))
MARCA = dict(zip(MEDIOS, ["o", "s", "^", "D"]))
# Energía: rampa secuencial de un solo tono (azul claro -> oscuro)
RAMPA_E = LinearSegmentedColormap.from_list("azul", ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
NORM_E = LogNorm(vmin=1, vmax=1e6)

mpl.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.25, "font.size": 11})


def leer(nombre):
    with open(RES / nombre) as f:
        filas = list(csv.DictReader(f, delimiter="\t"))
    for r in filas:
        for k, v in r.items():
            try:
                r[k] = float(v)
            except ValueError:
                pass
    return filas


resumen = leer("resumen_carga_campana.tsv")
planitud = {r["medio"]: r for r in leer("planitud_carga.tsv")}
HIST = {}
for r in leer("histograma_carga.tsv"):
    HIST.setdefault((r["energia"], r["medio"]), {})[int(r["carga_pe"])] = r["cuentas"]


def serie(medio, col):
    s = [r for r in resumen if r["medio"] == medio]
    return np.array([r["E_meV"] for r in s]), np.array([r[col] for r in s])


def guardar(fig, nombre):
    fig.savefig(SALIDA / f"{nombre}.pdf")
    fig.savefig(SALIDA / f"{nombre}.png", dpi=200)
    plt.show()
""")

md("## Matriz de histogramas de carga")
code(r"""
def matriz(normalizada, nombre):
    fig, axs = plt.subplots(2, 2, figsize=(12, 9), sharex=True)
    for ax, m in zip(axs.flat, MEDIOS):
        for e in ENERGIAS:
            h = HIST[(e, m)]
            q = np.arange(1, 201)
            y = np.array([h.get(int(x), 0) for x in q], dtype=float)
            if normalizada:
                y /= sum(h.values())
            ax.step(q, np.where(y > 0, y, np.nan), where="mid", lw=1.1, color=RAMPA_E(NORM_E(E_MEV[e])))
        ax.set_yscale("log")
        ax.set_xlim(0, 200)
        ax.set_title(ROTULO_MEDIO[m], fontsize=14)
        ax.set_ylabel("Fracción de eventos con señal" if normalizada else "Cuentas", fontsize=12)
    for ax in axs[1]:
        ax.set_xlabel("Carga total por evento (fotoelectrones)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 0.9, 1))
    cb = fig.colorbar(mpl.cm.ScalarMappable(norm=NORM_E, cmap=RAMPA_E), cax=fig.add_axes([0.915, 0.12, 0.018, 0.76]))
    cb.set_label("Energía del neutrón incidente (meV)", fontsize=12)
    guardar(fig, nombre)


matriz(False, "histograma_carga_matriz")
matriz(True, "histograma_carga_matriz_normalizada")
""")

md("## Captura, eficiencia y señal por captura")
code(r"""
def por_medio(ax, col, err=None, escala=1.0):
    for m in MEDIOS:
        x, y = serie(m, col)
        yerr = None if err is None else serie(m, err)[1] * escala
        ax.errorbar(x, y * escala, yerr=yerr, marker=MARCA[m], ms=5, lw=1.6, capsize=2, color=COLOR[m],
                    label=ROTULO_MEDIO[m])
    ax.set_xscale("log")
    ax.axvline(25, color="0.6", ls=":", lw=1)
    ax.set_xlabel("Energía del neutrón incidente (meV)")


fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
por_medio(axs[0], "eta_cap", escala=100)
axs[0].set_ylabel("Neutrones capturados (%)"); axs[0].set_title("(a) Fracción de captura")
por_medio(axs[1], "eps", "u_eps", escala=100)
axs[1].set_ylabel(r"$\varepsilon(Q\geq1)$ (%)"); axs[1].set_title("(b) Eficiencia de detección")
por_medio(axs[2], "P_senal_captura")
axs[2].set_ylabel("P(señal | captura)"); axs[2].set_title("(c) Señal por neutrón capturado")
axs[0].legend(fontsize=9)
fig.tight_layout()
guardar(fig, "eficiencia_captura_vs_energia")
""")

md("## Profundidad de captura")
code(r"""
fig, axs = plt.subplots(1, 2, figsize=(11, 4.4))
por_medio(axs[0], "profundidad_captura_media_mm", escala=0.1)
axs[0].set_ylabel("Profundidad media de captura (cm)"); axs[0].set_title("(a) Profundidad bajo la superficie del agua")
for m in MEDIOS:
    _, p = serie(m, "profundidad_captura_media_mm")
    _, s = serie(m, "P_senal_captura")
    axs[1].plot(p / 10, s, marker=MARCA[m], ms=5, lw=1.4, color=COLOR[m], label=ROTULO_MEDIO[m])
axs[1].set_xlabel("Profundidad media de captura (cm)"); axs[1].set_ylabel("P(señal | captura)")
axs[1].set_title("(b) Señal por captura frente a profundidad")
axs[1].legend(fontsize=9)
fig.tight_layout()
guardar(fig, "profundidad_captura")
""")

md("## Carga media y cola de alta carga")
code(r"""
fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
por_medio(axs[0], "Q_media_pe", "u_Q_media_pe")
for m in MEDIOS:
    axs[0].axhline(planitud[m]["Q_ponderada_pe"], color=COLOR[m], lw=0.8, ls="--", alpha=0.7)
axs[0].set_ylabel(r"$\langle Q\rangle$ de eventos con señal (pe)"); axs[0].set_title("(a) Carga media")
por_medio(axs[1], "f_Q20", escala=100)
axs[1].set_ylabel(r"Eventos con $Q\geq20$ pe (% de los eventos con señal)"); axs[1].set_title("(b) Cola de alta carga")
axs[1].set_yscale("log")
axs[0].legend(fontsize=9, loc="center left", bbox_to_anchor=(0.02, 0.42))
fig.tight_layout()
guardar(fig, "carga_vs_energia")
""")

md("## Eficiencia con umbral de carga")
code(r"""
fig, axs = plt.subplots(2, 2, figsize=(12, 8.5), sharex=True)
for ax, u in zip(axs.flat, [1, 5, 10, 20]):
    por_medio(ax, f"eps_Q{u}", escala=100)
    ax.set_title(rf"$Q\geq{u}$ pe")
    ax.set_ylabel(r"$\varepsilon(Q\geq q)$ (%)")
    if u >= 10:
        ax.set_yscale("log")
for ax in axs[0]:
    ax.set_xlabel("")
axs[0, 0].legend(fontsize=9)
fig.tight_layout()
guardar(fig, "eficiencia_umbral")
""")

nb = nbf.v4.new_notebook()
nb["cells"] = celdas
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, "figuras_carga_seccion_4.2.ipynb")
print("Escrito figuras_carga_seccion_4.2.ipynb")
