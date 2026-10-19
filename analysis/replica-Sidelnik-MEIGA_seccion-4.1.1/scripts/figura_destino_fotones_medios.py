#!/usr/bin/env python3
"""Destino de los fotones Cherenkov transportados en los cuatro medios (version multi-medio de la Fig. 7):
(a) destino final; (b) rebotes en el Tyvek antes del destino; (c) fraccion que llega al PMT segun la energia;
(d) fraccion absorbida en la pared y en el agua segun la energia.
Lee resultados/<medio>_fotones.npz (destino_fotones.py). Escribe figuras/fig07_destino_fotones y
resultados/destino_fotones_medios.json."""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
MED = [m for m in ["pura", "nacl25", "nacl5", "nacl10"] if os.path.exists(os.path.join(RES, f"{m}_fotones.npz"))]
ETQ = {"pura": "Agua pura", "nacl25": "Agua + 2,5 % NaCl", "nacl5": "Agua + 5 % NaCl", "nacl10": "Agua + 10 % NaCl"}
COL = {"pura": "#e34948", "nacl25": "#1baf7a", "nacl5": "#7b1fa2", "nacl10": "#eda100"}
CORTO = {"PMT": "llega al PMT", "absorcion_agua": "absorbido en el agua", "pared": "absorbido en la pared (Tyvek)", "tyvek": "perdido en Tyvek/acero"}
eb = np.linspace(1.9, 4.3, 13); ec = 0.5 * (eb[1:] + eb[:-1])
out = {}
for m in MED:
    z = np.load(os.path.join(RES, f"{m}_fotones.npz"))
    D = list(z["DEST"]); d, reb, E = z["dest"], z["rebotes"], z["E"]
    o = {"fotones": int(len(d)), "destino": {k: float((d == i).mean()) for i, k in enumerate(D[:4])},
         "rebotes_medios": float(reb.mean()), "rebotes_hist": np.histogram(reb, np.arange(0, 81))[0].tolist(),
         "prob_absorcion_por_choque_pared": float((d == 2).sum() / (reb.sum() + (d == 2).sum())), "por_energia": {}}
    for i, k in enumerate(D[:4]):
        o["por_energia"][k] = [float((d[(E >= a) & (E < b)] == i).mean()) for a, b in zip(eb[:-1], eb[1:])]
    out[m] = o; del z, d, reb, E
    print(m, {k: round(100 * v, 2) for k, v in o["destino"].items()}, round(o["rebotes_medios"], 2), round(100 * o["prob_absorcion_por_choque_pared"], 2))
json.dump({"E_eV": ec.tolist(), "medios": out}, open(os.path.join(RES, "destino_fotones_medios.json"), "w"), indent=1)

estilo.aplicar()
fig, axs = plt.subplots(2, 2, figsize=(8, 10.4))
a = axs[0, 0]; ks = ["PMT", "absorcion_agua", "pared", "tyvek"]; h = 0.8 / len(MED)
for j, m in enumerate(MED):
    y = np.arange(len(ks)) + (len(MED) / 2 - j - 0.5) * h
    v = [100 * out[m]["destino"][k] for k in ks]
    a.barh(y, v, h, color=COL[m])
    for yy, vv in zip(y, v):
        a.text(vv + 1, yy, f"{vv:.1f}".replace(".", ","), va="center", fontsize=10)
a.set_yticks(range(len(ks))); a.set_yticklabels(["llega\nal PMT", "absorbido\nen el agua", "absorbido\nen la pared", "perdido en\nTyvek/acero"]); a.set_xlim(0, 100)
a.set_xlabel("% de los fotones transportados"); a.set_title("(a) Destino final de los fotones", fontsize=10.5)
a = axs[0, 1]
for m in MED:
    hh = np.array(out[m]["rebotes_hist"], float); a.step(np.arange(80), hh / hh.sum(), where="mid", color=COL[m], lw=1.3)
a.set_yscale("log"); a.set_xlabel("Rebotes en el Tyvek"); a.set_ylabel("Fracción de fotones")
a.set_title("(b) Rebotes antes del destino\n(medias: " + ", ".join(f"{out[m]['rebotes_medios']:.1f}".replace(".", ",") for m in MED) + ")", fontsize=10.5)
a = axs[1, 0]
for m in MED:
    a.plot(ec, [100 * x for x in out[m]["por_energia"]["PMT"]], "o-", ms=4, color=COL[m])
a.set_xlabel("Energía del fotón [eV]"); a.set_ylabel("% que llega al PMT"); a.set_ylim(0, 11)
a.set_title("(c) Fotones que llegan al PMT\nsegún su energía", fontsize=10.5)
a = axs[1, 1]
for m in MED:
    a.plot(ec, [100 * x for x in out[m]["por_energia"]["pared"]], "o-", ms=4, color=COL[m])
    a.plot(ec, [100 * x for x in out[m]["por_energia"]["absorcion_agua"]], "s--", ms=3.5, color=COL[m], mfc="white")
a.set_xlabel("Energía del fotón [eV]"); a.set_ylabel("% de los fotones de esa energía"); a.set_ylim(0, 100)
a.legend(handles=[Line2D([], [], color="#555555", marker="o", ms=4, label="en la pared"),
                  Line2D([], [], color="#555555", marker="s", ms=3.5, mfc="white", ls="--", label="en el agua")], loc="center right", bbox_to_anchor=(1.0, 0.5), fontsize=10.5, title="absorbido:", title_fontsize=10.5)
a.set_title("(d) Absorción en la pared y en el agua\nsegún la energía", fontsize=10.5)
estilo.leyenda_medios(fig, MED, COL, ETQ)
fig.tight_layout(rect=(0, 0.05, 1, 1))
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig07_destino_fotones.{e}"))
