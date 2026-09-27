#!/usr/bin/env python3
"""Verificación de la Tabla 4.23 de la tesis (sección 4.6) y cantidades derivadas.

Único insumo: los valores N_inc(E_i) y eps_j(E_i) publicados en la Tabla 4.23
(idénticos a la salida de la celda 2 de Medicion-humedad.ipynb). No se leen
archivos de simulación.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

AQUI = Path(__file__).resolve().parent
RES = AQUI.parent / "resultados"
FIG = AQUI.parent / "informe" / "figuras"

E = np.array([10, 25, 80, 100, 300, 500, 700, 1000, 10000], float)       # meV
BORDES = np.array([8.3666, 15.8114, 44.7214, 89.4427, 173.2051, 387.2983,
                   591.6080, 836.6600, 3162.2777, 31622.7766])            # meV
NINC = np.array([12485, 55828, 42311, 22026, 15525, 7639, 6233, 24280, 21642])
EPS = {  # %
    "Agua pura": [11.829, 13.962, 15.942, 16.157, 17.149, 17.743, 17.704, 17.984, 17.871],
    "NaCl 2.5 %": [15.948, 18.457, 20.761, 21.349, 22.512, 22.817, 22.756, 22.927, 23.417],
    "NaCl 5 %": [18.638, 21.563, 24.103, 24.710, 25.922, 26.628, 26.377, 26.631, 26.396],
    "NaCl 10 %": [23.417, 26.474, 29.661, 30.107, 31.204, 31.610, 31.467, 31.753, 31.653],
}
NDET_TESIS = {"Agua pura": 32931, "NaCl 2.5 %": 43073, "NaCl 5 %": 49887, "NaCl 10 %": 60665}

tabla = pd.DataFrame({"E_meV": E, "borde_inf_meV": BORDES[:-1],
                      "borde_sup_meV": BORDES[1:], "N_inc": NINC})
res = []
agua = None
for m, e in EPS.items():
    e = np.array(e) / 100
    ndet = NINC * e
    tabla[f"eps_{m}"] = e
    tabla[f"Ndet_{m}"] = ndet
    tot = ndet.sum()
    sig = np.sqrt((e**2 * NINC).sum())            # sólo Poisson de N_inc
    agua = tot if agua is None else agua
    res.append({
        "medio": m, "Ndet_calc": tot, "Ndet_tesis": NDET_TESIS[m],
        "sigma_Poisson_Ninc": sig, "sigma_rel_%": 100 * sig / tot,
        "eps_efectiva_%": 100 * tot / NINC.sum(),
        "Delta_vs_agua_%": 100 * (tot - agua) / agua,
        "frac_Ndet_10-173meV_%": 100 * ndet[:4].sum() / tot,
        "eps(10eV)/eps(10meV)": e[-1] / e[0],
    })
tabla.to_csv(RES / "tabla_4_23_reconstruida.csv", index=False)
res = pd.DataFrame(res)
res.to_csv(RES / "resumen_respuesta_referencia_seca.csv", index=False)
print("N_inc total:", NINC.sum(), "| fracción N_inc <= 100 meV: %.1f %%" % (100 * NINC[:4].sum() / NINC.sum()))
print(res.round(3).to_string(index=False))

# ---- figura -----------------------------------------------------------------
col = {"Agua pura": "#c0392b", "NaCl 2.5 %": "#27ae60", "NaCl 5 %": "#8e44ad", "NaCl 10 %": "#e67e22"}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6))
for m, e in EPS.items():
    a1.plot(E, e, "o-", color=col[m], label=m)
a1.set_xscale("log"); a1.set_xlabel("Energía representativa del intervalo [meV]")
a1.set_ylabel(r"$\varepsilon_j(E_i)$ [%]"); a1.set_title("(a) Eficiencia usada en la Tabla 4.23")
a1.grid(alpha=.3, which="both"); a1.legend()
# intervalos efectivos: el espectro sólo cubre 10.0011–10000.2 meV
BEF = np.clip(BORDES, 10.0011, 10000.2)
w = np.diff(np.log10(BEF))
a2.bar(np.log10(BEF[:-1]), NINC, width=w, align="edge", color="#bbb", edgecolor="k", lw=.5,
       label=r"$N_\mathrm{inc}$")
for m in EPS:
    a2.step(np.log10(BEF), np.r_[tabla[f"Ndet_{m}"], tabla[f"Ndet_{m}"].iloc[-1]], where="post",
            color=col[m], label=rf"$N_\mathrm{{det}}$ {m}")
a2.set_xlabel(r"$\log_{10}(E/\mathrm{meV})$ (intervalos efectivos, 10 meV–10 eV)"); a2.set_ylabel("Neutrones / intervalo (12 h, 1 m²)")
a2.set_title("(b) Incidentes y detectados por intervalo"); a2.legend(fontsize=8, loc="upper right"); a2.grid(alpha=.3)
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(FIG / f"tabla_4_23_eficiencia_y_conteos.{ext}", dpi=160)
