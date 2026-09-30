"""Razones de mejora de la señal (Tabla tab:signal_comparison) reconstruidas desde los datos crudos.

Lee las cargas por pulso que produce extraer_eventos.sh (ev_<medio>_<toma>.tsv, res_<medio>_<toma>.tsv)
y calcula, para 2.5 % y 10 % de NaCl, la señal neta relativa al agua pura con varias definiciones:

  cuentas netas        N_fuente - N_fondo              (con y sin normalizar por el tiempo)
  carga neta           suma Q_fuente - suma Q_fondo    (con y sin normalizar por el tiempo)
  cuentas sobre umbral cuentas netas con Q >= umbral, barriendo el umbral

La incertidumbre es la de Poisson de las cuentas, propagada a la razón (para la carga se usa la
varianza sum Q^2). Salidas: razones.tsv, razones_umbral.tsv y fig_razones_umbral.{pdf,png}.

Uso: python3 calcular_razones.py <carpeta con ev_*.tsv y res_*.tsv>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

CARPETA = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
MEDIOS = ["pura", "2.5", "10"]
DOPADOS = {"2.5": "2.5 % NaCl", "10": "10 % NaCl"}
TESIS = {"2.5": (11.2, 0.1, 13.2), "10": (35.6, 0.2, 31.8)}   # experimental, error, simulado
CARGAS = ["carga_figura", "carga_ventana", "carga_pretrig"]
COLOR = {"2.5": "#2a78d6", "10": "#eb6834"}

q, t = {}, {}
for m in MEDIOS:
    for k in ["neutrones", "fondo"]:
        t[m, k] = pd.read_csv(CARPETA / f"res_{m}_{k}.tsv", sep="\t").tiempo_s[0]
        q[m, k] = pd.read_csv(CARPETA / f"ev_{m}_{k}.tsv", sep="\t")


def neto(m, x, por_tiempo):
    """Señal neta y su varianza. x(df) -> (valor, varianza) de la toma."""
    (vn, sn), (vf, sf) = x(q[m, "neutrones"]), x(q[m, "fondo"])
    tn, tf = (t[m, "neutrones"], t[m, "fondo"]) if por_tiempo else (1, 1)
    return vn / tn - vf / tf, sn / tn**2 + sf / tf**2


def razones(x, por_tiempo):
    s0, v0 = neto("pura", x, por_tiempo)
    fila = {}
    for m in DOPADOS:
        s, v = neto(m, x, por_tiempo)
        r = s / s0
        fila[m] = (r, abs(r) * np.sqrt(v / s**2 + v0 / s0**2))
    return fila


def cuentas(umbral=-np.inf, col="carga_figura"):
    def f(df):
        n = int((df[col] >= umbral).sum())
        return n, n
    return f


def carga(col):
    def f(df):
        c = df[col].clip(lower=0)
        return c.sum(), (c**2).sum()
    return f


# ---------------------------------------------------------------- definiciones directas
filas = []
for tiempo in (False, True):
    norma = "por segundo" if tiempo else "sin normalizar por el tiempo"
    defs = [("cuentas netas (todos los disparos)", cuentas(col="carga_figura"))]
    defs += [(f"carga neta ({c})", carga(c)) for c in CARGAS]
    for nombre, x in defs:
        r = razones(x, tiempo)
        filas.append({"definicion": nombre, "normalizacion": norma,
                      "razon_2.5": r["2.5"][0], "error_2.5": r["2.5"][1],
                      "razon_10": r["10"][0], "error_10": r["10"][1]})
tab = pd.DataFrame(filas)
tab.to_csv("razones.tsv", sep="\t", index=False, float_format="%.3f")

tiempos = pd.DataFrame([{"medio": m, "toma": k, "eventos": len(q[m, k]), "tiempo_s": t[m, k],
                         "tasa_Hz": len(q[m, k]) / t[m, k]} for m in MEDIOS for k in ["neutrones", "fondo"]])
tiempos.to_csv("tiempos_adquisicion.tsv", sep="\t", index=False, float_format="%.2f")

# ---------------------------------------------------------------- barrido en umbral
umbrales = np.unique(np.round(np.logspace(np.log10(1500), np.log10(60000), 80), -1))
barr = []
for col in CARGAS:
    for tiempo in (False, True):
        for u in umbrales:
            s0, _ = neto("pura", cuentas(u, col), False)
            if s0 < 100:          # exceso de agua pura demasiado pequeño para una razón estable
                continue
            r = razones(cuentas(u, col), tiempo)
            barr.append({"carga": col, "por_segundo": int(tiempo), "umbral_ADC": u, "neto_pura": s0,
                         "razon_2.5": r["2.5"][0], "error_2.5": r["2.5"][1],
                         "razon_10": r["10"][0], "error_10": r["10"][1]})
barr = pd.DataFrame(barr)
barr.to_csv("razones_umbral.tsv", sep="\t", index=False, float_format="%.3f")

# Distancia a los valores de la tesis: ¿existe un umbral común que dé ambos?
barr["dist"] = (abs(barr["razon_2.5"] - 11.2) / 11.2 + abs(barr["razon_10"] - 35.6) / 35.6)
mejor = barr.loc[barr.groupby(["carga", "por_segundo"]).dist.idxmin()]

pd.set_option("display.width", 160)
print(tiempos.to_string(index=False), "\n")
print(tab.to_string(index=False, float_format=lambda v: f"{v:.3f}"), "\n")
print("Umbral más cercano a (11.2, 35.6) para cada definición:")
print(mejor.drop(columns="neto_pura").to_string(index=False, float_format=lambda v: f"{v:.2f}"))

# ---------------------------------------------------------------- figura
fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True, constrained_layout=True)
for ax, tiempo in zip(axs, (1, 0)):
    b = barr[(barr.carga == "carga_figura") & (barr.por_segundo == tiempo)]
    for m, et in DOPADOS.items():
        ax.fill_between(b.umbral_ADC, b[f"razon_{m}"] - b[f"error_{m}"], b[f"razon_{m}"] + b[f"error_{m}"],
                        color=COLOR[m], alpha=0.2, lw=0)
        ax.plot(b.umbral_ADC, b[f"razon_{m}"], color=COLOR[m], lw=2, label=f"{et} (datos crudos)")
        ax.axhline(TESIS[m][0], color=COLOR[m], lw=1.2, ls="--", label=f"{et}: tesis {TESIS[m][0]}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(umbrales[0], umbrales[-1])
    ax.set_ylim(1, 100)
    ax.set_xlabel("Umbral de carga [ADC]")
    ax.set_title("Cuentas netas por segundo" if tiempo else "Cuentas netas sin normalizar por el tiempo",
                 fontsize=11)
    ax.grid(True, which="major", alpha=0.25)
axs[0].set_ylabel("Razón respecto al agua pura")
axs[0].legend(fontsize=8.5, loc="upper left")
fig.savefig("fig_razones_umbral.pdf")
fig.savefig("fig_razones_umbral.png", dpi=200)
