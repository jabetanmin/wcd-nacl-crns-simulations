"""Razones de mejora desde los histogramas de carga del análisis de Bariloche.

Los histogramas ../datos-derivados/histogramas-carga/*_charge_hist.csv son la salida del programa de
procesamiento del grupo del Centro Atómico Bariloche (process.py, no incluido; ver README.md). Las
razones publicadas en Sarmiento-Cano et al. (arXiv:2601.17595) y en la Tabla tab:signal_comparison
de la tesis salen de esos histogramas. Aquí se reproduce su tratamiento, tal como está en process.py:

  - espectro neto = neutrones - fondo, bin a bin, sin normalizar por el tiempo;
  - agua pura: eje de carga dividido por 1.4 ("corrección tanque con agua pura") y exceso anulado
    por encima de 13 000 ADU;
  - simulación: número de fotones -> carga con 1000/3.95 ADU por fotón.

Como la publicación no indica el intervalo de carga usado, se barre el umbral inferior U y se calcula
la razón del exceso con Q >= U. Salidas: razones_bariloche_umbral.tsv y fig_razones_bariloche.{pdf,png}.

Uso: python3 razones_histogramas_bariloche.py [archivo de simulación counts-number-photons.txt]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

AQUI = Path(__file__).resolve().parent
HIST = AQUI.parent / "datos-derivados" / "histogramas-carga"
SIM = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI.parent / "datos-derivados" / "simulacion" / "counts-number-photons.txt"
CORRECCION_PURA, CORTE_PURA, ADU_POR_FOTON = 1.4, 13000.0, 1000 / 3.95
TESIS = {"2.5": (11.2, 13.2), "10": (35.6, 31.8)}
COLOR = {"2.5": "#2a78d6", "10": "#eb6834"}

exp = {}
for m in ["pura", "2.5", "10"]:
    n = pd.read_csv(HIST / f"{m}_neutrones_charge_hist.csv")
    f = pd.read_csv(HIST / f"{m}_fondo_charge_hist.csv")
    x = n.bin_center_adu.to_numpy()
    exp[m] = (x, n.counts.to_numpy(), f.counts.to_numpy())

sim = pd.read_csv(SIM, sep=r"\s+", comment="#", names=["fotones", "pura", "2.5", "5", "10"])
q_sim = sim.fotones.to_numpy() * ADU_POR_FOTON


def neto_exp(m, u):
    x, n, f = exp[m]
    if m == "pura":
        x = x / CORRECCION_PURA
        sel = (x >= u) & (x < CORTE_PURA)
    else:
        sel = x >= u
    return (n[sel] - f[sel]).sum(), (n[sel] + f[sel]).sum()     # exceso y su varianza de Poisson


filas = []
for u in np.arange(1200, 6001, 20):
    s0, v0 = neto_exp("pura", u)
    fila = {"umbral_ADU": u}
    for m in ["2.5", "10"]:
        s, v = neto_exp(m, u)
        r = s / s0
        fila[f"exp_{m}"], fila[f"err_{m}"] = r, r * np.sqrt(v / s**2 + v0 / s0**2)
        a = sim.loc[q_sim >= u, "pura"].sum()
        fila[f"sim_{m}"] = sim.loc[q_sim >= u, m].sum() / a if a > 0 else np.nan
    filas.append(fila)
tab = pd.DataFrame(filas)
tab.to_csv(AQUI / "razones_bariloche_umbral.tsv", sep="\t", index=False, float_format="%.3f")

print("Umbral en el que cada razón experimental coincide con la publicada:")
for m in ["2.5", "10"]:
    i = (tab[f"exp_{m}"] - TESIS[m][0]).abs().idxmin()
    otra = "10" if m == "2.5" else "2.5"
    print(f"  {m} %: U = {tab.umbral_ADU[i]:.0f} ADU -> {tab[f'exp_{m}'][i]:.2f} ± {tab[f'err_{m}'][i]:.2f}"
          f"  (con ese U, {otra} % = {tab[f'exp_{otra}'][i]:.2f})")
i = ((tab["exp_2.5"] - 11.2).abs() / 11.2 + (tab["exp_10"] - 35.6).abs() / 35.6).idxmin()
print(f"  mejor umbral común: U = {tab.umbral_ADU[i]:.0f} ADU -> {tab['exp_2.5'][i]:.2f} y {tab['exp_10'][i]:.2f}")

fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True, constrained_layout=True)
for ax, (tipo, titulo) in zip(axs, [("exp", "Experimento (histogramas de Bariloche)"), ("sim", "Simulación")]):
    for m, et in [("2.5", "2.5 % NaCl"), ("10", "10 % NaCl")]:
        if tipo == "exp":
            ax.fill_between(tab.umbral_ADU, tab[f"exp_{m}"] - tab[f"err_{m}"], tab[f"exp_{m}"] + tab[f"err_{m}"],
                            color=COLOR[m], alpha=0.25, lw=0)
            ax.plot(tab.umbral_ADU, tab[f"exp_{m}"], color=COLOR[m], lw=2, label=et)
        else:
            ax.step(tab.umbral_ADU, tab[f"sim_{m}"], where="post", color=COLOR[m], lw=2, label=et)
        ax.axhline(TESIS[m][0 if tipo == "exp" else 1], color=COLOR[m], ls="--", lw=1.2,
                   label=f"publicado: {TESIS[m][0 if tipo == 'exp' else 1]}")
    ax.set_yscale("log")
    ax.set_ylim(1, 100)
    ax.set_xlim(1200, 6000)
    ax.set_xlabel("Umbral inferior de carga [ADU]")
    ax.set_title(titulo, fontsize=11)
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8.5, loc="upper left")
axs[0].set_ylabel("Razón respecto al agua pura")
fig.savefig(AQUI / "fig_razones_bariloche.pdf")
fig.savefig(AQUI / "fig_razones_bariloche.png", dpi=200)
