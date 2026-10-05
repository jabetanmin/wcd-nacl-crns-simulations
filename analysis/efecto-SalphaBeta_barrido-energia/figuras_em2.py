#!/usr/bin/env python3
"""Analisis 7, 8 y 9 del barrido: procesos gamma, electrones secundarios, luz Cherenkov y carga.

Lee em_procesos.tsv, em_electrones.tsv y em_luz.tsv (em_cadena.sh) y em_eventos.tsv (em_detalle.sh):
  fig_procesos_luz.{png,pdf}         interacciones gamma por proceso y material, y origen de la luz
  fig_electrones_cherenkov.{png,pdf} espectro de los electrones Compton y fotones por electron
  fig_luz_carga.{png,pdf}            fotones por evento, probabilidad de senal y espectro de carga
  resumen_em2.tsv                    cifras principales
"""
import csv
import math
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from figuras_barrido import FISICAS, TINTA, TINTA_2, AQUI

UMBRAL_CHERENKOV_MEV = 0.264   # agua, n = 1.33: T = m_e (1/sqrt(1 - 1/n^2) - 1)
BARRA = "#2a78d6"               # un solo color: las barras no codifican identidad
ORIGEN = {"captura_agua": ("#1baf7a", "Captura en agua (H)"),
          "captura_estructura": ("#eda100", "Captura en acero")}
NOMBRE_MAT = {"Water_TS_H_of_Water": "agua", "SaltyWater_NaCl_2.5pct": "agua", "SaltyWater_NaCl_5.0pct": "agua",
              "SaltyWater_NaCl_10.0pct": "agua", "G4_STAINLESS-STEEL": "acero", "Tyvek_HDPE": "Tyvek",
              "Air": "aire", "Pyrex": "Pyrex"}
NOMBRE_PROC = {"compt": "Compton", "phot": "Fotoeléctrico", "Rayl": "Rayleigh", "conv": "Pares"}


def nombre_mat(m):
    return NOMBRE_MAT.get(m, m)


def figura_procesos_luz(proc, fuentes):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 3.9), gridspec_kw={"wspace": 0.55})
    for ax, datos, titulo in ((ax1, proc, "a) Interacciones de los gammas"),
                              (ax2, fuentes, "b) Origen de la luz Cherenkov")):
        items = sorted(datos.items(), key=lambda x: x[1])
        total = sum(v for _, v in items)
        items = [(k, 100 * v / total) for k, v in items if 100 * v / total >= 0.3]
        y = range(len(items))
        ax.barh(y, [v for _, v in items], color=BARRA, height=0.62, zorder=3)
        ax.set_yticks(list(y), [k for k, _ in items], fontsize=9)
        for yi, (_, v) in zip(y, items):
            ax.annotate(f"{v:.1f} %", xy=(v, yi), xytext=(4, 0), textcoords="offset points",
                        va="center", fontsize=8.5, color=TINTA)
        ax.set_xlim(0, 110)
        ax.set_xlabel("Porcentaje")
        ax.grid(axis="y", visible=False)
        ax.set_title(titulo, loc="left", fontsize=10, color=TINTA)
    fig.text(0.01, -0.04, "Todas las corridas y ambas físicas juntas (las proporciones coinciden entre físicas "
             "a 0.1 %). Se omiten categorías por debajo del 0.3 %.", fontsize=7.5, color=TINTA_2)
    for ext in ("png", "pdf"):
        fig.savefig(AQUI / f"fig_procesos_luz.{ext}", bbox_inches="tight")
    plt.close(fig)


def figura_electrones(esp, rend):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.0), gridspec_kw={"wspace": 0.3})
    bordes = [i * 0.05 for i in range(0, 45)]  # 0 a 2.2 MeV
    for f, estilo in FISICAS.items():
        t = esp[f]
        cuentas = [0] * (len(bordes) - 1)
        for x in t:
            if x < bordes[-1]:
                cuentas[int(x / 0.05)] += 1
        ax1.stairs([c / len(t) for c in cuentas], bordes, color=estilo["color"], linewidth=2,
                   label=estilo["etiqueta"].split(" (")[0])
    ax1.set_yscale("log")
    ax1.set_xlim(0, 2.2)
    ax1.axvline(UMBRAL_CHERENKOV_MEV, color=TINTA_2, linewidth=0.9, linestyle="--")
    frac = {f: 100 * sum(1 for x in esp[f] if x > UMBRAL_CHERENKOV_MEV) / len(esp[f]) for f in FISICAS}
    ax1.annotate(f"umbral Cherenkov 0.264 MeV\n{frac['QGSP_BERT_HP']:.1f} % por encima (con S(α,β))\n"
                 f"{frac['QGSP_BERT_HP_NoThermal']:.1f} % por encima (sin S(α,β))",
                 xy=(UMBRAL_CHERENKOV_MEV, 2e-4), xytext=(6, 0), textcoords="offset points",
                 fontsize=8, color=TINTA_2, va="bottom")
    ax1.set_xlabel("Energía cinética inicial del electrón (MeV)")
    ax1.set_ylabel("Fracción de electrones por 0.05 MeV")
    ax1.set_title("a) Electrones Compton creados en el agua", loc="left", fontsize=10, color=TINTA)
    ax1.legend(loc="upper right", fontsize=8.5)
    for f, estilo in FISICAS.items():
        xs, ys = [], []
        for b in sorted(rend[f]):
            n, s = rend[f][b]
            if n >= 30:
                xs.append((b + 0.5) * 0.1)
                ys.append(s / n)
        ax2.plot(xs, ys, color=estilo["color"], marker=estilo["marker"], markersize=4, linewidth=2,
                 markeredgecolor="white", markeredgewidth=0.6, label=estilo["etiqueta"].split(" (")[0])
    ax2.axvline(UMBRAL_CHERENKOV_MEV, color=TINTA_2, linewidth=0.9, linestyle="--")
    ax2.set_xlim(0, 2.2)
    ax2.set_ylim(0, 320)  # los electrones de los gammas del acero (> 2.2 MeV) quedan fuera del rango
    ax2.set_xlabel("Energía cinética inicial del electrón (MeV)")
    ax2.set_ylabel("Fotones Cherenkov por electrón")
    ax2.set_title("b) Luz emitida según la energía del electrón", loc="left", fontsize=10, color=TINTA)
    ax2.legend(loc="upper left", fontsize=8.5)
    fig.text(0.01, -0.04, "Electrones creados por efecto Compton en el agua, todas las corridas. b): media en "
             "intervalos de 0.1 MeV con al menos 30 electrones; incluye la luz de sus rayos delta.",
             fontsize=7.5, color=TINTA_2)
    for ext in ("png", "pdf"):
        fig.savefig(AQUI / f"fig_electrones_cherenkov.{ext}", bbox_inches="tight")
    plt.close(fig)


def figura_luz_carga(fot, prob, carga, eficiencia):
    fig, axs = plt.subplots(1, 3, figsize=(12.0, 3.9), gridspec_kw={"wspace": 0.32})
    # a) fotones Cherenkov por evento (eventos con luz)
    bordes = [10 ** (i / 10) for i in range(0, 36)]  # 1 a ~3000
    for d, (col, etiq) in ORIGEN.items():
        v = [x for x in fot[d] if x > 0]
        cuentas = [0] * (len(bordes) - 1)
        for x in v:
            i = int(10 * math.log10(x))
            if i < len(cuentas):
                cuentas[i] += 1
        axs[0].stairs([c / len(v) for c in cuentas], bordes, color=col, linewidth=2,
                      label=f"{etiq}: mediana {sorted(v)[len(v) // 2]}")
    axs[0].set_xscale("log")
    axs[0].set_xlabel("Fotones Cherenkov creados por evento")
    axs[0].set_ylabel("Fracción de eventos con luz")
    axs[0].set_title("a) Luz creada por neutrón capturado", loc="left", fontsize=10, color=TINTA)
    axs[0].set_ylim(0, 0.27)
    axs[0].legend(loc="upper left", fontsize=7.5)
    # b) probabilidad de senal frente a fotones creados, con el modelo de Poisson
    xs, ys, es = [], [], []
    for b in sorted(prob):
        n, k = prob[b]
        if n >= 30:
            p = k / n
            xs.append(10 ** ((b + 0.5) / 10))
            ys.append(100 * p)
            es.append(100 * math.sqrt(p * (1 - p) / n))
    axs[1].errorbar(xs, ys, yerr=es, color=TINTA, marker="o", markersize=4, linestyle="none",
                    capsize=2, elinewidth=1, label="simulación")
    xm = [10 ** (i / 20) for i in range(0, 72)]
    axs[1].plot(xm, [100 * (1 - math.exp(-eficiencia * x)) for x in xm], color=TINTA_2, linewidth=1.2,
                linestyle="--", label=f"Poisson, ε = {eficiencia * 100:.2f} %")
    axs[1].set_xscale("log")
    axs[1].set_ylim(0, 105)
    axs[1].set_xlabel("Fotones Cherenkov creados en el evento, N")
    axs[1].set_ylabel("Eventos con señal, Q ≥ 1 pe (%)")
    axs[1].set_title("b) Probabilidad de señal", loc="left", fontsize=10, color=TINTA)
    axs[1].legend(loc="upper left", fontsize=7.5)
    # c) espectro de carga de los eventos con senal
    for d, (col, etiq) in ORIGEN.items():
        v = [q for q in carga[d] if q >= 1]
        qmax = 30
        cuentas = [0] * qmax
        for q in v:
            cuentas[min(q, qmax) - 1] += 1
        axs[2].stairs([c / len(v) for c in cuentas], [q + 0.5 for q in range(0, qmax + 1)], color=col,
                      linewidth=2, label=f"{etiq}: media {sum(v) / len(v):.1f} pe")
    axs[2].set_yscale("log")
    axs[2].set_xlim(0.5, 30.5)
    axs[2].set_xlabel("Carga Q (fotoelectrones)")
    axs[2].set_ylabel("Fracción de eventos con señal")
    axs[2].set_title("c) Espectro de carga", loc="left", fontsize=10, color=TINTA)
    axs[2].set_ylim(2e-5, 3)
    axs[2].legend(loc="upper right", fontsize=7.5)
    fig.text(0.01, -0.05, "Todas las corridas y ambas físicas juntas. El último intervalo de c) reúne Q ≥ 30 pe. "
             "Los fotones se cuentan al crearse, antes de la eficiencia cuántica del PMT.",
             fontsize=7.5, color=TINTA_2)
    for ext in ("png", "pdf"):
        fig.savefig(AQUI / f"fig_luz_carga.{ext}", bbox_inches="tight")
    plt.close(fig)


def main():
    proc = defaultdict(float)
    with open(AQUI / "em_procesos.tsv", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            proc[f"{NOMBRE_PROC.get(r['proceso'], r['proceso'])} ({nombre_mat(r['material'])})"] += int(r["interacciones"])

    fuentes = defaultdict(float)
    esp = defaultdict(list)
    rend = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    with open(AQUI / "em_electrones.tsv", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            n = int(r["fotones_cherenkov"])
            creador = {"compt": "Compton", "phot": "fotoeléctrico", "conv": "pares", "eIoni": "rayo delta"}.get(
                r["creador"], r["creador"])
            fuentes[f"{r['particula']} {creador} ({nombre_mat(r['material'])})"] += n
            if r["particula"] == "e-" and r["creador"] == "compt" and "Water" in r["material"]:
                t = float(r["energia_inicial_MeV"])
                esp[r["fisica"]].append(t)
                b = int(t / 0.1)
                rend[r["fisica"]][b][0] += 1
                rend[r["fisica"]][b][1] += n

    luz = {}
    with open(AQUI / "em_luz.tsv", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            luz[(r["fisica"], r["energia_eV"], r["run_id"])] = int(r["fotones_agua"]) + int(r["fotones_otros"])
    fot, carga = defaultdict(list), defaultdict(list)
    prob = defaultdict(lambda: [0, 0])
    tot_fot = tot_q = 0
    with open(AQUI / "em_eventos.tsv", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            n = luz.get((r["fisica"], r["energia_eV"], r["run_id"]), 0)
            q = int(r["carga_pe"])
            tot_fot += n
            tot_q += q
            if r["destino"] in ORIGEN:
                fot[r["destino"]].append(n)
                carga[r["destino"]].append(q)
            if n > 0:
                b = int(10 * math.log10(n))
                prob[b][0] += 1
                prob[b][1] += q >= 1
    eficiencia = tot_q / tot_fot

    figura_procesos_luz(proc, fuentes)
    figura_electrones(esp, rend)
    figura_luz_carga(fot, prob, carga, eficiencia)

    with open(AQUI / "resumen_em2.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["magnitud", "valor"])
        tp = sum(proc.values())
        for k, v in sorted(proc.items(), key=lambda x: -x[1]):
            w.writerow([f"interacciones gamma: {k} (%)", f"{100 * v / tp:.2f}"])
        tf = sum(fuentes.values())
        for k, v in sorted(fuentes.items(), key=lambda x: -x[1])[:8]:
            w.writerow([f"luz Cherenkov de: {k} (%)", f"{100 * v / tf:.2f}"])
        for f in FISICAS:
            t = esp[f]
            w.writerow([f"electrones Compton en agua sobre el umbral, {f} (%)",
                        f"{100 * sum(1 for x in t if x > UMBRAL_CHERENKOV_MEV) / len(t):.2f}"])
        w.writerow(["fotoelectrones por foton Cherenkov creado", f"{eficiencia:.5f}"])
        for d in ORIGEN:
            v = fot[d]
            w.writerow([f"fotones por evento, {d} (media)", f"{sum(v) / len(v):.1f}"])
            vq = [q for q in carga[d] if q >= 1]
            w.writerow([f"carga media de eventos con senal, {d} (pe)", f"{sum(vq) / len(vq):.2f}"])
    print(f"Figuras y resumen_em2.tsv generados; pe por foton creado = {eficiencia:.5f}")


if __name__ == "__main__":
    main()
