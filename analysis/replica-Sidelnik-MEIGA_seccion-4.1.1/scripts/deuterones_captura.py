#!/usr/bin/env python3
"""Distribucion de energia de los deuterones de la captura 1H(n,g)2H en el medio (formato de la Fig. 4.6 de la tesis).
Usa los productos de captura de <medio>.npz (secundarias-captura-neutron). Las cuentas de corridas parciales se escalan
a 150000 neutrones primarios para que las alturas sean comparables. Media y RMS se calculan con todos los deuterones
(como en la Fig. 4.6), y tambien en la ventana 1,2-1,45 keV.
Escribe figuras/fig16_deuterones_captura.{png,pdf} y resultados/deuterones_captura.json"""
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
ETQ = {"pura": "Agua pura", "nacl25": "Agua + 2,5 % NaCl", "nacl5": "Agua + 5 % NaCl", "nacl10": "Agua + 10 % NaCl"}
COL = {"pura": "#e41a1c", "nacl25": "#1a8a1a", "nacl5": "#7b1fa2", "nacl10": "#f5a623"}
MD = 1875.61294                                  # masa del deuteron [MeV]
out = {}
b = np.arange(0.00120, 0.0014501, 0.0000005)    # 0,5 eV
estilo.aplicar()
fig, ax = plt.subplots(figsize=(8, 5.0))
for m in MED:
    z = np.load(os.path.join(RES, f"{m}.npz")); N = int(z["N"])
    cap = pd.DataFrame({"run": z["cap_run_id"], "trk": z["cap_track_id"], "Z": z["cap_target_Z"], "mat": z["cap_material"]})
    cap = cap[(cap.Z == 1) & cap.mat.str.startswith(("Water", "SaltyWater"))]
    sc = pd.DataFrame({"run": z["sc_run"], "trk": z["sc_ptrk"], "p": z["sc_part"], "E": z["sc_E"]})
    d = sc[sc.p == "deuteron"].merge(cap[["run", "trk"]], on=["run", "trk"]).E.to_numpy()
    g = sc[sc.p == "gamma"].merge(cap[["run", "trk"]], on=["run", "trk"]).E.to_numpy()
    w = (d > 0.0012) & (d < 0.00145)
    out[m] = {"N_primarios": N, "deuterones": int(len(d)), "media_MeV": float(d.mean()), "RMS_MeV": float(d.std()),
              "mediana_MeV": float(np.median(d)), "media_ventana_MeV": float(d[w].mean()), "sigma_ventana_MeV": float(d[w].std()),
              "frac_fuera_ventana": float(1 - w.mean()), "max_MeV": float(d.max()),
              "E_retroceso_teorico_MeV": float(np.mean(g) ** 2 / (2 * MD))}
    k = 150000 / N
    h, _ = np.histogram(d, b)
    ax.step(0.5e3 * (b[1:] + b[:-1]), h * k, where="mid", color=COL[m], lw=1.5,
            label=f"{ETQ[m]}: mediana {1e3 * np.median(d):.3f} keV, σ = {1e6 * d[w].std():.1f} eV".replace(".", ","))
ax.set_xlim(1.20, 1.45); ax.set_ylim(0, 1.45 * ax.get_ylim()[1]); ax.grid(alpha=0.4)
ax.set_xlabel("Energía cinética del deuterón [keV]"); ax.set_ylabel("Deuterones por 150 000 neutrones")
ax.legend(fontsize=11.5, loc="upper left", handlelength=1.5)
fig.tight_layout()
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig16_deuterones_captura.{e}"), dpi=160)
json.dump(out, open(os.path.join(RES, "deuterones_captura.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
