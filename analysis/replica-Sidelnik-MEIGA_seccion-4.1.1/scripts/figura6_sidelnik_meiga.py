#!/usr/bin/env python3
"""Reproduce la Fig. 6 de Sidelnik et al. (2020) con los datos de MEIGA, en su mismo formato:
fotones Cherenkov aceptados por la QE por neutron (antes del transporte optico), cuentas absolutas
por bin de 10 fotones, 0-2500, escala log. Superpone la curva digitalizada de Sidelnik sin reescalar.
Uso: figura6_sidelnik_meiga.py [medio ...]"""
import os, sys, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
TODOS = ["pura", "nacl25", "nacl5", "nacl10"]
MED = [m for m in (sys.argv[1:] or TODOS) if (os.path.exists(os.path.join(RES, f"{m}_aceptados_por_run.npy")) or os.path.exists(os.path.join(RES, f"{m}_fotones.npz")))]
def aceptados_por_run(m):
    """Fotones aceptados por la QE (= transportados en eFast) por neutron. Usa resultados/<m>_aceptados_por_run.npy
    (pequeno, va en el repositorio); si no existe lo calcula una vez desde <m>_fotones.npz (destino_fotones.py)."""
    f = os.path.join(RES, f"{m}_aceptados_por_run.npy")
    if not os.path.exists(f):
        N = len(np.load(os.path.join(RES, f"{m}.npz"))["Q"])
        np.save(f, np.bincount(np.load(os.path.join(RES, f"{m}_fotones.npz"))["run"], minlength=N).astype(np.int32))
    return np.load(f)


ETQ = {"pura": "Pure H$_2$O", "nacl25": "2.5% NaCl in H$_2$O", "nacl5": "5% NaCl in H$_2$O", "nacl10": "10% NaCl in H$_2$O"}
COL = {"pura": "#e41a1c", "nacl25": "#009e73", "nacl5": "#7b1fa2", "nacl10": "#e69f00"}
EST = {"pura": "-", "nacl25": (0, (8, 4)), "nacl5": (0, (6, 2, 1, 2, 1, 2)), "nacl10": (0, (1, 3))}
COLREF = {"pura": "Pure_H2O_counts_digitized", "nacl25": "NaCl_2p5_counts_digitized",
          "nacl5": "NaCl_5_counts_digitized", "nacl10": "NaCl_10_counts_digitized"}
REF6 = os.path.join(R, "datos", "fig6_sidelnik_digitalizada_700pts.csv")   # Fig. 6 de Sidelnik digitalizada (700 puntos)
ref = pd.read_csv(REF6)
# artefactos de la digitalizacion: la leyenda capturada (1590-1800) y el borde final en las curvas NaCl
for c in list(COLREF.values())[1:]:
    mal = ((ref.Numero_de_fotones.between(1590, 1800)) & (ref[c] > 40)) | (ref.Numero_de_fotones > 2470)
    ref.loc[mal, c] = np.nan
DATOS = os.environ.get("CORRIDAS_SIDELNIK", "")   # carpeta con las corridas (solo para separar los eventos con piones)
CARP = {"pura": "150000N-500MeV-Sidelnik-H2O-pura-sinSab-20261012-061022",
        "nacl25": ["42649N-parcial-500MeV-Sidelnik-H2O-2.5NaCl-sinSab-20261013", "107351N-500MeV-Sidelnik-H2O-2.5NaCl-sinSab-20261013-135213"]}
xb = np.arange(0, 2510, 10); xc = xb[:-1] + 5
estilo.aplicar()
fig, axs = plt.subplots(1, 2, figsize=(8, 6.0), sharey=True)
filas = []; PI = {}
for m in TODOS:
    axs[0].plot(ref.Numero_de_fotones, ref[COLREF[m]], color=COL[m], ls=EST[m], lw=1.8, label=ETQ[m])
for m in MED:
    a = aceptados_por_run(m)
    k = 150000 / len(a)        # corridas parciales: cuentas escaladas a 150000 neutrones, como en el articulo
    h = np.histogram(a[a >= 1], xb)[0] * k
    axs[1].plot(xc, np.where(h > 0, h, np.nan), color=COL[m], ls=EST[m], lw=1.8,
                label=f"MEIGA {ETQ[m]}" + ("" if k == 1 else f" (×{k:.2f})".replace(".", ",")))
    f = os.path.join(DATOS, CARP.get(m, "-") if isinstance(CARP.get(m, "-"), str) else "-", "Datos-simulacion", "secundarias-inelastica-neutron.tsv")
    if m == "pura" and os.path.exists(f):  # separa eventos con produccion de piones en una inelastica
        sec = pd.read_csv(f, sep="\t", skiprows=1, header=None, usecols=[0, 7], names=["run", "part"], on_bad_lines="skip")
        sec = sec[pd.to_numeric(sec.run, errors="coerce") < len(a)]; sec["run"] = sec.run.astype(int)
        pic = np.zeros(len(a), bool); pic[sec.run[sec.part.isin(["pi+", "pi-"])].unique()] = True
        pi0 = np.zeros(len(a), bool); pi0[sec.run[sec.part == "pi0"].unique()] = True
        pi = pic | pi0
        PI[m] = {"frac_eventos_con_piones": float(pi.mean()), "frac_con_pi_cargado": float(pic.mean()), "frac_con_pi0": float(pi0.mean()),
                 "frac_ge500_todos": float((a >= 500).mean()), "frac_ge500_sin_piones": float((a[~pi] >= 500).mean()),
                 "frac_ge500_con_piones_entre_ge500": float(pi[a >= 500].mean()), "media_aceptados_con_piones": float(a[pi].mean()),
                 "media_aceptados_sin_piones": float(a[~pi].mean()), "intervalos": []}
        for lo, hi in [(1, 100), (100, 500), (500, 1000), (1000, 2500), (2500, None)]:
            sl = (a >= lo) & (a < (hi or 10**9))
            PI[m]["intervalos"].append({"intervalo": f"{lo}-{hi}" if hi else f">={lo}", "n": int(sl.sum()),
                                        "pi_cargado": float(pic[sl].mean()), "pi0": float(pi0[sl].mean()), "algun_pion": float(pi[sl].mean())})
        np.savez(os.path.join(RES, f"piones_hist_{m}.npz"), con=np.histogram(a[pi & (a >= 1)], xb)[0], sin=np.histogram(a[~pi & (a >= 1)], xb)[0],
                 frac=pi.mean())
        filas.append({"medio": m, "intervalo": ">=500 con piones (%)", "MEIGA_cuentas": round(100 * pi[a >= 500].mean(), 1), "Sidelnik_cuentas": None, "cociente": None})
    fp = os.path.join(RES, f"piones_hist_{m}.npz")
    if os.path.exists(fp):                  # histogramas guardados: la figura no necesita las corridas
        P_ = np.load(fp)
        for key, nom, ls in [("con", "con piones", ":"), ("sin", "sin piones", "-.")]:
            fr = float(P_["frac"]) if key == "con" else 1 - float(P_["frac"])
            axs[1].plot(xc, np.where(P_[key] > 0, P_[key], np.nan), color="#555555", ls=ls, lw=1.2, label=f"{ETQ[m]}: eventos {nom} ({100 * fr:.1f} %)".replace(".", ","))
    if m == "pura":
        axs[1].plot(ref.Numero_de_fotones, ref[COLREF[m]], color="#0b0b0b", lw=1.0, alpha=0.6, label="Sidelnik, Pure H$_2$O")
    ok = ref[COLREF[m]].notna(); yr = np.interp(xc, ref.Numero_de_fotones[ok], ref[COLREF[m]][ok])   # sin los artefactos enmascarados
    for x0, x1 in [(0, 100), (100, 500), (500, 1000), (1000, 2500)]:
        s = (xc >= x0) & (xc < x1)
        filas.append({"medio": m, "intervalo": f"{x0}-{x1}", "MEIGA_cuentas": round(h[s].sum()),
                      "Sidelnik_cuentas": round(float(yr[s].sum())), "cociente": round(h[s].sum() / yr[s].sum(), 2)})
    filas.append({"medio": m, "intervalo": ">2500", "MEIGA_cuentas": round((a > 2500).sum() * k), "Sidelnik_cuentas": None, "cociente": None})
for a, t in zip(axs, ["(a) Sidelnik et al. (2020), Fig. 6", "(b) MEIGA (cuentas para 150 000 n)"]):
    a.set_yscale("log"); a.set_ylim(1, 1e5); a.set_xlim(0, 2500); a.set_title(t, fontsize=10.5)
    a.set_xlabel("Fotones aceptados por la QE"); a.grid(alpha=0.3)
axs[0].set_ylabel("Cuentas / 10 fotones")
from matplotlib.lines import Line2D
ETQ_ES = {"pura": "Agua pura", "nacl25": "Agua + 2,5 % NaCl", "nacl5": "Agua + 5 % NaCl", "nacl10": "Agua + 10 % NaCl"}
H_ = [Line2D([], [], color=COL[m], ls=EST[m], lw=2, label=ETQ_ES[m]) for m in TODOS]
H_ += [l for l in axs[1].get_lines() if l.get_label().startswith(("Pure", "Sidelnik"))]
for l in H_[len(TODOS):]:
    l.set_label(l.get_label().replace("Pure H$_2$O: eventos", "(b) agua pura, eventos").replace("Sidelnik, Pure H$_2$O", "(b) Sidelnik, agua pura"))
fig.legend(handles=H_, loc="lower center", ncol=2, frameon=False, columnspacing=1.5, handlelength=2.2)
fig.tight_layout(rect=(0, 0.2, 1, 1))
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig10_figura6_sidelnik_vs_meiga.{e}"), dpi=160)
if PI:                                   # sin las corridas se conserva el resultado guardado
    json.dump(PI, open(os.path.join(RES, "piones_cola.json"), "w"), indent=1)
t = pd.DataFrame(filas); t.to_csv(os.path.join(RES, "figura6_cuentas_por_intervalo.csv"), index=False); print(t.to_string(index=False))
