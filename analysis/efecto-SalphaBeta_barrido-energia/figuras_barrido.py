#!/usr/bin/env python3
"""Figuras del barrido en energia con y sin S(alpha,beta) (10 000 neutrones por punto).

El medio y la carpeta de trabajo se eligen con las variables de entorno MEDIO (AguaPura, Agua25NaCl,
Agua5NaCl o Agua10NaCl; por defecto AguaPura) y SALIDA (por defecto, la carpeta del script).

Lee balance_destinos.tsv (generado por balance_destinos.sh) y produce:
  fig_captura_N_vs_energia.{png,pdf}   captura en el agua y <N> frente a la energia
  fig_destinos_vs_energia.{png,pdf}    reflexion, captura en la estructura, escape lateral
                                       y profundidad media de captura
  resumen_barrido.tsv                  porcentajes e incertidumbres por punto
"""
import csv
import math
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

AQUI = Path(os.environ.get("SALIDA", Path(__file__).resolve().parent)).resolve()
MEDIO = os.environ.get("MEDIO", "AguaPura")
MEDIO_TEXTO = {"AguaPura": "Agua pura", "Agua25NaCl": "Agua + 2.5 % de NaCl",
               "Agua5NaCl": "Agua + 5 % de NaCl", "Agua10NaCl": "Agua + 10 % de NaCl"}[MEDIO]
Z_SUPERFICIE_AGUA = 133.062  # cm, cara superior del agua (medida en los datos de la Campana 2)
LIMITE_SAB_EV = 4.0          # G4ThermalNeutrons actua por debajo de 4 eV

# Paleta categorica de referencia (slots 1 y 2) y tintas de texto/ejes.
FISICAS = {
    "QGSP_BERT_HP": {"color": "#2a78d6", "etiqueta": "Con S(α,β)", "marker": "o"},
    "QGSP_BERT_HP_NoThermal": {"color": "#eb6834", "etiqueta": "Sin S(α,β) (gas libre)", "marker": "s"},
}
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
REJILLA = "#e4e3df"

plt.rcParams.update({
    "font.size": 10,
    "axes.edgecolor": TINTA_2,
    "axes.labelcolor": TINTA,
    "xtick.color": TINTA_2,
    "ytick.color": TINTA_2,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": REJILLA,
    "grid.linewidth": 0.6,
    "legend.frameon": False,
    "savefig.dpi": 300,
})


def leer():
    datos = {f: [] for f in FISICAS}
    with open(AQUI / "balance_destinos.tsv", newline="") as fh:
        for fila in csv.DictReader(fh, delimiter="\t"):
            n = int(fila["incidentes"])
            reg = {"E": float(fila["energia_eV"]), "etiqueta": fila["etiqueta"], "n": n}
            for clave in ("captura_agua", "captura_estructura", "reflexion_tapa",
                          "escape_lateral", "transmision_fondo", "desviado_en_aire"):
                k = int(fila[clave])
                p = k / n
                reg[clave] = 100 * p
                reg[clave + "_err"] = 100 * math.sqrt(p * (1 - p) / n)
            reg["N"] = float(fila["N_medio_captura_agua"])
            reg["N_err"] = float(fila["N_error_medio"])
            reg["profundidad"] = Z_SUPERFICIE_AGUA - float(fila["z_medio_captura_agua_cm"])
            datos[fila["fisica"]].append(reg)
    for f in datos:
        datos[f].sort(key=lambda r: r["E"])
    return datos


def eje_energia(ax):
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(
        lambda x, _: f"{x * 1000:g} meV" if x < 1 else (f"{x:g} eV" if x < 1000 else f"{x / 1000:g} keV")))
    ax.axvline(LIMITE_SAB_EV, color=TINTA_2, linewidth=0.9, linestyle=(0, (4, 3)))


def serie(ax, datos, clave, con_error=True):
    for f, estilo in FISICAS.items():
        xs = [r["E"] for r in datos[f]]
        ys = [r[clave] for r in datos[f]]
        es = [r[clave + "_err"] for r in datos[f]] if con_error else None
        ax.errorbar(xs, ys, yerr=es, color=estilo["color"], marker=estilo["marker"], markersize=5,
                    markeredgecolor="white", markeredgewidth=0.8, linewidth=2, capsize=2,
                    elinewidth=1, label=estilo["etiqueta"], zorder=3)


def cruce(datos):
    """Energia donde captura_agua(con) - captura_agua(sin) cambia de signo (interpolacion en log E)."""
    con = {r["E"]: r["captura_agua"] for r in datos["QGSP_BERT_HP"]}
    sin = {r["E"]: r["captura_agua"] for r in datos["QGSP_BERT_HP_NoThermal"]}
    es = sorted(set(con) & set(sin))
    for a, b in zip(es, es[1:]):
        da, db = con[a] - sin[a], con[b] - sin[b]
        if da < 0 <= db:
            t = -da / (db - da)
            return 10 ** (math.log10(a) + t * (math.log10(b) - math.log10(a)))
    return None


def figura_captura(datos):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 7.0), sharex=True,
                                   gridspec_kw={"height_ratios": [1.15, 1], "hspace": 0.12})
    serie(ax1, datos, "captura_agua")
    ax1.set_ylabel("Neutrones capturados en el agua (%)")
    ax1.set_ylim(0, 50)
    ax1.legend(loc="upper left")
    ec = cruce(datos)
    if ec:
        ax1.axvline(ec, color=TINTA_2, linewidth=0.8, linestyle=":")
        ax1.annotate(f"cruce ≈ {ec:.2f} eV", xy=(ec, 5), xytext=(-5, 0), textcoords="offset points",
                     color=TINTA_2, fontsize=8.5, va="center", ha="right")
    ax1.annotate("4 eV: límite superior\nde S(α,β)", xy=(LIMITE_SAB_EV, 5), xytext=(5, 0),
                 textcoords="offset points", ha="left", va="center", color=TINTA_2, fontsize=8.5)
    # Etiquetas directas al final de cada curva
    for f, estilo in FISICAS.items():
        ult = datos[f][-1]
        ax1.annotate(estilo["etiqueta"].split(" (")[0], xy=(ult["E"], ult["captura_agua"]), xytext=(8, 0),
                     textcoords="offset points", va="center", color=TINTA, fontsize=9)
    eje_energia(ax1)
    ax1.set_title("a) Captura en el agua", loc="left", fontsize=10, color=TINTA)

    serie(ax2, datos, "N")
    ax2.set_ylabel("⟨N⟩ dispersiones elásticas\nantes de la captura")
    ax2.set_ylim(0, 140)
    eje_energia(ax2)
    ax2.set_xlabel("Energía inicial del neutrón")
    ax2.set_title("b) Número medio de colisiones de los neutrones capturados", loc="left", fontsize=10, color=TINTA)
    ax2.set_xlim(6e-4, 3e3)
    fig.text(0.01, 0.005, f"{MEDIO_TEXTO}, geometría de la Campaña 2 (acero 0.5 mm, PMT al 65 %), 10 000 neutrones por punto; "
             "barras: incertidumbre estadística (1σ).", fontsize=7.5, color=TINTA_2)
    for ext in ("png", "pdf"):
        fig.savefig(AQUI / f"fig_captura_N_vs_energia.{ext}", bbox_inches="tight")
    plt.close(fig)
    return ec


def figura_destinos(datos):
    fig, axs = plt.subplots(2, 2, figsize=(9.0, 6.6), sharex=True,
                            gridspec_kw={"hspace": 0.28, "wspace": 0.28})
    paneles = [
        ("reflexion_tapa", "a) Reflexión: salen por la tapa", "Neutrones incidentes (%)", True, (50, 80)),
        ("captura_estructura", "b) Captura en la estructura (acero y Tyvek)", "Neutrones incidentes (%)", True, (0, 10)),
        ("escape_lateral", "c) Escape por la pared lateral", "Neutrones incidentes (%)", True, (0, 1.4)),
        ("profundidad", "d) Profundidad media de captura", "Bajo la superficie del agua (cm)", False, (0, 7)),
    ]
    for ax, (clave, titulo, ylab, err, ylim) in zip(axs.flat, paneles):
        serie(ax, datos, clave, con_error=err)
        ax.set_title(titulo, loc="left", fontsize=10, color=TINTA)
        ax.set_ylabel(ylab)
        ax.set_ylim(*ylim)
        eje_energia(ax)
        ax.set_xlim(6e-4, 3e3)
        ax.set_xticks([1e-3, 1e-1, 1e1, 1e3])  # una etiqueta cada dos decadas: los paneles son estrechos
    for ax in axs[1]:
        ax.set_xlabel("Energía inicial del neutrón")
    axs[0, 0].legend(loc="lower left")
    fig.text(0.01, 0.005, "Sin transmisión por el fondo en ninguna corrida; entre 2 y 6 % de los neutrones se desvían "
             "en el aire antes de llegar al tanque (igual con ambas físicas). Línea discontinua: 4 eV.",
             fontsize=7.5, color=TINTA_2)
    for ext in ("png", "pdf"):
        fig.savefig(AQUI / f"fig_destinos_vs_energia.{ext}", bbox_inches="tight")
    plt.close(fig)


def tabla(datos):
    campos = ["captura_agua", "reflexion_tapa", "captura_estructura", "escape_lateral",
              "transmision_fondo", "desviado_en_aire"]
    with open(AQUI / "resumen_barrido.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["energia_eV", "etiqueta", "fisica"] + [c + "_pct" for c in campos]
                   + ["captura_agua_err_pct", "N_medio", "N_err", "profundidad_media_cm"])
        for f in FISICAS:
            for r in datos[f]:
                w.writerow([r["E"], r["etiqueta"], f] + [f"{r[c]:.2f}" for c in campos]
                           + [f"{r['captura_agua_err']:.2f}", f"{r['N']:.2f}", f"{r['N_err']:.2f}",
                              f"{r['profundidad']:.2f}"])


if __name__ == "__main__":
    d = leer()
    ec = figura_captura(d)
    figura_destinos(d)
    tabla(d)
    print(f"Cruce del efecto de S(alpha,beta): {ec:.3f} eV" if ec else "Sin cruce")
