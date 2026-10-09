#!/usr/bin/env python3
"""Genera el notebook figuras_seccion_4.1.1.ipynb (sin salidas).

Uso: python3 construir_notebook.py
"""
import nbformat as nbf

celdas = []


def md(texto):
    celdas.append(nbf.v4.new_markdown_cell(texto.strip("\n")))


def code(texto):
    celdas.append(nbf.v4.new_code_cell(texto.strip("\n")))


md(r"""
# Validación numérica con neutrones de 500 MeV: figuras (Sección 4.1.1)

Se simularon $2\times10^5$ neutrones por medio; los conteos absolutos se muestran normalizados a $1.5\times10^5$
neutrones incidentes para compararlos con la referencia. Réplica de Sidelnik et al. (2020, *Adv. Space Res.* 65, 2216): WCD de 1 m³ con agua pura y con 0.5, 1, 2.5, 5 y 10 %
de NaCl, irradiado con neutrones de 500 MeV. Este notebook solo lee los resúmenes de `resultados/`
(`procesar_500MeV.py` y `analizar_validacion.py`).

| Figura | Contenido |
|---|---|
| `histograma_carga` | Distribución de la carga por evento (fotoelectrones) en los seis medios |
| `razon_carga_medios` | Razón NaCl/agua pura de las cinco concentraciones simuladas (25 pe, error de Poisson) |
| `razon_simulacion_referencia` | Razón simulada frente a la digitalizada de Sidelnik et al., cruda y sin artefactos |
| `digitalizacion_artefactos` | Curvas digitalizadas de la referencia: picos de la leyenda y su corrección |
| `control_pearson` | Correlación de Pearson y razón media de cada simulación frente a cada curva de referencia |
| `ajustes_tramos` | Pendientes log–log por tramo: tesis frente a ajuste de Poisson |
| `espectro_gamma` | Energía del fotón en cada interacción que crea un e± (cuatro medios) |
| `espectro_electrones` | Energía del e± creado, con el medio real de cada archivo |
""")

code(r"""
import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RES = Path("resultados")
SALIDA = Path("figuras")
SALIDA.mkdir(exist_ok=True)

MEDIOS = ["Agua-pura", "Agua+0.5NaCl", "Agua+1NaCl", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
ROTULO = dict(zip(MEDIOS, ["Agua pura", "0.5 % NaCl", "1 % NaCl", "2.5 % NaCl", "5 % NaCl", "10 % NaCl"]))
COLOR = dict(zip(MEDIOS, ["red", "#8c6d31", "#17becf", "green", "purple", "darkorange"]))
SALES = ["Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]

mpl.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.alpha": 0.25, "font.size": 11})
leer = lambda n: pd.read_csv(RES / n, sep="\t")
# Se simularon 2e5 neutrones por medio; los conteos absolutos se muestran normalizados a 1.5e5 neutrones incidentes.
N_SIMULADOS, N_NORMALIZACION = 200_000, 150_000
NORM = N_NORMALIZACION / N_SIMULADOS


def guardar(fig, nombre):
    fig.savefig(SALIDA / f"{nombre}.pdf", bbox_inches="tight")
    fig.savefig(SALIDA / f"{nombre}.png", dpi=200, bbox_inches="tight")
    plt.show()
""")

md("## Distribución de la carga")
code(r"""
h = leer("histograma_carga.tsv")
bordes = np.arange(0, 4501, 10)
fig, ax = plt.subplots(figsize=(10, 5.5))
for m in MEDIOS:
    s = h[h.medio == m]
    c, _ = np.histogram(s.carga_pe, bordes, weights=s.cuentas * NORM)
    ax.step(0.5 * (bordes[1:] + bordes[:-1]), np.where(c > 0, c, np.nan), where="mid", color=COLOR[m],
            lw=1.2, label=f"{ROTULO[m]} (N = {s.cuentas.sum() * NORM:,.0f})".replace(",", " "))
ax.set_yscale("log")
ax.set_xlim(0, 4500)
ax.set_xlabel("Carga por evento (fotoelectrones)")
ax.set_ylabel("Eventos por intervalo de 10 pe\n(por $1.5\\times10^5$ neutrones)")
ax.legend(fontsize=9)
guardar(fig, "histograma_carga")
""")

md("## Razón NaCl/agua pura de las cinco concentraciones simuladas")
code(r"""
r = leer("razon_25pe.tsv")
fig, ax = plt.subplots(figsize=(10, 5.5))
for m in MEDIOS[1:]:
    ax.errorbar(r.Q_pe, r[f"R_{m}"], yerr=r[f"err_{m}"], fmt="o-", ms=3, lw=1.2, capsize=2, color=COLOR[m],
                label=ROTULO[m])
ax.axhline(1, color="k", ls="--", lw=1)
ax.set_xlim(0, 800)
ax.set_ylim(0.6, 3.0)
ax.set_xlabel("Carga por evento (fotoelectrones)")
ax.set_ylabel("Razón respecto al agua pura")
ax.legend(fontsize=9)
guardar(fig, "razon_carga_medios")
""")

md("## Simulación frente a la referencia digitalizada")
code(r"""
fig, axs = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
for ax, m in zip(axs, SALES):
    ax.axvspan(100, 400, color="0.9", zorder=0)
    ax.errorbar(r.Q_pe, r[f"R_{m}"], yerr=r[f"err_{m}"], fmt="o-", ms=3, lw=1.3, capsize=2, color=COLOR[m],
                label="Simulación (25 pe)")
    ax.plot(r.Q_pe, r[f"Rref_{m}"], "k--", lw=1.4, label="Referencia digitalizada")
    ax.plot(r.Q_pe, r[f"Rref_limpia_{m}"], "k:", lw=1.8, label="Referencia sin artefactos")
    ax.axhline(1, color="0.5", lw=0.8)
    ax.set_xlim(0, 700)
    ax.set_ylim(0.5, 4.5)
    ax.set_title(ROTULO[m])
    ax.set_xlabel("Número de fotones (pe)")
axs[0].set_ylabel("Razón respecto al agua pura")
axs[0].legend(fontsize=9)
guardar(fig, "razon_simulacion_referencia")
""")

md("## Artefactos de la digitalización")
code(r"""
ref = pd.read_csv("datos/digitalizacion_histograma_carga_referencia_700pts.csv")
fig, ax = plt.subplots(figsize=(10, 5.5))
for col, m in [("Pure_H2O", "Agua-pura"), ("NaCl_2p5", "Agua+2.5NaCl"), ("NaCl_5", "Agua+5NaCl"),
               ("NaCl_10", "Agua+10NaCl")]:
    ax.plot(ref.Numero_de_fotones, ref[f"{col}_counts_digitized"], color=COLOR[m], lw=1.1, label=ROTULO[m])
ax.axvspan(1550, 1850, color="0.85", zorder=0, label="Leyenda capturada como curva")
ax.set_yscale("log")
ax.set_xlim(0, 2500)
ax.set_ylim(1, 2e4)
ax.set_xlabel("Número de fotones")
ax.set_ylabel("Cuentas digitalizadas")
ax.legend(fontsize=9)
guardar(fig, "digitalizacion_artefactos")
""")

md("## ¿Distingue la correlación de Pearson la concentración?")
code(r"""
c = leer("control_pearson.tsv")
c = c[c.referencia_limpia == 1]
conc = {"Agua+0.5NaCl": 0.5, "Agua+1NaCl": 1, "Agua+2.5NaCl": 2.5, "Agua+5NaCl": 5, "Agua+10NaCl": 10}
fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
for mr in SALES:
    s = c[c.referencia == mr].copy()
    s["x"] = s.simulacion.map(conc)
    axs[0].plot(s.x, s.r, "o-", color=COLOR[mr], label=f"Referencia {ROTULO[mr]}")
    if mr == SALES[0]:
        axs[1].plot(s.x, s.R_sim_media, "o-", color="0.3", label="Simulación")
    axs[1].axhline(s.R_ref_media.iloc[0], color=COLOR[mr], ls="--", label=f"Referencia {ROTULO[mr]}")
axs[0].set_xscale("log"); axs[1].set_xscale("log")
axs[0].set_xlabel("Concentración simulada (% NaCl)"); axs[1].set_xlabel("Concentración simulada (% NaCl)")
axs[0].set_ylabel("r de Pearson (100–400 pe)"); axs[1].set_ylabel("Razón media en 100–400 pe")
axs[0].set_title("(a) Correlación"); axs[1].set_title("(b) Amplitud")
axs[0].legend(fontsize=9); axs[1].legend(fontsize=9)
guardar(fig, "control_pearson")
""")

md("## Ajustes por tramos")
code(r"""
a = leer("ajustes_tramos.tsv")
tramos = ["0-100", "100-500", "500-1000", "1000-1500", "1500-3500"]
fig, axs = plt.subplots(1, len(tramos), figsize=(17, 4.2))
for ax, t in zip(axs, tramos):
    s = a[a.tramo == t]
    x = np.arange(len(s))
    ax.errorbar(x - 0.1, s.pendiente_tesis, yerr=s.err_pend_tesis, fmt="s", color="0.4", label="Tesis")
    ax.errorbar(x + 0.1, s.pend_poisson_10pe, yerr=s.err_pend_poisson, fmt="o", color="C0",
                label="Poisson, 10 pe")
    ax.set_xticks(x)
    ax.set_xticklabels([ROTULO[m].replace(" NaCl", "") for m in s.medio], rotation=30)
    ax.set_title(f"{t} pe")
axs[0].set_ylabel("Pendiente log–log")
axs[0].legend(fontsize=9)
fig.tight_layout()
guardar(fig, "ajustes_tramos")
""")

md("## Espectros de fotones y electrones")
code(r"""
g = leer("espectro_gamma.tsv")
lin = leer("lineas_gamma.tsv")
fig, ax = plt.subplots(figsize=(11, 5.5))
for m in ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]:
    s = g[(g.serie == m) & (g.escala == "lineal_5keV") & (g.E_max_MeV <= 10)]
    ax.step(s.E_min_MeV + 0.0025, s.cuentas * NORM, where="mid", color=COLOR[m], lw=0.9, label=ROTULO[m])
for nombre in ["H 2223.25", "Cl35 517.07", "Cl35 788.42", "Cl35 1164.86", "Cl35 1951.14", "Cl35 6110.84",
               "Cl35 8578.6"]:
    E = lin[(lin.linea == nombre) & (lin.medio == "Agua+10NaCl")].E_geant4_keV.iloc[0] / 1000
    ax.axvline(E, color="0.5", ls=":", lw=0.8)
    ax.text(E, 2e6, f"{nombre.split()[0]} {E:.3f}", rotation=90, fontsize=8, va="top", ha="right")
ax.set_yscale("log")
ax.set_xlim(0, 10)
ax.set_xlabel("Energía del fotón al interactuar (MeV)")
ax.set_ylabel("Interacciones por intervalo de 5 keV\n(por $1.5\\times10^5$ neutrones)")
ax.legend(fontsize=9, loc="lower left")
guardar(fig, "espectro_gamma")

e = leer("espectro_electrones.tsv")
v = leer("verificacion_archivos.tsv")
# Medio real de cada archivo de electrones (emparejamiento línea a línea con los archivos de fotones)
fig, axs = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
uso_tesis = [("agua-pura", "Agua pura"), ("agua-25NaCl", "2.5 % NaCl"), ("agua-5NaCl", "5 % NaCl"),
             ("agua-10NaCl-1", "10 % NaCl")]
real = {"agua-pura": "Agua-pura", "agua-25NaCl": "Agua+5NaCl", "agua-5NaCl": "Agua+10NaCl",
        "agua-10NaCl-1": "Agua+5NaCl"}
for ax, titulo, etiqueta in [(axs[0], "(a) Rótulos usados en la tesis", lambda a, r: r),
                             (axs[1], "(b) Medio real de cada archivo", lambda a, r: ROTULO[real[a]] + f"  [{a}]")]:
    for (arch, rot), col in zip(uso_tesis, ["red", "green", "purple", "darkorange"]):
        s = e[(e.serie == arch) & (e.escala == "lineal_5keV") & (e.E_max_MeV <= 12)]
        ax.step(s.E_min_MeV + 0.0025, s.cuentas * NORM, where="mid", lw=0.9,
                color=col if ax is axs[0] else COLOR[real[arch]], ls="-" if arch != "agua-10NaCl-1" else "--",
                label=etiqueta(arch, rot))
    ax.set_yscale("log")
    ax.set_xlim(0, 12)
    ax.set_title(titulo)
    ax.set_xlabel("Energía cinética del e± (MeV)")
    ax.legend(fontsize=8)
axs[0].set_ylabel("Electrones por intervalo de 5 keV\n(por $1.5\\times10^5$ neutrones)")
guardar(fig, "espectro_electrones")
""")

nb = nbf.v4.new_notebook()
nb["cells"] = celdas
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, "figuras_seccion_4.1.1.ipynb")
print("Escrito figuras_seccion_4.1.1.ipynb")
