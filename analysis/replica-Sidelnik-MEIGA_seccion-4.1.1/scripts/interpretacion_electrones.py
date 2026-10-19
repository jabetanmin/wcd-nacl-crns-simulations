#!/usr/bin/env python3
"""Interpretacion fisica de las diferencias con la Fig. 5 de Sidelnik usando la descomposicion por origen
(resultados/<medio>_origen_electrones.npz, de origen_electrones.py):
 - salto en el borde Compton de 1,994 MeV: J = (C_H + F_antes) / F_despues, con C_H = electrones de la captura en H
   y F = fondo de gammas de otros origenes (sobre todo dispersion inelastica de neutrones en O);
 - factor k por el que habria que dividir el fondo de MEIGA para obtener el salto de Sidelnik;
 - cociente NaCl/agua pura en 2-6 MeV con el fondo de MEIGA y con el fondo dividido por k.
Escribe resultados/interpretacion_electrones.json y figuras/fig14_origen_electrones.{png,pdf}"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
GR = [("captura H", "#2a78d6"), ("captura Cl", "#1baf7a"), ("captura otra", "#8fd3b6"), ("inelástica n", "#eda100"),
      ("otros hadrónicos", "#8a8984"), ("bremsstrahlung", "#e34948"), ("aniquilación", "#f4a3a3"), ("decaimiento radiactivo", "#4a3aa7")]
EL = json.load(open(os.path.join(RES, "espectro_electrones_tipo_sidelnik.json")))
D = {}
for m in ["pura", "nacl25"]:
    z = np.load(os.path.join(RES, f"{m}_origen_electrones.npz")); N = int(z["N"]); EB = z["EB"]
    D[m] = {g: z[f"h|{g}|todos"] * 150000 / N for g, _ in GR if f"h|{g}|todos" in z.files}
    D[m]["_sp"] = {g: z[f"h|{g}|sin_piones"] * 150000 / N for g, _ in GR if f"h|{g}|sin_piones" in z.files}
c = 0.5 * (EB[1:] + EB[:-1])
w = lambda h, a, b: float(h[(c > a) & (c < b)].mean())
CAP = ("captura H", "captura Cl", "captura otra")
def partes(m, a, b, sp=False):
    d = D[m]["_sp"] if sp else D[m]
    gs = [g for g in d if not g.startswith("_")]
    return sum(w(d[g], a, b) for g in gs if g in CAP), sum(w(d[g], a, b) for g in gs if g not in CAP)
out = {"composicion": {}}
for m in D:
    A = {g: w(D[m][g], 1.874, 1.964) for g in D[m] if g != "_sp"}; B = {g: w(D[m][g], 2.024, 2.114) for g in D[m] if g != "_sp"}
    out["composicion"][m] = {"antes_borde": A, "despues_borde": B,
                             "frac_inelastica_despues": B["inelástica n"] / sum(B.values()),
                             "salto": sum(A.values()) / sum(B.values())}
    ca, fa = partes(m, 1.874, 1.964); cb, fb = partes(m, 2.024, 2.114)
    cas, fas = partes(m, 1.874, 1.964, True); cbs, fbs = partes(m, 2.024, 2.114, True)
    out["composicion"][m]["salto_sin_piones"] = (cas + fas) / (cbs + fbs)
    Js = EL["saltos_bordes"][m]["2,223 (H)"]["Sidelnik"]
    # (ca + fa/k) / (cb + fb/k) = Js  ->  k
    k = (fa - Js * fb) / (Js * cb - ca)
    out["composicion"][m]["salto_Sidelnik"] = Js; out["composicion"][m]["k_fondo"] = k
kp = out["composicion"]["pura"]["k_fondo"]
out["NaCl_sobre_pura"] = {}
for a, b in [(0.5, 1.8), (2.05, 4.0), (4.0, 5.85), (7.0, 8.3)]:
    cp, fp = partes("pura", a, b); cn, fn = partes("nacl25", a, b)
    sid = [EL["NaCl_sobre_pura"]["nacl25"][e]["Sidelnik"] for e in EL["NaCl_sobre_pura"]["nacl25"] if a <= float(e) <= b]
    out["NaCl_sobre_pura"][f"{a}-{b}"] = {"MEIGA": (cn + fn) / (cp + fp), "MEIGA_fondo_entre_k": (cn + fn / kp) / (cp + fp / kp),
                                         "Sidelnik": float(np.median(sid)) if sid else None}
json.dump(out, open(os.path.join(RES, "interpretacion_electrones.json"), "w"), indent=1, ensure_ascii=False)

plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.color": "#e4e3df", "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "savefig.dpi": 160})
estilo.aplicar()
fig, axs = estilo.tres_paneles(10.2)
for a, m, t in [(axs[0], "pura", "(a) Agua pura"), (axs[1], "nacl25", "(b) Agua + 2,5 % NaCl")]:
    base = np.zeros_like(c)
    for g, col in GR:
        if g in D[m] and D[m][g].sum() > 0:
            a.fill_between(c, base, base + D[m][g], step="mid", color=col, lw=0, label=g); base = base + D[m][g]
    a.set_yscale("log"); a.set_ylim(10, 1e6); a.set_xlim(0, 10); a.set_xlabel("Energía del electrón [MeV]"); a.set_ylabel("Cuentas / 20 keV")
    a.set_title(f"{t}:\norigen del gamma del electrón", fontsize=10.5)
    for E in (1.994, 5.875, 8.33):
        a.axvline(E, color="#0b0b0b", ls=":", lw=0.7)
a = axs[2]
lab = list(out["NaCl_sobre_pura"]); x = np.arange(len(lab))
for i, (key, col, nom) in enumerate([("Sidelnik", "#0b0b0b", "Sidelnik"), ("MEIGA", "#1baf7a", "MEIGA"),
                                      ("MEIGA_fondo_entre_k", "#8fd3b6", f"MEIGA con fondo / {kp:.2f}")]):
    v = [out["NaCl_sobre_pura"][l][key] or 0 for l in lab]
    a.bar(x + (i - 1) * 0.27, v, 0.27, color=col, label=nom)
    for xx, vv in zip(x + (i - 1) * 0.27, v):
        a.text(xx, vv + 0.04, f"{vv:.2f}".replace(".", ","), ha="center", fontsize=10.5)
a.set_xticks(x); a.set_xticklabels([l.replace("-", "–").replace(".", ",") + " MeV" for l in lab], fontsize=11); a.axhline(1, color="#0b0b0b", lw=0.8)
a.set_ylabel("Electrones NaCl / agua pura"); a.set_ylim(0, 1.25 * a.get_ylim()[1]); a.legend(fontsize=9, ncol=3, loc="upper left"); a.set_title("(c) Cociente 2,5 % NaCl / agua pura y efecto del fondo", fontsize=10.5)
fig.legend(*axs[1].get_legend_handles_labels(), loc="lower center", ncol=4, frameon=False, columnspacing=1.0, handlelength=1.4, title="origen del gamma (a, b):", title_fontsize=11.5)
fig.tight_layout(rect=(0, 0.10, 1, 1))
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig14_origen_electrones.{e}"))
print(json.dumps({m: {k_: v for k_, v in d.items() if k_ not in ("antes_borde", "despues_borde")} for m, d in out["composicion"].items()}, indent=1, ensure_ascii=False))
print(json.dumps(out["NaCl_sobre_pura"], indent=1))
