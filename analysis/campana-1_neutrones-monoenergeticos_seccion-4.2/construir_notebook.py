#!/usr/bin/env python3
"""Genera el notebook figuras_seccion_4.2.ipynb (sin salidas).

Uso: python3 construir_notebook.py
"""
import nbformat as nbf

celdas = []


def md(texto):
    celdas.append(nbf.v4.new_markdown_cell(texto.strip("\n")))


def code(texto):
    celdas.append(nbf.v4.new_code_cell(texto.strip("\n")))


md(r"""
# Figuras de la Sección 4.2 de la tesis (Campaña 1)

Este notebook regenera las figuras de la respuesta del WCD a neutrones monoenergéticos (Campaña 1:
16 energías × 4 medios, 100 000 neutrones por corrida, `QGSP_BERT_HP` sin $S(\alpha,\beta)$).
Solo lee los resúmenes del repositorio (`resultados/resumen_campana.tsv` y `resultados/<energía>/<medio>/resumen.json`),
que produce `procesar_campana.py` a partir de los archivos crudos del simulador.

| Figura de la tesis | Contenido |
|---|---|
| 4.17 | Pasos `Transportation` por neutrón incidente |
| 4.18 | Dispersiones elásticas (`hadElastic`) por neutrón incidente |
| 4.19, D.1–D.3 | $P(N\mid\mathrm{captura})$, número de dispersiones elásticas antes de la captura |
| 4.20–4.23, D.4–D.6 | $\rho(\xi)$ por región de energía (fría, térmica, epitérmica, intermedia) |
| 4.24 | Coeficiente de captura $\eta_\mathrm{Cap}$ |
| 4.25 | Coeficiente de reflexión por la tapa $\eta_\mathrm{Refle}$ |
| 4.26 | Transmisión y otros destinos |
| 4.27 | Ganancia relativa de captura con NaCl |
| 4.28, 4.29 y Tabla 4.9 | Longitud de captura $\lambda_\mathrm{cap}$ |
| 4.48 | Histogramas del número de fotoelectrones por evento |
| 4.50 | Fotoelectrones medios por evento detectado |
| 4.51 | Eficiencia de detección (con el CRS1000 como referencia) |

**Definiciones.**
- $N$: número de dispersiones elásticas de la cadena ininterrumpida dentro del tanque que termina en la captura.
- $\xi$ (definición de la tesis): $\xi=\ln(E_\mathrm{pre}/E_\mathrm{post})$ de cada dispersión elástica de esas cadenas;
  $\langle\xi\rangle$ y $\sigma(\xi)$ se calculan sobre todas esas colisiones. La definición inicial por historia,
  reemplazada en el estudio, no se usa aquí.
- La carpeta `1000000meV` se rotula "1 keV", como en la tesis.

**Figuras no incluidas.** Las Figs. 4.30–4.47 y 4.49 usan los datos de partículas secundarias, que no forman parte de
este procesamiento.
""")

code(r"""
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

RESULTADOS = Path("resultados")
SALIDA = Path("figuras-seccion-4.2")
SALIDA.mkdir(exist_ok=True)

ENERGIAS = ["1meV", "2.5meV", "5meV", "7meV", "10meV", "25meV", "50meV", "80meV", "100meV",
            "300meV", "500meV", "700meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
VALOR_MEV = np.array([1, 2.5, 5, 7, 10, 25, 50, 80, 100, 300, 500, 700, 1e3, 1e4, 1e5, 1e6])
ROTULO = dict(zip(ENERGIAS, ["1 meV", "2.5 meV", "5 meV", "7 meV", "10 meV", "25 meV", "50 meV", "80 meV",
                             "100 meV", "300 meV", "500 meV", "700 meV", "1 eV", "10 eV", "100 eV", "1 keV"]))
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
NOMBRE = dict(zip(MEDIOS, ["Agua pura", "Agua + 2.5 % NaCl", "Agua + 5 % NaCl", "Agua + 10 % NaCl"]))
COLOR = dict(zip(MEDIOS, ["red", "green", "purple", "darkorange"]))     # convención de la tesis
MARCA = dict(zip(MEDIOS, ["o", "s", "^", "D"]))
CORTO = dict(zip(MEDIOS, ["AP", "A25NaCl", "A5NaCl", "A10NaCl"]))

plt.rcParams.update({"font.family": "serif", "font.size": 14, "axes.labelsize": 17,
                     "legend.fontsize": 12, "axes.linewidth": 1.1})

with open(RESULTADOS / "resumen_campana.tsv") as f:
    TABLA = {(r["energia"], r["medio"]): r for r in csv.DictReader(f, delimiter="\t")}
RESUMEN = {(e, m): json.loads((RESULTADOS / e / m / "resumen.json").read_text())
           for e in ENERGIAS for m in MEDIOS}
print(len(TABLA), "corridas cargadas")
""")

code(r"""
def serie(clave, medio):
    return np.array([float(TABLA[(e, medio)][clave]) for e in ENERGIAS])


def eje_energia(ax, rotulos_region=True):
    # Eje logarítmico de energía con los límites de los regímenes frío, térmico, epitérmico e intermedio.
    ax.set_xscale("log")
    ax.set_xlim(0.7, 1.5e6)
    ax.set_xticks([1, 10, 100, 1e3, 1e4, 1e5, 1e6])
    ax.set_xticklabels(["1 meV", "10 meV", "100 meV", "1 eV", "10 eV", "100 eV", "1 keV"])
    ax.set_xlabel("Energía del neutrón incidente")
    for x in (10, 100, 1e3):
        ax.axvline(x, color="0.35", ls="--", lw=1)
    if rotulos_region:
        for x, t in [(3.2, "Fríos"), (32, "Térmicos"), (320, "Epitérmicos"), (3.2e4, "Intermedios")]:
            ax.text(x, 1.01, t, transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=12)
    ax.grid(True, axis="y", ls=":", color="0.8")


def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(SALIDA / f"{nombre}.pdf")
    fig.savefig(SALIDA / f"{nombre}.png", dpi=200)
""")

md("## Figuras 4.17 y 4.18: pasos por neutrón incidente")

code(r"""
for clave, nombre, ylabel in [
        ("media_Transportation", "fig_4_17_transportation", r"$\overline{N}_\mathrm{Trans}$ por neutrón incidente"),
        ("media_hadElastic", "fig_4_18_hadElastic", r"$\overline{N}_\mathrm{hadElastic}$ por neutrón incidente")]:
    fig, ax = plt.subplots(figsize=(10, 6))
    for m in MEDIOS:
        ax.plot(VALOR_MEV, serie(clave, m), MARCA[m], color=COLOR[m], ms=7, mec="k", mew=0.5, label=NOMBRE[m])
    ax.set_ylabel(ylabel)
    eje_energia(ax)
    ax.legend(frameon=False)
    guardar(fig, nombre)
    plt.show()
""")

md(r"""
## Figuras 4.19 y D.1–D.3: $P(N\mid\mathrm{captura})$

Como en el generador de la versión final de la figura (`Histogramas_cita_diferente_energia.ipynb`): 200 intervalos
entre 0 y 200 normalizados por el número total de capturas $N_\mathrm{capt}$; posición del máximo refinada con un
ajuste parabólico de tres puntos; FWHM con interpolación lineal de los cruces a media altura; $\langle N\rangle$ y
$\sigma$ calculados directamente con los valores de $N$ (no con el histograma).
""")

code(r"""
ENERGIAS_N = ["1meV", "10meV", "100meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
COLORES_N = ["#E41A1C", "#FF7F00", "#E6AB02", "#33A02C", "#00A6D6", "#1F4BE3", "#8E24AA"]


def histograma_N(e, m):
    # Histograma de N con 200 intervalos en [0, 200], como np.histogram en el generador original.
    cuenta = np.array(RESUMEN[(e, m)]["N_tesis"]["histograma"], dtype=float)
    cuenta = np.pad(cuenta, (0, max(0, 201 - len(cuenta))))
    h = cuenta[:200].copy()
    h[199] += cuenta[200]          # el último intervalo incluye N = 200
    return h


def media_sigma_N(e, m):
    # Media y desviación estándar (ddof = 0) de todos los valores de N, a partir de su conteo exacto.
    cuenta = np.array(RESUMEN[(e, m)]["N_tesis"]["histograma"], dtype=float)
    n = np.arange(len(cuenta))
    media = np.sum(n * cuenta) / cuenta.sum()
    return media, np.sqrt(np.sum((n - media) ** 2 * cuenta) / cuenta.sum())


def maximo_refinado(x, y):
    i = int(np.argmax(y))
    if i in (0, len(y) - 1):
        return x[i]
    a, b, _ = np.polyfit(x[i - 1:i + 2], y[i - 1:i + 2], 2)
    return x[i] if np.isclose(a, 0.0) else -b / (2 * a)


def cruce(x1, y1, x2, y2, nivel):
    return 0.5 * (x1 + x2) if np.isclose(y1, y2) else x1 + (nivel - y1) * (x2 - x1) / (y2 - y1)


def fwhm(x, y):
    i = int(np.argmax(y))
    mitad = 0.5 * y[i]
    izq = np.where(y[:i] < mitad)[0]
    xi = x[0] if len(izq) == 0 else cruce(x[izq[-1]], y[izq[-1]], x[izq[-1] + 1], y[izq[-1] + 1], mitad)
    der = np.where(y[i + 1:] < mitad)[0]
    if len(der) == 0:
        xd = x[-1]
    else:
        k = i + 1 + der[0]
        xd = cruce(x[k - 1], y[k - 1], x[k], y[k], mitad)
    return xd - xi, xi, xd, mitad


def figura_N(m, nombre):
    fig, (ax, info) = plt.subplots(1, 2, figsize=(18, 8), gridspec_kw={"width_ratios": [2.05, 1.15]})
    info.axis("off")
    centros = np.arange(200) + 0.5
    filas = []
    for e, c in zip(ENERGIAS_N, COLORES_N):
        n_capt = RESUMEN[(e, m)]["capturas"]
        p = histograma_N(e, m) / n_capt
        ax.plot(centros, p, color=c, lw=2.4, label=ROTULO[e])
        imax = int(np.argmax(p))
        xmax = maximo_refinado(centros, p)
        ancho, xi, xd, mitad = fwhm(centros, p)
        media, sigma = media_sigma_N(e, m)
        ax.scatter(xmax, p[imax], s=55, color=c, edgecolor="white", zorder=5)
        ax.hlines(mitad, xi, xd, colors=c, linestyles=(0, (5, 3)), lw=1.7)
        filas.append([ROTULO[e], f"{xmax:.2f}", f"{ancho:.1f}", f"{media:.2f}", f"{sigma:.2f}", f"{n_capt}"])
    tabla = info.table(cellText=[f[1:] for f in filas], rowLabels=[f[0] for f in filas],
                       colLabels=[r"$x_{\max}$", "FWHM", r"$\langle N\rangle$", r"$\sigma$", r"$N_\mathrm{capt}$"],
                       loc="center", cellLoc="center")
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(13)
    tabla.scale(1, 1.6)
    for (fila, col), celda in tabla.get_celld().items():
        if col == -1 and fila > 0:
            celda.set_text_props(color=COLORES_N[fila - 1], weight="bold")
    info.set_title("Parámetros de las distribuciones", fontsize=15)
    ax.set_xlabel(r"Número de dispersiones elásticas, $N$")
    ax.set_ylabel(r"$P(N\,|\,\mathrm{captura})$")
    ax.set_xlim(0, 200)
    ax.grid(True, ls="--", alpha=0.6)
    ax.legend(title="Energía inicial del neutrón", ncol=2, fontsize=12)
    ax.text(0.01, 0.98, NOMBRE[m], transform=ax.transAxes, fontsize=18, va="top",
            bbox=dict(facecolor="white", edgecolor="black", alpha=0.8))
    guardar(fig, nombre)
    plt.show()
    return filas


TABLAS_N = {}
for m, nombre in zip(MEDIOS, ["fig_4_19_N_agua_pura", "fig_D_1_N_2.5NaCl", "fig_D_2_N_5NaCl", "fig_D_3_N_10NaCl"]):
    TABLAS_N[m] = figura_N(m, nombre)
for f in TABLAS_N["Agua-pura"]:
    print(f)
""")

md(r"""
## Figuras 4.20–4.23 y D.4–D.6: $\rho(\xi)$ por región de energía

Definición de la tesis: $\xi=\ln(E_\mathrm{pre}/E_\mathrm{post})$ de cada dispersión elástica de las cadenas que
terminan en captura. Histograma de 300 intervalos entre $-2$ y $2$ normalizado a área unitaria; $\langle\xi\rangle$ y
$\sigma$ se calculan con todas las colisiones (también las que caen fuera del intervalo representado).
La tesis muestra las cuatro regiones para agua pura (Figs. 4.20–4.23) y la región fría para las soluciones
(Figs. D.4–D.6); aquí se generan las dieciséis combinaciones.
""")

code(r"""
REGIONES = {
    "fria": ["1meV", "2.5meV", "5meV", "7meV", "10meV"],
    "termica": ["10meV", "25meV", "50meV", "80meV", "100meV"],
    "epitermica": ["100meV", "300meV", "500meV", "700meV", "1000meV"],
    "intermedia": ["1000meV", "10000meV", "100000meV", "1000000meV"],
}
COLORES_XI = ["red", "green", "purple", "orange", "blue"]
FIGURA_TESIS = {("Agua-pura", "fria"): "fig_4_20", ("Agua-pura", "termica"): "fig_4_21",
                ("Agua-pura", "epitermica"): "fig_4_22", ("Agua-pura", "intermedia"): "fig_4_23",
                ("Agua+2.5NaCl", "fria"): "fig_D_4", ("Agua+5NaCl", "fria"): "fig_D_5",
                ("Agua+10NaCl", "fria"): "fig_D_6"}


def figura_xi(m, region):
    fig, ax = plt.subplots(figsize=(14, 7))
    for e, c in zip(REGIONES[region], COLORES_XI):
        x = RESUMEN[(e, m)]["xi_tesis"]
        h = x["histograma"]
        bordes = np.linspace(*h["rango"], h["bins"] + 1)
        cuenta = np.array(h["conteos"], dtype=float)
        densidad = cuenta / (cuenta.sum() * np.diff(bordes))
        centros = 0.5 * (bordes[:-1] + bordes[1:])
        ax.plot(centros, densidad, color=c, lw=2,
                label=rf"{ROTULO[e]}  ($\langle\xi\rangle={x['media']:.3f},\ \sigma={x['sigma']:.3f}$)")
    ax.set_xlabel(r"$\xi$")
    ax.set_ylabel(r"$\rho(\xi)$")
    ax.grid(True, ls="--", alpha=0.6)
    ax.legend(fontsize=13)
    ax.text(0.01, 0.98, NOMBRE[m], transform=ax.transAxes, fontsize=18, va="top",
            bbox=dict(facecolor="white", edgecolor="black", alpha=0.8))
    prefijo = FIGURA_TESIS.get((m, region), "fig_complementaria")
    guardar(fig, f"{prefijo}_xi_{CORTO[m]}_{region}")
    plt.show()


for m in MEDIOS:
    for region in REGIONES:
        figura_xi(m, region)
""")

md("## Figuras 4.24–4.27: balance de destinos y ganancia relativa de captura")

code(r"""
def figura_eta(clave, nombre, ylabel):
    fig, ax = plt.subplots(figsize=(10, 6))
    for m in MEDIOS:
        ax.errorbar(VALOR_MEV, 100 * serie(clave, m), yerr=100 * serie("u_" + clave, m), fmt=MARCA[m],
                    color=COLOR[m], ms=7, mec="k", mew=0.5, capsize=2, ecolor="k", label=NOMBRE[m])
    ax.set_ylabel(ylabel)
    eje_energia(ax)
    ax.legend(frameon=False)
    guardar(fig, nombre)
    plt.show()


figura_eta("eta_cap", "fig_4_24_captura", r"$\eta_\mathrm{Cap}=N_\mathrm{capt}/N_\mathrm{inc}$  [%]")
figura_eta("eta_refle", "fig_4_25_reflexion", r"$\eta_\mathrm{Refle}=N_\mathrm{refle}/N_\mathrm{inc}$  [%]")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.5))
for ax, clave, titulo in [(a1, "eta_trans", "(a) Salida por el fondo o los laterales"),
                          (a2, "eta_otros", "(b) No ingreso al volumen activo e interacción inelástica")]:
    for m in MEDIOS:
        ax.errorbar(VALOR_MEV, 100 * serie(clave, m), yerr=100 * serie("u_" + clave, m), fmt=MARCA[m],
                    color=COLOR[m], ms=6, mec="k", mew=0.5, capsize=2, ecolor="k", label=NOMBRE[m])
    ax.set_title(titulo, fontsize=13)
    ax.set_ylabel("% de los neutrones incidentes")
    eje_energia(ax, rotulos_region=False)
a2.legend(frameon=False)
guardar(fig, "fig_4_26_transmision_otros")
plt.show()

fig, ax = plt.subplots(figsize=(10, 6))
base = serie("eta_cap", "Agua-pura")
u_base = serie("u_eta_cap", "Agua-pura")
for m in MEDIOS[1:]:
    eta, u = serie("eta_cap", m), serie("u_eta_cap", m)
    rel = eta / base
    u_rel = rel * np.sqrt((u / eta) ** 2 + (u_base / base) ** 2)
    ax.errorbar(VALOR_MEV, rel, yerr=u_rel, fmt=MARCA[m] + "-", color=COLOR[m], ms=7, mec="k", mew=0.5,
                capsize=2, label=NOMBRE[m])
ax.axhline(1, color="0.4", lw=1)
ax.set_ylabel(r"$\eta_\mathrm{capt,rel}=\eta_\mathrm{capt}(\mathrm{NaCl})/\eta_\mathrm{capt}(\mathrm{agua})$")
eje_energia(ax)
ax.legend(frameon=False)
guardar(fig, "fig_4_27_captura_relativa")
plt.show()
""")

md(r"""
## Figuras 4.28 y 4.29 y Tabla 4.9: longitud de captura $\lambda_\mathrm{cap}$

$\lambda_\mathrm{cap}$ es la distancia en línea recta entre el punto de la primera dispersión elástica del neutrón,
en la cara interior de la tapa ($z=1330.05$ mm), y el punto de captura, para los neutrones capturados cuya primera
interacción en el agua es esa dispersión. La distribución es asimétrica, con una cola larga, y su máximo es plano o
está junto a 0 cm a baja energía; por eso se usa la **mediana** como valor representativo, con su incertidumbre por
remuestreo, y el rango intercuartílico (percentiles 25 y 75) como medida de dispersión.
""")

code(r"""
def lam(e, m, k):
    return float(TABLA[(e, m)][k])


# Figura 4.28: distribuciones a 1 keV
fig, ax = plt.subplots(figsize=(11, 6.5))
for m in MEDIOS:
    h = RESUMEN[("1000000meV", m)]["lambda_cap"]
    cuenta = np.array(h["histograma"]["conteos"], dtype=float)
    ancho = h["histograma"]["ancho"] / 10          # cm
    bordes = np.arange(len(cuenta) + 1) * ancho
    densidad = cuenta / (h["n"] * ancho)
    ax.step(bordes[:-1], densidad, where="post", color=COLOR[m], lw=1.6,
            label=rf"{NOMBRE[m]}: mediana $={h['mediana']/10:.2f}\pm{h['u_mediana']/10:.2f}$ cm")
    ax.axvline(h["mediana"] / 10, color=COLOR[m], ls="--", lw=1)
ax.set_xlim(0, 40)
ax.set_xlabel(r"$\lambda_\mathrm{cap}$ [cm]")
ax.set_ylabel(r"Densidad de probabilidad [cm$^{-1}$]")
ax.grid(True, ls=":", color="0.8")
ax.legend(fontsize=12)
ax.text(0.98, 0.55, "Neutrones de 1 keV", transform=ax.transAxes, ha="right", fontsize=14)
guardar(fig, "fig_4_28_lambda_cap_1keV")
plt.show()

# Figura 4.29: mediana y rango intercuartílico frente a la energía, con ajuste lineal en log10(E/eV)
fig, axs = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=True)
AJUSTES = {}
for ax, m in zip(axs.flat, MEDIOS):
    med = np.array([lam(e, m, "lambda_mediana_cm") for e in ENERGIAS])
    u = np.array([lam(e, m, "u_lambda_mediana_cm") for e in ENERGIAS])
    p25 = np.array([lam(e, m, "lambda_p25_cm") for e in ENERGIAS])
    p75 = np.array([lam(e, m, "lambda_p75_cm") for e in ENERGIAS])
    ax.fill_between(VALOR_MEV, p25, p75, color=COLOR[m], alpha=0.15, label="Percentiles 25–75")
    ax.errorbar(VALOR_MEV, med, yerr=u, fmt=MARCA[m], color=COLOR[m], mec="k", mew=0.5, ms=7, capsize=2,
                label="Mediana")
    x = np.log10(VALOR_MEV * 1e-3)                  # log10(E/eV)
    pend, orden = np.polyfit(x, med, 1, w=1 / u)
    r2 = 1 - np.sum((med - (pend * x + orden)) ** 2) / np.sum((med - med.mean()) ** 2)
    AJUSTES[m] = (pend, orden, r2)
    xx = np.logspace(0, 6, 100)
    ax.plot(xx, pend * np.log10(xx * 1e-3) + orden, "--", color=COLOR[m], lw=1.2,
            label=rf"$\lambda={pend:.2f}\,\log_{{10}}(E/\mathrm{{eV}})+{orden:.2f}$, $R^2={r2:.3f}$")
    ax.set_title(NOMBRE[m], fontsize=15)
    ax.set_ylabel(r"$\lambda_\mathrm{cap}$ [cm]")
    eje_energia(ax, rotulos_region=False)
    ax.legend(fontsize=10, loc="upper left")
guardar(fig, "fig_4_29_lambda_cap_vs_energia")
plt.show()
for m, (pend, orden, r2) in AJUSTES.items():
    print(f"{NOMBRE[m]:20s} pendiente {pend:.3f} cm/década  ordenada (1 eV) {orden:.2f} cm  R2 {r2:.3f}")

# Tabla 4.9 en LaTeX: mediana ± incertidumbre
filas = []
for e in ENERGIAS:
    celdas = [rf"${lam(e, m, 'lambda_mediana_cm'):.2f}\pm{lam(e, m, 'u_lambda_mediana_cm'):.2f}$" for m in MEDIOS]
    filas.append(f"{ROTULO[e]} & " + " & ".join(celdas) + r" \\")
(SALIDA / "tabla_4_9_lambda_cap.tex").write_text("\n".join(filas) + "\n")
fraccion = [int(TABLA[k]["lambda_n"]) / int(TABLA[k]["capturas"]) for k in TABLA]
print(f"Fracción de capturas incluidas: {min(fraccion):.3f}–{max(fraccion):.3f}")
""")

md(r"""
## Figuras 4.48, 4.50 y 4.51: carga y eficiencia de detección

Los archivos `Carga_Total_*.txt` contienen el número de fotoelectrones aceptados por el PMT en cada evento con señal
(no incluyen eventos con 0 fotoelectrones). Con el umbral ideal de 1 fotoelectrón, la eficiencia de detección es
$\varepsilon = N_\mathrm{det}/N_\mathrm{inc}$, con $N_\mathrm{inc}=10^5$ e incertidumbre binomial.
""")

code(r"""
ENERGIAS_Q = ["1meV", "10meV", "100meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
COLORES_Q = ["red", "green", "purple", "orange", "blue", "brown", "gray"]

# Figura 4.48: histogramas del número de fotoelectrones por evento (cuentas, intervalos de 1 fotoelectrón)
fig, axs = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=True)
for ax, m in zip(axs.flat, MEDIOS):
    for e, c in zip(ENERGIAS_Q, COLORES_Q):
        h = np.array(RESUMEN[(e, m)]["carga"]["histograma_pe"], dtype=float)
        ax.step(np.arange(len(h)), h, where="mid", color=c, lw=1.2, label=ROTULO[e])
    ax.set_yscale("log")
    ax.set_xlim(0, 200)
    ax.set_ylim(0.8, None)
    ax.set_title(NOMBRE[m], fontsize=15)
    ax.grid(True, ls=":", color="0.8")
for ax in axs[1]:
    ax.set_xlabel("Número de fotoelectrones por evento")
for ax in axs[:, 0]:
    ax.set_ylabel("Eventos")
axs[0, 1].legend(fontsize=11, title="Energía del neutrón")
guardar(fig, "fig_4_48_histogramas_carga")
plt.show()

# Figura 4.50: número medio de fotoelectrones por evento detectado
fig, ax = plt.subplots(figsize=(10, 6))
for m in MEDIOS:
    media = np.array([RESUMEN[(e, m)]["carga"]["media_pe"] for e in ENERGIAS])
    u = np.array([RESUMEN[(e, m)]["carga"]["std_pe"] / np.sqrt(RESUMEN[(e, m)]["carga"]["eventos"])
                  for e in ENERGIAS])
    ax.errorbar(VALOR_MEV, media, yerr=u, fmt=MARCA[m] + "-", color=COLOR[m], mec="k", mew=0.5, ms=7,
                lw=1, capsize=2, label=NOMBRE[m])
ax.set_ylabel(r"$\langle k\rangle$ [fotoelectrones por evento detectado]")
ax.set_ylim(0, None)
eje_energia(ax)
ax.legend(frameon=False)
guardar(fig, "fig_4_50_fotoelectrones_medios")
plt.show()

# Figura 4.51: eficiencia de detección, con las curvas del CRS1000 (Köhli et al., 2018) como referencia cualitativa
crs = {"superior": ([], []), "lateral": ([], [])}
with open("datos/eficiencia_CRS1000_Kohli2018.tsv") as f:
    for linea in f:
        if linea.startswith("#") or linea.startswith("orientacion"):
            continue
        o, E, ef = linea.split()
        crs[o][0].append(float(E))
        crs[o][1].append(float(ef))
fig, ax = plt.subplots(figsize=(12, 7))
EFICIENCIA = {}
for m in MEDIOS:
    n = np.array([RESUMEN[(e, m)]["carga"]["eventos"] for e in ENERGIAS], dtype=float)
    eps = n / 1e5
    u = np.sqrt(eps * (1 - eps) / 1e5)
    EFICIENCIA[m] = (eps, u)
    ax.errorbar(VALOR_MEV, 100 * eps, yerr=100 * u, fmt=MARCA[m] + "-", color=COLOR[m], mec="k", mew=0.5, ms=6,
                lw=1, capsize=2, label=f"{NOMBRE[m]} (este trabajo)")
for o, c in [("superior", "black"), ("lateral", "blue")]:
    ax.plot(crs[o][0], crs[o][1], ".-", color=c, lw=1, ms=4, label=f"CRS1000, orientación {o} (Köhli et al., 2018)")
ax.set_xscale("log")
ax.set_xlim(0.7, 8e10)
for x in (10, 100, 1e3):
    ax.axvline(x, color="0.35", ls="--", lw=1)
ax.set_xlabel(r"Energía del neutrón incidente, $E_n$ [meV]")
ax.set_ylabel(r"$\varepsilon(E_n,C)$ [%]")
ax.grid(True, ls=":", color="0.8")
ax.legend(fontsize=11, loc="upper right")
guardar(fig, "fig_4_51_eficiencia_deteccion")
plt.show()
for m in MEDIOS:
    eps, u = EFICIENCIA[m]
    print(f"{NOMBRE[m]:20s} eficiencia 1 meV {100*eps[0]:.2f} ± {100*u[0]:.2f} %, 1 keV {100*eps[-1]:.2f} %, "
          f"<k> 1 meV {RESUMEN[('1meV', m)]['carga']['media_pe']:.2f}, 1 keV {RESUMEN[('1000000meV', m)]['carga']['media_pe']:.2f}")
""")

md(r"""
## Verificación frente a las cifras de la tesis

Valores citados en el texto, los pies de figura y el Capítulo 5.
""")

code(r"""
def fila(desc, calculado, tesis, tol):
    ok = abs(calculado - tesis) <= tol
    print(f"{desc:55s} {calculado:12.5f} {tesis:10.4f}  {'OK' if ok else 'REVISAR'}")


T = lambda e, m, k: float(TABLA[(e, m)][k])
print(f"{'Magnitud':55s} {'calculado':>12s} {'tesis':>10s}")
fila("<N>, agua pura, 1 meV", T("1meV", "Agua-pura", "N_tesis_media"), 44.78, 0.005)
fila("<N>, agua pura, 1 keV", T("1000000meV", "Agua-pura", "N_tesis_media"), 76.78, 0.005)
fila("<xi>, agua pura, 1 eV (Fig. 4.23)", T("1000meV", "Agua-pura", "xi_media"), 0.058, 0.0005)
fila("<xi>, agua pura, 1 keV (Fig. 4.23)", T("1000000meV", "Agua-pura", "xi_media"), 0.165, 0.0005)
fila("sigma(xi), agua pura, 1 eV", T("1000meV", "Agua-pura", "xi_sigma"), 1.016, 0.0005)
fila("sigma(xi), agua pura, 1 keV", T("1000000meV", "Agua-pura", "xi_sigma"), 1.053, 0.0005)
TESIS_419 = {"1meV": (0.50, 1.8), "10meV": (0.50, 4.7), "100meV": (3.35, 19.5), "1000meV": (5.81, 29.8),
             "10000meV": (10.63, 34.2), "100000meV": (13.74, 36.0), "1000000meV": (20.37, 41.4)}
for f, e in zip(TABLAS_N["Agua-pura"], ENERGIAS_N):
    fila(f"Fig. 4.19, {ROTULO[e]}: x_max", float(f[1]), TESIS_419[e][0], 0.005)
    fila(f"Fig. 4.19, {ROTULO[e]}: FWHM", float(f[2]), TESIS_419[e][1], 0.05)
fila("eta_Cap [%], agua pura, 1 meV", 100 * T("1meV", "Agua-pura", "eta_cap"), 17.418, 0.0005)
fila("eta_Cap [%], agua pura, 1 eV", 100 * T("1000meV", "Agua-pura", "eta_cap"), 35.88, 0.005)
fila("eta_Cap [%], 10 % NaCl, 1 eV", 100 * T("1000meV", "Agua+10NaCl", "eta_cap"), 51.38, 0.005)
fila("eta_Refle [%], agua pura, 1 meV", 100 * T("1meV", "Agua-pura", "eta_refle"), 76.6, 0.05)
fila("eficiencia [%], agua pura, 1 meV (Fig. 4.51)", 100 * EFICIENCIA["Agua-pura"][0][0], 8.021, 0.0005)
fila("eficiencia [%], 10 % NaCl, 1 keV (Fig. 4.51)", 100 * EFICIENCIA["Agua+10NaCl"][0][-1], 29.259, 0.0005)
fila("ganancia relativa, 10 % NaCl, 1 meV",
     T("1meV", "Agua+10NaCl", "eta_cap") / T("1meV", "Agua-pura", "eta_cap"), 1.61, 0.005)
""")

nb = nbf.v4.new_notebook()
nb["cells"] = celdas
nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                  "language_info": {"name": "python"}}
nbf.write(nb, "figuras_seccion_4.2.ipynb")
print("figuras_seccion_4.2.ipynb:", len(celdas), "celdas")
