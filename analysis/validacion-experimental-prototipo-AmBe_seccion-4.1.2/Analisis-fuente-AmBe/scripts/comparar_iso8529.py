#!/usr/bin/env python3
"""Compara el espectro ISO 8529 digitalizado con el espectro limpio de la digitalización previa
(dN/dE lineal y B_E·E en letargia). -> figuras/fig10, resultados/comparacion_iso8529.json"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
E1, E2, L = np.loadtxt(os.path.join(RES, "ISO8529_AmBe_digitalizado.txt"), unpack=True)
Eg, Sg = np.loadtxt(os.path.join(RES, "espectro_AmBe_limpio.txt"), unpack=True)

w = L * np.log(E2 / E1); w /= w.sum()                  # fracción por grupo
dNdE_iso = w / (E2 - E1)                                # MeV^-1, constante por grupo en letargia ~ aprox.
Em_iso = float(np.sum(L * (E2 - E1)) / np.sum(L * np.log(E2 / E1)))
Em_l = float(np.trapz(Eg * Sg, Eg))
# fracciones por banda
def frac_iso(a, b):
    s = 0.0
    for e1, e2, l in zip(E1, E2, L):
        lo, hi = max(a, e1), min(b, e2)
        if hi > lo: s += l * np.log(hi / lo)
    return s / np.sum(L * np.log(E2 / E1))
def frac_l(a, b):
    m = (Eg >= a) & (Eg <= b); return float(np.trapz(Sg[m], Eg[m]))
bandas = [(0.1, 1), (1, 2), (2, 4), (4, 6), (6, 8), (8, 11)]
R = {"E_media_ISO_digitalizado_MeV": Em_iso, "E_media_ISO_8529_1_2001_MeV": 4.16,
     "E_media_ISO_8529_1_2021_pequena_MeV": 4.17, "E_media_ISO_8529_1_2021_grande_MeV": 4.05,
     "E_media_digitalizacion_previa_limpia_MeV": Em_l, "grupos": int(len(L)),
     "fraccion_bandas_pct": {f"{a}-{b}": {"ISO": round(100 * frac_iso(a, b), 2), "previa": round(100 * frac_l(a, b), 2)}
                             for a, b in bandas}}
json.dump(R, open(os.path.join(RES, "comparacion_iso8529.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(R, indent=1, ensure_ascii=False))

plt.rcParams.update({"font.size": 11, "axes.labelsize": 13})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6))
# dN/dE: en cada grupo B_E·E constante -> dN/dE ∝ 1/E; se dibuja exacto
for e1, e2, l in zip(E1, E2, L):
    e = np.linspace(e1, e2, 20)
    a1.plot(e, l / e / np.sum(L * np.log(E2 / E1)), color="k", lw=1.6)
a1.plot([], [], color="k", lw=1.6, label=f"ISO 8529 digitalizado, $\\langle E\\rangle$={Em_iso:.2f} MeV")
a1.plot(Eg, Sg, color="royalblue", lw=1.6, alpha=0.8, label=f"Digitalización previa (limpia), {Em_l:.2f} MeV")
a1.set_xlabel("$E_n$ [MeV]"); a1.set_ylabel(r"$dN/dE$ [MeV$^{-1}$]"); a1.set_xlim(0, 11.5); a1.set_ylim(bottom=0)
a1.grid(alpha=0.3, ls="--"); a1.legend(fontsize=9)
a2.stairs(L / np.sum(L * np.log(E2 / E1)), np.append(E1, E2[-1]), color="k", lw=1.6, label="ISO 8529 digitalizado")
a2.plot(Eg, Eg * Sg, color="royalblue", lw=1.6, alpha=0.8, label="Digitalización previa (limpia)")
a2.set_xscale("log"); a2.set_xlim(0.08, 15)
a2.set_xlabel("$E_n$ [MeV]"); a2.set_ylabel(r"$E\,dN/dE$ (por unidad de letargia)")
a2.grid(alpha=0.3, ls="--", which="both"); a2.legend(fontsize=9)
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig10_iso8529_vs_previa.{ext}"), dpi=200)
