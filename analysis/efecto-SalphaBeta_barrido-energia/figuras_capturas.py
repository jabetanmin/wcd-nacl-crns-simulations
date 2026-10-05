#!/usr/bin/env python3
"""Analisis 3 y 4 del barrido: profundidad, tiempo y energia de las capturas en el agua.

Lee capturas_detalle.tsv (generado por capturas_detalle.sh) y produce:
  fig_profundidad_captura.{png,pdf}   distribucion de la profundidad de captura (4 energias)
  fig_tiempo_energia_captura.{png,pdf} tiempo mediano en el tanque, vida media termica
                                        efectiva y energia mediana antes de la captura
  resumen_capturas.tsv                 medianas, cuantiles y vida media por punto
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from figuras_barrido import FISICAS, TINTA, TINTA_2, LIMITE_SAB_EV, eje_energia, AQUI, MEDIO_TEXTO

T0_COLA_US = 100.0      # la vida media se estima con los tiempos mayores que este valor
TAU_AGUA_INF_US = 204.5  # 1/(Sigma_a v), agua a 2200 m/s: Sigma_a = 0.02223 cm^-1
KT_MEV = 25.3            # kT a 20 C
ENERGIAS_PROFUNDIDAD = [0.001, 0.025, 1.0, 1000.0]


def leer():
    d = defaultdict(lambda: defaultdict(list))
    with open(AQUI / "capturas_detalle.tsv", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            k = (float(r["energia_eV"]), r["fisica"])
            d[k]["prof"].append(float(r["profundidad_cm"]))
            d[k]["t"].append(float(r["tiempo_us"]))
            d[k]["e"].append(float(r["energia_previa_eV"]) * 1000)  # meV
            d[k]["etiqueta"] = r["etiqueta"]
    return d


def cuantil(v, p):
    v = sorted(v)
    x = p * (len(v) - 1)
    i = int(x)
    return v[i] if i + 1 >= len(v) else v[i] + (x - i) * (v[i + 1] - v[i])


def vida_media(t):
    """Estimador de maxima verosimilitud de una cola exponencial: media de (t - t0) para t > t0."""
    cola = [x - T0_COLA_US for x in t if x > T0_COLA_US]
    tau = sum(cola) / len(cola)
    return tau, tau / math.sqrt(len(cola))


def resumen(d):
    filas = []
    for (e, f), v in sorted(d.items()):
        tau, etau = vida_media(v["t"])
        filas.append({
            "E": e, "fisica": f, "etiqueta": v["etiqueta"], "n": len(v["t"]),
            "prof_med": cuantil(v["prof"], .5), "prof_p90": cuantil(v["prof"], .9),
            "t_med": cuantil(v["t"], .5), "t_p25": cuantil(v["t"], .25), "t_p75": cuantil(v["t"], .75),
            "tau": tau, "tau_err": etau,
            "e_med": cuantil(v["e"], .5), "e_p25": cuantil(v["e"], .25), "e_p75": cuantil(v["e"], .75),
            "frac_epi": 100 * sum(1 for x in v["e"] if x > 500) / len(v["e"]),
        })
    return filas


def figura_profundidad(d):
    fig, axs = plt.subplots(2, 2, figsize=(9.0, 6.4), sharex=True, sharey=True,
                            gridspec_kw={"hspace": 0.3, "wspace": 0.12})
    bordes = [i * 0.5 for i in range(0, 41)]  # 0 a 20 cm en pasos de 0.5 cm
    for ax, e in zip(axs.flat, ENERGIAS_PROFUNDIDAD):
        for f, estilo in FISICAS.items():
            prof = d[(e, f)]["prof"]
            n = len(prof)
            cuentas = [0] * (len(bordes) - 1)
            for p in prof:
                if p < bordes[-1]:
                    cuentas[int(p / 0.5)] += 1
            dens = [c / n / 0.5 for c in cuentas]  # fraccion de capturas por cm
            med = cuantil(prof, .5)
            ax.stairs(dens, bordes, color=estilo["color"], linewidth=2,
                      label=f"{estilo['etiqueta'].split(' (')[0]} (mediana {med:.1f} cm)")
        etiq = f"{e * 1000:g} meV" if e < 1 else (f"{e:g} eV" if e < 1000 else f"{e / 1000:g} keV")
        ax.set_title(f"Neutrones de {etiq}", loc="left", fontsize=10, color=TINTA)
        ax.set_yscale("log")
        ax.set_ylim(2e-4, 1)
        ax.set_xlim(0, 20)
        ax.legend(loc="upper right", fontsize=8.5)
    fig.supxlabel("Profundidad de captura bajo la superficie del agua (cm)", fontsize=10, color=TINTA, y=0.04)
    for ax in axs[:, 0]:
        ax.set_ylabel("Fracción de capturas por cm")
    fig.text(0.01, -0.01, f"Solo neutrones capturados en el agua; {MEDIO_TEXTO.lower()}, 10 000 neutrones incidentes por punto. "
             "Escala logarítmica: una recta indica una cola exponencial.", fontsize=7.5, color=TINTA_2)
    for ext in ("png", "pdf"):
        fig.savefig(AQUI / f"fig_profundidad_captura.{ext}", bbox_inches="tight")
    plt.close(fig)


def figura_tiempo_energia(filas):
    fig, axs = plt.subplots(3, 1, figsize=(7.2, 9.4), sharex=True, gridspec_kw={"hspace": 0.2})
    paneles = [
        ("t_med", "t_p25", "t_p75", "a) Tiempo en el tanque hasta la captura (mediana)", "Tiempo (µs)", (0, 250)),
        ("tau", None, None, "b) Vida media térmica efectiva (cola exponencial, t > 100 µs)", "τ (µs)", (100, 220)),
        ("e_med", "e_p25", "e_p75", "c) Energía del neutrón justo antes de la captura (mediana)", "Energía (meV)", (0, 60)),
    ]
    for ax, (clave, lo, hi, titulo, ylab, ylim) in zip(axs, paneles):
        for f, estilo in FISICAS.items():
            fs = [r for r in filas if r["fisica"] == f]
            xs = [r["E"] for r in fs]
            ys = [r[clave] for r in fs]
            if lo:
                err = [[r[clave] - r[lo] for r in fs], [r[hi] - r[clave] for r in fs]]
            else:
                err = [r["tau_err"] for r in fs]
            # Desplazamiento horizontal pequeno para que las barras de ambas fisicas no se tapen
            despl = 0.93 if f == "QGSP_BERT_HP" else 1.07
            ax.errorbar([x * despl for x in xs], ys, yerr=err, color=estilo["color"], marker=estilo["marker"], markersize=5,
                        markeredgecolor="white", markeredgewidth=0.8, linewidth=2, capsize=2, elinewidth=1,
                        label=estilo["etiqueta"], zorder=3)
        ax.set_title(titulo, loc="left", fontsize=10, color=TINTA)
        ax.set_ylabel(ylab)
        ax.set_ylim(*ylim)
        eje_energia(ax)
        ax.set_xlim(6e-4, 3e3)
    axs[0].legend(loc="upper left")
    axs[1].axhline(TAU_AGUA_INF_US, color=TINTA_2, linewidth=0.9, linestyle=":")
    axs[1].annotate("agua infinita, solo absorción: 1/(Σₐv) ≈ 205 µs", xy=(1e-3, TAU_AGUA_INF_US), xytext=(0, 4),
                    textcoords="offset points", color=TINTA_2, fontsize=8.5, va="bottom")
    axs[2].axhline(KT_MEV, color=TINTA_2, linewidth=0.9, linestyle=":")
    axs[2].annotate("línea punteada: kT a 20 °C = 25.3 meV", xy=(7e-4, 1), ha="left",
                    color=TINTA_2, fontsize=8.5, va="bottom")
    axs[2].set_xlabel("Energía inicial del neutrón")
    fig.text(0.01, 0.005, "Barras en a) y c): rango intercuartílico; en b): incertidumbre estadística (1σ). "
             "El tiempo se cuenta desde que el neutrón toca la tapa. Línea discontinua: 4 eV.",
             fontsize=7.5, color=TINTA_2)
    for ext in ("png", "pdf"):
        fig.savefig(AQUI / f"fig_tiempo_energia_captura.{ext}", bbox_inches="tight")
    plt.close(fig)


def tabla(filas):
    campos = ["E", "etiqueta", "fisica", "n", "prof_med", "prof_p90", "t_med", "t_p25", "t_p75",
              "tau", "tau_err", "e_med", "e_p25", "e_p75", "frac_epi"]
    nombres = ["energia_eV", "etiqueta", "fisica", "capturas_agua", "profundidad_mediana_cm",
               "profundidad_p90_cm", "tiempo_mediano_us", "tiempo_p25_us", "tiempo_p75_us",
               "vida_media_us", "vida_media_err_us", "energia_mediana_meV", "energia_p25_meV",
               "energia_p75_meV", "capturas_sobre_0.5eV_pct"]
    with open(AQUI / "resumen_capturas.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(nombres)
        for r in filas:
            w.writerow([r[c] if isinstance(r[c], str) else (f"{r[c]:g}" if c in ("E", "n") else f"{r[c]:.2f}")
                        for c in campos])


if __name__ == "__main__":
    d = leer()
    filas = resumen(d)
    figura_profundidad(d)
    figura_tiempo_energia(filas)
    tabla(filas)
    for f in FISICAS:
        taus = [r for r in filas if r["fisica"] == f and r["E"] >= 0.3]
        w = [1 / r["tau_err"] ** 2 for r in taus]
        tau = sum(r["tau"] * wi for r, wi in zip(taus, w)) / sum(w)
        print(f"{f}: vida media combinada (E >= 0.3 eV) = {tau:.1f} +- {1 / math.sqrt(sum(w)):.1f} us")
