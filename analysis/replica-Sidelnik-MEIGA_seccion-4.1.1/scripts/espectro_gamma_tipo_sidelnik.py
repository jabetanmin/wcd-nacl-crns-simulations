#!/usr/bin/env python3
"""Espectro de energia de los gammas creados en el medio, en el formato de la Fig. 3 de Sidelnik et al. (2020),
y comparacion con la figura digitalizada (datos/fig3_sidelnik_digitalizada.csv).
Lee resultados/<medio>_gamma_pasos.npz (espectro_gamma_pasos.py, bins de 1 keV) y resultados/<medio>.npz.
Escribe figuras/fig11_espectro_gamma_tipo_sidelnik.{png,pdf} y resultados/espectro_gamma_tipo_sidelnik.json.
Uso: espectro_gamma_tipo_sidelnik.py [medio]"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
m = sys.argv[1] if len(sys.argv) > 1 else "pura"
z = np.load(os.path.join(RES, f"{m}_gamma_pasos.npz")); p = np.load(os.path.join(RES, f"{m}.npz"))
ref = pd.read_csv(os.path.join(R, "datos", "fig3_sidelnik_digitalizada.csv"))
ETQ = {"pura": "Pure H$_2$O", "nacl25": "2.5% NaCl in H$_2$O", "nacl5": "5% NaCl in H$_2$O", "nacl10": "10% NaCl in H$_2$O"}
COLM = {"pura": "#e41a1c", "nacl25": "#1a8a1a", "nacl5": "#7b1fa2", "nacl10": "#f5a623"}   # colores de cada medio en la tesis
COLREF = {"pura": "pura", "nacl25": "nacl25", "nacl5": "nacl5", "nacl10": "nacl10"}[m]
W = 2                                            # keV: el cociente pico/continuo a 3-5 MeV coincide con el de Sidelnik
def reb(h, w):
    h = h[:len(h) // w * w].reshape(-1, w).sum(1); return h, (np.arange(len(h)) + 0.5) * w * 1e-3
h, c = reb(z["primer_paso_agua"], W)
def linea(hh, cc, E, ww=0.02):
    return float(hh[np.abs(cc - E) < ww].max())
def cont(hh, cc, E, ww=0.25):
    return float(np.median(hh[np.abs(cc - E) < ww]))
def lin_ref(E, ww=0.1):
    return float(ref[f"{COLREF}_max"][(ref.E_MeV - E).abs() < ww].max())
def cont_ref(E, ww=0.25):
    return float(ref[f"{COLREF}_mediana"][(ref.E_MeV - E).abs() < ww].median())
pk, pkr = linea(h, c, 2.2232), lin_ref(2.223)
sin_rd = z["primer_paso_agua"] - z["primer|RadioactiveDecayBase"]   # (casi todo en el agua)
h2, _ = reb(sin_rd, W)
pos = {k.split("|")[1]: int(p[k].sum()) for k in p.files if k.startswith("H_ecre|") and k.endswith("|e+")}
out = {"ancho_bin_keV": W, "gammas_creados_en_agua": int(z["primer_paso_agua"].sum()),
       "pico_2223": {"MEIGA_cuentas": pk, "Sidelnik_cuentas_aprox": pkr},
       "cociente_0511_2223": {"Sidelnik": lin_ref(0.511) / pkr, "MEIGA": linea(h, c, 0.511) / pk,
                              # los gammas de 0,511 los crea 'annihil': se quita la fraccion de positrones beta+ (estimacion)
                              "MEIGA_sin_decaimiento_radiactivo": linea(h, c, 0.511) / pk * (1 - pos.get("RadioactiveDecayBase", 0) / sum(pos.values()))},
       "cociente_6130_2223": {"Sidelnik": lin_ref(6.13) / pkr, "MEIGA": linea(h, c, 6.1294) / pk,
                              "MEIGA_sin_decaimiento_radiactivo": linea(h2, c, 6.1294) / pk},
       "pico_sobre_continuo": {str(E): {"Sidelnik": pkr / cont_ref(E), "MEIGA": pk / max(cont(h, c, E), 0.5)} for E in (1, 3, 4, 5, 10, 15)},
       "positrones_por_proceso": pos,
       "linea_0511_por_creador": {k.split("|")[1]: int(z[k][509:513].sum()) for k in z.files if k.startswith("primer|") and z[k][509:513].sum() > 0},
       "linea_6130_por_creador": {k.split("|")[1]: int(z[k][6126:6133].sum()) for k in z.files if k.startswith("primer|") and z[k][6126:6133].sum() > 0},
       "continuo_1_8_por_creador": {k.split("|")[1]: int(z[k][1000:8000].sum()) for k in z.files if k.startswith("primer|") and z[k][1000:8000].sum() > 100},
       "continuo_10_17_por_creador": {k.split("|")[1]: int(z[k][10000:17000].sum()) for k in z.files if k.startswith("primer|") and z[k][10000:17000].sum() > 20}}
SUF = "" if m == "pura" else f"_{m}"
N = len(p["Q"]); out["N"] = N
# lineas del cloro (captura en 35Cl) y del O: cociente con la de 2,223 MeV. La resolucion de la digitalizacion (25,6 keV/pixel)
# no separa 0,511/0,517 ni 6,11/6,13 MeV: se compara la linea mas alta dentro de +-30 keV en ambos casos.
LIN = {"0,511/0,517": 0.514, "1,165 (Cl)": 1.1647, "1,951 (Cl)": 1.9512, "6,11/6,13": 6.12, "7,41 (Cl)": 7.4141, "7,79 (Cl)": 7.7901, "8,58 (Cl)": 8.5785}
out["lineas_sobre_2223"] = {k: {"Sidelnik": lin_ref(E, 0.04) / pkr, "MEIGA": linea(h, c, E, 0.03) / pk} for k, E in LIN.items()}
json.dump(out, open(os.path.join(RES, f"espectro_gamma_tipo_sidelnik{SUF}.json"), "w"), indent=1)

estilo.aplicar()
fig, axs = plt.subplots(2, 2, figsize=(8, 10.3 if m == "pura" else 9.6))
a = axs[0, 0]; s = h > 0
a.plot(c[s], h[s], "-o", color=COLM[m], lw=0.5, ms=1.6, label={"pura": "MEIGA, agua pura", "nacl25": "MEIGA, agua + 2,5 % NaCl", "nacl5": "MEIGA, agua + 5 % NaCl", "nacl10": "MEIGA, agua + 10 % NaCl"}[m])
a.set_title(f"(a) MEIGA, formato de la Fig. 3\n(intervalos de {W} keV, {N} n)", fontsize=10.5)
a = axs[0, 1]; k = pkr / pk
a.plot(c[s], h[s] * k, "-", color=COLM[m], lw=0.6, alpha=0.8, label=f"MEIGA × {k:.2f}".replace(".", ","))
a.plot(ref.E_MeV, ref[f"{COLREF}_mediana"], "s", color="#0b0b0b", ms=2.5, label="Sidelnik (mediana)")
a.plot(ref.E_MeV, ref[f"{COLREF}_max"], "^", color="#6b6b6b", ms=2.5, label="Sidelnik (máximo)")
a.set_title("(b) Comparación con la Fig. 3\nde Sidelnik", fontsize=10.5)
for a in axs[0]:
    a.set_yscale("log"); a.set_ylim(0.8, 1e8); a.set_xlim(0, 20); a.set_xlabel("Energía [MeV]"); a.set_ylabel("Cuentas"); a.legend(fontsize=8.5, loc="upper right", handlelength=1.3)
# (c) composicion por proceso creador, bins de 50 keV
a = axs[1, 0]
grupos = [("nCapture", "captura n (H)" if m == "pura" else "captura n (H y Cl)", "#2a78d6"), ("neutronInelastic", "inelástica n", "#1baf7a"), ("eBrem", "bremsstrahlung", "#eda100"),
          ("annihil", "aniquilación e$^+$", "#e34948"), ("RadioactiveDecayBase", "decaimiento radiactivo", "#4a3aa7"),
          ("protonInelastic", "inelástica p", "#8a8984")]
for nom, et, col in grupos:
    hh, cc = reb(z[f"primer|{nom}"], 50); s = hh > 0
    a.step(cc[s], hh[s], where="mid", color=col, lw=1.2, label=et)
a.set_yscale("log"); a.set_xlim(0, 20); a.set_ylim(0.5, 1e7); a.set_xlabel("Energía [MeV]"); a.set_ylabel("Gammas / 50 keV")
a.set_title("(c) MEIGA: gammas según el\nproceso que los crea", fontsize=10.5)
# (d) cocientes de lineas
a = axs[1, 1]
if m == "pura":
    cs_ = [("0,511 / 2,223 MeV", "cociente_0511_2223"), ("6,13 / 2,223 MeV", "cociente_6130_2223")]
    xs = np.arange(2); wb = 0.27
    for i, (lab, key, col) in enumerate([("Sidelnik", "Sidelnik", "#0b0b0b"), ("MEIGA", "MEIGA", COLM[m]),
                                         ("MEIGA sin decaim. radiactivo", "MEIGA_sin_decaimiento_radiactivo", "#f4a3a3")]):
        v = [out[k_][key] for _, k_ in cs_]
        a.bar(xs + (i - 1) * wb, v, wb, color=col, label=lab)
        for x_, y_ in zip(xs + (i - 1) * wb, v):
            a.text(x_, y_ * 1.15, f"{y_:.3f}".replace(".", ","), ha="center", fontsize=8.5, rotation=90, va="bottom")
    a.set_yscale("log"); a.set_ylim(5e-3, 300); a.set_xticks(xs); a.set_xticklabels([l.replace(" / ", "\n/ ") for l, _ in cs_])
    a.set_ylabel("Altura / altura de 2,223 MeV"); a.legend(fontsize=8.5, loc="upper right")

else:
    L = out["lineas_sobre_2223"]; xs = np.arange(len(L)); wb = 0.38
    for i, (lab, key, col) in enumerate([("Sidelnik", "Sidelnik", "#0b0b0b"), ("MEIGA", "MEIGA", COLM[m])]):
        v = [L[k_][key] for k_ in L]
        a.bar(xs + (i - 0.5) * wb, v, wb, color=col, label=lab)
    a.set_yscale("log"); a.set_ylim(5e-3, 100); a.set_xticks(xs); a.set_xticklabels([k_.replace(" (Cl)", "") for k_ in L], fontsize=9, rotation=45, ha="right"); a.set_xlabel("Línea [MeV]")
    a.set_ylabel("Altura / altura de 2,223 MeV"); a.legend(fontsize=8.5, loc="upper right")
a.set_title("(d) Cocientes de líneas\n(no dependen del intervalo)", fontsize=10.5)
fig.legend(*axs[1, 0].get_legend_handles_labels(), loc="lower center", ncol=3, frameon=False, columnspacing=1.0, handlelength=1.4, title="(c) proceso creador:", title_fontsize=11.5)
fig.tight_layout(rect=(0, 0.085, 1, 1))
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig11_espectro_gamma_tipo_sidelnik{SUF}.{e}"))
print(json.dumps(out, indent=1))
