#!/usr/bin/env python3
"""Cascadas de gammas de las capturas en 35Cl, 23Na y 1H (secundarias de nCapture guardadas en <medio>.npz).
Compara la energia total emitida con el valor Q de la captura (35Cl: 8,579 MeV; 23Na: 6,959; 1H: 2,224).
Escribe resultados/cascadas_cloro_<medio>.json y figuras/fig12_cascadas_cloro_<medio>.{png,pdf}.
Uso: cascadas_cloro.py [medio]"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
m = sys.argv[1] if len(sys.argv) > 1 else "nacl25"
z = np.load(os.path.join(R, "resultados", f"{m}.npz"))
cap = pd.DataFrame({"run": z["cap_run_id"], "trk": z["cap_track_id"], "Z": z["cap_target_Z"], "A": z["cap_target_A"]})
sc = pd.DataFrame({"run": z["sc_run"], "trk": z["sc_ptrk"], "p": z["sc_part"], "E": z["sc_E"]})
g = sc[sc.p == "gamma"].groupby(["run", "trk"]).agg(n=("E", "size"), S=("E", "sum"), Emax=("E", "max"))
c = cap.merge(g, left_on=["run", "trk"], right_index=True, how="left").fillna({"n": 0, "S": 0, "Emax": 0})
QV = {(1, 1): 2.2246, (11, 23): 6.9594, (17, 35): 8.5794}
out = {}
for (Z, A), q in QV.items():
    d = c[(c.Z == Z) & (c.A == A)]
    if len(d) < 20:
        continue
    out[f"Z{Z}A{A}"] = {"capturas": int(len(d)), "Q_MeV": q, "gammas_por_captura": float(d.n.mean()),
                        "suma_media_MeV": float(d.S.mean()), "suma_p5_p50_p95": np.percentile(d.S, [5, 50, 95]).tolist(),
                        "frac_suma_igual_Q_1pct": float((np.abs(d.S - q) < 0.01 * q).mean()),
                        "frac_suma_mayor_Q": float((d.S > 1.01 * q).mean()), "frac_suma_menor_Q": float((d.S < 0.99 * q).mean()),
                        "frac_un_solo_gamma": float((d.n == 1).mean()),
                        "frac_con_gamma_8579": float(((d.Emax > 8.57) & (d.Emax < 8.59)).mean()) if Z == 17 else None,
                        "n_gammas": {int(k): int(v) for k, v in d.n.value_counts().sort_index().items()}}
json.dump(out, open(os.path.join(R, "resultados", f"cascadas_cloro_{m}.json"), "w"), indent=1)
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.color": "#e4e3df", "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "savefig.dpi": 160})
estilo.aplicar()
fig, axs = plt.subplots(1, 2, figsize=(8, 4.3))
for (Z, A), col, et in [((17, 35), "#1baf7a", "$^{35}$Cl (Q = 8,58 MeV)"), ((11, 23), "#4a3aa7", "$^{23}$Na (Q = 6,96 MeV)"), ((1, 1), "#2a78d6", "$^{1}$H (Q = 2,22 MeV)")]:
    d = c[(c.Z == Z) & (c.A == A)]
    if len(d) < 20:
        continue
    axs[0].hist(d.S, bins=np.arange(0, 25, 0.1), histtype="step", density=True, color=col, lw=1.4, label=et)
    axs[0].axvline(QV[(Z, A)], color=col, ls=":", lw=1)
    vc = d.n.value_counts(normalize=True).sort_index()
    axs[1].plot(vc.index, vc.values, "o-", color=col, label=et)
axs[0].set_yscale("log"); axs[0].set_xlabel("Energía total de los gammas [MeV]"); axs[0].set_ylabel("Densidad")
axs[0].set_title("(a) Energía emitida por captura\n(punteada: valor Q)", fontsize=10.5)
axs[1].set_xlabel("Número de gammas por captura"); axs[1].set_ylabel("Fracción de capturas")
axs[1].set_title("(b) Multiplicidad de la cascada", fontsize=10.5)
fig.legend(*axs[1].get_legend_handles_labels(), loc="lower center", ncol=3, frameon=False, columnspacing=1.2)
fig.tight_layout(rect=(0, 0.09, 1, 1))
for e in ("png", "pdf"):
    fig.savefig(os.path.join(R, "figuras", f"fig12_cascadas_cloro_{m}.{e}"))
print(json.dumps({k: {kk: v[kk] for kk in ("capturas", "suma_media_MeV", "frac_suma_igual_Q_1pct", "frac_suma_mayor_Q", "frac_un_solo_gamma")} for k, v in out.items()}, indent=1))
