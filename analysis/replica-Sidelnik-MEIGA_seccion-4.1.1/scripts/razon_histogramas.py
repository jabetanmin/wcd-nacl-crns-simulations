#!/usr/bin/env python3
"""Curvas de razon de los histogramas de fotones aceptados por la eficiencia cuantica (observable de la Fig. 6 de
Sidelnik) entre cada medio con NaCl y el agua pura, para MEIGA y para la Fig. 6 digitalizada, y metricas de
concordancia (Pearson, Spearman, RMSE, MAE), como en la validacion cuantitativa de la Sec. 4.1.1 de la tesis.
Lee resultados/histogramas_tipo_sidelnik_<medio>.csv (histograma_tipo_sidelnik.py).
Escribe resultados/razon_histogramas.csv y .json y figuras/fig22_razon_histogramas."""
import os, sys, json
import numpy as np, pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
ETQ = {"nacl25": "Agua + 2.5 % NaCl", "nacl5": "Agua + 5 % NaCl", "nacl10": "Agua + 10 % NaCl"}
COL = {"nacl25": "#1baf7a", "nacl5": "#7b1fa2", "nacl10": "#eda100"}
ANCHO = 50                  # fotones por bin para la razon (reduce las fluctuaciones de Poisson)
LIM = (50, 1000)            # intervalo comparado: sin el primer bin (artefacto de la digitalizacion) y dentro del eje
h = {m: pd.read_csv(os.path.join(RES, f"histogramas_tipo_sidelnik_{m}.csv")) for m in ["pura", "nacl25", "nacl5", "nacl10"]
     if os.path.exists(os.path.join(RES, f"histogramas_tipo_sidelnik_{m}.csv"))}


def rebin(y):
    """suma de 10 en 10 fotones -> bines de ANCHO fotones"""
    k = ANCHO // 10
    n = len(y) // k * k
    return np.asarray(y[:n]).reshape(-1, k).sum(1)


bc = rebin(h["pura"].bin_inf.to_numpy()) / (ANCHO // 10) + 5      # media de los limites inferiores + medio bin de 10
sel = (bc > LIM[0]) & (bc < LIM[1])
Mp, Sp = rebin(h["pura"].fotones_aceptados_QE.to_numpy()), rebin(h["pura"].Sidelnik_digitalizado.to_numpy())
filas, res, tab = [], {}, {"N_fotones": bc[sel]}
for m in [x for x in ETQ if x in h]:
    Mm, Sm = rebin(h[m].fotones_aceptados_QE.to_numpy()), rebin(h[m].Sidelnik_digitalizado.to_numpy())
    rM, rS = Mm / np.maximum(Mp, 1), Sm / np.maximum(Sp, 1e-9)
    eM = rM * np.sqrt(1 / np.maximum(Mm, 1) + 1 / np.maximum(Mp, 1))
    a, b = rM[sel], rS[sel]
    r, pr = stats.pearsonr(a, b)
    rho, prho = stats.spearmanr(a, b)
    res[m] = dict(pearson=float(r), p_pearson=float(pr), spearman=float(rho), p_spearman=float(prho),
                  RMSE=float(np.sqrt(np.mean((a - b) ** 2))), MAE=float(np.mean(np.abs(a - b))),
                  max_MEIGA=float(a.max()), N_max_MEIGA=float(bc[sel][np.argmax(a)]), max_Sidelnik=float(b.max()),
                  N_max_Sidelnik=float(bc[sel][np.argmax(b)]), media_MEIGA_100_500=float(a[(bc[sel] > 100) & (bc[sel] < 500)].mean()),
                  media_Sidelnik_100_500=float(b[(bc[sel] > 100) & (bc[sel] < 500)].mean()), bines=int(sel.sum()))
    tab[f"MEIGA_{m}"], tab[f"err_MEIGA_{m}"], tab[f"Sidelnik_{m}"] = a, eM[sel], b
pd.DataFrame(tab).to_csv(os.path.join(RES, "razon_histogramas.csv"), index=False, float_format="%.5g")
json.dump(dict(ancho_bin=ANCHO, intervalo=LIM, medios=res), open(os.path.join(RES, "razon_histogramas.json"), "w"), indent=1)

estilo.aplicar()
fig, ax = plt.subplots(figsize=(estilo.ANCHO, 4.2))
for m in res:
    ax.errorbar(tab["N_fotones"], tab[f"MEIGA_{m}"], tab[f"err_MEIGA_{m}"], fmt="o-", ms=3.5, lw=1.4, capsize=0, color=COL[m], label=f"MEIGA: {ETQ[m]}")
    ax.plot(tab["N_fotones"], tab[f"Sidelnik_{m}"], "--", lw=1.4, color=COL[m], label=f"Sidelnik (Fig. 6): {ETQ[m]}")
ax.axhline(1, color="k", lw=0.8)
ax.set_xlabel("Fotones Cherenkov aceptados por la eficiencia cuántica")
ax.set_ylabel("Razón NaCl / agua pura")
ax.set_xlim(0, LIM[1])
ax.set_ylim(0.5, 1.33 * max(max(tab[f"MEIGA_{m}"].max(), tab[f"Sidelnik_{m}"].max()) for m in res))
ax.legend(fontsize=8.5, ncol=2, loc="upper right")
fig.tight_layout()
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig22_razon_histogramas.{e}"))
print(json.dumps(res, indent=1))
