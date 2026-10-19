#!/usr/bin/env python3
"""Esquema de niveles y transiciones gamma de la captura 16O(n,g)17O con neutrones termicos (Fig. 4.2 de la tesis).
Datos de referencia: Firestone y Revay, Phys. Rev. C 93, 044311 (2016), Sec. II.B.1, Fig. 1 y Tabla III; CapGam/NNDC,
16O(N,G):E=THERMAL. Ademas compara las intensidades (por 100 capturas) con las de MEIGA en las capturas en 16O de las
corridas disponibles (<medio>.npz). Escribe figuras/fig18_esquema_niveles_O17.{png,pdf} (replica) y
figuras/fig18b_esquema_niveles_O17_MEIGA.{png,pdf} (con MEIGA), y resultados/intensidades_O17.json"""
import os, json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
# niveles: energia [keV], espin-paridad, texto secundario
NIV = [(0.0, "5/2$^+$", "estable"), (870.78, "1/2$^+$", "180 ps"), (3055.37, "1/2$^-$", "0.08 ps"), (4143.27, "1/2$^+$", None)]
SN = 4143.27            # como en la Fig. 4.2 de la tesis
SN_G4 = 4143.09         # energia del gamma unico que emite Geant4 (= S_n de 17O, 4143,08 keV en AME2020)
# transiciones: E_gamma, nivel inicial, nivel final, multipolaridad, intensidad por 100 capturas, x, color, grosor
TR = [(4142.60, 4143.27, 0.0, "E2", 3.36, 0.12, "#555555", 1.2),
      (3272.02, 4143.27, 870.78, "M1", 16.2, 0.50, "#2a5aa6", 1.4),
      (1087.89, 4143.27, 3055.37, "E1", 80.4, 0.58, "#d62728", 3.2),
      (2184.49, 3055.37, 870.78, "E1", 80.4, 0.80, "#d62728", 3.2),
      (870.76, 870.78, 0.0, "E2", 96.6, 0.92, "#d62728", 3.2)]

# intensidades en MEIGA: gammas de las capturas en 16O en el medio, por 100 capturas
cap_n, cuentas = 0, {t[0]: 0 for t in TR}; suma = []; unico = 0
for m in ["pura", "nacl25", "nacl5", "nacl10"]:
    f = os.path.join(RES, f"{m}.npz")
    if not os.path.exists(f):
        continue
    z = np.load(f)
    cap = pd.DataFrame({"run": z["cap_run_id"], "trk": z["cap_track_id"], "Z": z["cap_target_Z"], "A": z["cap_target_A"], "mat": z["cap_material"]})
    cap = cap[(cap.Z == 8) & (cap.A == 16) & cap.mat.str.startswith(("Water", "SaltyWater"))]
    sc = pd.DataFrame({"run": z["sc_run"], "trk": z["sc_ptrk"], "p": z["sc_part"], "E": z["sc_E"] * 1e3})
    g = sc[sc.p == "gamma"].merge(cap[["run", "trk"]], on=["run", "trk"])
    cap_n += len(cap); suma += g.groupby(["run", "trk"]).E.sum().tolist()
    for t in TR:
        cuentas[t[0]] += int((np.abs(g.E - t[0]) < 0.3).sum())
    unico += int((np.abs(g.E - SN_G4) < 0.3).sum())
out = {"capturas_O16_MEIGA": cap_n, "suma_media_keV": float(np.mean(suma)) if suma else None,
       "frac_suma_igual_Sn": float(np.mean(np.abs(np.array(suma) - SN) < 5)) if suma else None,
       "gamma_unico_Sn_por_100": 100 * unico / cap_n if cap_n else None, "gamma_unico_Sn_error": 100 * np.sqrt(unico) / cap_n if cap_n else None,
       "transiciones": {}}
for t in TR:
    k = cuentas[t[0]]
    out["transiciones"][f"{t[0]:.2f}"] = {"referencia": t[4], "MEIGA": 100 * k / cap_n if cap_n else None,
                                          "MEIGA_error": 100 * np.sqrt(k) / cap_n if cap_n else None, "cuentas": k}
json.dump(out, open(os.path.join(RES, "intensidades_O17.json"), "w"), indent=1)


def dibujar(con_meiga, nombre):
    plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})
    estilo.aplicar()
    fig, ax = plt.subplots(figsize=(8, 9.6))
    x0, x1 = 0.03, 1.0
    for E, jp, txt in NIV:
        es_cap = abs(E - SN) < 1
        ax.hlines(E, x0, x1, color="#0b0b0b", lw=3.2 if E == 0 else 1.3, ls="--" if es_cap else "-")
        ax.text(x0 - 0.015, E, jp, ha="right", va="center", fontsize=12.5)
        ax.text(x1 + 0.015, E + 40, f"{E:.2f} keV" if E > 0 else "0", ha="left", va="bottom", fontsize=12.5)
        if txt:
            ax.text(x1 + 0.015, E - 40, txt, ha="left", va="top", fontsize=11.5, color="#555555")
    ax.text(x1 + 0.015, SN + 190, "estado de captura ($S_n$)", ha="left", va="bottom", fontsize=11.5, color="#555555")
    for Eg, Ei, Ef, mult, I, x, col, lw in TR:
        ax.annotate("", xy=(x, Ef + 8), xytext=(x, Ei - 8),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, mutation_scale=8 + 3 * lw, shrinkA=0, shrinkB=0))
        ym = Ei - 0.18 * (Ei - Ef) if Ei - Ef > 1500 else (Ei + Ef) / 2 + 120
        if Eg == 4142.60:
            ym = 3750
        if Eg == 3272.02:
            ym = 2250
        etiqueta = f"{Eg:.2f} keV\n{mult}, {I:g} %".replace(".", ",", 0)
        if con_meiga:
            tt = out["transiciones"][f"{Eg:.2f}"]
            etiqueta += (f"\nMEIGA: {tt['MEIGA']:.1f} ± {tt['MEIGA_error']:.1f} %" if tt["cuentas"] else "\nMEIGA: ausente")
        izq = Eg in (870.76, 3272.02)           # a la izquierda de su flecha, para no tapar el nivel fundamental
        ax.text(x - 0.015 if izq else x + 0.015, 830 if Eg == 870.76 else ym, etiqueta, color=col if col != "#555555" else "#0b0b0b", fontsize=11.5, va="top", ha="right" if izq else "left")
    if con_meiga:
        xu = 0.06
        ax.annotate("", xy=(xu, 8), xytext=(xu, SN - 8),
                    arrowprops=dict(arrowstyle="-|>", color="#c51b8a", lw=2.0, ls="--", mutation_scale=13, shrinkA=0, shrinkB=0))
        ax.text(xu + 0.012, 230, f"solo MEIGA: γ único de {SN_G4:.2f} keV (= $S_n$)\n{out['gamma_unico_Sn_por_100']:.1f} ± {out['gamma_unico_Sn_error']:.1f} %",
                ha="left", va="center", fontsize=11.5, color="#c51b8a", bbox=dict(fc="white", ec="none", alpha=0.9, pad=1))
    ax.set_xlim(-0.1, 1.27); ax.set_ylim(-250, 4700)
    ax.set_xticks([]); ax.set_ylabel("Energía de excitación de $^{17}$O [keV]", fontsize=12.5)
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_bounds(-250, 4700)
    tit = "$^{16}$O(n,$\\gamma$)$^{17}$O con neutrones térmicos"
    if con_meiga:
        tit += f"\n(intensidades por 100 capturas; MEIGA: {cap_n} capturas en $^{{16}}$O)"
    ax.set_title(tit, fontsize=13)
    fig.tight_layout()
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{nombre}.{e}"), dpi=170)
    plt.close(fig)


dibujar(False, "fig18_esquema_niveles_O17")
dibujar(True, "fig18b_esquema_niveles_O17_MEIGA")
print(json.dumps(out, indent=1))
