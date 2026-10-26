#!/usr/bin/env python3
"""
Análisis del espectro de la fuente de neutrones 241Am-Be usada como entrada de MEIGA.

Lee los archivos de la carpeta Simulacion-fuente-241AmBe (sin modificarlos) y:
  1. Diagnostica la digitalización principal (espectro-neutrones-Am-Be-241-clean.txt):
     orden, duplicados, valores negativos y puntos espurios.
  2. Construye un espectro limpio S(E) (densidad de probabilidad, MeV^-1).
  3. Reconstruye el espectro realmente cargado en MEIGA
     (Espectro-completo-neutrones-fuente-AmBe241.txt) a partir de los momentos
     y lo compara con S(E): sesgo por la densidad de puntos digitalizados,
     espectro discreto y orden del archivo.
  4. Revisa la segunda digitalización (Datos-originales-...): eje y invertido.
  5. Revisa los archivos de "referencia" (AmBe_IAEA.txt, AmBe_ISO8529_spectrum.txt,
     AmBe_neutron_spectrum.txt).
Resultados numéricos -> resultados/resumen.json ; espectro limpio -> resultados/
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(AQUI, ".."))
DATOS = os.environ.get("FUENTE_AMBE_DATOS") or (os.path.join(BASE, "datos-entrada") if os.path.isdir(os.path.join(BASE, "datos-entrada"))
                                                 else os.path.abspath(os.path.join(BASE, "..")))   # archivos originales de la fuente


def entrada(nombre):
    """ruta de un archivo de entrada en DATOS; acepta la versión comprimida (.gz) que lleva el repositorio"""
    r = os.path.join(DATOS, nombre)
    return r if os.path.exists(r) or not os.path.exists(r + ".gz") else r + ".gz"
RES = os.path.join(BASE, "resultados")
FIG = os.path.join(BASE, "figuras")
os.makedirs(RES, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

M_N = 939.565          # MeV/c^2, el mismo valor usado en simulacion-241-AmBe.ipynb
E_MEDIA_ISO = 4.16     # MeV, energía media de fluencia del espectro ISO 8529-1 (241Am-Be)

plt.rcParams.update({"font.size": 11, "axes.labelsize": 13, "legend.fontsize": 10,
                     "xtick.labelsize": 11, "ytick.labelsize": 11,
                     "axes.formatter.use_locale": False})


def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, nombre + ".png"), dpi=200)
    fig.savefig(os.path.join(FIG, nombre + ".pdf"))
    plt.close(fig)


def media(E, w):
    return float(np.sum(E * w) / np.sum(w))


def momento_a_T(p_GeV):
    p = p_GeV * 1000.0
    return np.sqrt(p ** 2 + M_N ** 2) - M_N


R = {}

# ----------------------------------------------------------------------------
# 1. Digitalización principal
# ----------------------------------------------------------------------------
dig = np.loadtxt(entrada("espectro-neutrones-Am-Be-241-clean.txt"), delimiter=";")
E_d, y_d = dig[:, 0], dig[:, 1]
n_d = len(E_d)
R["digitalizacion"] = {
    "puntos": n_d,
    "energias_distintas": int(len(np.unique(E_d))),
    "pasos_hacia_atras_en_E": int(np.sum(np.diff(E_d) < 0)),
    "pares_repetidos_exactos": int(n_d - len(np.unique(dig, axis=0))),
    "valores_negativos": int(np.sum(y_d < 0)),
    "E_min": float(E_d.min()), "E_max": float(E_d.max()),
}

# Rechazo de puntos espurios: mediana local (vecinos a +-0.15 MeV, sin el propio punto)
orden = np.argsort(E_d, kind="stable")
Es, ys = E_d[orden], y_d[orden]
VENT = 0.15
med = np.empty_like(ys)
mad = np.empty_like(ys)
for i, e in enumerate(Es):
    sel = (np.abs(Es - e) <= VENT)
    sel[i] = False
    v = ys[sel]
    med[i] = np.median(v)
    mad[i] = 1.4826 * np.median(np.abs(v - med[i]))
UMBRAL = np.maximum(3.5 * mad, 1.0e-4)
espurio_s = np.abs(ys - med) > UMBRAL
espurio = np.zeros(n_d, bool)
espurio[orden] = espurio_s
R["digitalizacion"]["puntos_espurios"] = int(espurio.sum())
R["digitalizacion"]["peso_espurio_pct"] = float(100 * np.abs(y_d[espurio]).sum() / np.abs(y_d).sum())
R["digitalizacion"]["indices_espurios"] = [int(i) for i in np.where(espurio)[0]]

# Espectro limpio: promedio de puntos válidos en bins de 0.05 MeV, interpolado
ok = ~espurio
Ec, yc = E_d[ok], np.clip(y_d[ok], 0, None)
DB = 0.05
bordes = np.arange(0.10, 10.95 + 1e-9, DB)
cent = 0.5 * (bordes[1:] + bordes[:-1])
idx = np.digitize(Ec, bordes) - 1
prom = np.array([yc[idx == k].mean() if np.any(idx == k) else np.nan for k in range(len(cent))])
v = ~np.isnan(prom)
S_bin = np.interp(cent, cent[v], prom[v])
# Suavizado ligero (3 bins, núcleo binomial) para quitar el ruido de digitalización
S_bin = np.convolve(np.pad(S_bin, 1, mode="edge"), [0.25, 0.5, 0.25], mode="valid")
# Malla fina, extremo superior forzado a cero (último punto digitalizado y<=0 a 10.9 MeV)
Eg = np.linspace(0.10, 10.95, 2171)        # paso 5 keV
Sg = np.clip(np.interp(Eg, cent, S_bin), 0, None)
Sg[Eg >= 10.85] = 0.0
Sg /= np.trapz(Sg, Eg)
np.savetxt(os.path.join(RES, "espectro_AmBe_limpio.txt"), np.column_stack([Eg, Sg]),
           fmt="%.5f %.6e", header="E[MeV]  S(E)[1/MeV] (normalizado a 1 entre 0.10 y 10.95 MeV)")

cdf = np.concatenate([[0], np.cumsum(0.5 * (Sg[1:] + Sg[:-1]) * np.diff(Eg))])
R["espectro_limpio"] = {
    "E_media_MeV": float(np.trapz(Eg * Sg, Eg)),
    "E_mediana_MeV": float(np.interp(0.5, cdf, Eg)),
    "E_moda_MeV": float(Eg[np.argmax(Sg)]),
    "E_rms_MeV": float(np.sqrt(np.trapz(Eg ** 2 * Sg, Eg))),
}
# Máximos locales (en S_bin suavizado) para ubicar la estructura
from scipy.signal import find_peaks
pk, _ = find_peaks(np.interp(Eg, cent, S_bin), prominence=5e-5, distance=40)
R["espectro_limpio"]["picos_MeV"] = [round(float(Eg[k]), 2) for k in pk]
bandas = [(0.1, 1), (1, 2), (2, 4), (4, 6), (6, 8), (8, 11)]
R["espectro_limpio"]["fraccion_bandas_pct"] = {
    f"{a}-{b}": round(float(100 * np.trapz(Sg[(Eg >= a) & (Eg <= b)], Eg[(Eg >= a) & (Eg <= b)])), 2)
    for a, b in bandas}

# ----------------------------------------------------------------------------
# 2. Fuente realmente cargada en MEIGA
# ----------------------------------------------------------------------------
ruta_fuente = entrada("Espectro-completo-neutrones-fuente-AmBe241.txt")
fuente = np.loadtxt(ruta_fuente)
N = len(fuente)
T = momento_a_T(fuente[:, 3])
cols_ctes = np.delete(fuente, 3, axis=1)
R["fuente_meiga"] = {
    "archivo": os.path.basename(ruta_fuente).removesuffix(".gz"),
    "neutrones": int(N),
    "id_corsika_unicos": sorted({int(x) for x in fuente[:, 0]}),
    "todas_las_demas_columnas_cero_salvo_id": bool(np.all(cols_ctes[:, 1:] == 0)),
    "direccion": "+z (px = py = 0)",
    "energias_distintas": int(len(np.unique(np.round(T, 6)))),
    "E_media_MeV": float(T.mean()),
    "E_min_MeV": float(T.min()), "E_max_MeV": float(T.max()),
}
# Coherencia con el archivo de energías intermedio
e_txt = np.loadtxt(entrada("Espectro-energia-neutrones-AmBe-241.txt"))
R["fuente_meiga"]["max_dif_T_vs_archivo_energias_keV"] = float(1000 * np.max(np.abs(np.sort(T) - np.sort(e_txt))))
# Peso de los puntos espurios y negativos en la fuente
frec = np.loadtxt(entrada("espectro_procesado_frecuencia_redondeado.txt"))
R["fuente_meiga"]["neutrones_de_puntos_espurios"] = int(frec[espurio, 1].sum())
R["fuente_meiga"]["neutrones_de_valores_negativos_abs"] = int(frec[y_d < 0, 1].sum())
# Sesgo de orden: el archivo sigue el orden de la digitalización
orden_info = {}
for frac in (0.01, 0.10, 0.25, 0.50):
    k = int(frac * N)
    orden_info[f"{int(frac*100)}%"] = {"E_media": round(float(T[:k].mean()), 3),
                                       "E_max": round(float(T[:k].max()), 3)}
R["fuente_meiga"]["primeras_lineas"] = orden_info

# Comparación por bins de 0.25 MeV: fuente vs espectro limpio
B = np.arange(0.0, 11.0 + 1e-9, 0.25)
h_f, _ = np.histogram(T, bins=B)
dens_f = h_f / (N * np.diff(B))
dens_l = np.array([np.trapz(Sg[(Eg >= a) & (Eg <= b)], Eg[(Eg >= a) & (Eg <= b)]) / (b - a)
                   for a, b in zip(B[:-1], B[1:])])
# Densidad de puntos digitalizados (válidos) por bin
h_pts, _ = np.histogram(Ec, bins=B)
cB = 0.5 * (B[1:] + B[:-1])
with np.errstate(divide="ignore", invalid="ignore"):
    razon = np.where(dens_l > 0, dens_f / dens_l, np.nan)
R["sesgo_bins_0.25MeV"] = {
    "razon_fuente/limpio_min": float(np.nanmin(razon[cB < 10.5])),
    "razon_fuente/limpio_max": float(np.nanmax(razon[cB < 10.5])),
    "correlacion_razon_vs_puntos_por_bin": float(np.corrcoef(razon[(cB > 0.25) & (cB < 10.5)],
                                                             h_pts[(cB > 0.25) & (cB < 10.5)])[0, 1]),
}
np.savetxt(os.path.join(RES, "comparacion_bins_0.25MeV.txt"),
           np.column_stack([cB, dens_f, dens_l, razon, h_pts]),
           fmt="%.3f %.5e %.5e %.4f %d",
           header="E_centro[MeV] dens_fuente_MEIGA[1/MeV] dens_limpia[1/MeV] razon puntos_digitalizados")

# ----------------------------------------------------------------------------
# 3. Segunda digitalización (Datos-originales / Funcion-espectro-final)
# ----------------------------------------------------------------------------
d2 = np.loadtxt(entrada("Datos-mejorados-segunda-toma-espectro-AmBe-241.txt"), delimiter=";")
E2, y2 = d2[:, 0], d2[:, 1]
fin = np.loadtxt(entrada("Funcion-espectro-AmBe-241-final.txt"))
S_ref2 = np.interp(E2, Eg, Sg)                # forma limpia en sus energías
# Hipótesis: eje y calibrado al revés -> y_real = C - y. Ajuste lineal y = a + b*S
A = np.column_stack([np.ones_like(E2), S_ref2])
coef, *_ = np.linalg.lstsq(A, y2, rcond=None)
corr_inv = float(np.corrcoef(y2, S_ref2)[0, 1])
corr_rev = float(np.corrcoef(fin[:, 1], np.interp(fin[:, 0], Eg, Sg))[0, 1])
C = float(np.max(y2) + np.min(y2))             # suma de extremos ~ tope del eje
y2_corr = C - y2
corr_corr = float(np.corrcoef(y2_corr, S_ref2)[0, 1])
R["segunda_digitalizacion"] = {
    "puntos": int(len(E2)),
    "correlacion_original_vs_limpio": corr_inv,
    "ajuste_y=a+b*S": {"a": float(coef[0]), "b": float(coef[1])},
    "correlacion_columna_invertida_(notebook)_vs_limpio": corr_rev,
    "C=ymax+ymin": C,
    "correlacion_(C-y)_vs_limpio": corr_corr,
}

# ----------------------------------------------------------------------------
# 4. Archivos de referencia
# ----------------------------------------------------------------------------
refs = {}
for fn in ("AmBe_IAEA.txt", "AmBe_ISO8529_spectrum.txt", "AmBe_neutron_spectrum.txt"):
    a = np.loadtxt(entrada(fn))
    x, s = a[:, 0], a[:, 1]
    d1 = np.diff(s)
    refs[fn] = {
        "puntos": int(len(x)),
        "paso_E_MeV": sorted({round(float(t), 4) for t in np.diff(x)}),
        "E_media_MeV": float(np.trapz(x * s, x) / np.trapz(s, x)),
        "maximos_locales": int(np.sum((d1[:-1] > 0) & (d1[1:] < 0))),
        "valor_en_Emax": float(s[-1]),
    }
R["referencias"] = refs

with open(os.path.join(RES, "resumen.json"), "w") as f:
    json.dump(R, f, indent=2, ensure_ascii=False)

# ----------------------------------------------------------------------------
# Figuras
# ----------------------------------------------------------------------------
# fig01: digitalización y puntos espurios
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.plot(E_d[ok], 1e3 * y_d[ok], ".", ms=4, color="0.45", label=f"Puntos digitalizados válidos ({ok.sum()})")
ax.plot(E_d[espurio], 1e3 * y_d[espurio], "x", ms=7, mew=1.6, color="crimson",
        label=f"Puntos espurios rechazados ({espurio.sum()})")
norma_d = np.trapz(S_bin, cent)
ax.plot(Eg, 1e3 * Sg * norma_d, "-", lw=2, color="royalblue", label="Espectro limpio $S(E)$ (reescalado)")
ax.axhline(0, color="k", lw=0.6)
ax.set_xlabel("$E_n$ [MeV]")
ax.set_ylabel(r"Cuentas/n [$10^{-3}$ u.a.]")
ax.set_xlim(0, 11.2)
ax.grid(alpha=0.3, ls="--")
ax.legend(loc="upper right")
guardar(fig, "fig01_digitalizacion_espurios")

# fig02: orden de la digitalización (índice vs energía)
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(np.arange(n_d), E_d, "-", lw=0.7, color="0.6")
ax.plot(np.arange(n_d)[ok], E_d[ok], ".", ms=3, color="0.3", label="válido")
ax.plot(np.arange(n_d)[espurio], E_d[espurio], "x", ms=6, color="crimson", label="espurio")
ax.set_xlabel("Índice de línea en el archivo digitalizado")
ax.set_ylabel("$E_n$ [MeV]")
ax.grid(alpha=0.3, ls="--")
ax.legend()
guardar(fig, "fig02_orden_digitalizacion")

# fig03: fuente MEIGA vs espectro limpio + razón
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6.4), sharex=True, gridspec_kw={"height_ratios": [2.2, 1]})
a1.stairs(dens_f, B, color="crimson", lw=1.6, label="Fuente cargada en MEIGA (1 637 458 n)")
a1.stairs(dens_l, B, color="royalblue", lw=1.6, ls="--", label="Espectro limpio $S(E)$")
a1.set_ylabel(r"$dN/dE$ normalizado [MeV$^{-1}$]")
a1.legend()
a1.grid(alpha=0.3, ls="--")
a2.plot(cB, razon, "o-", ms=4, color="k", label="fuente / limpio")
a2b = a2.twinx()
a2b.stairs(h_pts, B, color="darkorange", alpha=0.7, label="puntos digitalizados por bin")
a2b.set_ylabel("puntos/bin", color="darkorange")
a2.axhline(1, color="royalblue", lw=0.8)
a2.set_ylabel("Razón")
a2.set_xlabel("$E_n$ [MeV]")
a2.set_xlim(0, 11)
a2.set_ylim(0.4, 1.8)
a2.grid(alpha=0.3, ls="--")
guardar(fig, "fig03_fuente_vs_limpio")

# fig04: espectro discreto de la fuente (bins finos) -> origen de los picos del "suavizado"
fig, ax = plt.subplots(figsize=(8, 4.2))
Bf = np.linspace(0, 11, 601)
h, _ = np.histogram(T, bins=Bf)
ax.stairs(h / (N * np.diff(Bf)), Bf, color="crimson", lw=0.8, label="Fuente MEIGA, 600 bins (como en el notebook)")
ax.plot(Eg, Sg, color="royalblue", lw=2, label="Espectro limpio $S(E)$")
ax.set_xlabel("$E_n$ [MeV]")
ax.set_ylabel(r"$dN/dE$ [MeV$^{-1}$]")
ax.set_xlim(0, 11)
ax.grid(alpha=0.3, ls="--")
ax.legend()
guardar(fig, "fig04_fuente_discreta")

# fig05: segunda digitalización
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
a1.plot(E2, 1e3 * y2, ".", ms=3, color="0.5", label="Datos-originales (tal cual)")
a1.plot(fin[:, 0], 1e3 * fin[:, 1], ".", ms=3, color="darkorange", label="Columna 2 invertida (notebook)")
a1.plot(E2, 1e3 * y2_corr, ".", ms=3, color="seagreen", label=r"Corregida: $y' = C - y$")
a1.set_xlabel("$E_n$ [MeV]")
a1.set_ylabel(r"[$10^{-3}$ u.a.]")
a1.legend(fontsize=9)
a1.grid(alpha=0.3, ls="--")
a2.plot(E_d[ok], 1e3 * y_d[ok], ".", ms=3, color="0.6", label="Digitalización principal")
y2_lin = (coef[0] - y2) / (-coef[1]) * norma_d     # inversión lineal ajustada, misma escala
a2.plot(E2, 1e3 * y2_lin, "-", lw=1.6, color="seagreen", label=r"Segunda digitalización, $y'=(a-y)/|b|$")
a2.set_xlabel("$E_n$ [MeV]")
a2.legend(fontsize=9)
a2.grid(alpha=0.3, ls="--")
guardar(fig, "fig05_segunda_digitalizacion")

# fig06: referencias
fig, ax = plt.subplots(figsize=(8, 4.6))
ax.plot(Eg, Sg, color="royalblue", lw=2.2, label=f"Espectro limpio, $\\langle E\\rangle$={R['espectro_limpio']['E_media_MeV']:.2f} MeV")
estilos = {"AmBe_IAEA.txt": ("k", "--"), "AmBe_ISO8529_spectrum.txt": ("purple", ":"),
           "AmBe_neutron_spectrum.txt": ("darkorange", "-.")}
for fn, (c, ls) in estilos.items():
    a = np.loadtxt(entrada(fn))
    s = a[:, 1] / np.trapz(a[:, 1], a[:, 0])
    ax.plot(a[:, 0], s, color=c, ls=ls, lw=1.8, label=f"{fn}, $\\langle E\\rangle$={refs[fn]['E_media_MeV']:.2f} MeV")
ax.axvline(E_MEDIA_ISO, color="0.3", lw=0.8)
ax.text(E_MEDIA_ISO + 0.05, ax.get_ylim()[1] * 0.93, "4.16 MeV\n(ISO 8529-1)", fontsize=9, color="0.3")
ax.set_xlabel("$E_n$ [MeV]")
ax.set_ylabel(r"$S(E)$ [MeV$^{-1}$]")
ax.set_xlim(0, 11.2)
ax.set_ylim(bottom=0)
ax.grid(alpha=0.3, ls="--")
ax.legend(fontsize=8.5, loc="upper right")
guardar(fig, "fig06_referencias")

# fig07: sesgo de orden
fig, ax = plt.subplots(figsize=(8, 4.0))
k = np.arange(1, N + 1)
paso = 2000
ax.plot(k[::paso] / N * 100, (np.cumsum(T) / k)[::paso], color="crimson", lw=1.8,
        label="Archivo original (orden de digitalización)")
rng = np.random.default_rng(1)
Tm = rng.permutation(T)
ax.plot(k[::paso] / N * 100, (np.cumsum(Tm) / k)[::paso], color="royalblue", lw=1.8,
        label="Mismo archivo barajado")
ax.set_xlabel("Fracción del archivo leída [%]")
ax.set_ylabel(r"$\langle E\rangle$ de los primeros neutrones [MeV]")
ax.set_xscale("log")
ax.grid(alpha=0.3, ls="--", which="both")
ax.legend()
guardar(fig, "fig07_sesgo_orden")

print(json.dumps(R, indent=1, ensure_ascii=False)[:6000])
