"""Regenera cinco figuras de la tesis a partir de fórmulas, datos de simulación o del código del simulador.

  fig_umbral_cherenkov        umbral Cherenkov de e, mu, p y E_gamma mínima (Compton a 180 grados) frente a n
  fig_klein_nishina           d sigma/dT_e de Klein-Nishina para las líneas gamma de captura
  fig_fotones_cherenkov_e     fotones Cherenkov (300-600 nm) de un electrón que se frena en agua
  fig_dispersiones_elasticas  P(N | captura, medio) para el flujo térmico de Bucaramanga
  fig_qe_pmt                  eficiencia cuántica del PMT implementada en el simulador

Las fórmulas son las de los notebooks originales del autor (lineas-espectrales-teoria.ipynb,
Compton_diferente_config.ipynb, Histogramas_cita_n_tremicos_Bga.ipynb), salvo lo indicado en cada función.

Uso: python3 regenerar_figuras_2.py <salida>
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SAL = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
BGA = Path(os.environ.get("DATOS_NEUTRONES_BGA", "datos/Neutrones-termicos/Neutrones-termico-Bga"))
ME, MMU, MP = 0.51099895, 105.6583755, 938.272088      # MeV
N_AGUA = 1.33
COLOR = {"Agua-pura": "#d62728", "Agua+2.5NaCl": "#2ca02c", "Agua+5NaCl": "#8e44ad", "Agua+10NaCl": "#f39c12"}
NOMBRE = {"Agua-pura": "Agua pura", "Agua+2.5NaCl": "Agua + 2.5 % de NaCl",
          "Agua+5NaCl": "Agua + 5 % de NaCl", "Agua+10NaCl": "Agua + 10 % de NaCl"}

plt.rcParams.update({"font.size": 11, "axes.linewidth": 0.9, "xtick.direction": "in", "ytick.direction": "in",
                     "xtick.top": True, "ytick.right": True, "savefig.bbox": "tight"})


def guardar(fig, nombre):
    fig.savefig(SAL / f"{nombre}.pdf")
    fig.savefig(SAL / f"{nombre}.png", dpi=300)
    plt.close(fig)


# ---------------------------------------------------------------- umbral Cherenkov
def T_umbral(m, n):
    return (1 / np.sqrt(1 - 1 / n**2) - 1) * m


def E_gamma_min(T):
    """Energía del fotón que, por Compton a 180 grados, deja al electrón con energía cinética T."""
    return 0.5 * (T + np.sqrt(T**2 + 2 * ME * T))


def fig_umbral():
    n = np.linspace(1.01, 1.5, 500)
    fig, ax = plt.subplots(figsize=(8.5, 5.8))
    curvas = [(T_umbral(MP, n), T_umbral(MP, N_AGUA), "#2ca02c", "-", "$p$"),
              (T_umbral(MMU, n), T_umbral(MMU, N_AGUA), "#ff7f0e", "-", r"$\mu^\pm$"),
              (E_gamma_min(T_umbral(ME, n)), E_gamma_min(T_umbral(ME, N_AGUA)), "#d62728", "--",
               r"$\gamma$ (Compton a 180°)"),
              (T_umbral(ME, n), T_umbral(ME, N_AGUA), "#1f77b4", "-", r"$e^\pm$")]
    for y, y0, c, ls, et in curvas:
        texto = f"{y0:.3f} MeV" if y0 < 100 else f"{y0:.1f} MeV"
        ax.plot(n, y, color=c, ls=ls, lw=2, label=f"{et}: {texto} en agua")
        ax.plot(N_AGUA, y0, "o", color=c, mec="k", ms=7, zorder=5)
    ax.axvline(N_AGUA, color="0.4", ls=":", lw=1)
    ax.text(N_AGUA + 0.005, 0.13, "agua, $n$ = 1.33", fontsize=9.5, color="0.3")
    ax.set_yscale("log")
    ax.set_ylim(0.1, 6e4)
    ax.set_xlim(1.0, 1.5)
    ax.set_xlabel("Índice de refracción $n$")
    ax.set_ylabel("Energía cinética umbral [MeV]")
    ax.legend(fontsize=9.5, loc="upper right")
    ax.grid(True, which="major", alpha=0.3)
    guardar(fig, "fig_umbral_cherenkov")
    return {"T_e": T_umbral(ME, N_AGUA), "T_mu": T_umbral(MMU, N_AGUA), "T_p": T_umbral(MP, N_AGUA),
            "E_gamma_min": E_gamma_min(T_umbral(ME, N_AGUA))}


# ---------------------------------------------------------------- Klein-Nishina
def dsigma_dT(E, T):
    """d sigma/dT (barn/MeV por electrón), Klein-Nishina."""
    r0 = 2.8179403262e-13                                     # cm
    Ep = E - T
    cos_t = np.clip(1 - ME * T / (E * Ep), -1, 1)
    q = Ep / E
    dsdo = 0.5 * r0**2 * q**2 * (q + 1 / q - (1 - cos_t**2))  # cm^2/sr
    return dsdo * 2 * np.pi * ME / Ep**2 * 1e24              # barn/MeV


def fig_klein_nishina():
    lineas = [0.517, 1.165, 2.223, 6.111, 8.578]
    colores = ["#0B3C5D", "#8B1E3F", "#006400", "#7B3F00", "#4B0082"]
    fig, ax = plt.subplots(figsize=(9, 5.8))
    filas = []
    for E, c in zip(lineas, colores):
        Tmax = 2 * E**2 / (ME + 2 * E)                        # borde Compton
        T = np.linspace(1e-4, Tmax * (1 - 1e-9), 3000)
        y = 10 * dsigma_dT(E, T)                              # por molécula de H2O (10 electrones)
        ax.plot(T, y, color=c, lw=2, label=f"$E_\\gamma$ = {E} MeV")
        ax.vlines(Tmax, 1e-3, y[-1], color=c, lw=1.2)
        ax.plot(Tmax, y[-1], "o", color=c, mec="k", ms=6)
        ax.text(Tmax, y[-1] * 1.25, f"{Tmax:.3f} MeV", color=c, ha="center", fontsize=9, fontweight="bold")
        filas.append({"E_gamma_MeV": E, "T_borde_Compton_MeV": Tmax,
                      "sigma_total_barn_por_molecula": np.trapz(y, T)})
    ax.set_yscale("log")
    ax.set_ylim(0.1, 50)
    ax.set_xlim(0, 9)
    ax.set_xlabel("Energía cinética del electrón Compton $T_e$ [MeV]")
    ax.set_ylabel(r"$d\sigma_\mathrm{KN}/dT_e$ por molécula de H$_2$O [barn/MeV]")
    ax.legend(fontsize=9.5, loc="upper right")
    ax.grid(True, which="both", alpha=0.25)
    guardar(fig, "fig_klein_nishina")
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- fotones Cherenkov de un electrón
def alcance_katz_penfold(T):
    """Alcance CSDA en agua (g/cm2 = cm), Katz y Penfold (1952), ambos tramos."""
    T = np.asarray(T, float)
    bajo = 0.412 * T ** (1.265 - 0.0954 * np.log(T))
    alto = 0.530 * T - 0.106
    return np.where(T <= 2.5, bajo, alto)


def fig_fotones():
    alpha = 1 / 137.035999084
    l1, l2 = 300e-7, 600e-7                                   # cm
    T = np.linspace(0.01, 10, 4000)
    g = 1 + T / ME
    beta2 = 1 - 1 / g**2
    dNdx = 2 * np.pi * alpha * (1 / l1 - 1 / l2) * np.clip(1 - 1 / (beta2 * N_AGUA**2), 0, None)   # 1/cm
    dRdT = np.gradient(alcance_katz_penfold(T), T)            # cm/MeV
    N = np.concatenate([[0], np.cumsum(0.5 * (dNdx[1:] * dRdT[1:] + dNdx[:-1] * dRdT[:-1]) * np.diff(T))])
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    ax.plot(T, N, color="#1f4e9c", lw=2)
    Tum = T_umbral(ME, N_AGUA)
    ax.axvline(Tum, color="#d62728", ls="--", lw=1)
    ax.text(Tum + 0.12, N.max() * 0.93, f"umbral $T_\\mathrm{{um}}$ = {Tum:.3f} MeV", color="#d62728", fontsize=9.5)
    puntos = []
    for Tp in [1, 2, 5, 10]:
        Np = np.interp(Tp, T, N)
        puntos.append({"T_MeV": Tp, "fotones": Np, "alcance_cm": float(alcance_katz_penfold(Tp))})
        ax.plot(Tp, Np, "o", color="#1f4e9c", mec="k", ms=7, zorder=5)
        # La etiqueta de 1 MeV se coloca encima del punto para no superponerse con los números del eje x.
        dx, dy, va = {1: (10, -2, "center")}.get(Tp, (8, -14, "top"))
        ax.annotate(f"{Tp} MeV: {Np:.0f} fotones", (Tp, Np), xytext=(dx, dy), textcoords="offset points",
                    ha="left" if Tp < 10 else "right", va=va, fontsize=9.5)
    ax.set_xlim(0, 10.3)
    ax.set_ylim(0, N.max() * 1.05)
    ax.set_xlabel("Energía cinética del electrón $T_e$ [MeV]")
    ax.set_ylabel("Fotones Cherenkov por electrón (300–600 nm)")
    ax.grid(True, alpha=0.3)
    guardar(fig, "fig_fotones_cherenkov_e")
    return pd.DataFrame(puntos)


# ---------------------------------------------------------------- dispersiones elásticas antes de la captura
def fig_dispersiones():
    archivos = {"Agua-pura": "Agua-pura/numero-dispersiones-elasticas-AP-termicos-Bga.txt",
                "Agua+2.5NaCl": "Agua+2.5NaCl/numero-dispersiones-elasticas-A-25NaCl-termicos-Bga.txt",
                "Agua+5NaCl": "Agua+5NaCl/numero-dispersiones-elasticas-A-5NaCl-termicos-Bga.txt",
                "Agua+10NaCl": "Agua+10NaCl/numero-dispersiones-elasticas-A-10NaCl-termicos-Bga.txt"}
    fig, ax = plt.subplots(figsize=(9, 5.8))
    filas = []
    for m, a in archivos.items():
        N = np.loadtxt(BGA / a)
        cuentas, bordes = np.histogram(N, bins=200, range=(0, 200))      # un valor entero por intervalo
        p = cuentas / len(N)                                             # P(N | captura), normalizada al total
        centros = 0.5 * (bordes[1:] + bordes[:-1])
        ax.step(centros, p, where="mid", color=COLOR[m], lw=1.4,
                label=f"{NOMBRE[m]}: $\\langle N\\rangle$ = {N.mean():.1f}, mediana = {np.median(N):.0f}")
        filas.append({"medio": m, "N_capturas": len(N), "media": N.mean(), "desv": N.std(),
                      "mediana": np.median(N), "moda": centros[p.argmax()], "P_moda": p.max(),
                      "fraccion_N_mayor_200": np.mean(N >= 200)})
    ax.set_xlim(0, 200)
    ax.set_ylim(0, None)
    ax.set_xlabel("Número de dispersiones elásticas antes de la captura, $N$")
    ax.set_ylabel(r"$P(N\mid\mathrm{captura,\ medio})$")
    ax.legend(fontsize=9.5, loc="upper right")
    ax.grid(True, alpha=0.3)
    guardar(fig, "fig_dispersiones_elasticas")
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- eficiencia cuántica del PMT
def fig_qe():
    # src/Framework/Detector/OptDevice.cc, caso ePMT
    bordes = np.arange(250, 701, 50)
    qe_c1 = [0.01, 0.03, 0.20, 0.25, 0.20, 0.14, 0.07, 0.03, 0.06]          # etiqueta campana-1-QGSP_BERT_HP
    qe_tabla = [0.01, 0.03, 0.20, 0.25, 0.20, 0.14, 0.07, 0.03, 0.01]       # Tabla tab:qeff_pmt
    l_c2 = [300, 350, 400, 450, 500, 550, 600, 650]
    qe_c2 = [0.03, 0.20, 0.25, 0.20, 0.14, 0.07, 0.03, 0.00]                # campana-2 (interpolación lineal)
    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    ax.stairs(np.array(qe_tabla) * 100, bordes, color="#1f4e9c", lw=2,
              label="Escalones de 50 nm (Tabla de eficiencia cuántica)")
    ax.stairs(np.array(qe_c1) * 100, bordes, color="#ff7f0e", lw=1.4, ls="--",
              label="Código de la Campaña 1 (650–700 nm: 6 %)")
    ax.plot(l_c2, np.array(qe_c2) * 100, "o-", color="#2ca02c", lw=1.6, ms=5,
            label="Código de la Campaña 2 (interpolación lineal)")
    ax.plot(390, 25, "*", color="k", ms=12, label="Hamamatsu: 25 % típico a 390 nm")
    ax.axvspan(300, 600, color="0.85", alpha=0.5, lw=0)
    ax.text(450, 0.7, "intervalo 300–600 nm", ha="center", fontsize=9.5, color="0.35")
    ax.set_xlim(240, 710)
    ax.set_ylim(0, 30)
    ax.set_xlabel("Longitud de onda [nm]")
    ax.set_ylabel("Eficiencia cuántica [%]")
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3)
    guardar(fig, "fig_qe_pmt")


if __name__ == "__main__":
    SAL.mkdir(parents=True, exist_ok=True)
    print(fig_umbral())
    print(fig_klein_nishina().to_string(index=False))
    print(fig_fotones().to_string(index=False))
    d = fig_dispersiones()
    d.to_csv(SAL / "dispersiones_elasticas.tsv", sep="\t", index=False, float_format="%.4f")
    print(d.to_string(index=False))
    fig_qe()
