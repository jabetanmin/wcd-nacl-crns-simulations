#!/usr/bin/env python3
"""
Espectro de neutrones Am-Be moderados entre 10 meV y 10 eV, tomado de MEIGA, y archivo de entrada lateral.

1. Espectro: flujo por longitud de traza, φ(E) = Σ longitudes de paso / ΔE, de los neutrones del HAZ (espectro
   ISO 8529) de la corrida del montaje en agua pura, dentro del agua (pasos-neutrones.tsv; extracción con
   flujo.awk). Es el espectro de los neutrones Am-Be ya frenados por el agua.
2. Archivo: N neutrones con energías muestreadas de ese φ(E) en [E_min, E_max], que entran por el costado desde el
   plano frente al tanque (x = -R-0.1 cm, |y| <= R, 0 <= z <= H), con direcciones según la ley del coseno
   (corriente de un flujo isótropo) o, con --horizontal, todos en +x (haz paralelo ancho). Formato ARTI de MEIGA: "13 px py pz x y z C 0 0 0 0" (GeV/c, cm, pz invertido).
Uso: generar_ambe_moderado.py <tabla_flujo.tsv> [--N 207969] [--Emin 0.01] [--Emax 10] (eV) [--salida carpeta]
"""
import argparse, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from generar_irradiacion_compuesta import R, H, ZC, M_N, corta, generar

ap = argparse.ArgumentParser()
ap.add_argument("tabla", help="flujo_*.tsv: componente, log10(E/MeV), longitud de traza [cm], pasos")
ap.add_argument("--N", type=int, default=207969)
ap.add_argument("--Emin", type=float, default=0.01, help="eV")
ap.add_argument("--Emax", type=float, default=10.0, help="eV")
ap.add_argument("--componente", type=int, default=1, help="1 = haz ISO 8529 (por defecto)")
ap.add_argument("--semilla", type=int, default=20261023)
ap.add_argument("--salida", default=None)
ap.add_argument("--horizontal", action="store_true", help="haz paralelo en +x sobre toda la silueta (en vez de ley del coseno)")
ap.add_argument("--radio-haz", type=float, default=None, help="cm; con --horizontal: haz circular de este radio centrado a media altura (y=0, z=ZC)")
a = ap.parse_args()
rng = np.random.default_rng(a.semilla)

T = np.loadtxt(a.tabla)
T = T[T[:, 0] == a.componente]
lc = np.unique(T[:, 1]); w = np.round(np.diff(lc).min(), 6)
L = np.array([T[T[:, 1] == x, 2].sum() for x in lc])            # suma de las 4 partes
n_pasos = np.array([T[T[:, 1] == x, 3].sum() for x in lc])
E1, E2 = 10 ** (lc - w / 2) * 1e6, 10 ** (lc + w / 2) * 1e6     # eV
sel = (E1 >= a.Emin * 0.999) & (E2 <= a.Emax * 1.001)
# muestreo: bin con probabilidad ∝ longitud de traza (flujo integrado en el bin), uniforme en log E dentro del bin
p = L[sel] / L[sel].sum()
k = rng.choice(sel.sum(), size=a.N, p=p)
E = E1[sel][k] * (E2[sel][k] / E1[sel][k]) ** rng.random(a.N)   # eV

X_CARA = -R - 0.1
def org(m, rng):
    if a.horizontal and a.radio_haz:                          # disco de radio r centrado a media altura
        rr = a.radio_haz * np.sqrt(rng.random(m)); f = 2 * np.pi * rng.random(m)
        return np.column_stack([np.full(m, X_CARA), rr * np.cos(f), ZC + rr * np.sin(f)])
    return np.column_stack([np.full(m, X_CARA), rng.uniform(-R, R, m), rng.uniform(0, H, m)])
def dir_coseno(m, rng):
    c = np.sqrt(rng.random(m)); f = 2 * np.pi * rng.random(m); s = np.sqrt(1 - c * c)
    return np.column_stack([c, s * np.cos(f), s * np.sin(f)])
def dir_horizontal(m, rng): return np.tile([1.0, 0.0, 0.0], (m, 1))
S, u, _, acept = generar(a.N, rng, org, dir_horizontal if a.horizontal else dir_coseno, lambda n, r: np.zeros(n))
Em = E * 1e-6                                                    # MeV
P = (np.sqrt(Em * (Em + 2 * M_N)) / 1000.0)[:, None] * u
P[:, 2] *= -1                                                    # convención de MEIGA (ParticleFiller usa -pz)

nombre = f"AmBe-moderado-{a.Emin:g}-{a.Emax:g}eV-" + ((f"horizontal-mitad-r{a.radio_haz:g}cm" if a.radio_haz else "horizontal") if a.horizontal else "costado")
d = a.salida or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados", nombre)
os.makedirs(d, exist_ok=True)
ruta = os.path.join(d, f"{a.N}N-{nombre}.txt")
np.savetxt(ruta, np.column_stack([P, S, np.full(a.N, 4)]), fmt="13 %.6e %.6e %.6e %.4f %.4f %.4f %d 0 0 0 0")
np.savetxt(ruta.replace(".txt", "-componentes.txt"), np.column_stack([np.full(a.N, 4), E]), fmt="%d %.6e",
           header="componente (4 = Am-Be moderado)  E[eV]   (línea k = run_id k)")
prueba = os.path.join(d, "prueba"); os.makedirs(prueba, exist_ok=True)
for suf in (".txt", "-componentes.txt"):
    src = ruta.replace(".txt", suf); lines = open(src).read().splitlines()
    cab = [l for l in lines if l.startswith("#")]; dat = [l for l in lines if not l.startswith("#")][:30]
    open(os.path.join(prueba, os.path.basename(src).replace(f"{a.N}N", "30N")), "w").write("\n".join(cab + dat) + "\n")
np.savetxt(os.path.join(d, "espectro_flujo_MEIGA.tsv"), np.column_stack([E1, E2, L, n_pasos]), fmt="%.6e %.6e %.6g %d",
           header="E1[eV] E2[eV] longitud_traza_cm pasos  (haz ISO 8529 frenado en agua pura, corrida del montaje)")

# comprobación y figura: φ por unidad de letargia
let = L / (w * np.log(10))
fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
Ec = np.sqrt(E1 * E2)
ax[0].loglog(Ec, let / let[sel].max(), color="k", lw=1.2, label="MEIGA: haz ISO frenado en agua")
ax[0].axvspan(a.Emin, a.Emax, color="royalblue", alpha=0.1, label=f"{a.Emin:g} eV – {a.Emax:g} eV")
kT = 0.0253; Em2 = np.geomspace(1e-3, 1, 200); mx = (Em2 / kT) ** 2 * np.exp(-Em2 / kT)
ax[0].loglog(Em2, mx / mx.max() * (let[sel].max() / let[sel].max()) * let[(Ec > 0.02) & (Ec < 0.03)].mean() / let[sel].max() / (mx[(Em2 > 0.02) & (Em2 < 0.03)].mean() / mx.max()),
             "--", color="crimson", lw=1, label="maxwelliano kT = 25.3 meV (forma)")
ax[0].set_xlabel("E [eV]"); ax[0].set_ylabel("E·φ(E), normalizado"); ax[0].set_ylim(1e-3, 3); ax[0].grid(alpha=0.3, which="both", ls="--")
ax[0].legend(fontsize=8); ax[0].set_title("Espectro de flujo (por unidad de letargia)", fontsize=10)
b = np.geomspace(a.Emin, a.Emax, 61)
h = np.histogram(E, b)[0] / np.log(b[1:] / b[:-1])
ref = np.interp(np.sqrt(b[1:] * b[:-1]), Ec[sel], let[sel])
ax[1].stairs(h / h.sum(), b, color="seagreen", lw=1.4, label=f"archivo generado ({a.N:,} n)".replace(",", " "))
ax[1].plot(np.sqrt(b[1:] * b[:-1]), ref / ref.sum(), "k--", lw=1, label="MEIGA")
ax[1].set_xscale("log"); ax[1].set_xlabel("E [eV]"); ax[1].set_ylabel("Fracción por unidad de letargia")
ax[1].grid(alpha=0.3, which="both", ls="--"); ax[1].legend(fontsize=8); ax[1].set_title("Energías del archivo", fontsize=10)
fig.tight_layout()
for x in ("png", "pdf"): fig.savefig(os.path.join(d, f"espectro_{nombre}.{x}"), dpi=170)

dec = [(0.01, 0.1), (0.1, 1), (1, 10)]
res = {"archivo": os.path.basename(ruta), "N": a.N, "E_min_eV": a.Emin, "E_max_eV": a.Emax, "semilla": a.semilla,
       "componente_origen": a.componente, "aceptacion_geometrica": acept,
       "E_media_eV": float(E.mean()), "E_mediana_eV": float(np.median(E)),
       "fraccion_por_decada": {f"{x}-{y} eV": float(np.mean((E >= x) & (E < y))) for x, y in dec},
       "fraccion_del_flujo_en_rango": float(L[sel].sum() / L.sum()),
       "geometria": (f"x={X_CARA:.3f} cm; " if a.radio_haz else f"plano x={X_CARA:.3f} cm, |y|<={R}, 0<=z<={H}; ") + ((f"haz paralelo horizontal (+x), disco de radio {a.radio_haz:g} cm centrado en y=0, z={ZC} cm (media altura)" if a.radio_haz else "haz paralelo horizontal (+x)") if a.horizontal else "direcciones ley del coseno hacia +x"),
       "injectionMode": "eFromFile"}
json.dump(res, open(os.path.join(d, "resumen.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
