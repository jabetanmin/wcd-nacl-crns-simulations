#!/usr/bin/env python3
"""Diagnostico de la carga en el PMT: destino de los fotones opticos seguidos, rebotes en el Tyvek,
dependencia con la energia y comparacion de tres magnitudes con la Fig. 6 de Sidelnik.
Lee resultados/<medio>.npz y <medio>_fotones.npz; escribe resultados/diagnostico_<medio>.json y figuras."""
import os, sys, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
m = sys.argv[1] if len(sys.argv) > 1 else "pura"
REF6 = os.path.join(R, "datos", "fig6_sidelnik_digitalizada_700pts.csv")   # Fig. 6 de Sidelnik digitalizada (700 puntos)
COLREF = {"pura": "Pure_H2O_counts_digitized", "nacl25": "NaCl_2p5_counts_digitized",
          "nacl5": "NaCl_5_counts_digitized", "nacl10": "NaCl_10_counts_digitized"}
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.color": "#e4e3df", "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "savefig.dpi": 160})
ETQD = {"PMT": "llega al PMT", "absorcion_agua": "absorbido en el agua", "pared": "absorbido en la pared (Tyvek)",
        "tyvek": "perdido dentro del Tyvek/acero"}
CD = {"PMT": "#2a78d6", "absorcion_agua": "#1baf7a", "pared": "#eb6834", "tyvek": "#8a8984"}

z = np.load(os.path.join(RES, f"{m}_fotones.npz")); p = np.load(os.path.join(RES, f"{m}.npz"))
D = list(z["DEST"]); d, reb, L, E, run = z["dest"], z["rebotes"], z["L"], z["E"], z["run"]
q, nch = p["Q"], p["cher_n_por_run"]; N = len(q)
seg = np.bincount(run, minlength=N)
lleg = np.bincount(run[d == 0], minlength=N)
out = {"fotones_creados_por_neutron": float(nch.mean()), "fotones_seguidos_por_neutron": float(seg.mean()),
       "fraccion_seguidos": float(seg.sum() / nch.sum()), "llegan_PMT_por_neutron": float(lleg.mean()),
       "Q_media": float(q.mean()), "eventos_Q_igual_llegadas": float((lleg == q).mean()),
       "suma_llegadas": int(lleg.sum()), "suma_Q": int(q.sum())}
out["destino"] = {k: {"frac": float((d == i).mean()), "rebotes_medios": float(reb[d == i].mean()) if (d == i).any() else 0.0,
                      "camino_medio_cm": float(L[d == i].mean()) if (d == i).any() else 0.0} for i, k in enumerate(D) if (d == i).any()}
out["prob_muerte_por_choque_pared"] = float((d == 2).sum() / (reb.sum() + (d == 2).sum()))
out["rebotes_p10_p50_p90"] = np.percentile(reb, [10, 50, 90]).tolist()
eb = np.linspace(1.9, 4.3, 13); ec = 0.5 * (eb[1:] + eb[:-1])
frac = {k: [] for k in D[:4]}; nE = []
for a, b in zip(eb[:-1], eb[1:]):
    s = (E >= a) & (E < b); nE.append(int(s.sum()))
    for i, k in enumerate(D[:4]):
        frac[k].append(float((d[s] == i).mean()) if s.any() else np.nan)
out["por_energia"] = {"E_eV": ec.tolist(), "n": nE, **frac}
# comparacion con Fig. 6 de Sidelnik
r = pd.read_csv(REF6); x = r.Numero_de_fotones.to_numpy(); y = r[COLREF[m]].to_numpy()
qb = np.arange(0, 2510, 10); c = qb[:-1] + 5
ref = np.interp(c, x, y, left=np.nan, right=np.nan); ok = np.isfinite(ref)
out["comparacion_fig6"] = {}
ETQ6 = {"p.e. en el PMT (tras transporte)": "p.e. en el PMT", "fotones aceptados por la QE al crearse": "aceptados por la QE",
        "fotones Cherenkov creados": "Cherenkov creados"}
CORTO = {"PMT": "llega al PMT", "absorcion_agua": "absorbido en el agua", "pared": "absorbido en la pared", "tyvek": "perdido en Tyvek/acero"}
estilo.aplicar()
fig, axs = plt.subplots(1, 2, figsize=(8, 4.4), gridspec_kw={"width_ratios": [1.5, 1]})
for v, nom, col in [(q, "p.e. en el PMT (tras transporte)", "#e34948"), (seg, "fotones aceptados por la QE al crearse", "#2a78d6"),
                    (nch, "fotones Cherenkov creados", "#8a8984")]:
    h = np.histogram(v[v >= 1], qb)[0].astype(float); a = h[ok] / h[ok].sum(); bb = ref[ok] / ref[ok].sum()
    out["comparacion_fig6"][nom] = {"media_sim": float(np.average(c[ok], weights=a)), "media_ref": float(np.average(c[ok], weights=bb)),
                                    "corr_log": float(np.corrcoef(np.log(a + 1e-9), np.log(bb + 1e-9))[0, 1])}
    axs[0].step(c, h / h[ok].sum(), where="mid", color=col, label=f"MEIGA: {ETQ6[nom]}")
axs[0].plot(c[ok], ref[ok] / ref[ok].sum(), "--", color="#0b0b0b", lw=1.2, label="Sidelnik, Fig. 6")
axs[0].set_yscale("log"); axs[0].set_xlim(0, 2500); axs[0].set_ylim(1e-5, 30); axs[0].set_xlabel("Fotones o fotoelectrones por neutrón")
axs[0].set_ylabel("Fracción / 10"); axs[0].legend(fontsize=8.5, loc="upper right"); axs[0].set_title("(a) ¿Qué cuenta la Fig. 6 de Sidelnik?", fontsize=10.5)
pasos = [("creados", nch.mean()), ("aceptados\npor la QE", seg.mean()), ("llegan al\nPMT", lleg.mean())]
axs[1].bar(range(3), [v for _, v in pasos], color=["#8a8984", "#2a78d6", "#e34948"])
for i, (_, v) in enumerate(pasos):
    axs[1].text(i, v * 1.12, f"{v:.1f}".replace(".", ","), ha="center", fontsize=9.5)
axs[1].set_xticks(range(3)); axs[1].set_xticklabels([n for n, _ in pasos], fontsize=9.5); axs[1].set_yscale("log"); axs[1].set_ylim(5, 4000)
axs[1].set_ylabel("Fotones por neutrón (media)"); axs[1].set_title("(b) Balance de luz por neutrón", fontsize=10.5)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig06_balance_luz_y_fig6.png")); fig.savefig(os.path.join(FIG, "fig06_balance_luz_y_fig6.pdf")); plt.close(fig)

fig, axs = estilo.tres_paneles(7.0)
v = [out["destino"][k]["frac"] for k in D[:4] if k in out["destino"]]
ks = [k for k in D[:4] if k in out["destino"]]
axs[0].barh(range(len(ks)), [100 * x for x in v], color=[CD[k] for k in ks])
axs[0].set_yticks(range(len(ks))); axs[0].set_yticklabels([CORTO[k] for k in ks], fontsize=9.5)
for i, x in enumerate(v):
    axs[0].text(100 * x + 1, i, f"{100*x:.1f} %", va="center", fontsize=9)
axs[0].set_xlabel("% de los fotones seguidos"); axs[0].set_title("(a) Destino de los fotones", fontsize=10.5); axs[0].set_xlim(0, 100)
for i, k in enumerate(D[:4]):
    s = d == i
    if s.any():
        axs[1].hist(reb[s], bins=np.arange(0, 80), histtype="step", density=True, color=CD[k], lw=1.4, label=ETQD[k])
axs[1].set_yscale("log"); axs[1].set_xlabel("Rebotes en el Tyvek"); axs[1].set_ylabel("Densidad"); axs[1].set_title("(b) Rebotes antes del destino", fontsize=10.5)
for k in D[:4]:
    axs[2].plot(ec, [100 * x for x in frac[k]], "o-", color=CD[k], ms=4, label=ETQD[k])
axs[2].set_xlabel("Energía del fotón [eV]"); axs[2].set_ylabel("% de los fotones de esa energía"); axs[2].legend(fontsize=8.5)
axs[2].set_title("(c) Destino según la energía del fotón (colores como en (b))", fontsize=10.5)
fig.tight_layout(); fig.savefig(os.path.join(FIG, f"fig07_destino_fotones_{m}.png")); fig.savefig(os.path.join(FIG, f"fig07_destino_fotones_{m}.pdf"))   # la figura de los cuatro medios la hace figura_destino_fotones_medios.py; plt.close(fig)
json.dump(out, open(os.path.join(RES, f"diagnostico_{m}.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False)[:2500])
