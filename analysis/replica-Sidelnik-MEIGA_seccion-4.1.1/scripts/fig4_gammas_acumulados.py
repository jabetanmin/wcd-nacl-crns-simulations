#!/usr/bin/env python3
"""Fig. 4 de Sidelnik et al. (2020): gammas producidos, acumulados de derecha a izquierda (N(>=E), bines de 1 MeV).
Digitaliza los marcadores de las dos imagenes del articulo (completa 0-100 MeV y zoom 1-9 MeV) por color y compara con
MEIGA (resultados/<medio>_gammas_hasta600.npz, de gammas_acumulados.py), con cuentas por 150000 neutrones.
Escribe datos/fig4_sidelnik_digitalizada.csv, resultados/fig4_gammas_acumulados.json y figuras/fig17_gammas_acumulados.{png,pdf}"""
import os, json
import numpy as np, pandas as pd
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG, DAT = (os.path.join(R, d) for d in ("resultados", "figuras", "datos"))
def colores(im):
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    return {"pura": (r > 190) & (g < 90) & (b < 90),
            "nacl25": (r < 160) & (g > 165) & (b > 135) & (b < 205) & (g - r > 40),
            "nacl5": (r > 100) & (r < 190) & (g < 70) & (b > 160),
            "nacl10": (r > 220) & (g > 150) & (g < 230) & (b < 185) & (g - b > 30)}
def digit(f, x0, dx, y_dec, px_dec, Es, ylim):
    im = np.asarray(Image.open(os.path.join(DAT, f)).convert("RGB")).astype(int); C = colores(im); out = {}
    for m, mk in C.items():
        v = []
        for E in Es:
            c = int(round(x0 + E * dx)); sub = mk[ylim[0]:ylim[1], c - 7:c + 8]
            rows = np.flatnonzero(sub.any(1)) + ylim[0]
            if len(rows) < 3:
                v.append(np.nan); continue
            # marcador = grupo de filas contiguas mas grande
            grupos = np.split(rows, np.flatnonzero(np.diff(rows) > 2) + 1); gmax = max(grupos, key=len)
            v.append(10 ** (y_dec[1] + (y_dec[0] - np.median(gmax)) / px_dec))
        out[m] = v
    return out
EZ = np.arange(1, 10); EC = np.arange(1, 100)
z = digit("fig4_sidelnik_acumulado_zoom.png", 380, 74.9, (511, 4), 209, EZ, (35, 505))       # fila 511 = 1e4
c = digit("fig4_sidelnik_acumulado.png", 258, 7.49, (578, 2), 96, EC, (100, 575))             # fila 578 = 1e2
for m in c:                                                     # recuadro de la leyenda (E > 60 MeV, N > 1e5): no son datos
    c[m] = [np.nan if (E > 60 and v > 1e5) else v for E, v in zip(EC, c[m])]
ref = pd.DataFrame({"E_MeV": EC})
for m in z:
    v = np.array(c[m], float); v[:9] = np.where(np.isfinite(z[m]), z[m], v[:9]); ref[m] = v
# desde 9 MeV las cuatro curvas del articulo se superponen y los marcadores se tapan: se usa el valor comun (mediana de los colores)
comun = np.nanmedian(ref[["pura", "nacl25", "nacl5", "nacl10"]].to_numpy(), axis=1)
for m in ("pura", "nacl25", "nacl5", "nacl10"):
    ref.loc[ref.E_MeV >= 9, m] = comun[ref.E_MeV >= 9]
ref.to_csv(os.path.join(DAT, "fig4_sidelnik_digitalizada.csv"), index=False)
# MEIGA
ETQ = {"pura": "Pure H$_2$O", "nacl25": "2.5% NaCl in H$_2$O", "nacl5": "5% NaCl in H$_2$O", "nacl10": "10% NaCl in H$_2$O"}
COL = {"pura": "#e41a1c", "nacl25": "#1baf7a", "nacl5": "#7b1fa2", "nacl10": "#e69f00"}
MED = [m for m in ETQ if os.path.exists(os.path.join(RES, f"{m}_gammas_hasta600.npz"))]
cum = {}
for m in MED:
    q = np.load(os.path.join(RES, f"{m}_gammas_hasta600.npz")); k = 150000 / int(q["N"])
    for tag in ("todos", "sin_piones"):
        h = q[tag] * k; cs = np.cumsum(h[::-1])[::-1]
        cum[(m, tag)] = np.array([cs[int(round(E / 0.01))] for E in EC])
out = {"puntos": {}, "NaCl_sobre_pura": {}, "cociente_Sidelnik_MEIGA_pura": {}}
for m in MED:
    out["puntos"][m] = {int(E): {"MEIGA": float(cum[(m, "todos")][i]), "MEIGA_sin_piones": float(cum[(m, "sin_piones")][i]),
                                 "Sidelnik": float(ref[m][i]) if np.isfinite(ref[m][i]) else None} for i, E in enumerate(EC) if E in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 17, 20, 30, 50, 70, 90, 99)}
for i, E in enumerate(EC):
    if E <= 20 or E % 10 == 0:
        out["cociente_Sidelnik_MEIGA_pura"][int(E)] = float(ref.pura[i] / cum[("pura", "todos")][i])
        if "nacl25" in MED:
            out["NaCl_sobre_pura"][int(E)] = {"MEIGA": float(cum[("nacl25", "todos")][i] / cum[("pura", "todos")][i]),
                                             "Sidelnik": float(ref.nacl25[i] / ref.pura[i])}
# linea de 2,223 MeV respecto a los gammas de >= 3 MeV
for m in MED:
    out.setdefault("N2menosN3_sobre_N3", {})[m] = {"MEIGA": float((cum[(m, "todos")][1] - cum[(m, "todos")][2]) / cum[(m, "todos")][2]),
                                                  "Sidelnik": float((ref[m][1] - ref[m][2]) / ref[m][2])}
    out.setdefault("N20_sobre_N3", {})[m] = {"MEIGA": float(cum[(m, "todos")][19] / cum[(m, "todos")][2]),
                                            "MEIGA_sin_piones": float(cum[(m, "sin_piones")][19] / cum[(m, "sin_piones")][2]),
                                            "Sidelnik": float(ref[m][19] / ref[m][2])}
json.dump(out, open(os.path.join(RES, "fig4_gammas_acumulados.json"), "w"), indent=1)
estilo.aplicar()
fig, axs = plt.subplots(2, 2, figsize=(8, 10.0))
for a, lim in ((axs[0, 0], (0, 100)), (axs[0, 1], (0, 10))):
    for m in MED:
        a.plot(EC, cum[(m, "todos")], "s" if m == "pura" else "o", color=COL[m], ms=4)
        a.plot(EC, ref[m], "s" if m == "pura" else "o", mfc="none", mec=COL[m], ms=6, mew=1.2)
    a.set_yscale("log"); a.set_xlim(*lim); a.set_xlabel("Energía [MeV]"); a.set_ylabel("N(≥E) por 150 000 n")
axs[0, 0].set_ylim(1e2, 1e7); axs[0, 0].set_title("(a) Gammas acumulados de derecha\na izquierda (Fig. 4 de Sidelnik)", fontsize=10.5)
axs[0, 1].set_ylim(1e4, 2e6); axs[0, 1].set_title("(b) Detalle por debajo de 10 MeV", fontsize=10.5)
a = axs[1, 0]
for m in MED:
    a.plot(EC, cum[(m, "todos")] / cum[(m, "todos")][2], "-", color=COL[m])
    a.plot(EC, cum[(m, "sin_piones")] / cum[(m, "sin_piones")][2], ":", color=COL[m])
    a.plot(EC, ref[m] / ref[m][2], "s" if m == "pura" else "o", mfc="none", mec=COL[m], ms=5)
a.set_yscale("log"); a.set_xlim(0, 100); a.set_xlabel("Energía [MeV]"); a.set_ylabel("N(≥E) / N(≥3 MeV)")
a.set_title("(c) Forma: normalizado a N(≥3 MeV)", fontsize=10.5)
a = axs[1, 1]
if "nacl25" in MED:
    Ei = np.arange(1, 21)
    for m_ in MED[1:]:
        a.plot(Ei, cum[(m_, "todos")][:20] / cum[("pura", "todos")][:20], "o-", color=COL[m_], ms=4)
        a.plot(Ei, ref[m_][:20] / ref.pura[:20], "o--", color=COL[m_], mfc="none", ms=5, lw=1)
    a.axhline(1, color="#8a8984", lw=0.8); a.set_xlabel("Energía [MeV]"); a.set_ylabel("N(≥E) NaCl / N(≥E) pura")
    a.set_title("(d) Efecto del NaCl\n(no depende de la normalización)", fontsize=10.5)
from matplotlib.lines import Line2D
h_ = [Line2D([], [], ls="none", marker="s", color="#8a8984", label="MEIGA (lleno; línea continua)"),
      Line2D([], [], ls="none", marker="s", mfc="none", mec="#0b0b0b", label="Sidelnik (vacío; línea discontinua)"),
      Line2D([], [], ls=":", color="#8a8984", label="MEIGA sin eventos con piones")]
h_ += [Line2D([], [], ls="-", lw=6, color=COL[m], label={"pura": "Agua pura", "nacl25": "Agua + 2,5 % NaCl", "nacl5": "Agua + 5 % NaCl", "nacl10": "Agua + 10 % NaCl"}[m]) for m in MED]
fig.legend(handles=h_, loc="lower center", ncol=2, fontsize=9, columnspacing=1.5)
fig.tight_layout(rect=(0, 0.115, 1, 1))
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig17_gammas_acumulados.{e}"))
print(json.dumps({k: out[k] for k in ("cociente_Sidelnik_MEIGA_pura", "NaCl_sobre_pura", "N2menosN3_sobre_N3", "N20_sobre_N3")}, indent=1))
