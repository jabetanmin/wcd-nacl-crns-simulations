#!/usr/bin/env python3
"""Espectros gamma de la captura de neutrones en cada nucleo (formato de la Fig. 4.1 de la tesis):
(a) 16O(n,g)17O y (b) 1H(n,g)2H con ajuste gaussiano de la linea de 2,224 MeV en agua pura;
(c) 35Cl(n,g)36Cl y (d) 37Cl(n,g)38Cl en agua + 2,5 % NaCl. Gammas emitidos en la captura
(secundarias-captura-neutron, enlazadas con el nucleo de capturas-neutrones), solo capturas en el medio.
Escribe figuras/fig15_espectros_captura_nucleo.{png,pdf} y resultados/lineas_captura_nucleo.csv"""
import os
import numpy as np, pandas as pd
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
def gammas(m, Z, A):
    z = np.load(os.path.join(RES, f"{m}.npz"))
    cap = pd.DataFrame({"run": z["cap_run_id"], "trk": z["cap_track_id"], "Z": z["cap_target_Z"], "A": z["cap_target_A"], "mat": z["cap_material"]})
    cap = cap[(cap.Z == Z) & (cap.A == A) & cap.mat.str.startswith(("Water", "SaltyWater"))]
    sc = pd.DataFrame({"run": z["sc_run"], "trk": z["sc_ptrk"], "p": z["sc_part"], "E": z["sc_E"]})
    g = sc[sc.p == "gamma"].merge(cap[["run", "trk"]], on=["run", "trk"])
    return g.E.to_numpy() * 1e3, len(cap)          # keV
filas = []
def lineas(E, n, panel, nombre, top):
    """lineas = bines de 1 keV con cuentas; intensidad por 100 capturas y relativa a la mas intensa"""
    b = np.arange(0.5, E.max() + 2, 1.0); h, _ = np.histogram(E, b)   # bordes en x,5 keV: las lineas (x,0-x,9) no se parten
    idx = np.flatnonzero(h); Ec = np.array([E[(E >= b[i]) & (E < b[i + 1])].mean() for i in idx]); hc = h[idx]
    rel = 100 * hc / hc.max()
    for i in np.argsort(-hc)[:12]:
        filas.append({"reaccion": nombre, "E_keV": round(Ec[i], 1), "por_100_capturas": round(100 * hc[i] / n, 2), "relativa": round(rel[i], 1), "capturas": n})
    return Ec, rel, [i for i in np.argsort(-hc)[:top]]
# Referencias (mismas que en los esquemas de niveles y en la Tabla 4.2 unificada del informe), intensidad por 100 capturas:
# 16O: Firestone y Revay, PRC 93, 044311 (2016) (Fig. 4.2 de la tesis); 35Cl: ENSDF (Nica et al. 2012), Ig[b]*100/33,22;
# 37Cl: energias de la Tabla 4.2 (sin intensidades).
REF = {"16O": [(870.76, 96.6), (1087.89, 80.4), (2184.49, 80.4), (3272.02, 16.2), (4142.60, 3.36)],
       "35Cl": [(e, 100 * ib / 33.22) for e, ib in [(517.07, 7.58), (786.30, 3.419), (788.42, 5.42), (1164.86, 8.91), (1170.94, 1.82),
                                                    (1951.13, 6.33), (1959.34, 4.10), (2863.81, 1.818), (5715.36, 1.818), (6110.98, 6.59),
                                                    (6619.73, 2.530), (6627.94, 1.466), (7414.09, 3.29), (7790.45, 2.66), (8578.70, 0.883)]],
       "37Cl": [(637.69, None), (755.43, None), (788.42, None), (1692.11, None), (2166.90, None), (4134.13, None)]}
ETIQ = {"16O": [870.76, 1087.89, 2184.49, 3272.02, 4142.60], "35Cl": [517.07, 788.42, 1164.86, 1951.13, 1959.34, 6110.98, 8578.70],
        "37Cl": [637.69, 755.43, 788.42, 1692.11, 2166.90, 4134.13]}         # lineas de la Tabla 4.2 (energias unificadas)
plt.rcParams.update({"font.size": 12, "axes.spines.top": True, "axes.spines.right": True, "savefig.dpi": 200,
                     "axes.labelsize": 12.5, "xtick.labelsize": 11.5, "ytick.labelsize": 11.5})
fig, axs = plt.subplots(2, 2, figsize=(8.6, 9.8))   # ancho real de la pagina: las letras se imprimen casi a su tamano
MAG = "#c51b8a"
SN = {"16O": 4143.08, "35Cl": 8579.79, "37Cl": 6107.8}   # energia de separacion del nucleo compuesto [keV]


def stick(a, E, n, col, nombre, caja, iso, xmax, panel):
    Ec, rel, _ = lineas(E, n, panel, nombre, 0)
    I = rel * 0 + np.array([((E > e - 0.5) & (E < e + 0.5)).sum() for e in Ec]) * 100 / n   # por 100 capturas
    refs = REF[iso]; Emax_ref = max(e for e, _ in refs)
    # gamma unico de S_n (solo Geant4): linea por encima de todas las de referencia con > 2 por 100 capturas
    sn = [k for k in np.flatnonzero(np.abs(Ec - SN[iso]) < 0.6) if I[k] > 2]
    normal = np.ones(len(Ec), bool); normal[sn] = False
    a.vlines(Ec[normal], 0, I[normal], color=col, lw=1.1, label="MEIGA")
    a.vlines(Ec[sn], 0, I[sn], color=MAG, lw=1.8, label="MEIGA: γ único de $S_n$")
    con_I = [(e, r) for e, r in refs if r is not None]
    if con_I:
        a.plot([e for e, _ in con_I], [r for _, r in con_I], "D", mfc="none", mec="#0b0b0b", ms=6, mew=1.1, label="referencia")
    ymax = 1.3 * max(I.max(), max([r for _, r in con_I], default=0))
    for e, _ in refs:
        if all(r is None for _, r in refs):
            a.plot([e] * 2, [ymax * 0.0, ymax * 0.035], color="#0b0b0b", lw=2)
    if not con_I:
        a.plot([], [], color="#0b0b0b", lw=2, label="energía de referencia (Tabla 4.2)")
    etiquetas = [(e, None) for e in ETIQ[iso]] + [(Ec[k], "sn") for k in sn]
    for j_, (e, tipo) in enumerate(sorted(etiquetas)):
        k = np.argmin(np.abs(Ec - e)); hay = abs(Ec[k] - e) < 0.4 or tipo == "sn"
        x, y = (Ec[k] if hay else e), (I[k] if hay else 0)
        yt = ymax * (0.95 - 0.082 * j_); xt = x + 0.04 * xmax if x < 0.5 * xmax else x - 0.4 * xmax
        if tipo == "sn":
            txt, ec_ = f"{e:.1f}: γ único $S_n$".replace(".", ","), MAG
        else:
            txt, ec_ = (f"{e:.2f}".replace(".", ",") + ("" if hay else " (ausente)")), (col if hay else "#8a8984")
        a.annotate(txt, (x, y), (xt, yt), fontsize=9.5, color="#0b0b0b",
                   bbox=dict(boxstyle="square,pad=0.15", fc="white", ec=ec_, lw=0.9), arrowprops=dict(arrowstyle="-", color=ec_, lw=0.8))
    a.set_xlim(0, xmax); a.set_ylim(0, ymax); a.set_xlabel("Energía del fotón γ [keV]"); a.set_ylabel("Fotones por 100 capturas")
    a.text(0.98, 0.97, caja + f"\n$N_{{\\rm capt}}$ = {n}", transform=a.transAxes, ha="right", va="top", fontsize=9.5,
           bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#8a8984"))
    a.text(-0.16, 1.03, panel, transform=a.transAxes, fontweight="bold", fontsize=12.5)


E, n = gammas("pura", 8, 16); stick(axs[0, 0], E, n, "#e41a1c", "16O(n,g)17O", "Agua pura\n$^{16}$O(n,γ)$^{17}$O", "16O", 5000, "(a)")
# (b) 1H(n,g)2H: ajuste gaussiano
E, n = gammas("pura", 1, 1); x = E - 2224
b = np.arange(0.315, 0.4351, 0.01); h, _ = np.histogram(x, b); c = 0.5 * (b[1:] + b[:-1]); s = np.sqrt(np.maximum(h, 1))
f = lambda t, A, mu, sg: A * np.exp(-0.5 * ((t - mu) / sg) ** 2)
p, cv = curve_fit(f, c, h, p0=[h.max(), 0.373, 0.013], sigma=s, absolute_sigma=True)
chi2 = np.sum(((h - f(c, *p)) / s) ** 2) / (len(c) - 3)
a = axs[0, 1]; tt = np.linspace(0.31, 0.44, 400)
a.plot(tt, f(tt, *p), "-", color="#e41a1c", label="Ajuste gaussiano"); a.errorbar(c, h, s, fmt="s", color="#2a5aa6", ms=4, label="Simulación")
a.set_xlabel("Energía del fotón γ − 2224 [keV]"); a.set_ylabel("Fotones por intervalo"); a.legend(fontsize=11, loc="upper center", bbox_to_anchor=(0.5, 0.66), ncol=2, handlelength=1.3, columnspacing=1.0); a.set_ylim(-1500, 1.95 * h.max())
a.set_xticks([0.32, 0.36, 0.40, 0.44])
a.text(0.02, 0.97, f"Agua pura\n$^1$H(n,γ)$^2$H\n$N_{{\\rm capt}}$ = {n}", transform=a.transAxes, va="top", fontsize=9.5, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#8a8984"))
a.text(0.98, 0.97, f"μ = {2224 + p[1]:.5f} ± {np.sqrt(cv[1, 1]):.5f} keV\nσ = {abs(p[2]):.5f} ± {np.sqrt(cv[2, 2]):.5f} keV\n$\\chi^2_{{\\rm red}}$ = {chi2:.1f}",
       transform=a.transAxes, ha="right", va="top", fontsize=9, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#8a8984"))
a.text(0.98, 0.8, "Valor medido: 2223,25 keV\n(1,12 keV por debajo,\nfuera de la escala)", transform=a.transAxes, ha="right", va="top", fontsize=9.5, color="#555555")
a.text(-0.16, 1.03, "(b)", transform=a.transAxes, fontweight="bold", fontsize=12.5)
filas.append({"reaccion": "1H(n,g)2H", "E_keV": round(2224 + p[1], 5), "por_100_capturas": round(100 * len(E) / n, 2), "relativa": 100, "capturas": n})
E, n = gammas("nacl25", 17, 35); stick(axs[1, 0], E, n, "#1a8a1a", "35Cl(n,g)36Cl", "Agua + 2,5 % de NaCl\n$^{35}$Cl(n,γ)$^{36}$Cl", "35Cl", 9000, "(c)")
E, n = gammas("nacl25", 17, 37); stick(axs[1, 1], E, n, "#1a8a1a", "37Cl(n,g)38Cl", "Agua + 2,5 % de NaCl\n$^{37}$Cl(n,γ)$^{38}$Cl", "37Cl", 7000, "(d)")
from matplotlib.lines import Line2D
h_ = [Line2D([], [], color="#e41a1c", lw=1.5, label="MEIGA (agua pura)"), Line2D([], [], color="#1a8a1a", lw=1.5, label="MEIGA (agua + 2,5 % NaCl)"),
      Line2D([], [], color=MAG, lw=2, label="MEIGA: γ único de $S_n$ (no físico)"),
      Line2D([], [], ls="none", marker="D", mfc="none", mec="#0b0b0b", label="referencia (por 100 capturas)"),
      Line2D([], [], color="#0b0b0b", lw=2, label="energía de referencia ($^{37}$Cl)")]
fig.legend(handles=h_, loc="lower center", ncol=2, fontsize=11.5, frameon=False)
fig.tight_layout(rect=(0, 0.095, 1, 1))
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig15_espectros_captura_nucleo.{e}"))
t = pd.DataFrame(filas); t.to_csv(os.path.join(RES, "lineas_captura_nucleo.csv"), index=False)
print(f"H: mu = {2224 + p[1]:.5f} +- {np.sqrt(cv[1,1]):.5f}  sigma = {abs(p[2]):.5f}  chi2red = {chi2:.1f}")
print(t.groupby("reaccion").head(8).to_string(index=False))
