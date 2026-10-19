#!/usr/bin/env python3
"""Diagnostico del Tyvek (agua pura): (a) probabilidad de absorcion por choque con la pared segun la energia del foton,
frente a la reflectividad del codigo de MEIGA y a valores de la literatura; (b) espectro de los fotones transportados
que se absorben en la pared; (c) carga media estimada para otras reflectividades y longitudes de absorcion del agua.
Lee resultados/sensibilidad_tyvek_<medio>.json (sensibilidad_tyvek.py) y, si existe, <medio>_fotones.npz (destino_fotones.py);
el espectro de (b) se guarda en resultados/tyvek_espectro_<medio>.json para regenerar la figura sin el archivo grande.
Escribe figuras/fig08_tyvek_diagnostico.{png,pdf}. Uso: tyvek_diagnostico.py [medio]"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
m = sys.argv[1] if len(sys.argv) > 1 else "pura"
S = json.load(open(os.path.join(RES, f"sensibilidad_tyvek_{m}.json")))
# reflectividad relativa del Tyvek en el codigo (linerReflectivity); en MEIGA se multiplica por scaleLinerRef = 0,94
Eg = np.array([2.08,2.16,2.19,2.23,2.27,2.32,2.36,2.41,2.46,2.50,2.56,2.61,2.67,2.72,2.79,2.85,2.92,2.99,3.06,3.14,3.22,3.31,3.40,3.49,3.59,3.70,3.81,3.94,4.07,4.20])
Rt = np.array([0.9957,0.9953,0.9948,0.9942,0.9939,0.9937,0.9937,0.9940,0.9945,0.9954,0.9964,0.9975,0.9985,0.9993,1.0,1.0,0.9993,0.9977,0.9948,0.9903,0.9840,0.9753,0.9642,0.9500,0.9334,0.9108,0.8849,0.8541,0.8178,0.7755])
fe = os.path.join(RES, f"tyvek_espectro_{m}.json"); fz = os.path.join(RES, f"{m}_fotones.npz")
if os.path.exists(fz):
    z = np.load(fz); b = np.arange(2.0, 4.31, 0.1)
    pared = (z["dest"] == 2) | (z["dest"] == 3)
    esp = {"bordes_eV": b.tolist(), "pared": np.histogram(z["E"][pared], b)[0].tolist(), "otros": np.histogram(z["E"][~pared], b)[0].tolist()}
    json.dump(esp, open(fe, "w"))
esp = json.load(open(fe))
estilo.aplicar()
fig, axs = estilo.tres_paneles(9.0)
a = axs[0]; E = np.array([f["E"] for f in S["por_energia"]]); A = np.array([f["a"] for f in S["por_energia"]])
a.plot(E, 100 * A, "o-", color="#e34948", ms=4, label="MEIGA: medida por choque")
a.plot(Eg, 100 * (1 - 0.94 * Rt), "-", color="#eb6834", label="código: 1 − 0,94·R(E)")
a.plot(Eg, 100 * (1 - Rt), "--", color="#2a78d6", label="tabla sin 0,94: 1 − R(E)")
for v, c, et in [(0.940, "#8a8984", "Auger (R = 0,940)"), (0.973, "#4a3aa7", "Auger alt. (0,973)"), (0.985, "#1baf7a", "LHAASO (0,985)")]:
    a.axhline(100 * (1 - v), ls=":", color=c, label=et)
a.set_xlabel("Energía del fotón [eV]"); a.set_ylabel("Absorción por choque [%]"); a.set_ylim(-1, 62); a.legend(fontsize=8.5, loc="upper left", ncol=1, handlelength=1.6)
a.set_title("(a) Absorción del Tyvek por choque", fontsize=10.5)
a = axs[1]; b = np.array(esp["bordes_eV"]); c = 0.5 * (b[1:] + b[:-1]); w = np.diff(b)
pa, ot = np.array(esp["pared"]) / 1e6, np.array(esp["otros"]) / 1e6
a.bar(c, pa, w * 0.9, color="#eb6834", label="absorbidos en la pared"); a.bar(c, ot, w * 0.9, bottom=pa, color="#c3c2b7", label="otros destinos"); a.set_ylim(0, 1.3 * (pa + ot).max())
a.set_xlabel("Energía del fotón [eV]"); a.set_ylabel("Fotones transportados [millones]"); a.legend(fontsize=8.5, loc="upper right")
a.set_title("(b) Fotones absorbidos por el Tyvek", fontsize=10.5)
a = axs[2]; ce = S["carga_media_estimada"]; ks = list(ce)
a.barh(range(len(ks)), [ce[k] for k in ks], color=["#e34948"] + ["#2a78d6"] * (len(ks) - 1))
for i, k in enumerate(ks):
    a.text(ce[k] + 0.3, i, f"{ce[k]:.1f}".replace(".", ","), va="center", fontsize=9)
a.set_yticks(range(len(ks))); a.set_yticklabels(ks, fontsize=9); a.invert_yaxis()
a.set_xlabel("Carga media estimada [p.e. por neutrón]"); a.set_title("(c) Carga según el Tyvek y la longitud de absorción del agua", fontsize=10.5)
a.set_xlim(0, 1.15 * max(ce.values()))
fig.tight_layout()
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig08_tyvek_diagnostico.{e}"))
print("fig08 ok")
