#!/usr/bin/env python3
"""Figura de las interacciones inelasticas del neutron primario (resultados de inelasticas_primario.py):
(a) profundidad de la inelastica a lo largo del haz, (b) multiplicidad media de productos, (c) espectro de energia de los
productos (agua pura), (d) nucleos residuales mas frecuentes. Escribe figuras/fig20_inelasticas_primario.{png,pdf}"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
MED = [m for m in ["pura", "nacl25", "nacl5", "nacl10"] if os.path.exists(os.path.join(RES, f"inelasticas_primario_{m}.json"))]
ETQ = {"pura": "Agua pura", "nacl25": "Agua + 2,5 % NaCl", "nacl5": "Agua + 5 % NaCl", "nacl10": "Agua + 10 % NaCl"}
COL = {"pura": "#e41a1c", "nacl25": "#1a8a1a", "nacl5": "#7b1fa2", "nacl10": "#f5a623"}
J = {m: json.load(open(os.path.join(RES, f"inelasticas_primario_{m}.json"))) for m in MED}
Z = {m: np.load(os.path.join(RES, f"inelasticas_primario_{m}.npz")) for m in MED}
estilo.aplicar()
fig, axs = plt.subplots(2, 2, figsize=(8, 10.4))
a = axs[0, 0]; b = np.arange(0, 100.5, 2)
for m in MED:
    pr = Z[m]["prof"]; agua = np.char.startswith(Z[m]["mat"], "Water") | np.char.startswith(Z[m]["mat"], "SaltyWater")
    a.hist(pr[agua], b, histtype="step", lw=1.5, color=COL[m], weights=np.full(agua.sum(), 1 / J[m]["N"]), label=ETQ[m])
x = np.linspace(0, 96, 200); lam = J["pura"]["prof_media_cm"]
a.axvline(0.062, color="#555555", ls=":", lw=1); a.set_xlabel("Profundidad desde la cara de entrada [cm]"); a.set_ylabel("Inelásticas por neutrón / 2 cm")
a.set_title("(a) Dónde: profundidad de la inelástica\ndel primario en el medio", fontsize=10.5)
a = axs[0, 1]; T = ["neutron", "proton", "deuteron", "triton", "He3", "alpha", "pi+", "pi-", "pi0", "gamma", "núcleo residual"]
NOM = ["n", "p", "d", "t", "$^3$He", "α", "π$^+$", "π$^-$", "π$^0$", "γ", "res."]
xx = np.arange(len(T)); w = 0.8 / len(MED)
for i, m in enumerate(MED):
    v = [J[m]["multiplicidad_media"][t] for t in T]
    a.bar(xx + (i - (len(MED) - 1) / 2) * w, v, w, color=COL[m], label=ETQ[m])
a.set_yscale("log"); a.set_ylim(0.01, 5); a.set_xticks(xx); a.set_xticklabels(NOM, fontsize=9.5)
a.set_ylabel("Partículas por inelástica"); a.set_title("(b) Resultado: multiplicidad\nde los productos", fontsize=10.5)
a = axs[1, 0]; EB = Z["pura"]["EB"]; c = np.sqrt(EB[1:] * EB[:-1]); dl = np.log(EB[1:] / EB[:-1]); n = J["pura"]["inelasticas"]
for t, et, col in [("neutron", "n", "#0b0b0b"), ("proton", "p", "#2a78d6"), ("alpha", "α", "#eda100"), ("deuteron", "d", "#8a8984"),
                   ("pi-", "π$^-$", "#7b1fa2"), ("pi0", "π$^0$", "#c51b8a"), ("gamma", "γ", "#1baf7a")]:
    h = Z["pura"][f"E|{t}"] / n / dl; s = h > 0
    a.step(c[s], h[s], where="mid", color=col, lw=1.3, label=et)
a.axvline(500, color="#e41a1c", ls=":", lw=1)
a.set_xscale("log"); a.set_yscale("log"); a.set_xlim(0.05, 600); a.set_ylim(1e-4, 5)
a.set_xlabel("Energía cinética [MeV]"); a.set_ylabel("dN/d(ln E) por inelástica")
a.set_title("(c) Energía de los productos\n(agua pura; punteada: 500 MeV)", fontsize=10.5); a.set_ylim(1e-4, 60); a.legend(fontsize=8.5, ncol=4, loc="upper left", columnspacing=0.8, handlelength=1.2)
a = axs[1, 1]; rs = list(J["pura"]["nucleos_residuales"])[:12]; yy = np.arange(len(rs))
for i, m in enumerate(MED):
    a.barh(yy + (i - (len(MED) - 1) / 2) * w, [100 * J[m]["nucleos_residuales"].get(k, 0) for k in rs], w, color=COL[m], label=ETQ[m])
import re
a.set_yticks(yy); a.set_yticklabels([re.sub(r"([A-Za-z]+)(\d+)", r"$^{\2}$\1", k) for k in rs], fontsize=9.5); a.invert_yaxis()
a.set_xlabel("% de las inelásticas"); a.set_title("(d) Núcleo residual\n(blanco $^{16}$O en el 97 %)", fontsize=10.5)
estilo.leyenda_medios(fig, MED, COL, ETQ)
fig.tight_layout(rect=(0, 0.035, 1, 1))
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig20_inelasticas_primario.{e}"))
print("ok")
