#!/usr/bin/env python3
"""Esquema de niveles y principales transiciones gamma de la captura 35Cl(n,g)36Cl con neutrones termicos.
Datos de referencia: evaluacion ENSDF 35Cl(n,g) E=thermal (N. Nica, J. Cameron y B. Singh, Nucl. Data Sheets 113, 1 (2012);
intensidades de 2007ChZX/PGAA-IAEA). Las intensidades Ig de la evaluacion son secciones eficaces parciales; por 100 capturas
se multiplican por 100/sigma = 100/33,22 b. Se incluyen las transiciones con mas de ~2,5 por 100 capturas.
Ademas compara con las intensidades de MEIGA en las capturas en 35Cl (<medio>.npz). Los niveles se dibujan sin escala.
Escribe figuras/fig19_esquema_niveles_Cl36.{png,pdf}, figuras/fig19b_esquema_niveles_Cl36_MEIGA.{png,pdf} y resultados/intensidades_Cl36.json"""
import os, json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
SIG = 33.22                                      # b; Ig(por 100 capturas) = 100 * Ig(b) / SIG
SN = 8579.7945
# niveles: energia [keV], J^pi, T1/2, posicion en el dibujo (sin escala)
NIV = [(0.0, "2$^+$", "3,01×10$^5$ a", 0.0), (788.4329, "3$^+$", None, 2.2), (1164.8802, "1$^+$", None, 4.2),
       (1951.1857, "2", "1,25 ps", 6.2), (1959.3945, "2", "44 fs", 7.3), (2468.2594, "3$^-$", "0,83 ps", 9.0),
       (2863.9311, "(2,3)$^+$", "15 fs", 10.5), (SN, "2$^+$", None, 14.6)]
Y = {E: y for E, _, _, y in NIV}
# transiciones: E_gamma [keV], Ig [b], nivel inicial, nivel final, multipolaridad
TR = [(8578.696, 0.883, SN, 0.0, "M1+E2"), (7790.454, 2.66, SN, 788.4329, "M1+E2"), (7414.09, 3.29, SN, 1164.8802, "M1+E2"),
      (6627.945, 1.466, SN, 1951.1857, ""), (6619.732, 2.530, SN, 1959.3945, ""), (6110.9802, 6.59, SN, 2468.2594, "E1"),
      (5715.356, 1.818, SN, 2863.9311, "M1+E2"),
      (2863.807, 1.818, 2863.9311, 0.0, ""), (517.06962, 7.58, 2468.2594, 1951.1857, ""), (1170.941, 1.82, 1959.3945, 788.4329, ""),
      (1959.337, 4.10, 1959.3945, 0.0, ""), (786.29643, 3.419, 1951.1857, 1164.8802, ""), (1951.12647, 6.33, 1951.1857, 0.0, ""),
      (1164.860, 8.91, 1164.8802, 0.0, "M1+E2"), (788.4236, 5.42, 788.4329, 0.0, "M1+E2")]
COLM = {"E1": "#d62728", "M1+E2": "#2a5aa6", "": "#444444"}

# MEIGA: gammas de las capturas en 35Cl en el medio, por 100 capturas
cap_n, cuentas, suma, unico = 0, {t[0]: 0 for t in TR}, [], 0
for m in ["nacl25", "nacl5", "nacl10"]:
    f = os.path.join(RES, f"{m}.npz")
    if not os.path.exists(f):
        continue
    z = np.load(f)
    cap = pd.DataFrame({"run": z["cap_run_id"], "trk": z["cap_track_id"], "Z": z["cap_target_Z"], "A": z["cap_target_A"], "mat": z["cap_material"]})
    cap = cap[(cap.Z == 17) & (cap.A == 35) & cap.mat.str.startswith(("Water", "SaltyWater"))]
    sc = pd.DataFrame({"run": z["sc_run"], "trk": z["sc_ptrk"], "p": z["sc_part"], "E": z["sc_E"] * 1e3})
    g = sc[sc.p == "gamma"].merge(cap[["run", "trk"]], on=["run", "trk"])
    cap_n += len(cap); suma += g.groupby(["run", "trk"]).E.sum().tolist()
    for t in TR:
        cuentas[t[0]] += int((np.abs(g.E - t[0]) < 0.3).sum())
    unico += int((np.abs(g.E - SN) < 0.3).sum())     # gamma unico con toda la energia de separacion (sin retroceso)
out = {"capturas_Cl35_MEIGA": cap_n, "suma_media_keV": float(np.mean(suma)) if suma else None,
       "gamma_unico_Sn_por_100": 100 * unico / cap_n if cap_n else None, "transiciones": {}}
for t in TR:
    k = cuentas[t[0]]
    out["transiciones"][f"{t[0]:.2f}"] = {"referencia": 100 * t[1] / SIG, "MEIGA": 100 * k / cap_n if cap_n else None,
                                          "MEIGA_error": 100 * np.sqrt(k) / cap_n if cap_n else None, "Ei": t[2], "Ef": t[3]}
json.dump(out, open(os.path.join(RES, "intensidades_Cl36.json"), "w"), indent=1)


def dibujar(con_meiga, nombre):
    plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(figsize=(13.5, 8.0))   # apaisada: va en una pagina horizontal del informe
    x0, x1 = 0.0, 1.0
    for E, jp, t12, y in NIV:
        cap = E == SN
        ax.hlines(y, x0, x1, color="#0b0b0b", lw=3.2 if E == 0 else 1.2, ls="--" if cap else "-")
        ax.text(x0 - 0.01, y, jp, ha="right", va="center", fontsize=14.4)
        ax.text(x1 + 0.01, y + 0.08, f"{E:.2f} keV".replace(".", ",") if E > 0 else "0", ha="left", va="bottom", fontsize=13.8)
        if t12:
            ax.text(x1 + 0.01, y - 0.08, t12, ha="left", va="top", fontsize=12, color="#555555")
    ax.text(x1 + 0.01, Y[SN] + 0.55, "estado de captura ($S_n$)", ha="left", va="bottom", fontsize=12.6, color="#555555")
    yb = (Y[2863.9311] + Y[SN]) / 2                  # corte del eje: los niveles no estan a escala
    for d in (-0.12, 0.12):
        ax.plot([-0.035, -0.015], [yb + d - 0.1, yb + d + 0.1], color="#0b0b0b", lw=1.2, clip_on=False)
    xs = np.linspace(0.025, 0.925, len(TR))
    for x, (Eg, Ib, Ei, Ef, mult) in zip(xs, TR):
        I = 100 * Ib / SIG; col = COLM[mult]; lw = 0.8 + I / 6
        ax.annotate("", xy=(x, Y[Ef] + 0.04), xytext=(x, Y[Ei] - 0.04),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, mutation_scale=7 + 2.5 * lw, shrinkA=0, shrinkB=0))
        et = f"{Eg:.2f} keV\n{I:.1f} %".replace(".", ",")
        if con_meiga:
            et += f" [{out['transiciones'][f'{Eg:.2f}']['MEIGA']:.1f}]".replace(".", ",")
        if Ei == SN:
            ym, va_ = Y[Ei] - 0.25, "top"
        elif Y[Ei] - Y[Ef] < 3.2:                   # transicion corta: etiqueta desde el nivel final hacia arriba
            ym, va_ = Y[Ef] + 0.15, "bottom"
        else:
            ym, va_ = (Y[Ei] + Y[Ef]) / 2, "center"
        ax.text(x + 0.003 + 0.0025 * lw, ym, et, rotation=90, ha="left", va=va_, fontsize=12.6, color=col, linespacing=1.0,
                bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.85))
    if con_meiga:                                   # gamma unico de energia S_n que emite Geant4 (no existe en la naturaleza)
        xu = 0.975
        ax.annotate("", xy=(xu, Y[0.0] + 0.04), xytext=(xu, Y[SN] - 0.04),
                    arrowprops=dict(arrowstyle="-|>", color="#c51b8a", lw=2.2, ls="--", mutation_scale=14, shrinkA=0, shrinkB=0))
        ax.text(xu - 0.015, Y[SN] - 2.6, f"solo MEIGA:\nγ único de {SN:.1f} keV\n(= $S_n$, sin retroceso)\n[{out['gamma_unico_Sn_por_100']:.1f} % de las capturas]".replace(".", ","),
                ha="right", va="center", fontsize=12.6, color="#c51b8a", linespacing=1.15)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=COLM["E1"], lw=2.5, label="E1"), Line2D([], [], color=COLM["M1+E2"], lw=2.5, label="M1+E2"),
         Line2D([], [], color=COLM[""], lw=2.5, label="multipolaridad no asignada")]
    if con_meiga:
        h.append(Line2D([], [], color="#c51b8a", lw=2.2, ls="--", label="γ único de $S_n$ (solo MEIGA)"))
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=2, frameon=False, fontsize=13.2)
    ax.set_xlim(-0.07, 1.14); ax.set_ylim(-0.5, 15.6); ax.axis("off")
    tit = "$^{35}$Cl(n,$\\gamma$)$^{36}$Cl con neutrones térmicos\n(niveles sin escala; intensidades por 100 capturas"
    tit += f"; entre corchetes: MEIGA, {cap_n} capturas)" if con_meiga else ")"
    ax.set_title(tit, fontsize=15)
    fig.tight_layout()
    for e in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{nombre}.{e}"), dpi=170)
    plt.close(fig)


dibujar(False, "fig19_esquema_niveles_Cl36")
dibujar(True, "fig19b_esquema_niveles_Cl36_MEIGA")
for k, v in out["transiciones"].items():
    print(f"{k:>9}  ref {v['referencia']:5.2f}  MEIGA {v['MEIGA']:5.2f} ± {v['MEIGA_error']:.2f}")
print("capturas", cap_n, "suma media", out["suma_media_keV"], "gamma unico Sn %", out["gamma_unico_Sn_por_100"])
