#!/usr/bin/env python3
"""Figura y tabla de la reconstruccion de vertices elasticos (resultados de elasticas_vertices.py):
(a) blanco reconstruido segun la energia del neutron; (b) masa del blanco reconstruida solo con el neutron;
(c) fraccion de energia perdida por colision (H y O) frente al limite cinematico; (d) angulo de dispersion en el laboratorio;
(e) decremento logaritmico medio xi segun la energia frente a la teoria; (f) balance de energia e impulso por vertice.
Escribe figuras/fig21_elasticas.{png,pdf} y resultados/elasticas_resumen.json"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo
from matplotlib.lines import Line2D
K_ = "#0b0b0b"
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
MED = [m for m in ["pura", "nacl25", "nacl5", "nacl10"] if os.path.exists(os.path.join(RES, f"elasticas_{m}.npz"))]
ETQ = {"pura": "Agua pura", "nacl25": "Agua + 2,5 % NaCl", "nacl5": "Agua + 5 % NaCl", "nacl10": "Agua + 10 % NaCl"}
COL = {"pura": "#e41a1c", "nacl25": "#1a8a1a", "nacl5": "#7b1fa2", "nacl10": "#f5a623"}
def figura():
    Z = {m: np.load(os.path.join(RES, f"elasticas_{m}.npz")) for m in MED}
    AO = 15.86                                   # masa del 16O en unidades de masa del neutron
    aO = ((AO - 1) / (AO + 1)) ** 2; XI_O = 1 + aO * np.log(aO) / (1 - aO); PERD_O = 1 - aO
    estilo.aplicar()
    fig, axs = plt.subplots(3, 2, figsize=(8.6, 10.0))
    eb = np.logspace(-6, np.log10(600), 33); ec = np.sqrt(eb[1:] * eb[:-1]); resumen = {}
    a = axs[0, 0]
    for m in MED:
        E, b = Z[m]["Ein"], Z[m]["blanco_cin"]; ok = np.isin(b, ["H", "O", "Na", "Cl"])
        n = np.histogram(E[ok], eb)[0].astype(float)
        for bl, ls in [("H", "-"), ("O", "--"), ("Na+Cl", ":")]:
            sel = ok & (np.isin(b, ["Na", "Cl"]) if bl == "Na+Cl" else (b == bl))
            if m == "pura" and bl == "Na+Cl":
                continue
            f_ = np.histogram(E[sel], eb)[0] / np.maximum(n, 1); f_[n < 200] = np.nan
            a.plot(ec, 100 * f_, ls, color=COL[m], lw=1.5, label=f"{ETQ[m]}: {bl}")
    a.set_xscale("log"); a.set_xlabel("Energía del neutrón [MeV]"); a.set_ylabel("% de las colisiones elásticas")
    a.set_title("(a) Con quién: blanco según la energía\n(reconstruido por cinemática, E > 1 eV)", fontsize=10.5); a.set_ylim(0, 135)
    a.legend(handles=[Line2D([], [], color=K_, ls=l_, label=t_) for l_, t_ in [("-", "H"), ("--", "O"), (":", "Na + Cl")]], ncol=3, loc="upper center", handlelength=1.8, columnspacing=1.0)
    a = axs[0, 1]; mb = np.logspace(2.5, 4.7, 300)
    for m in MED:
        Mk = Z[m]["M_rec_cin"]; Mk = Mk[np.isfinite(Mk) & (Z[m]["Ein"] > 1e-3)]
        a.hist(Mk, mb, histtype="step", color=COL[m], lw=1.3, label=ETQ[m])
    for M_, t, yy in [(938.27, "p", 0.92), (14895.1, "$^{16}$O", 0.92), (21409, "$^{23}$Na", 0.82), (32573, "$^{35}$Cl", 0.92)]:
        a.axvline(M_, color="#555555", ls=":", lw=0.9); a.text(M_ * 1.03, yy, t, transform=a.get_xaxis_transform(), fontsize=9)
    a.set_xscale("log"); a.set_yscale("log"); a.set_xlabel("Masa del blanco reconstruida [MeV]"); a.set_ylabel("Colisiones")
    a.set_title("(b) Masa del blanco deducida\ndel neutrón (E > 1 keV)", fontsize=10.5)
    a = axs[1, 0]; fb = np.linspace(0, 1, 101); z = Z["pura"]; sel = (z["Ein"] > 1e-3) & (z["Ein"] < 1)
    for bl, col, et in [("H", "#2a78d6", "H"), ("O", "#d62728", "$^{16}$O")]:
        s = sel & (z["blanco_cin"] == bl); fr = (z["Ein"][s] - z["Eout"][s]) / z["Ein"][s]
        a.hist(fr, fb, histtype="step", color=col, lw=1.5, density=True, label=f"blanco {et}")
    a.plot([0, 1], [1, 1], ":", color="#2a78d6", lw=1, label="teoría H")
    a.plot([0, PERD_O, PERD_O], [1 / PERD_O, 1 / PERD_O, 0], ":", color="#d62728", lw=1, label="teoría $^{16}$O")
    a.set_yscale("log"); a.set_ylim(0.05, 3000); a.set_xlabel("Fracción de energía perdida ΔE/E"); a.set_ylabel("Densidad")
    a.set_title("(c) Energía: pérdida por colisión\n(agua pura, 1 keV–1 MeV)", fontsize=10.5); a.legend(fontsize=8, ncol=2, loc="upper right", columnspacing=0.6, handlelength=1.2)
    a = axs[1, 1]; cb = np.linspace(-1, 1, 81)
    for (lo, hi, ls, et) in [(1e-3, 1, "-", "1 keV–1 MeV"), (20, 600, "--", "> 20 MeV")]:
        s0 = (z["Ein"] > lo) & (z["Ein"] < hi)
        for bl, col in [("H", "#2a78d6"), ("O", "#d62728")]:
            s = s0 & (z["blanco_cin"] == bl)
            a.hist(z["cos_lab"][s], cb, histtype="step", color=col, ls=ls, lw=1.3, density=True, label=f"{bl}, {et}".replace("1 keV–1 MeV", "< 1 MeV"))
    a.set_yscale("log"); a.set_ylim(top=a.get_ylim()[1] * 300); a.set_xlabel("cos θ del neutrón en el laboratorio"); a.set_ylabel("Densidad")
    a.set_title("(d) Ángulo de dispersión\n(agua pura)", fontsize=10.5); a.legend(fontsize=8, ncol=2, loc="upper right", columnspacing=0.6, handlelength=1.2)
    a = axs[2, 0]
    for m in MED:
        E, b, xi = Z[m]["Ein"], Z[m]["blanco_cin"], Z[m]["xi"]
        for bl, mk in [("H", "o"), ("O", "s")]:
            s = b == bl; idx = np.digitize(E[s], eb) - 1
            v = np.array([xi[s][idx == i].mean() if (idx == i).sum() > 300 else np.nan for i in range(len(ec))])
            a.plot(ec, v, mk, color=COL[m], ms=4, mfc="none" if m != "pura" else COL[m], label=f"{ETQ[m]}: {bl}")
    a.axhline(1, color="#2a78d6", ls=":", lw=1); a.axhline(XI_O, color="#d62728", ls=":", lw=1)
    a.text(30, 0.62, "ξ$_H$ = 1", fontsize=9, color="#2a78d6"); a.text(1e-3, XI_O * 0.72, f"ξ$_O$ = {XI_O:.3f}".replace(".", ","), fontsize=9, color="#d62728")
    a.set_xscale("log"); a.set_yscale("log"); a.set_ylim(5e-3, 3); a.set_xlabel("Energía del neutrón [MeV]"); a.set_ylabel("ξ = ⟨ln(E/E')⟩")
    a.set_title("(e) Decremento logarítmico medio\n(punteado: teoría, dispersión isótropa en el CM)", fontsize=10.5); a.legend(handles=[Line2D([], [], color=K_, marker=m_, ls="", label=t_) for m_, t_ in [("o", "H"), ("s", "O")]], ncol=2, loc="lower left")
    a = axs[2, 1]
    for m in MED:
        rec = Z[m]["rec"]; s = rec != "sin retroceso"
        dE = np.abs(Z[m]["dE_cons"][s]) / Z[m]["Ein"][s]; dp = Z[m]["dp_rel"][s]
        a.hist(np.log10(np.maximum(dE, 1e-12)), np.linspace(-12, 0, 61), histtype="step", color=COL[m], lw=1.3, label=f"{ETQ[m]}: |ΔE|/E")
        a.hist(np.log10(np.maximum(dp[np.isfinite(dp)], 1e-12)), np.linspace(-12, 0, 61), histtype="step", color=COL[m], ls="--", lw=1.3, label=f"{ETQ[m]}: |Δp|/p")
    a.set_yscale("log"); a.set_xlabel("log$_{10}$ del desbalance relativo"); a.set_ylabel("Vértices con retroceso")
    a.set_title("(f) Conservación de energía e impulso\nen cada vértice", fontsize=10.5); a.set_ylim(top=a.get_ylim()[1] * 30)
    a.legend(handles=[Line2D([], [], color=K_, ls="-", label="|ΔE|/E"), Line2D([], [], color=K_, ls="--", label="|Δp|/p")], ncol=2, loc="upper left")
    estilo.leyenda_medios(fig, MED, COL, ETQ, ncol=2)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"fig21_elasticas.{e}"))
    resumen = {"xi_O_teoria": XI_O, "perdida_max_O_teoria": PERD_O}
    json.dump(resumen, open(os.path.join(RES, "elasticas_resumen.json"), "w"), indent=1)
    print(resumen)


if MED:
    figura()
else:      # los elasticas_<medio>.npz (~400 MB) no van al repositorio: se conserva la figura y elasticas_resumen.json
    print("Faltan resultados/elasticas_<medio>.npz (se regeneran con elasticas_vertices.py); se usa la figura guardada.")

