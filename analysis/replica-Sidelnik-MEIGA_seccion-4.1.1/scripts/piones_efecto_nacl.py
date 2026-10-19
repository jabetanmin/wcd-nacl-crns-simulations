#!/usr/bin/env python3
"""Efecto del NaCl en la Fig. 6 con y sin los eventos con produccion de piones.
Marca cada neutron (run_id) cuyo arbol tiene una inelastica de neutron que produce pi+, pi- o pi0
(secundarias-inelastica-neutron.tsv de cada corrida) y recalcula el aumento de cuentas entre 100 y 500
fotones aceptados por la QE respecto al agua pura. Lee resultados/<m>_aceptados_por_run.npy.
Uso: piones_efecto_nacl.py   (ruta de las corridas en CORRIDAS_SIDELNIK)
Escribe resultados/piones_por_run_<m>.npy, resultados/piones_efecto_nacl.json y figuras/fig24_piones_efecto_nacl."""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
C = os.environ.get("CORRIDAS_SIDELNIK", "/media/ubuntu/ADATA HD330/Corridas-Sidelnik-500MeV")
CARP = {"pura": ["150000N-500MeV-Sidelnik-H2O-pura-sinSab-20261012-061022"],
        "nacl25": ["42649N-parcial-500MeV-Sidelnik-H2O-2.5NaCl-sinSab-20261013", "107351N-500MeV-Sidelnik-H2O-2.5NaCl-sinSab-20261013-135213"],
        "nacl5": ["150000N-500MeV-Sidelnik-H2O-5NaCl-sinSab-20261014-065724"],
        "nacl10": ["150000N-500MeV-Sidelnik-H2O-10NaCl-sinSab-20261015-081303"]}
SID = {"nacl25": 52.9, "nacl5": 66.9, "nacl10": 53.9}           # aumento 100-500 fotones en la Fig. 6 digitalizada [%]
ETQ = {"pura": "Agua pura", "nacl25": "Agua + 2,5 % NaCl", "nacl5": "Agua + 5 % NaCl", "nacl10": "Agua + 10 % NaCl"}
COL = {"pura": "#e34948", "nacl25": "#1baf7a", "nacl5": "#7b1fa2", "nacl10": "#eda100"}


def piones(m, N):
    f = os.path.join(RES, f"piones_por_run_{m}.npy")
    if os.path.exists(f):
        return np.load(f)
    pi = np.zeros(N, bool); off = 0
    for carpeta in CARP[m]:
        d = os.path.join(C, carpeta, "Datos-simulacion")
        d = d if os.path.isdir(d) else os.path.join(C, carpeta)        # tramo copiado sin subcarpeta
        ncomp = sum(1 for l in open(os.path.join(d, "Carga-total.txt")) if len(l.split()) >= 2 and l.endswith("\n"))
        sec = pd.read_csv(os.path.join(d, "secundarias-inelastica-neutron.tsv"), sep="\t", skiprows=1, header=None,
                          usecols=[0, 7], names=["run", "part"], on_bad_lines="skip")
        sec["run"] = pd.to_numeric(sec.run, errors="coerce"); sec = sec[sec.run < ncomp]
        r = sec.run[sec.part.isin(["pi+", "pi-", "pi0"])].astype(int).unique() + off
        pi[r[r < N]] = True; off += ncomp
    np.save(f, pi)
    return pi


A, P = {}, {}
for m in CARP:
    A[m] = np.load(os.path.join(RES, f"{m}_aceptados_por_run.npy")); P[m] = piones(m, len(A[m]))
    print(m, len(A[m]), "eventos con piones:", round(100 * P[m].mean(), 2), "%")
cnt = lambda a, s: int(((a >= 100) & (a < 500) & s).sum())
out = {"medios": {}}
for m in CARP:
    a, pi = A[m], P[m]
    out["medios"][m] = {"frac_eventos_con_piones": float(pi.mean()), "cuentas_100_500_todos": cnt(a, np.ones_like(pi)),
                        "cuentas_100_500_sin_piones": cnt(a, ~pi), "cuentas_100_500_con_piones": cnt(a, pi)}
o0 = out["medios"]["pura"]
for m in ("nacl25", "nacl5", "nacl10"):
    o = out["medios"][m]
    o["aumento_todos_pct"] = 100 * (o["cuentas_100_500_todos"] / o0["cuentas_100_500_todos"] - 1)
    o["aumento_sin_piones_pct"] = 100 * (o["cuentas_100_500_sin_piones"] / o0["cuentas_100_500_sin_piones"] - 1)
    o["aumento_Sidelnik_pct"] = SID[m]
    o["excedente_NaCl"] = o["cuentas_100_500_todos"] - o0["cuentas_100_500_todos"]
    o["excedente_NaCl_sin_piones"] = o["cuentas_100_500_sin_piones"] - o0["cuentas_100_500_sin_piones"]
json.dump(out, open(os.path.join(RES, "piones_efecto_nacl.json"), "w"), indent=1)
print(json.dumps(out, indent=1))

estilo.aplicar()
fig, axs = plt.subplots(1, 2, figsize=(8, 4.4))
xb = np.arange(0, 1010, 20); xc = 0.5 * (xb[1:] + xb[:-1])
for m in ("nacl25", "nacl5", "nacl10"):
    for sel, ls, lw in [(None, "-", 1.8), ("sin", "--", 1.4)]:
        h = lambda mm: np.histogram(A[mm][(A[mm] >= 1) & (~P[mm] if sel else True)], xb)[0].astype(float)
        r_ = h(m) / np.maximum(h("pura"), 1)
        if sel:
            r_[xc > 520] = np.nan      # sin piones el agua pura casi no tiene eventos por encima de ~550 fotones
        axs[0].plot(xc, r_, ls=ls, lw=lw, color=COL[m])
axs[0].axhline(1, color="k", lw=0.8); axs[0].set_xlabel("Fotones aceptados por la QE"); axs[0].set_ylabel("NaCl / agua pura")
axs[0].set_title("(a) Razón: todos (continua) y sin eventos\ncon piones (discontinua, hasta 520 fotones)", fontsize=10.5); axs[0].set_yscale("log"); axs[0].set_ylim(0.5, 25)
axs[0].set_yticks([0.5, 1, 2, 5, 10, 20]); axs[0].set_yticklabels(["0,5", "1", "2", "5", "10", "20"]); axs[0].minorticks_off()
ms = ["nacl25", "nacl5", "nacl10"]; x = np.arange(3); w = 0.27
for i, (k, nom, col) in enumerate([("aumento_todos_pct", "MEIGA, todos", "#8a8984"), ("aumento_sin_piones_pct", "MEIGA, sin piones", "#2a78d6"),
                                    ("aumento_Sidelnik_pct", "Sidelnik, Fig. 6", "#0b0b0b")]):
    v = [out["medios"][m][k] for m in ms]
    axs[1].bar(x + (i - 1) * w, v, w, color=col, label=nom)
    for xx, vv in zip(x + (i - 1) * w, v):
        axs[1].text(xx, vv + 1.5, f"{vv:.0f}", ha="center", fontsize=10.5)
axs[1].set_xticks(x); axs[1].set_xticklabels(["2,5 %", "5 %", "10 %"]); axs[1].set_ylabel("Aumento 100–500 fotones [%]")
axs[1].set_ylim(0, 1.55 * max(max(out["medios"][m][k] for m in ms) for k in ("aumento_todos_pct", "aumento_sin_piones_pct", "aumento_Sidelnik_pct")))
axs[1].legend(loc="upper left", fontsize=10); axs[1].set_title("(b) Aumento de cuentas respecto\nal agua pura", fontsize=10.5)
estilo.leyenda_medios(fig, ms, COL, ETQ, ncol=3)
fig.tight_layout(rect=(0, 0.08, 1, 1))
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig24_piones_efecto_nacl.{e}"))
