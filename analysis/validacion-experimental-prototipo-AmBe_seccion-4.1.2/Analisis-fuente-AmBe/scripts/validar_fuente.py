#!/usr/bin/env python3
"""Valida la fuente corregida: reconstruye T desde el momento, compara con S(E)
(chi2 por bin, medias) y con la fuente original. -> figuras/fig08, resultados/validacion.json"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(AQUI, ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
DATOS = os.environ.get("FUENTE_AMBE_DATOS") or (os.path.join(BASE, "datos-entrada") if os.path.isdir(os.path.join(BASE, "datos-entrada"))
                                                 else os.path.abspath(os.path.join(BASE, "..")))   # archivos originales de la fuente


def entrada(nombre):
    """ruta de un archivo de entrada en DATOS; acepta la versión comprimida (.gz) que lleva el repositorio"""
    r = os.path.join(DATOS, nombre)
    return r if os.path.exists(r) or not os.path.exists(r + ".gz") else r + ".gz"
M_N = 939.565
arch = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".txt") else os.path.join(RES, "Fuente-AmBe241-corregida-1637458n.txt")

def T_de(ruta):
    a = np.loadtxt(ruta, usecols=(0, 1, 2, 3))
    p = 1000 * np.linalg.norm(a[:, 1:4], axis=1)
    return a[:, 0], np.sqrt(p ** 2 + M_N ** 2) - M_N

ids, T = T_de(arch)
_, T0 = T_de(entrada("Espectro-completo-neutrones-fuente-AmBe241.txt"))
Eg, Sg = np.loadtxt(os.path.join(RES, "espectro_AmBe_limpio.txt"), unpack=True)
N = len(T)
B = np.arange(0.10, 10.85 + 1e-9, 0.05)
h, _ = np.histogram(T, bins=B)
esp = np.array([np.trapz(Sg[(Eg >= a - 1e-9) & (Eg <= b + 1e-9)], Eg[(Eg >= a - 1e-9) & (Eg <= b + 1e-9)]) for a, b in zip(B[:-1], B[1:])]) * N
m = esp > 20
chi2 = float(np.sum((h[m] - esp[m]) ** 2 / esp[m])); ndf = int(m.sum())
k = np.arange(1, N + 1)
V = {"archivo": os.path.basename(arch), "neutrones": N, "ids": sorted({int(i) for i in ids}),
     "E_media_MeV": float(T.mean()), "E_media_esperada_MeV": float(np.trapz(Eg * Sg, Eg)),
     "E_media_original_MeV": float(T0.mean()),
     "chi2": chi2, "ndf": ndf, "chi2_ndf": chi2 / ndf,
     "energias_distintas": int(len(np.unique(T))),
     "E_media_primer_1pct": float(T[: N // 100].mean()),
     "E_media_primer_10pct": float(T[: N // 10].mean())}
json.dump(V, open(os.path.join(RES, "validacion.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(V, indent=1, ensure_ascii=False))

plt.rcParams.update({"font.size": 11, "axes.labelsize": 13})
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6.2), sharex=True, gridspec_kw={"height_ratios": [2.2, 1]})
a1.stairs(h / (N * 0.05), B, color="seagreen", lw=1.4, label="Fuente corregida (muestreo de $S(E)$)")
B0 = np.linspace(0, 11, 221)
h0, _ = np.histogram(T0, bins=B0)
a1.stairs(h0 / (len(T0) * np.diff(B0)), B0, color="crimson", lw=0.9, alpha=0.75, label="Fuente original")
a1.plot(Eg, Sg, color="royalblue", lw=1.8, ls="--", label="$S(E)$")
a1.set_ylabel(r"$dN/dE$ [MeV$^{-1}$]"); a1.legend(); a1.grid(alpha=0.3, ls="--")
c = 0.5 * (B[1:] + B[:-1])
a2.plot(c[m], (h[m] - esp[m]) / np.sqrt(esp[m]), ".", ms=3, color="seagreen")
a2.axhline(0, color="k", lw=0.7)
a2.set_ylabel("Residuo [$\\sigma$]"); a2.set_xlabel("$E_n$ [MeV]")
a2.text(0.02, 0.85, f"$\\chi^2$/ndf = {chi2:.0f}/{ndf}", transform=a2.transAxes)
a2.set_xlim(0, 11); a2.grid(alpha=0.3, ls="--")
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig08_validacion_fuente_corregida.{ext}"), dpi=200)
