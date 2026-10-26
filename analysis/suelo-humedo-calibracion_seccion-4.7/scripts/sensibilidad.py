#!/usr/bin/env python3
"""
Sensibilidad del WCD a la humedad, S_j(θ_v) = -(1/R_j) dR_j/dθ_v (Ec. 4.130 de la tesis), y resolución estadística
σ_θv = sqrt(N)/|dN/dθ_v|, a partir de las curvas de calibración R_j = N/N0 del plegado (cuatro medios) y de la
simulación directa (agua pura y 10 % NaCl), con Q >= 1 p.e. y con la ventana 1 <= Q < 20 p.e.
La derivada sale del ajuste de la forma de Desilets en θ_v, R = a1 + a0/(θ_v + a2), a los seis suelos; θ_v = w ρ con
ρ = (w/1 + (1-w)/2.7)^-1. N = R N0 t con N0 en cuentas por hora (normalización de 12 h, ver normalizacion.py).
Solo neutrones: el fondo de muones y de la componente electromagnética, que no depende de la humedad, bajaría S_j.
-> resultados/sensibilidad.json, informe/tablas/sensibilidad.tex, figuras/fig25_sensibilidad
"""
import json, os
import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG, TAB = (os.path.join(BASE, d) for d in ("resultados", "figuras", os.path.join("informe", "tablas")))
W = np.array([0, 0.05, 0.10, 0.15, 0.25, 0.30]); TV = W / (W / 1.0 + (1 - W) / 2.7)
COL = {"Agua pura": "red", "2.5 % NaCl": "green", "5 % NaCl": "purple", "10 % NaCl": "darkorange"}
f = lambda t, a0, a1, a2: a1 + a0 / (t + a2)
F = json.load(open(os.path.join(RES, "curva_calibracion_wcd.json")))["resultados"]["completo"]
D = json.load(open(os.path.join(RES, "curva_calibracion_tanque.json")))["medios"]

out = {"theta_v": TV.tolist(), "casos": []}
for met, src in (("plegado", F), ("directa", D)):
    for u, un in (("eps", "Q\u22651"), ("ventana", "ventana")):
        for mn in COL:
            if mn not in src: continue
            R = np.array(src[mn][u]["cociente"]); N0 = src[mn][u]["N0_h"]
            p, _ = curve_fit(f, TV, R, p0=(0.02, 0.85, 0.2), maxfev=50000)
            Rf = f(TV, *p); dR = -p[0] / (TV + p[2]) ** 2; S = -dR / Rf
            sig = {t: (np.sqrt(R * N0 * t) / (np.abs(dR) * N0 * t)).tolist() for t in (1, 24)}
            out["casos"].append({"metodo": met, "umbral": u, "medio": mn, "a": p.tolist(), "residuo": float(np.max(np.abs(Rf - R))),
                                 "S": S.tolist(), "S_media": float(-np.log(R[-1]) / TV[-1]), "sigma_1h": sig[1], "sigma_24h": sig[24], "N0_h": N0})
json.dump(out, open(os.path.join(RES, "sensibilidad.json"), "w"), indent=1, ensure_ascii=False)

with open(os.path.join(TAB, "sensibilidad.tex"), "w") as fo:
    fo.write("\\begin{tabular}{lll rrr rr rr}\n\\toprule\n & & & \\multicolumn{3}{c}{$S_j$} & \\multicolumn{2}{c}{$\\sigma_{\\theta_v}$, 1~h} & "
             "\\multicolumn{2}{c}{$\\sigma_{\\theta_v}$, 24~h} \\\\\n\\cmidrule(lr){4-6}\\cmidrule(lr){7-8}\\cmidrule(lr){9-10}\n"
             "Método & Señal & Medio & seco & 30~\\% & media & seco & 30~\\% & seco & 30~\\% \\\\\n\\midrule\n")
    prev = None
    for c in out["casos"]:
        g = (c["metodo"], c["umbral"])
        if prev and g != prev: fo.write("\\midrule\n")
        fo.write(f"{c['metodo'] if g != prev else ''} & {('$Q\\geq1$' if c['umbral'] == 'eps' else '$1\\leq Q<20$') if g != prev else ''} & "
                 f"{c['medio'].replace('%', chr(92) + '%')} & {c['S'][0]:.3f} & {c['S'][-1]:.3f} & {c['S_media']:.3f} & "
                 f"{c['sigma_1h'][0]:.4f} & {c['sigma_1h'][-1]:.4f} & {c['sigma_24h'][0]:.4f} & {c['sigma_24h'][-1]:.4f} \\\\\n")
        prev = g
    fo.write("\\bottomrule\n\\end{tabular}\n")

fig, ax = plt.subplots(1, 2, figsize=(14, 5.4))
tt = np.linspace(0, TV[-1], 200)
for c in out["casos"]:
    col = COL[c["medio"]]; a0, a1, a2 = c["a"]
    S = (a0 / (tt + a2) ** 2) / f(tt, a0, a1, a2); s1 = np.interp(tt, TV, c["sigma_1h"])
    ls = "-" if c["umbral"] == "eps" else "--"
    if c["metodo"] == "plegado":
        lab = f"{c['medio']}, {'Q ≥ 1' if c['umbral'] == 'eps' else 'ventana'}"
        ax[0].plot(tt, S, ls, color=col, lw=1.8, label=lab); ax[1].plot(TV, c["sigma_1h"], ls, color=col, lw=1.6, marker="o", ms=4, label=lab)
    else:
        mk = "s" if c["umbral"] == "eps" else "^"
        lab = f"{c['medio']}, directa, {'Q ≥ 1' if c['umbral'] == 'eps' else 'ventana'}"
        ax[0].plot(TV, c["S"], mk, color=col, mec="k", mew=0.6, ms=7, label=lab)
        ax[1].plot(TV, c["sigma_1h"], mk, color=col, mec="k", mew=0.6, ms=7, label=lab)
ax[0].set_xlabel(r"Contenido volumétrico de agua $\theta_v$ [m$^3$ m$^{-3}$]"); ax[0].set_ylabel(r"$S_j(\theta_v) = -\dfrac{1}{R_j}\dfrac{dR_j}{d\theta_v}$")
ax[0].set_title("Sensibilidad (líneas: plegado; símbolos: simulación directa)", fontsize=10)
ax[1].set_xlabel(r"Contenido volumétrico de agua $\theta_v$ [m$^3$ m$^{-3}$]"); ax[1].set_ylabel(r"$\sigma_{\theta_v}$ en 1 h (solo estadística)")
ax[1].set_title("Resolución en humedad, 1 h de medida (24 h: ÷ 4.9)", fontsize=10)
for a in ax: a.grid(alpha=0.3, ls="--")
ax[0].legend(fontsize=7, ncol=2, loc="upper right"); ax[1].legend(fontsize=7, ncol=2, loc="upper left")
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig25_sensibilidad.{e}"), dpi=170)
plt.close(fig)
for c in out["casos"]: print(f"{c['metodo']:8s} {c['umbral']:8s} {c['medio']:11s} S {c['S'][0]:.3f}->{c['S'][-1]:.3f} media {c['S_media']:.3f}  σ1h {c['sigma_1h'][0]:.4f}/{c['sigma_1h'][-1]:.4f}")
