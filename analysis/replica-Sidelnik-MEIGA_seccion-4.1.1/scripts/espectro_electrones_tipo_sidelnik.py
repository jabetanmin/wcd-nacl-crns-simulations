#!/usr/bin/env python3
"""Espectro de electrones producidos por gammas en el agua (Compton, fotoelectrico y pares; e-) en el formato
de la Fig. 5 de Sidelnik et al. (2020) y comparacion con la figura digitalizada (datos/fig5_sidelnik_digitalizada.csv).
Las cuentas de MEIGA se escalan a 150000 neutrones. Compara: (a) escala con bines de 20 keV, (b) forma,
(c) cociente NaCl/agua pura (no depende de la normalizacion), (d) saltos en los bordes Compton.
Escribe figuras/fig13_espectro_electrones_tipo_sidelnik.{png,pdf} y resultados/espectro_electrones_tipo_sidelnik.json"""
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
MED = [m for m in ["pura", "nacl25", "nacl5", "nacl10"] if os.path.exists(os.path.join(RES, f"{m}.npz"))]
ETQ = {"pura": "Pure H$_2$O", "nacl25": "2.5% NaCl in H$_2$O", "nacl5": "5% NaCl in H$_2$O", "nacl10": "10% NaCl in H$_2$O"}
COL = {"pura": "#e41a1c", "nacl25": "#009e73", "nacl5": "#7b1fa2", "nacl10": "#e69f00"}
ref = pd.read_csv(os.path.join(R, "datos", "fig5_sidelnik_digitalizada.csv"))
W = 4                                            # bines de 5 keV agrupados de a 4 = 20 keV
# bordes Compton E_c = E (2E/m)/(1+2E/m) de las lineas principales
LINEAS = {"2,223 (H)": 2.2232, "6,13 (O) / 6,11 (Cl)": 6.12, "7,41 (Cl)": 7.4141, "7,79 (Cl)": 7.7901, "8,58 (Cl)": 8.5785}
borde = lambda E: E * (2 * E / 0.511) / (1 + 2 * E / 0.511)
esp = {}
for m in MED:
    z = np.load(os.path.join(RES, f"{m}.npz")); N = int(z["N"]); GB = z["GB"]
    h = (z["H_egamlin|compt|e-"] + z["H_egamlin|phot|e-"] + z["H_egamlin|conv|e-"]).astype(float) * 150000 / N
    h = h[:len(h) // W * W].reshape(-1, W).sum(1); c = (np.arange(len(h)) + 0.5) * 0.005 * W
    esp[m] = (c, h, N)
def nivel(c, h, E, w=0.1):
    s = np.abs(c - E) < w; return float(np.mean(h[s]))
def nivel_ref(m, E, w=0.1):
    s = (ref.E_MeV - E).abs() < w; return float(np.nanmedian(ref[f"{m}_mediana"][s]))
EV = [0.5, 1.0, 1.5, 1.9, 2.1, 3.0, 4.0, 5.0, 5.8, 6.1, 7.0, 7.4, 7.7, 8.0, 9.0]
out = {"ancho_bin_keV": 5 * W, "niveles": {}, "cociente_Sidelnik_MEIGA": {}, "NaCl_sobre_pura": {}, "saltos_bordes": {}}
for m in MED:
    c, h, N = esp[m]
    out["niveles"][m] = {str(E): {"MEIGA": nivel(c, h, E), "Sidelnik": nivel_ref(m, E)} for E in EV}
    rr = [out["niveles"][m][str(E)]["Sidelnik"] / out["niveles"][m][str(E)]["MEIGA"] for E in EV if E <= 7.0]
    out["cociente_Sidelnik_MEIGA"][m] = {"mediana": float(np.nanmedian(rr)), "min": float(np.nanmin(rr)), "max": float(np.nanmax(rr))}
    # salto en cada borde Compton: nivel 0,10-0,04 MeV antes / 0,04-0,10 MeV despues
    out["saltos_bordes"][m] = {}
    for k, E in LINEAS.items():
        Ec = borde(E)
        a = np.mean(h[(c > Ec - 0.12) & (c < Ec - 0.03)]); b = np.mean(h[(c > Ec + 0.03) & (c < Ec + 0.12)])
        sa = ref[(ref.E_MeV > Ec - 0.12) & (ref.E_MeV < Ec - 0.03)][f"{m}_mediana"].median()
        sb = ref[(ref.E_MeV > Ec + 0.03) & (ref.E_MeV < Ec + 0.12)][f"{m}_mediana"].median()
        out["saltos_bordes"][m][k] = {"borde_MeV": Ec, "MEIGA": float(a / b) if b > 0 else None,
                                      "Sidelnik": float(sa / sb) if np.isfinite(sa) and np.isfinite(sb) and sb > 0 else None}
for m in MED[1:]:
    out["NaCl_sobre_pura"][m] = {str(E): {"MEIGA": out["niveles"][m][str(E)]["MEIGA"] / out["niveles"]["pura"][str(E)]["MEIGA"],
                                          "Sidelnik": nivel_ref(m, E) / nivel_ref("pura", E)} for E in EV}
json.dump(out, open(os.path.join(RES, "espectro_electrones_tipo_sidelnik.json"), "w"), indent=1)

estilo.aplicar()
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
fig, axs = plt.subplots(2, 2, figsize=(8, 10.8))
a = axs[0, 0]
for m in MED:
    c, h, N = esp[m]; s = h > 0
    a.plot(c[s], h[s], "-", color=COL[m], lw=0.9)
a.set_title(f"(a) MEIGA, formato de la Fig. 5\n(intervalos de {5 * W} keV, 150 000 n)")
a = axs[0, 1]
fac = []
for m in MED:
    c, h, N = esp[m]; k = out["cociente_Sidelnik_MEIGA"][m]["mediana"]; s = h > 0
    a.plot(c[s], h[s] * k, "-", color=COL[m], lw=0.8, alpha=0.8)
    a.plot(ref.E_MeV, ref[f"{m}_mediana"], "o", color=COL[m], mec="#0b0b0b", mew=0.3, ms=2.2)
    fac.append(f"{k:.2f}".replace(".", ","))
for k_, E in LINEAS.items():
    a.axvline(borde(E), color="#8a8984", ls=":", lw=0.8)
a.text(0.97, 0.97, "factor MEIGA:\n" + " / ".join(fac), transform=a.transAxes, ha="right", va="top", fontsize=11)
a.set_title("(b) MEIGA × factor frente a Sidelnik\n(punteadas: bordes Compton)")
for a in axs[0]:
    a.set_yscale("log"); a.set_ylim(10, 1e6); a.set_xlim(0, 10); a.set_xlabel("Energía [MeV]"); a.set_ylabel("Cuentas")
a = axs[1, 0]
for m in MED[1:]:
    c, h, N = esp[m]; c0, h0, _ = esp["pura"]
    hh = lambda x, y: np.convolve(y, np.ones(10) / 10, "same")
    a.plot(c, hh(c, h) / np.maximum(hh(c0, h0), 1e-9), "-", color=COL[m], lw=1.2)
    rp = np.interp(ref.E_MeV, ref.E_MeV[ref.pura_mediana.notna()], ref.pura_mediana.dropna())
    a.plot(ref.E_MeV, ref[f"{m}_mediana"] / rp, "o", color=COL[m], mec="#0b0b0b", mew=0.3, ms=2.5)
a.axhline(1, color="#0b0b0b", lw=0.8); a.set_ylim(0.5, 4); a.set_xlim(0, 10)
a.set_xlabel("Energía [MeV]"); a.set_ylabel("NaCl / agua pura")
a.set_title("(c) Efecto del NaCl\n(no depende de la normalización)")
a = axs[1, 1]
sb0 = out["saltos_bordes"]["pura"]; claves = list(sb0)
nb = 2 * len(MED); w_ = 0.84 / nb
for i, m in enumerate(MED):
    sb = out["saltos_bordes"][m]
    for j, k_ in enumerate(claves):
        if not sb[k_]["MEIGA"] or (m == "pura" and "Cl" in k_ and "O" not in k_):
            continue
        x0 = j - 0.42 + (2 * i + 0.5) * w_
        a.bar(x0, sb[k_]["MEIGA"], w_, color=COL[m])
        a.bar(x0 + w_, sb[k_]["Sidelnik"] or 0, w_, color=COL[m], alpha=0.4, hatch="//", edgecolor="#0b0b0b", lw=0.3)
a.set_xticks(np.arange(len(claves))); a.set_xticklabels([f"{sb0[k_]['borde_MeV']:.2f}".replace(".", ",") for k_ in claves]); a.set_xlabel("Borde Compton [MeV]")
a.axhline(1, color="#0b0b0b", lw=0.8); a.set_ylabel("Nivel antes / después"); a.set_ylim(0, 9.5)
a.set_title("(d) Saltos en los bordes Compton\n(líneas de 2,22; 6,1; 7,41; 7,79; 8,58 MeV)")
H = [Patch(color=COL[m], label={"pura": "Agua pura", "nacl25": "Agua + 2.5 % NaCl", "nacl5": "Agua + 5 % NaCl", "nacl10": "Agua + 10 % NaCl"}[m]) for m in MED] + \
    [Line2D([], [], color="#0b0b0b", lw=1.2, label="MEIGA (líneas, barras llenas)"),
     Line2D([], [], color="#0b0b0b", marker="o", ls="", ms=4, label="Sidelnik (puntos, barras rayadas)")]
fig.legend(handles=H, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.0), columnspacing=1.2, handlelength=1.6)
fig.tight_layout(rect=(0, 0.06, 1, 1))
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig13_espectro_electrones_tipo_sidelnik.{e}"))
print(json.dumps({k: out[k] for k in ("cociente_Sidelnik_MEIGA", "saltos_bordes")}, indent=1))
for m, v in out["NaCl_sobre_pura"].items():
    print(m, {E: (round(x["MEIGA"], 2), round(x["Sidelnik"], 2)) for E, x in v.items()})
