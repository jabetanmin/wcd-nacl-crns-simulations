#!/usr/bin/env python3
"""Figuras y tablas del informe técnico del procesamiento de la Campaña 1 (64 corridas).

Lee solo las salidas de procesar_campana.py (resultados/) y escribe en <salida>:
figuras PDF y tablas LaTeX (tablas_*.tex) usadas por el informe.

Uso: python3 figuras_informe.py <carpeta resultados> <carpeta de salida>
"""
import csv
import gzip
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from procesar_campana import ENERGIAS, MEDIOS

VALOR_MEV = [1, 2.5, 5, 7, 10, 25, 50, 80, 100, 300, 500, 700, 1e3, 1e4, 1e5, 1e6]
# La carpeta 1000000meV se rotula "1 keV" en la tesis por decisión del autor.
ROTULO = ["1 meV", "2.5 meV", "5 meV", "7 meV", "10 meV", "25 meV", "50 meV", "80 meV", "100 meV",
          "300 meV", "500 meV", "700 meV", "1 eV", "10 eV", "100 eV", "1 keV"]
ETIQ_MEDIO = ["Agua pura", "Agua + 2.5 % NaCl", "Agua + 5 % NaCl", "Agua + 10 % NaCl"]
COLOR = ["red", "green", "purple", "orange"]          # convención de la tesis
MARCA = ["D", "s", "^", "o"]

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})


def eje_energia(ax):
    ax.set_xscale("log")
    ax.set_xlim(0.7, 1.5e6)
    ax.set_xticks([1, 10, 100, 1e3, 1e4, 1e5, 1e6])
    ax.set_xticklabels(["1 meV", "10 meV", "100 meV", "1 eV", "10 eV", "100 eV", "1 keV"])
    ax.set_xlabel("Energía de inyección")
    ax.grid(True, axis="y", ls=":", color="0.8")


def leer_resumen(res):
    return {(r["energia"], r["medio"]): r for r in csv.DictReader(open(res / "resumen_campana.tsv"), delimiter="\t")}


def serie(R, medio, clave):
    return np.array([float(R[(e, medio)][clave]) for e in ENERGIAS])


def curvas(ax, R, clave, escala=1.0, error=None):
    for m, et, c, mk in zip(MEDIOS, ETIQ_MEDIO, COLOR, MARCA):
        y = serie(R, m, clave) * escala
        yerr = serie(R, m, error) * escala if error else None
        ax.errorbar(VALOR_MEV, y, yerr=yerr, fmt=mk + "-", color=c, lw=1.2, ms=5, capsize=2, label=et)


def historias(res, e, m, columnas):
    out = {c: [] for c in columnas}
    with gzip.open(res / e / m / "historias.tsv.gz", "rt") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            for c in columnas:
                out[c].append(r[c])
    return out


def main():
    res, sal = Path(sys.argv[1]), Path(sys.argv[2])
    sal.mkdir(parents=True, exist_ok=True)
    R = leer_resumen(res)

    # 1. Balance de destinos
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
    for a, (k, t) in zip(ax, [("eta_cap", "Captura"), ("eta_refle", "Reflexión por la tapa"),
                               ("eta_otros", "Otros destinos")]):
        curvas(a, R, k, 100, "u_" + k)
        a.set_title(t)
        a.set_ylabel("% de los neutrones incidentes")
        eje_energia(a)
    ax[0].legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(sal / "balance_destinos.pdf")
    plt.close(fig)

    # 2. Pasos medios por historia
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for a, (k, t) in zip(ax, [("media_Transportation", "Transportation"), ("media_hadElastic", "hadElastic")]):
        curvas(a, R, k)
        a.set_title(f"Pasos {t} por neutrón incidente")
        a.set_ylabel("Media por historia")
        eje_energia(a)
    ax[1].legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(sal / "pasos_por_historia.pdf")
    plt.close(fig)

    # 3. <N> con las dos definiciones
    fig, ax = plt.subplots(figsize=(7, 4.4))
    for m, et, c, mk in zip(MEDIOS, ETIQ_MEDIO, COLOR, MARCA):
        ax.plot(VALOR_MEV, serie(R, m, "N_tesis_media"), mk + "-", color=c, ms=5, lw=1.2, label=et)
        ax.plot(VALOR_MEV, serie(R, m, "N_total_media"), ":", color=c, lw=1)
    ax.set_ylabel(r"$\langle N\rangle$ (dispersiones elásticas antes de la captura)")
    ax.text(0.02, 0.97, "continua: definición de la tesis; punteada: todos los hadElastic",
            transform=ax.transAxes, fontsize=8, va="top")
    eje_energia(ax)
    ax.legend(fontsize=9, frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(sal / "N_medio.pdf")
    plt.close(fig)

    # 4. Distribuciones de N (agua pura y 10 % NaCl, tres energías)
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2), sharey=True)
    for a, (e, et) in zip(ax, [("1meV", "1 meV"), ("25meV", "25 meV"), ("1000000meV", "1 keV")]):
        for m, etm, c in zip(MEDIOS, ETIQ_MEDIO, COLOR):
            n = np.array([int(x) for x in historias(res, e, m, ["N_tesis"])["N_tesis"] if x != ""])
            a.hist(n, bins=np.arange(0, 251, 5), density=True, histtype="step", color=c, lw=1.4, label=etm)
        a.set_title(et)
        a.set_xlabel("N")
        a.grid(True, axis="y", ls=":", color="0.8")
    ax[0].set_ylabel(r"$P(N\mid$captura$)$")
    ax[2].legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(sal / "N_distribuciones.pdf")
    plt.close(fig)

    # 5. <xi> con las dos definiciones
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
    curvas(ax[0], R, "xi_colision_capturadas")
    ax[0].set_title(r"Definición de la tesis: $\xi$ por colisión, $\langle\ln(E_\mathrm{pre}/E_\mathrm{post})\rangle$", fontsize=10)
    curvas(ax[1], R, "xi_historia_inicial_media")
    ax[1].set_title(r"Definición inicial (reemplazada): $\langle\ln(E_0/E_\mathrm{cap})/N\rangle$ por historia", fontsize=10)
    for a in ax:
        a.axhline(0, color="0.4", lw=0.8)
        a.set_ylabel(r"$\langle\xi\rangle$")
        eje_energia(a)
    ax[0].legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(sal / "xi_medio.pdf")
    plt.close(fig)

    # 6. Profundidad de captura bajo la tapa interior (z = 1330 mm)
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2), sharey=True)
    for a, (e, et) in zip(ax, [("1meV", "1 meV"), ("25meV", "25 meV"), ("1000000meV", "1 keV")]):
        for m, etm, c in zip(MEDIOS, ETIQ_MEDIO, COLOR):
            h = historias(res, e, m, ["z_cap", "destino"])
            z = np.array([float(z) for z, d in zip(h["z_cap"], h["destino"]) if d == "cap_dentro"])
            a.hist((1330 - z) / 10, bins=np.arange(0, 25.25, 0.5), density=True, histtype="step", color=c,
                   lw=1.4, label=etm)
        a.set_title(et)
        a.set_xlabel("Profundidad de captura bajo la tapa [cm]")
        a.grid(True, axis="y", ls=":", color="0.8")
    ax[0].set_ylabel("Densidad de probabilidad [1/cm]")
    ax[2].legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(sal / "profundidad_captura.pdf")
    plt.close(fig)

    # 7. Carga
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
    curvas(ax[0], R, "carga_media_pe")
    ax[0].set_ylabel("Fotoelectrones medios por evento con señal")
    for m, et, c, mk in zip(MEDIOS, ETIQ_MEDIO, COLOR, MARCA):
        ax[1].plot(VALOR_MEV, serie(R, m, "carga_eventos") / 1000, mk + "-", color=c, ms=5, lw=1.2, label=et)
    ax[1].set_ylabel("Eventos con señal (por 100 000 neutrones) [miles]")
    for a in ax:
        eje_energia(a)
    ax[0].legend(fontsize=9, frameon=False)
    fig.tight_layout()
    fig.savefig(sal / "carga.pdf")
    plt.close(fig)

    # Tablas LaTeX por medio
    for m, et in zip(MEDIOS, ETIQ_MEDIO):
        filas = []
        for e, rot in zip(ENERGIAS, ROTULO):
            r = R[(e, m)]
            filas.append(f"{rot} & {100*float(r['eta_cap']):.2f} & {100*float(r['eta_refle']):.2f} & "
                         f"{100*float(r['eta_trans']):.3f} & {100*float(r['eta_otros']):.2f} & "
                         f"{float(r['N_tesis_media']):.2f} & {float(r['xi_colision_capturadas']):.4f} & "
                         f"{float(r['xi_historia_inicial_media']):.4f} & {float(r['carga_media_pe']):.2f} \\\\")
        (sal / f"tabla_{m}.tex").write_text("\n".join(filas) + "\n")
    print("figuras y tablas en", sal)


if __name__ == "__main__":
    main()
