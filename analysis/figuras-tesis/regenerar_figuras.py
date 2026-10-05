"""Regenera, desde los datos de simulación, cuatro figuras del Capítulo 4 de la tesis.

  1. fig_lineas_gamma_captura   líneas gamma de captura en 16O, 1H, 35Cl y 37Cl (neutrones de 500 MeV)
  2. fig_esquema_niveles_O17    esquema de niveles de 16O(n,g)17O (datos nucleares de referencia)
  3. fig_energia_deuterones     energía de los deuterones de 1H(n,g)2H (medios disponibles)
  4. fig_captura_relativa       N_capt(agua+NaCl)/N_capt(agua pura) frente a la energía (Campaña 1)

Uso: python3 regenerar_figuras.py <salida>
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

SAL = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
E500 = Path(os.environ.get("DATOS_ESPECTROS_500MEV", "datos/Espectros-500MeV"))
CAPT = Path(__file__).resolve().parent / "capturas_malla_fina.tsv"
COL = ["particula", "evento", "traza", "madre", "proceso", "x", "y", "z", "E"]
COLOR = {"Agua-pura": "#d62728", "Agua+2.5NaCl": "#2ca02c", "Agua+5NaCl": "#8e44ad", "Agua+10NaCl": "#f39c12"}
NOMBRE = {"Agua-pura": "Agua pura", "Agua+2.5NaCl": "Agua + 2.5 % de NaCl",
          "Agua+5NaCl": "Agua + 5 % de NaCl", "Agua+10NaCl": "Agua + 10 % de NaCl"}

plt.rcParams.update({"font.size": 11, "axes.linewidth": 0.9, "xtick.direction": "in", "ytick.direction": "in",
                     "xtick.top": True, "ytick.right": True, "savefig.bbox": "tight"})


def guardar(fig, nombre):
    fig.savefig(SAL / f"{nombre}.pdf")
    fig.savefig(SAL / f"{nombre}.png", dpi=300)
    plt.close(fig)


def leer(archivo):
    return pd.read_csv(E500 / archivo, sep=r"\s+", names=COL)


# ---------------------------------------------------------------- 1. líneas gamma de captura
def panel_lineas(ax, gam_keV, n_capt, color, etiquetas, titulo, reaccion, xmax):
    """etiquetas: {energía keV: (dx, dy) desplazamiento de la etiqueta en puntos}."""
    lineas = np.round(gam_keV, 1).value_counts()
    y = lineas / lineas.max() * 100                  # intensidad relativa: línea más intensa = 100
    ax.vlines(y.index / 1000, 0, y.values, color=color, lw=1.0)
    for E, (dx, dy) in etiquetas.items():
        i = (abs(y.index - E)).argmin()
        Ex, Iy = y.index[i], y.values[i]
        ax.annotate(f"{Ex:.1f} keV", (Ex / 1000, Iy), xytext=(dx, dy), textcoords="offset points",
                    ha="left" if dx > 0 else ("right" if dx < 0 else "center"), va="bottom", fontsize=8.5,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, lw=0.7),
                    arrowprops=dict(arrowstyle="-", color=color, lw=0.6) if dx else None)
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, 128)
    ax.set_xlabel("Energía del fotón $\\gamma$ [MeV]")
    ax.set_ylabel("Intensidad relativa")
    ax.text(0.98, 0.97, f"{titulo}\n{reaccion}\n$N_\\mathrm{{capt}}$ = {n_capt}", transform=ax.transAxes,
            ha="right", va="top", fontsize=9, bbox=dict(boxstyle="round", fc="white", ec="0.6"))


def fig_lineas():
    o = leer("Matriz-lineas-espectrales/O17.txt")
    n_o = o.groupby(["evento", "traza", "madre"]).ngroups     # O17.txt no guarda el núcleo residual
    h = leer("Agua-pura/captura-hidrogeno.txt")
    c36 = leer("Matriz-lineas-espectrales/Cl36.txt")
    c38 = leer("Matriz-lineas-espectrales/Cl38.txt")

    fig, axs = plt.subplots(2, 2, figsize=(12, 8.2), constrained_layout=True)
    panel_lineas(axs[0, 0], o[o.particula == "gamma"].E * 1000, n_o, COLOR["Agua-pura"],
                 {870.8: (0, 4), 1088.0: (28, 18), 2184.2: (26, -4), 3272.2: (0, 4), 4143.1: (18, 12)}, "Agua pura",
                 r"$^{16}$O(n,$\gamma$)$^{17}$O", 12)

    # (b) línea de 2.224 MeV con ajuste gaussiano
    ax = axs[0, 1]
    g = h[h.particula == "gamma"].E.to_numpy() * 1000
    # El archivo guarda E con 6 cifras significativas: las energías toman valores discretos cada
    # 0.01 keV. Cada intervalo se centra en uno de esos valores.
    bordes = np.round(np.arange(2224.315, 2224.4351, 0.01), 3)
    n, _ = np.histogram(g, bordes)
    x = 0.5 * (bordes[1:] + bordes[:-1])
    s = np.sqrt(np.maximum(n, 1))
    gauss = lambda x, a, mu, sig, c: a * np.exp(-0.5 * ((x - mu) / sig) ** 2) + c
    p, cov = curve_fit(gauss, x, n, p0=[n.max(), x[n.argmax()], 0.02, 0], sigma=s, absolute_sigma=True)
    chi2 = np.sum(((n - gauss(x, *p)) / s) ** 2) / (len(x) - 4)
    xf = np.linspace(bordes[0], bordes[-1], 400)
    ax.errorbar(x - 2224, n, yerr=s, fmt="s", ms=4, color="#1f4e9c",
                ecolor="0.3", elinewidth=0.8, capsize=0, label="Simulación")
    ax.plot(xf - 2224, gauss(xf, *p), color=COLOR["Agua-pura"], lw=1.4, label="Ajuste gaussiano")
    ax.set_xlabel("Energía del fotón $\\gamma$ $-$ 2224 [keV]")
    ax.set_ylabel("Fotones por intervalo")
    ax.legend(loc="center right", fontsize=9, frameon=False)
    ax.text(0.03, 0.97, "Agua pura\n$^{1}$H(n,$\\gamma$)$^{2}$H\n"
            f"$N_\\mathrm{{capt}}$ = {len(g)}", transform=ax.transAxes, ha="left", va="top", fontsize=9,
            bbox=dict(boxstyle="round", fc="white", ec="0.6"))
    ax.text(0.97, 0.97, f"$\\mu$ = {p[1]:.5f} ± {np.sqrt(cov[1, 1]):.5f} keV\n"
            f"$\\sigma$ = {abs(p[2]):.5f} ± {np.sqrt(cov[2, 2]):.5f} keV\n"
            f"$\\chi^2_\\mathrm{{red}}$ = {chi2:.1f}", transform=ax.transAxes, ha="right", va="top", fontsize=9,
            bbox=dict(boxstyle="round", fc="white", ec="0.6"))
    ax.set_ylim(0, n.max() * 1.35)
    ajuste = {"mu_keV": p[1], "err_mu": np.sqrt(cov[1, 1]), "sigma_keV": abs(p[2]),
              "err_sigma": np.sqrt(cov[2, 2]), "chi2_red": chi2}

    panel_lineas(axs[1, 0], c36[c36.particula == "gamma"].E * 1000, int((c36.particula == "Cl36").sum()),
                 COLOR["Agua+2.5NaCl"], {1164.9: (0, 4), 517.1: (-8, 14), 788.4: (8, 22), 1951.1: (0, 4), 6110.8: (0, 4)},
                 "Agua + 2.5 % de NaCl",
                 r"$^{35}$Cl(n,$\gamma$)$^{36}$Cl", 9)
    panel_lineas(axs[1, 1], c38[c38.particula == "gamma"].E * 1000, int((c38.particula == "Cl38").sum()),
                 COLOR["Agua+2.5NaCl"], {755.5: (0, 4), 1692.2: (0, 4), 4126.9: (0, 4)}, "Agua + 2.5 % de NaCl",
                 r"$^{37}$Cl(n,$\gamma$)$^{38}$Cl", 7)
    for ax, l in zip(axs.flat, "abcd"):
        ax.text(-0.09, 1.02, f"({l})", transform=ax.transAxes, fontsize=12, fontweight="bold")
    guardar(fig, "fig_lineas_gamma_captura")
    return ajuste, n_o


# ---------------------------------------------------------------- 2. esquema de niveles de 17O
def fig_niveles():
    # Niveles y transiciones de la figura original del autor (datos de Firestone y Révay 2016 / CapGam).
    niveles = [(0.0, "5/2$^+$", "estable"), (870.78, "1/2$^+$", "180 ps"),
               (3055.37, "1/2$^-$", "0.08 ps"), (4143.27, "1/2$^+$", "")]
    trans = [(4143.27, 0.0, 4142.6, "E2", 3.36, "0.2"), (4143.27, 870.78, 3272.02, "M1", 16.2, "#1f4e9c"),
             (4143.27, 3055.37, 1087.89, "E1", 80.4, "#d62728"), (3055.37, 870.78, 2184.49, "E1", 80.4, "#d62728"),
             (870.78, 0.0, 870.76, "E2", 96.6, "#d62728")]
    fig, ax = plt.subplots(figsize=(10, 6.4))
    for E, jp, t in niveles:
        ax.plot([0, 12], [E, E], color="k", ls="--" if E > 4000 else "-", lw=3 if E == 0 else 1.3)
        ax.text(-0.25, E, jp, ha="right", va="center", fontsize=12)
        ax.text(12.2, E + 35, f"{E:.2f} keV" if E else "0", ha="left", va="bottom", fontsize=10.5)
        ax.text(12.2, E - 35, t, ha="left", va="top", fontsize=9.5, color="0.3")
    for k, (Ei, Ef, Eg, mult, I, c) in enumerate(trans):
        x = 1.3 + 2.35 * k
        ax.annotate("", xy=(x, Ef), xytext=(x, Ei),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=0.6 + 3.2 * I / 100, mutation_scale=14))
        ax.text(x + 0.15, 0.5 * (Ei + Ef), f"{Eg:.2f} keV\n{mult}, {I:g} %", ha="left", va="center",
                fontsize=9, color="k" if c == "0.2" else c,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9))
    ax.text(12.2, 4143.27 + 260, "estado de captura ($S_n$)", ha="left", va="bottom", fontsize=9.5, color="0.3")
    ax.set_title("$^{16}$O(n,$\\gamma$)$^{17}$O con neutrones térmicos", fontsize=12)
    ax.set_xlim(-1.5, 16)
    ax.set_ylim(-250, 4700)
    ax.set_ylabel("Energía de excitación de $^{17}$O [keV]")
    ax.set_xticks([])
    for s in ["top", "right", "bottom"]:
        ax.spines[s].set_visible(False)
    ax.tick_params(right=False, top=False)
    guardar(fig, "fig_esquema_niveles_O17")


# ---------------------------------------------------------------- 3. energía de los deuterones
def fig_deuterones():
    rutas = {"Agua-pura": "Agua-pura/captura-hidrogeno.txt", "Agua+2.5NaCl": "Agua+2.5NaCl/captura-hidrogeno.txt"}
    bordes = np.arange(0.00120, 0.00145 + 2.5e-7, 2.5e-7)
    fig, ax = plt.subplots(figsize=(9, 5.6))
    filas = []
    for m, r in rutas.items():
        e = leer(r)
        e = e[e.particula == "deuteron"].E.to_numpy()
        pico = e[(e > bordes[0]) & (e < bordes[-1])]
        ax.hist(e, bordes, histtype="step", color=COLOR[m], lw=1.3,
                label=f"{NOMBRE[m]}: N = {len(e)}\n  pico: {1e3 * pico.mean():.4f} ± {1e3 * pico.std():.4f} keV")
        filas.append({"medio": m, "N_deuterones": len(e), "media_total_keV": 1e3 * e.mean(),
                      "rms_total_keV": 1e3 * e.std(), "media_pico_keV": 1e3 * pico.mean(),
                      "desv_pico_keV": 1e3 * pico.std()})
    ax.axvline(2.22437 ** 2 / (2 * 1875.613) , color="0.4", ls="--", lw=0.8)
    ax.text(2.22437 ** 2 / (2 * 1875.613) - 3e-6, ax.get_ylim()[1] * 0.95,
            "$E_\\gamma^2/2M_dc^2$ = 1.319 keV", fontsize=9, color="0.3", ha="right", va="top")
    ax.set_xlim(bordes[0], bordes[-1])
    ax.set_xlabel("Energía cinética del deuterón [MeV]")
    ax.set_ylabel("Deuterones por intervalo (2.5·10$^{-7}$ MeV)")
    ax.legend(fontsize=9, loc="upper right")
    ax.ticklabel_format(axis="x", style="plain", useOffset=False)
    guardar(fig, "fig_energia_deuterones")
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- 4. captura relativa (Campaña 1)
def fig_captura_relativa():
    t = pd.read_csv(CAPT, sep="\t", names=["carpeta", "medio", "N", "capt", "capt_tanque"])
    # La carpeta 1000000meV contiene neutrones de 10 keV (verificado con la energía del primer paso).
    energia = {c: float(c.replace("meV", "")) for c in t.carpeta.unique()}
    # Por decisión del autor, este punto se rotula como 1 keV en toda la tesis.
    energia["1000000meV"] = 1e6
    t["E_meV"] = t.carpeta.map(energia)
    pura = t[t.medio == "Agua-pura"].set_index("E_meV")
    fig, ax = plt.subplots(figsize=(9, 5.8))
    for m, mk in [("Agua+10NaCl", "D"), ("Agua+5NaCl", "s"), ("Agua+2.5NaCl", "o")]:
        s = t[t.medio == m].set_index("E_meV").sort_index()
        p = pura.loc[s.index]
        ps, pp = s.capt / s.N, p.capt / p.N
        r = s.capt / p.capt
        er = r * np.sqrt((1 - ps) / s.capt + (1 - pp) / p.capt)
        ax.errorbar(s.index, r, yerr=er, fmt=mk, ms=6, color=COLOR[m], mec="k", mew=0.5, capsize=2,
                    elinewidth=0.9, label=NOMBRE[m])
        t.loc[s.index.map(lambda E: t.index[(t.medio == m) & (t.E_meV == E)][0]), "razon"] = r.values
        t.loc[t.index[(t.medio == m)], "err_razon"] = er.reindex(t.loc[t.medio == m, "E_meV"]).values
    for x in [10, 100, 1000]:
        ax.axvline(x, color="#1f4e9c", ls="--", lw=0.9)
    for x, txt in [(3, "Fríos"), (31, "Térmicos"), (316, "Epitérmicos"), (3e4, "Intermedios")]:
        ax.text(x, 1.675, txt, ha="center", fontsize=9.5, fontweight="bold")
    ax.set_xscale("log")
    ax.set_xlim(0.6, 2e6)
    ax.set_ylim(1.05, 1.70)
    ticks = [1, 10, 100, 1e3, 1e4, 1e5, 1e6]
    ax.set_xticks(ticks)
    ax.set_xticklabels(["1 meV", "10 meV", "100 meV", "1 eV", "10 eV", "100 eV", "1 keV"])
    ax.set_xlabel("Energía del neutrón incidente")
    ax.set_ylabel(r"$\eta_\mathrm{capt\text{-}rel}=N_\mathrm{capt}(\mathrm{agua+NaCl})\,/\,N_\mathrm{capt}(\mathrm{agua\ pura})$")
    ax.legend(loc="upper right", bbox_to_anchor=(1, 0.93), fontsize=10)
    ax.grid(True, which="major", alpha=0.3)
    guardar(fig, "fig_captura_relativa")
    return t


if __name__ == "__main__":
    SAL.mkdir(parents=True, exist_ok=True)
    ajuste, n_o = fig_lineas()
    fig_niveles()
    deu = fig_deuterones()
    cap = fig_captura_relativa()
    pd.DataFrame([ajuste]).to_csv(SAL / "ajuste_linea_H.tsv", sep="\t", index=False, float_format="%.5f")
    deu.to_csv(SAL / "deuterones.tsv", sep="\t", index=False, float_format="%.5f")
    cap.to_csv(SAL / "captura_relativa.tsv", sep="\t", index=False, float_format="%.4f")
    print("capturas en 16O:", n_o)
    print(pd.DataFrame([ajuste]).to_string(index=False))
    print(deu.to_string(index=False))
    print(cap[cap.medio != "Agua-pura"].pivot(index="E_meV", columns="medio", values="razon").round(3).to_string())
