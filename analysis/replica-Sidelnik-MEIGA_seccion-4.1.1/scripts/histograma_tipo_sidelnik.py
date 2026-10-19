#!/usr/bin/env python3
"""Histogramas al estilo de la Fig. 6 de Sidelnik et al. (2020).

(a) 'Fotones aceptados por la eficiencia cuantica': por neutron, fotones Cherenkov que pasan la QE del
    R5912 al crearse (en el modo eFast de MEIGA son exactamente los fotones que se transportan),
    SIN transporte optico. Es lo que grafica Sidelnik.
(b) Carga en el PMT (fotoelectrones) despues del transporte optico: el aporte de este trabajo.
Solo eventos con >= 1 foton / p.e. (la Fig. 6 no muestra el pico en cero). Ambos se comparan con la curva de agua pura de la Fig. 6 digitalizada.
Uso: histograma_tipo_sidelnik.py [medio ...]   (por defecto los medios con <medio>_fotones.npz)
"""
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
MED = [m for m in (sys.argv[1:] or ["pura", "nacl25", "nacl5", "nacl10"]) if (os.path.exists(os.path.join(RES, f"{m}_aceptados_por_run.npy")) or os.path.exists(os.path.join(RES, f"{m}_fotones.npz")))]
def aceptados_por_run(m):
    """Fotones aceptados por la QE (= transportados en eFast) por neutron. Usa resultados/<m>_aceptados_por_run.npy
    (pequeno, va en el repositorio); si no existe lo calcula una vez desde <m>_fotones.npz (destino_fotones.py)."""
    f = os.path.join(RES, f"{m}_aceptados_por_run.npy")
    if not os.path.exists(f):
        N = len(np.load(os.path.join(RES, f"{m}.npz"))["Q"])
        np.save(f, np.bincount(np.load(os.path.join(RES, f"{m}_fotones.npz"))["run"], minlength=N).astype(np.int32))
    return np.load(f)


ETQ = {"pura": "Agua pura", "nacl25": "Agua + 2,5 % NaCl", "nacl5": "Agua + 5 % NaCl", "nacl10": "Agua + 10 % NaCl"}
COL = {"pura": "#e34948", "nacl25": "#1baf7a", "nacl5": "#7b1fa2", "nacl10": "#eda100"}
COLREF = {"pura": "Pure_H2O_counts_digitized", "nacl25": "NaCl_2p5_counts_digitized",
          "nacl5": "NaCl_5_counts_digitized", "nacl10": "NaCl_10_counts_digitized"}
REF6 = os.path.join(R, "datos", "fig6_sidelnik_digitalizada_700pts.csv")   # Fig. 6 de Sidelnik digitalizada (700 puntos)
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.color": "#e4e3df", "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "savefig.dpi": 160})
ref = pd.read_csv(REF6)
xb = np.arange(0, 1010, 10); xc = xb[:-1] + 5
res = {}; tablas = {}
estilo.aplicar()
fig, axs = plt.subplots(2, 2, figsize=(8, 10.4))
for m in MED:
    p = np.load(os.path.join(RES, f"{m}.npz")); N = len(p["Q"])
    acept = aceptados_por_run(m)                     # fotones aceptados por la QE (antes del transporte)
    q = p["Q"]                                       # fotoelectrones en el PMT (tras el transporte)
    ha = np.histogram(acept[acept >= 1], xb)[0]; hq = np.histogram(q[q >= 1], xb)[0]   # como la Fig. 6: sin eventos vacios
    yr = np.interp(xc, ref.Numero_de_fotones, ref[COLREF[m]])
    def forma(h):
        return h / h.sum()
    # correlacion de la forma en escala log, intervalo 0-1000
    corr = lambda a, b: float(np.corrcoef(np.log(forma(a) + 1e-9), np.log(forma(b) + 1e-9))[0, 1])
    res[m] = {"N": N,
              "aceptados_QE": {"media": float(acept.mean()), "mediana": float(np.median(acept)), "frac_0": float((acept == 0).mean()),
                               "frac_100_600": float(((acept >= 100) & (acept < 600)).mean()), "frac_ge600": float((acept >= 600).mean()),
                               "corr_forma_Sidelnik_0_1000": corr(ha, yr)},
              "carga_pe": {"media": float(q.mean()), "mediana": float(np.median(q)), "frac_0": float((q == 0).mean()),
                           "frac_ge1": float((q >= 1).mean()), "frac_ge100": float((q >= 100).mean()),
                           "corr_forma_Sidelnik_0_1000": corr(hq, yr)},
              "Sidelnik_media_0_1000": float(np.average(xc, weights=yr)),
              "MEIGA_aceptados_media_0_1000": float(np.average(xc, weights=ha)), "MEIGA_carga_media_0_1000": float(np.average(xc, weights=hq))}
    tablas[m] = pd.DataFrame({"bin_inf": xb[:-1], "bin_sup": xb[1:], "fotones_aceptados_QE": ha, "fotoelectrones_PMT": hq,
                              "Sidelnik_digitalizado": yr})
    tablas[m].to_csv(os.path.join(RES, f"histogramas_tipo_sidelnik_{m}.csv"), index=False)
    # (a) cuentas absolutas, como la Fig. 6; (b) normalizado; (c) carga en el PMT; (d) efecto del transporte optico
    axs[0, 0].step(xc, ha, where="mid", color=COL[m], lw=1.6)
    axs[0, 0].plot(xc, yr * ha.sum() / yr.sum(), "--", color="#0b0b0b", lw=1.1)
    axs[0, 1].step(xc, forma(ha), where="mid", color=COL[m], lw=1.6)
    axs[0, 1].plot(xc, forma(yr), "--", color="#0b0b0b", lw=1.1)
    axs[1, 0].step(xc, hq, where="mid", color=COL[m], lw=1.6)
    axs[1, 1].step(xc, forma(ha), where="mid", color=COL[m], lw=1.3, alpha=0.45)
    axs[1, 1].step(xc, forma(hq), where="mid", color=COL[m], lw=1.8)
    axs[1, 1].plot(xc, forma(yr), "--", color="#0b0b0b", lw=1.1)
axs[0, 0].set_title("(a) Fotones aceptados por la QE\n(como la Fig. 6 de Sidelnik)", fontsize=10.5)
axs[0, 0].set_xlabel("Fotones aceptados por la QE"); axs[0, 0].set_ylabel("Cuentas / 10 fotones")
axs[0, 1].set_title("(b) Igual, normalizado\n(escala logarítmica)", fontsize=10.5); axs[0, 1].set_yscale("log")
axs[0, 1].set_xlabel("Fotones aceptados por la QE"); axs[0, 1].set_ylabel("Fracción / 10 fotones")
axs[1, 0].set_title("(c) Aporte: carga en el PMT\n(con transporte óptico)", fontsize=10.5)
axs[1, 0].set_xlabel("Fotoelectrones en el PMT"); axs[1, 0].set_ylabel("Cuentas / 10 p.e."); axs[1, 0].set_yscale("log")
axs[1, 1].set_title("(d) Efecto del transporte óptico", fontsize=10.5); axs[1, 1].set_yscale("log")
axs[1, 1].set_xlabel("Fotones o fotoelectrones"); axs[1, 1].set_ylabel("Fracción / 10")
for a in axs.flat:
    a.set_xlim(0, 1000)
from matplotlib.lines import Line2D
h_ = [Line2D([], [], color=COL[m], lw=1.8, label=f"MEIGA, {ETQ[m]}" + ("" if res[m]["N"] == 150000 else f" ({res[m]['N']} n)")) for m in MED]
h_ += [Line2D([], [], color="#0b0b0b", ls="--", lw=1.1, label="Sidelnik, Fig. 6 (en (a), área igualada)"),
       Line2D([], [], color="#8a8984", lw=1.3, alpha=0.45, label="(d) trazo claro: aceptados por la QE; oscuro: p.e. en el PMT")]
fig.legend(handles=h_, loc="lower center", ncol=2, fontsize=9)
fig.tight_layout(rect=(0, 0.115, 1, 1))
fig.savefig(os.path.join(FIG, "fig09_histograma_tipo_sidelnik.png")); fig.savefig(os.path.join(FIG, "fig09_histograma_tipo_sidelnik.pdf"))
json.dump(res, open(os.path.join(RES, "histograma_tipo_sidelnik.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
