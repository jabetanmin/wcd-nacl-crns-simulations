#!/usr/bin/env python3
"""
Gráficas de espectros por humedad y humedad frente a la razón de neutrones (forma de Desilets).

Lee resultados/espectros_albedo.tsv (corridas completas, de analizar_albedo.py) y resultados/curva_humedad.json
(de curva_humedad.py). La humedad se dibuja con una rampa azul ordinal (5 % azul, 10 % cian, 15 % marrón, 25 % rosa, 30 % oliva: ninguno coincide con los colores
de los medios, rojo, verde, púrpura y naranja); el seco de MEIGA en negro a trazos, el seco de la tesis en negro continuo y el flujo que baja en gris.
-> figuras/fig05_espectros_humedades, fig06_seco_meiga_y_humedades, fig07_seco_tesis_y_humedades,
   fig08_humedad_vs_neutrones
"""
import csv, json, os, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from regiones import COLOR, AJUSTE, sombrear

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
# paleta categórica (orden fijo): azul, naranja, aqua, amarillo, magenta, verde, violeta, rojo
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
HUM_COL = {5: "#1f5fbf", 10: "#17becf", 15: "#8c564b", 25: "#e377c2", 30: "#bcbd22"}   # humedades: sin rojo, verde, púrpura ni naranja (colores de los medios)
BANDA_COL = COLOR                                                 # regiones de la Tabla 2.2 de la tesis (regiones.py)
SECO_MEIGA, SECO_TESIS, BAJA = "#0b0b0b", "#0b0b0b", "#a8a6a0"   # referencias en negro y gris

with open(os.path.join(RES, "espectros_albedo.tsv")) as f:
    filas = list(csv.reader(f, delimiter="\t"))
cab, dat = filas[0], np.array(filas[1:], dtype=float)
B = np.concatenate([dat[:, 0], dat[-1:, 1]])
col = {c: dat[:, i] for i, c in enumerate(cab) if i >= 2}
hum = sorted(((int(re.search(r"humedo-(\d+)", c).group(1)), c) for c in col if "humedo-" in c))
color_h = {w: HUM_COL.get(w, "0.3") for w, _ in hum}
seco_m = next(c for c in col if "seco" in c and "MEIGA" in c)
seco_t = next(c for c in col if "seco" in c and "tesis" in c)
baja = next(c for c in col if c.startswith("Baja"))

def base(ax, titulo):
    sombrear(ax, 1e-10, 1e4)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1e-10, 1e4); ax.set_ylim(1e-1, 3e3)
    ax.set_xlabel("Energía cinética $E_n$ [MeV]"); ax.set_ylabel(r"$E\,d\Phi/dE$ [n m$^{-2}$ s$^{-1}$]")
    ax.set_title(titulo, fontsize=11); ax.grid(alpha=0.25, ls=":", which="both", color="0.6")

def humedades(ax):
    for w, c in hum:
        ax.stairs(np.clip(col[c], 1e-4, None), B, color=color_h[w], lw=1.8, label=f"{w} % de agua (MEIGA)")

def guardar(fig, nombre):
    fig.tight_layout()
    for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"{nombre}.{e}"), dpi=170)
    plt.close(fig)

fig, ax = plt.subplots(figsize=(11, 5.8)); base(ax, "Flujo que sube del suelo: todas las humedades (MEIGA)")
humedades(ax); ax.legend(fontsize=9, loc="lower center", ncol=3, title="Humedad gravimétrica w"); guardar(fig, "fig05_espectros_humedades")

fig, ax = plt.subplots(figsize=(11, 5.8)); base(ax, "Suelo seco de MEIGA y suelos húmedos (mismo montaje)")
ax.stairs(np.clip(col[seco_m], 1e-4, None), B, color=SECO_MEIGA, lw=2.0, ls="--", label="seco (MEIGA)")
humedades(ax); ax.legend(fontsize=9, loc="lower center", ncol=3); guardar(fig, "fig06_seco_meiga_y_humedades")

fig, ax = plt.subplots(figsize=(11, 5.8)); base(ax, "Suelo seco de la tesis y suelos húmedos de MEIGA")
ax.stairs(np.clip(col[baja], 1e-4, None), B, color=BAJA, lw=1.4, label="baja (tesis, entrada)")
ax.stairs(np.clip(col[seco_t], 1e-4, None), B, color=SECO_TESIS, lw=2.2, label="sube, seco (tesis)")
humedades(ax); ax.legend(fontsize=9, loc="lower center", ncol=3); guardar(fig, "fig07_seco_tesis_y_humedades")

# --- validación: suelo seco de la tesis frente al de MEIGA, con el cociente por energía ---
VAL = "#1f5fbf"                                                   # seco de MEIGA en la validación (azul)
fig, (ax, axr) = plt.subplots(2, 1, figsize=(11, 7.2), sharex=True, gridspec_kw={"height_ratios": [3, 1.3]})
base(ax, "Validación del suelo seco: tesis frente a MEIGA")
ax.stairs(np.clip(col[baja], 1e-4, None), B, color=BAJA, lw=1.4, label="baja (tesis, entrada)")
ax.stairs(np.clip(col[seco_t], 1e-4, None), B, color=SECO_TESIS, lw=2.2, label="sube, seco (tesis)")
ax.stairs(np.clip(col[seco_m], 1e-4, None), B, color=VAL, lw=1.8, ls="--", label="sube, seco (MEIGA)")
ax.set_xlabel(""); ax.legend(fontsize=9, loc="lower center", ncol=3)
B2 = np.logspace(-10, 4, 57); du_ = np.log(B[1:] / B[:-1])
def rebin(y):
    cnt = y * du_; return np.array([cnt[(B[:-1] >= a_ * 0.999) & (B[1:] <= b_ * 1.001)].sum() for a_, b_ in zip(B2[:-1], B2[1:])])
rt, rm = rebin(col[seco_t]), rebin(col[seco_m]); ok = rt > 0.02 * rt.max()   # se ocultan los intervalos casi vacíos
axr.stairs(np.where(ok, rm / np.where(ok, rt, 1), np.nan), B2, color=VAL, lw=1.8, baseline=None)
sombrear(axr, 1e-10, 1e4, etiquetas=False)
axr.axhline(1, color=SECO_TESIS, lw=1); axr.axhspan(0.9, 1.1, color="0.85", alpha=0.6, zorder=0)
axr.set_xscale("log"); axr.set_ylim(0.4, 1.6); axr.set_xlim(1e-10, 1e4); axr.grid(alpha=0.25, ls=":", which="both")
axr.set_ylabel("MEIGA / tesis"); axr.set_xlabel("Energía cinética $E_n$ [MeV]")
axr.text(2e-10, 1.45, "franja gris: ±10 %", fontsize=8, color="0.35")
guardar(fig, "fig11_validacion_seco")

# --- todas las curvas: entrada, los dos secos y todas las humedades ---
fig, ax = plt.subplots(figsize=(11, 6.2)); base(ax, "Flujo que baja y flujo que sube del suelo: todas las corridas")
ax.stairs(np.clip(col[baja], 1e-4, None), B, color=BAJA, lw=1.4, label="baja (tesis, entrada)")
ax.stairs(np.clip(col[seco_t], 1e-4, None), B, color=SECO_TESIS, lw=2.2, label="sube, seco (tesis)")
ax.stairs(np.clip(col[seco_m], 1e-4, None), B, color=SECO_MEIGA, lw=1.8, ls="--", label="sube, seco (MEIGA)")
humedades(ax); ax.legend(fontsize=8.5, loc="lower center", ncol=3); guardar(fig, "fig12_todas_las_corridas")

# --- humedad frente a la razón de neutrones N/N0 (inversa de la forma de Desilets) ---
C = json.load(open(os.path.join(RES, "curva_humedad.json")))
V = C["validacion"]; aj = C["ajustes"]; L = C["desilets_literatura"]
inv = lambda r, a0, a1, a2: a0 / (r - a1) - a2
fig, ax = plt.subplots(figsize=(9, 6))
for reg, cc, mk in ((AJUSTE[0], BANDA_COL[AJUSTE[0]], "o"), (AJUSTE[1], BANDA_COL[AJUSTE[1]], "s")):
    x = np.array([f["cociente"][reg] for f in V]); e = np.array([f["err"][reg] for f in V]); y = np.array([f["tg"] for f in V])
    p = aj[reg]; rr = np.linspace(p["a1"] + p["a0"] / (max(y) * 1.15 + p["a2"]), 1.0, 300)
    ax.plot(rr, inv(rr, p["a0"], p["a1"], p["a2"]), color=cc, lw=2,
            label=f"{reg.lower()}: ajuste $\\theta_g = {p['a0']:.4f}/(N/N_0 - {p['a1']:.3f}) - {p['a2']:.3f}$")
    ax.errorbar(x, y, xerr=e, fmt=mk, color=cc, ms=8, capsize=3, mec="white", mew=1.2, label=f"{reg.lower()} (MEIGA)")
    if reg == AJUSTE[0]:
        for f, xi, yi in zip(V, x, y):
            if f["w"] > 0: ax.annotate(f"{100 * f['w']:.0f} %", (xi, yi), xytext=(7, 4), textcoords="offset points", fontsize=8, color="0.25")
rr = np.linspace(L["a1"] + L["a0"] / (0.5 + L["a2"]), 1.0, 300)
ax.plot(rr, inv(rr, L["a0"], L["a1"], L["a2"]), "k--", lw=1.4, label="Desilets et al. (2010), parámetros de la literatura")
ax.set_xlabel("Razón de neutrones que suben $N/N_0$ (húmedo / seco)"); ax.set_ylabel(r"Humedad gravimétrica $\theta_g = w/(1-w)$ [g/g]")
ax.set_ylim(-0.01, 0.5); ax.set_xlim(0.38, 1.02); ax.grid(alpha=0.3, ls="--")
ax.set_title("Humedad del suelo en función de la razón de neutrones (forma de Desilets)", fontsize=11)
ax.legend(fontsize=8, loc="upper right"); guardar(fig, "fig08_humedad_vs_neutrones")
print("figuras 05-08 listas;", len(hum), "humedades")
