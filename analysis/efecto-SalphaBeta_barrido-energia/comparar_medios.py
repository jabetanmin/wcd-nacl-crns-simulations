#!/usr/bin/env python3
"""Comparacion entre medios detectores del barrido con y sin S(alpha,beta).

Lee salida/<MEDIO>/{resumen_barrido,resumen_em}.tsv y salida/<MEDIO>/em_eventos.tsv de los medios
disponibles y produce en salida/comparacion/:
  fig_comparacion_medios.{png,pdf}  (a) captura en el agua, (b) eficiencia de deteccion,
                                    (c) efecto de S(alpha,beta) sobre la captura y
                                    (d) carga media de los eventos detectados
  fig_captura_por_nucleo.{png,pdf}  fraccion de las capturas en el agua por nucleo
  comparacion_medios.tsv            cifras por medio, energia y fisica
  cruces.tsv                        energia de cruce del efecto de S(alpha,beta)
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from figuras_barrido import TINTA, TINTA_2, eje_energia

BASE = Path(__file__).resolve().parent / "salida"
OUT = BASE / "comparacion"
MEDIOS = {"AguaPura": ("Agua pura", "#d62728"), "Agua25NaCl": ("Agua + 2.5 % NaCl", "#2ca02c"),
          "Agua5NaCl": ("Agua + 5 % NaCl", "#8e44ad"), "Agua10NaCl": ("Agua + 10 % NaCl", "#f39c12")}
FIS = {"QGSP_BERT_HP": ("con S(α,β)", "-", "o"), "QGSP_BERT_HP_NoThermal": ("sin S(α,β)", "--", "s")}


def leer_tsv(p):
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def cruce(E, d):
    """Energia (interpolacion logaritmica) donde d = con - sin pasa de negativo a positivo."""
    for i in range(len(d) - 1):
        if d[i] < 0 <= d[i + 1]:
            return math.exp(math.log(E[i]) + (-d[i]) / (d[i + 1] - d[i]) * math.log(E[i + 1] / E[i]))
    return float("nan")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    medios = [m for m in MEDIOS if (BASE / m / "resumen_em.tsv").exists()]
    datos, nucleos = {}, {}
    for m in medios:
        b = {(float(r["energia_eV"]), r["fisica"]): r for r in leer_tsv(BASE / m / "resumen_barrido.tsv")}
        e = {(float(r["energia_eV"]), r["fisica"]): r for r in leer_tsv(BASE / m / "resumen_em.tsv")}
        datos[m] = {k: {**b[k], **e[k]} for k in b}
        cuenta = defaultdict(lambda: defaultdict(int))
        for r in leer_tsv(BASE / m / "em_eventos.tsv"):
            if r["destino"] == "captura_agua":
                cuenta[(float(r["energia_eV"]), r["fisica"])][r["nucleo"]] += 1
        nucleos[m] = cuenta

    fig, axs = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
    filas, cruces = [], []
    for m in medios:
        nombre, color = MEDIOS[m]
        for f, (et, ls, mk) in FIS.items():
            ks = sorted(k for k in datos[m] if k[1] == f)
            E = [k[0] for k in ks]
            cap = [float(datos[m][k]["captura_agua_pct"]) for k in ks]
            cerr = [float(datos[m][k]["captura_agua_err_pct"]) for k in ks]
            ef = [float(datos[m][k]["eficiencia_Q1_pct"]) for k in ks]
            eerr = [float(datos[m][k]["eficiencia_Q1_err_pct"]) for k in ks]
            q = [float(datos[m][k]["carga_media_detectados_pe"]) for k in ks]
            kw = dict(color=color, linestyle=ls, marker=mk, markersize=4, linewidth=1.6, capsize=2,
                      markeredgecolor="white", markeredgewidth=0.6, label=f"{nombre}, {et}")
            axs[0, 0].errorbar(E, cap, yerr=cerr, **kw)
            axs[0, 1].errorbar(E, ef, yerr=eerr, **kw)
            axs[1, 1].plot(E, q, **{k: v for k, v in kw.items() if k != "capsize"})
            for k, a, b_, c in zip(ks, cap, ef, q):
                n = nucleos[m][k]
                tot = sum(n.values())
                filas.append({"medio": m, "energia_eV": k[0], "fisica": f, "captura_agua_pct": a,
                              "eficiencia_Q1_pct": b_, "carga_media_detectados_pe": c,
                              **{f"fraccion_{nu}_pct": round(100 * n[nu] / tot, 2) for nu in ("H", "Cl35", "Cl37", "Na23", "O")}})
        con = {k[0]: datos[m][k] for k in datos[m] if k[1] == "QGSP_BERT_HP"}
        sin = {k[0]: datos[m][k] for k in datos[m] if k[1] == "QGSP_BERT_HP_NoThermal"}
        E = sorted(con)
        d = [float(con[x]["captura_agua_pct"]) - float(sin[x]["captura_agua_pct"]) for x in E]
        derr = [math.hypot(float(con[x]["captura_agua_err_pct"]), float(sin[x]["captura_agua_err_pct"])) for x in E]
        de = [float(con[x]["eficiencia_Q1_pct"]) - float(sin[x]["eficiencia_Q1_pct"]) for x in E]
        axs[1, 0].errorbar(E, d, yerr=derr, color=color, marker="o", markersize=4, linewidth=1.6, capsize=2,
                           markeredgecolor="white", markeredgewidth=0.6, label=nombre)
        cruces.append({"medio": m, "cruce_captura_eV": round(cruce(E, d), 3), "cruce_eficiencia_eV": round(cruce(E, de), 3)})
    axs[1, 0].axhline(0, color=TINTA_2, linewidth=0.8)
    titulos = ["(a) Captura en el agua", "(b) Eficiencia de detección (Q ≥ 1 pe)",
               "(c) Efecto de S(α,β) sobre la captura (con − sin)", "(d) Carga media de los eventos detectados"]
    ylab = ["Neutrones capturados en el agua (%)", "Neutrones detectados (%)", "Diferencia (puntos porcentuales)",
            "Carga media (pe)"]
    for ax, t, y in zip(axs.flat, titulos, ylab):
        eje_energia(ax)
        ax.set_title(t, loc="left", fontsize=10.5, color=TINTA)
        ax.set_ylabel(y)
    axs[0, 0].legend(fontsize=8, ncol=1)
    axs[1, 0].legend(fontsize=8)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"fig_comparacion_medios.{ext}", bbox_inches="tight")
    plt.close(fig)

    # Fraccion de las capturas en el agua por nucleo (medios con NaCl)
    salinos = [m for m in medios if m != "AguaPura"]
    if salinos:
        fig, ax = plt.subplots(figsize=(7.5, 4.6), constrained_layout=True)
        for m in salinos:
            nombre, color = MEDIOS[m]
            for f, (et, ls, mk) in FIS.items():
                ks = sorted(k for k in nucleos[m] if k[1] == f)
                fr = [100 * nucleos[m][k]["Cl35"] / sum(nucleos[m][k].values()) for k in ks]
                ax.plot([k[0] for k in ks], fr, color=color, linestyle=ls, marker=mk, markersize=4,
                        label=f"{nombre}, {et}")
        eje_energia(ax)
        ax.set_ylim(0, 100)
        ax.set_ylabel("Capturas en el agua en $^{35}$Cl (%)")
        ax.legend(fontsize=8)
        for ext in ("png", "pdf"):
            fig.savefig(OUT / f"fig_captura_por_nucleo.{ext}", bbox_inches="tight")
        plt.close(fig)

    with open(OUT / "comparacion_medios.tsv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]), delimiter="\t")
        w.writeheader()
        w.writerows(filas)
    with open(OUT / "cruces.tsv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cruces[0]), delimiter="\t")
        w.writeheader()
        w.writerows(cruces)
    for c in cruces:
        print(c)


if __name__ == "__main__":
    main()
