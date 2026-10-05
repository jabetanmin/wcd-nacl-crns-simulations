#!/usr/bin/env python3
"""Analisis 5 y 6 del barrido: eficiencia de deteccion y contencion de los gammas de captura.

Lee em_eventos.tsv y em_gammas.tsv (generados por em_detalle.sh) y produce:
  fig_eficiencia_deteccion.{png,pdf}  eficiencia por neutron incidente, probabilidad de senal
                                      tras la captura y carga media de los eventos detectados
  fig_contencion_gamma.{png,pdf}      interaccion de los gammas de 2.2 MeV frente a la energia
                                      inicial y a la profundidad de captura, y energia transferida
  resumen_em.tsv                      cifras por punto
"""
import csv
import math
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from figuras_barrido import FISICAS, TINTA, TINTA_2, eje_energia, AQUI, MEDIO_TEXTO

UMBRALES = (1, 3)


def binom(k, n):
    p = k / n if n else 0.0
    return 100 * p, 100 * math.sqrt(p * (1 - p) / n) if n else 0.0


def leer():
    ev = defaultdict(lambda: defaultdict(float))
    with open(AQUI / "em_eventos.tsv", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            k = (float(r["energia_eV"]), r["fisica"])
            q = int(r["carga_pe"])
            e = ev[k]
            e["n"] += 1
            for t in UMBRALES:
                e[f"q{t}"] += q >= t
            if r["destino"] == "captura_agua":
                e["cap"] += 1
                e["cap_q1"] += q >= 1
                if q >= 1:
                    e["cap_qsum"] += q
            if r["destino"] == "captura_estructura":
                e["est"] += 1
                e["est_q1"] += q >= 1
                if q >= 1:
                    e["est_qsum"] += q
            if q >= 1:
                e["qdet"] += q
    ga = defaultdict(lambda: defaultdict(float))
    por_prof = defaultdict(lambda: defaultdict(float))
    edep = defaultdict(list)
    with open(AQUI / "em_gammas.tsv", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            # Solo los gammas de 2.223 MeV de la captura en hidrogeno del agua
            if r["origen"] != "agua" or r.get("nucleo", "H") != "H":
                continue
            f = r["fisica"]
            k = (float(r["energia_eV"]), f)
            g = ga[k]
            g["n"] += 1
            g["int"] += int(r["interactua_agua"])
            g[r["salida"]] += 1
            prof = float(r["profundidad_captura_cm"])
            b = min(int(prof), 20)  # intervalos de 1 cm; el ultimo reune 20 cm o mas
            p = por_prof[(f, b)]
            p["n"] += 1
            p["int"] += int(r["interactua_agua"])
            p["tapa"] += r["salida"] == "sale_tapa"
            edep[f].append(float(r["energia_transferida_agua_MeV"]))
    return ev, ga, por_prof, edep


def serie(ax, xs_por_f, ys_por_f, es_por_f, estilo_linea="-", etiqueta_extra="", marcador=True):
    for f, estilo in FISICAS.items():
        ax.errorbar(xs_por_f[f], ys_por_f[f], yerr=es_por_f[f], color=estilo["color"],
                    marker=estilo["marker"] if marcador else None, markersize=5, markeredgecolor="white",
                    markeredgewidth=0.8, linewidth=2, linestyle=estilo_linea, capsize=2, elinewidth=1,
                    label=estilo["etiqueta"].split(" (")[0] + etiqueta_extra, zorder=3)


def figura_eficiencia(ev):
    fig, axs = plt.subplots(3, 1, figsize=(7.2, 9.0), sharex=True, gridspec_kw={"hspace": 0.2})
    energias = sorted({k[0] for k in ev})
    # a) eficiencia por neutron incidente, umbrales 1 y 3 fotoelectrones
    for t, ls in zip(UMBRALES, ("-", "--")):
        xs, ys, es = {}, {}, {}
        for f in FISICAS:
            vals = [binom(ev[(e, f)][f"q{t}"], ev[(e, f)]["n"]) for e in energias]
            xs[f], ys[f], es[f] = energias, [v[0] for v in vals], [v[1] for v in vals]
        serie(axs[0], xs, ys, es, ls, f", Q ≥ {t} pe", marcador=(t == 1))
    axs[0].set_ylabel("Neutrones incidentes\ncon señal (%)")
    axs[0].set_ylim(0, 28)
    axs[0].legend(loc="upper left", fontsize=8, ncol=2, frameon=True, framealpha=1, edgecolor="none")
    axs[0].set_title("a) Eficiencia de detección por neutrón incidente", loc="left", fontsize=10, color=TINTA)
    # b) probabilidad de senal (Q >= 1) una vez capturado el neutron en el agua
    xs, ys, es = {}, {}, {}
    for f in FISICAS:
        vals = [binom(ev[(e, f)]["cap_q1"], ev[(e, f)]["cap"]) for e in energias]
        xs[f], ys[f], es[f] = energias, [v[0] for v in vals], [v[1] for v in vals]
    serie(axs[1], xs, ys, es)
    axs[1].set_ylabel("Capturas en el agua\ncon señal (%)")
    axs[1].set_ylim(30, 55)
    axs[1].set_title("b) Probabilidad de señal (Q ≥ 1 pe) tras una captura en el agua", loc="left",
                     fontsize=10, color=TINTA)
    # c) carga media de los eventos detectados
    xs, ys = {}, {}
    for f in FISICAS:
        xs[f] = energias
        ys[f] = [ev[(e, f)]["qdet"] / ev[(e, f)]["q1"] for e in energias]
    serie(axs[2], xs, ys, {f: None for f in FISICAS})
    axs[2].set_ylabel("Fotoelectrones")
    axs[2].set_ylim(0, 6)
    axs[2].set_title("c) Carga media de los eventos con señal", loc="left", fontsize=10, color=TINTA)
    axs[2].set_xlabel("Energía inicial del neutrón")
    for ax in axs:
        eje_energia(ax)
        ax.set_xlim(6e-4, 3e3)
    fig.text(0.01, 0.005, f"{MEDIO_TEXTO}, 10 000 neutrones incidentes por punto; barras: incertidumbre estadística (1σ). "
             "Línea discontinua vertical: 4 eV.", fontsize=7.5, color=TINTA_2)
    for ext in ("png", "pdf"):
        fig.savefig(AQUI / f"fig_eficiencia_deteccion.{ext}", bbox_inches="tight")
    plt.close(fig)


def figura_contencion(ga, por_prof, edep):
    fig = plt.figure(figsize=(9.0, 7.4))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.28)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])
    energias = sorted({k[0] for k in ga})
    # a) fraccion de gammas que interactuan en el agua frente a la energia inicial del neutron
    xs, ys, es = {}, {}, {}
    for f in FISICAS:
        vals = [binom(ga[(e, f)]["int"], ga[(e, f)]["n"]) for e in energias]
        xs[f], ys[f], es[f] = energias, [v[0] for v in vals], [v[1] for v in vals]
    serie(ax1, xs, ys, es)
    eje_energia(ax1)
    ax1.set_xlim(6e-4, 3e3)
    ax1.set_xticks([1e-3, 1e-1, 1e1, 1e3])
    ax1.set_ylim(45, 70)
    ax1.set_xlabel("Energía inicial del neutrón")
    ax1.set_ylabel("Gammas que interactúan en el agua (%)")
    ax1.set_title("a) Frente a la energía inicial", loc="left", fontsize=10, color=TINTA)
    ax1.legend(loc="lower right", fontsize=8.5)
    # b) frente a la profundidad de captura (todas las energias juntas)
    for f, estilo in FISICAS.items():
        bs = sorted(b for (ff, b) in por_prof if ff == f and por_prof[(f, b)]["n"] >= 50)
        x = [b + 0.5 for b in bs]
        for clave, ls, etiq in (("int", "-", "interactúan en el agua"), ("tapa", "--", "salen por la tapa")):
            vals = [binom(por_prof[(f, b)][clave], por_prof[(f, b)]["n"]) for b in bs]
            ax2.errorbar(x, [v[0] for v in vals], yerr=[v[1] for v in vals], color=estilo["color"],
                         marker=estilo["marker"] if clave == "int" else None, markersize=4, linewidth=2,
                         linestyle=ls, capsize=2, elinewidth=1,
                         label=estilo["etiqueta"].split(" (")[0] if clave == "int" else None)
    ax2.set_xlim(0, 20)
    ax2.set_ylim(0, 100)
    ax2.set_xlabel("Profundidad de captura bajo la superficie (cm)")
    ax2.set_ylabel("Gammas de captura (%)")
    ax2.set_title("b) Frente a la profundidad de captura", loc="left", fontsize=10, color=TINTA)
    ax2.annotate("interactúan en el agua (línea continua)", xy=(10.5, 88), color=TINTA_2, fontsize=8, ha="center")
    ax2.annotate("salen por la tapa (línea discontinua)", xy=(10.5, 8), color=TINTA_2, fontsize=8, ha="center")
    ax2.legend(loc="center right", fontsize=8)
    # c) energia transferida al agua por cada gamma de 2.2 MeV que interactua
    bordes = [i * 0.05 for i in range(0, 47)]  # 0 a 2.3 MeV
    ymax = 0.0
    for f, estilo in FISICAS.items():
        v = [x for x in edep[f] if x > 0]
        cuentas = [0] * (len(bordes) - 1)
        for x in v:
            i = min(int(x / 0.05), len(cuentas) - 1)
            cuentas[i] += 1
        frac = [c / len(v) for c in cuentas]
        ymax = max(ymax, max(frac))
        ax3.stairs(frac, bordes, color=estilo["color"], linewidth=2,
                   label=estilo["etiqueta"].split(" (")[0])
    ax3.axvline(2.223, color=TINTA_2, linewidth=0.9, linestyle=":")
    ax3.axvline(2.223 * (2 * 2.223 / 0.511) / (1 + 2 * 2.223 / 0.511), color=TINTA_2, linewidth=0.9, linestyle="--")
    ytxt = 0.95 * ymax * 1.12
    ax3.annotate("borde Compton\n(1.99 MeV)", xy=(1.99, ytxt), xytext=(-6, 0), textcoords="offset points",
                 ha="right", color=TINTA_2, fontsize=8.5, va="top")
    ax3.annotate("absorción\ntotal\n(2.22 MeV)", xy=(2.26, ytxt), xytext=(4, 0), textcoords="offset points",
                 ha="left", color=TINTA_2, fontsize=8.5, va="top")
    ax3.set_xlim(0, 2.6)
    ax3.set_ylim(0, ymax * 1.12)
    ax3.set_xlabel("Energía transferida al agua por el gamma de 2.2 MeV (MeV)")
    ax3.set_ylabel("Fracción de gammas por 0.05 MeV")
    ax3.set_title("c) Energía que cada gamma que interactúa entrega a los electrones del agua (todas las energías)",
                  loc="left", fontsize=10, color=TINTA)
    ax3.legend(loc="upper left", fontsize=8.5)
    fig.text(0.01, 0.005, "Gammas de 2.223 MeV de la captura en hidrógeno. "
             "b): intervalos de 1 cm con al menos 50 gammas. "
             "c): suma de las pérdidas del gamma primario en sus interacciones Compton, fotoeléctrica y de pares.",
             fontsize=7.5, color=TINTA_2)
    for ext in ("png", "pdf"):
        fig.savefig(AQUI / f"fig_contencion_gamma.{ext}", bbox_inches="tight")
    plt.close(fig)


def tabla(ev, ga):
    with open(AQUI / "resumen_em.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["energia_eV", "fisica", "eficiencia_Q1_pct", "eficiencia_Q1_err_pct", "eficiencia_Q3_pct",
                    "senal_tras_captura_agua_pct", "senal_tras_captura_estructura_pct", "carga_media_detectados_pe",
                    "carga_media_captura_agua_pe", "carga_media_captura_estructura_pe",
                    "gammas_interactuan_agua_pct", "gammas_salen_tapa_pct", "gammas_salen_lateral_pct",
                    "gammas_absorbidos_agua_pct", "gammas_absorbidos_estructura_pct"])
        for k in sorted(ev):
            e, g = ev[k], ga[k]
            q1, eq1 = binom(e["q1"], e["n"])
            w.writerow([f"{k[0]:g}", k[1], f"{q1:.2f}", f"{eq1:.2f}", f"{100 * e['q3'] / e['n']:.2f}",
                        f"{100 * e['cap_q1'] / e['cap']:.2f}", f"{100 * e['est_q1'] / max(e['est'], 1):.2f}",
                        f"{e['qdet'] / e['q1']:.2f}", f"{e['cap_qsum'] / max(e['cap_q1'], 1):.2f}",
                        f"{e['est_qsum'] / max(e['est_q1'], 1):.2f}",
                        f"{100 * g['int'] / g['n']:.2f}", f"{100 * g['sale_tapa'] / g['n']:.2f}",
                        f"{100 * g['sale_lateral'] / g['n']:.2f}", f"{100 * g['absorbido_agua'] / g['n']:.2f}",
                        f"{100 * g['absorbido_estructura'] / g['n']:.2f}"])


if __name__ == "__main__":
    ev, ga, por_prof, edep = leer()
    figura_eficiencia(ev)
    figura_contencion(ga, por_prof, edep)
    tabla(ev, ga)
    print("Figuras y resumen_em.tsv generados")
