#!/usr/bin/env python3
"""
Coeficientes de captura, reflexión, transmisión y otros destinos del neutrón incidente en el WCD, de 1 meV a 1 GeV,
para los cuatro medios, con la definición y el formato de la Tabla 4.8 y las Tablas C.3--C.5 de la tesis, y la figura
de η_Cap con el esquema de la figura 4.24 (regiones de la Tabla 2.2, energía en meV, mismos colores y marcadores).
- 1 meV a 1 keV: Campaña 1, balance_caras_tanque.tsv del repositorio (los mismos números de la tesis; 1e5 neutrones).
- 10 keV a 1 GeV: barrido rápido, resultados/balance_rapidos.tsv (balance_rapidos.py, misma clasificación;
  1000 a 10 000 neutrones). Si todavía no existe, la figura y las tablas llegan hasta 1 keV.
Incertidumbre: binomial, sqrt(η(1-η)/N) (1σ), como en la tesis.
-> figuras/fig15_captura_wcd, informe/tablas/balance_<medio>.tex, informe/tablas/captura_wcd.tex (resumen de η_Cap),
   resultados/captura_wcd.json
"""
import csv, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from regiones import REGIONES

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG, TAB = (os.path.join(BASE, d) for d in ("resultados", "figuras", os.path.join("informe", "tablas")))
REPO = os.environ.get("REPO_TESIS", os.path.abspath(os.path.join(BASE, "..", "..")))
C1 = os.path.join(REPO, "analysis", "revision-tesis_2026-10", "resultados_balance", "balance_caras_tanque.tsv")
RAP = os.path.join(RES, "balance_rapidos.tsv")
# medio, etiqueta, color, marcador (los de la figura 4.24 de la tesis), nombre corto para archivos
MEDIOS = [("Agua-pura", "Agua pura", "red", "o", "agua_pura"), ("Agua+2.5NaCl", "Agua + 2.5 % de NaCl", "green", "s", "nacl25"),
          ("Agua+5NaCl", "Agua + 5 % de NaCl", "purple", "D", "nacl5"), ("Agua+10NaCl", "Agua + 10 % de NaCl", "darkorange", "^", "nacl10")]
K = ("eta_cap", "eta_refle", "eta_trans", "eta_otros")

def emev(etq):                                    # "2.5meV" -> 2.5; la carpeta 1000000meV es 1 keV
    return float(etq.replace("meV", ""))

D = {m: [] for m, *_ in MEDIOS}
for r in csv.DictReader(open(C1), delimiter="\t"):
    D[r["medio"]].append((emev(r["energia"]), int(r["N"]), [float(r[k]) for k in K], "Campaña 1"))
if os.path.exists(RAP):
    for r in csv.DictReader(open(RAP), delimiter="\t"):
        if float(r["E_meV"]) > 0.9999e6: D[r["medio"]].append((float(r["E_meV"]), int(r["N"]), [float(r[k]) for k in K], "barrido rápido"))
for m in D: D[m].sort(key=lambda x: (x[0], x[3] != "Campaña 1"))   # en 1 keV, primero la Campaña 1
completo = all(max(x[0] for x in D[m]) > 1e11 for m in D)
err = lambda p, n: float(np.sqrt(p * (1 - p) / n))
json.dump({m: [{"E_meV": E, "N": N, **dict(zip(K, v)), **{k + "_err": err(x, N) for k, x in zip(K, v)}, "fuente": f}
               for E, N, v, f in D[m]] for m in D}, open(os.path.join(RES, "captura_wcd.json"), "w"), indent=2, ensure_ascii=False)

def etq_E(E):
    for f, u in ((1e12, "GeV"), (1e9, "MeV"), (1e6, "keV"), (1e3, "eV"), (1, "meV")):
        if E >= f * 0.9999: return f"${E / f:g}\\,\\mathrm{{{u}}}$"
# --- figuras: η_Cap con el esquema de la figura 4.24 y η_Refle con el de la figura 4.25 de la tesis ---
EMAX = 2e12 if completo else 2e6
uni = ["1 meV", "10 meV", "100 meV", "1 eV", "10 eV", "100 eV", "1 keV", "10 keV", "100 keV", "1 MeV", "10 MeV", "100 MeV", "1 GeV"]
def figura(k, nombre, ylabel, escala, marcas, borde, ylim, leyenda):
    fig, ax = plt.subplots(figsize=(13 if completo else 10.5, 6.4))
    for n, lo, hi, *_ in REGIONES:
        a, b = max(lo * 1e9, 0.6), min(hi * 1e9, EMAX)
        if a >= b: continue
        if lo * 1e9 > 0.6: ax.axvline(lo * 1e9, color="#2b4fb3", ls="--", lw=1.1)
        ax.text(np.sqrt(a * b), 0.985, n, ha="center", va="top", fontsize=9.5 if completo else 11, fontweight="bold",
                transform=ax.get_xaxis_transform())
    for (m, nom, col, _, _), mk in zip(MEDIOS, marcas):
        for f in ("Campaña 1", "barrido rápido"):
            q = [x for x in D[m] if x[3] == f]
            if not q: continue
            ax.errorbar([x[0] for x in q], [escala * x[2][k] for x in q], yerr=[escala * err(x[2][k], x[1]) for x in q], fmt=mk,
                        color=col, ms=7, capsize=3, elinewidth=1.2, label=nom if f == "Campaña 1" else None,
                        mfc=col if f == "Campaña 1" else "white",
                        **({"mec": "k" if f == "Campaña 1" else col, "mew": 0.6 if f == "Campaña 1" else 1.4, "ecolor": "k"} if borde else {"mew": 1.4}))
    ax.set_xscale("log"); ax.set_xlim(0.6, EMAX); ax.set_ylim(*ylim)
    ax.grid(axis="y", ls=":", color="0.7"); ax.grid(axis="x", which="major", ls=":", color="0.85")
    nt = 13 if completo else 7
    ax.set_xticks(10.0 ** np.arange(nt)); ax.set_xticklabels([f"$10^{{{i}}}$\n({uni[i]})" for i in range(nt)], fontsize=9)
    ax.set_xlabel("Energía [meV]", fontsize=13); ax.set_ylabel(ylabel, fontsize=14)
    ax.legend(fontsize=11, frameon=True, edgecolor="0.2", **leyenda)
    fig.tight_layout()
    for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"{nombre}.{e}"), dpi=170)
    plt.close(fig)
ymax = max(x[2][0] for m in D for x in D[m])
figura(0, "fig15_captura_wcd", r"$\eta_{\rm Cap} = \left[\dfrac{N_{\rm capt}}{N_{\rm inc}}\right]$", 1, "osD^", False,
       (0.0 if completo else 0.10, np.ceil((ymax + 0.08) * 20) / 20),
       {"loc": "center left", "bbox_to_anchor": (0.0, 0.66)} if completo else {"loc": "lower right"})
rr = [100 * x[2][1] for m in D for x in D[m]]
figura(1, "fig16_reflexion_wcd", r"$\eta_{\rm Refle} = N_{\rm refle}/N_{\rm inc}$  [%]", 100, "Ds^o", True,
       (max(-2, np.floor(min(rr) / 5) * 5 - 5), np.ceil(max(rr) / 5) * 5 + 5), {"loc": "lower left"} if completo else {"loc": "lower right"})

# --- figura de transmisión y otros destinos con el esquema de la figura 4.26 de la tesis ---
fig, axs = plt.subplots(1, 2, figsize=(14 if completo else 13, 5.8))
for ax, k, tit, yl in ((axs[0], 2, "(a) Salida por el fondo o los laterales", r"$\eta_{\rm Trans} = N_{\rm trans}/N_{\rm inc}$  [%]"),
                       (axs[1], 3, "(b) No ingreso al volumen activo e interacción inelástica", r"$\eta_{\rm Otros} = N_{\rm otros}/N_{\rm inc}$  [%]")):
    for n, lo, hi, *_ in REGIONES:
        a, b = max(lo * 1e9, 0.6), min(hi * 1e9, EMAX)
        if a >= b: continue
        if lo * 1e9 > 0.6: ax.axvline(lo * 1e9, color="#2b4fb3", ls="--", lw=1.0)
        ax.text(np.sqrt(a * b), 0.985, n, ha="center", va="top", fontsize=8, fontweight="bold", transform=ax.get_xaxis_transform())
    for (m, nom, col, _, _), mk in zip(MEDIOS, "Ds^o"):
        for f in ("Campaña 1", "barrido rápido"):
            q = [x for x in D[m] if x[3] == f]
            if not q: continue
            ax.errorbar([x[0] for x in q], [100 * x[2][k] for x in q], yerr=[100 * err(x[2][k], x[1]) for x in q], fmt=mk, color=col,
                        ms=6, capsize=2, mec="k" if f == "Campaña 1" else col, mew=0.5 if f == "Campaña 1" else 1.3, ecolor="k",
                        label=nom if f == "Campaña 1" else None, mfc=col if f == "Campaña 1" else "white")
    vmax = max(100 * x[2][k] for m in D for x in D[m])
    ax.set_ylim(0, (0.1 if k == 2 else 7) if not completo else vmax * 1.25)
    ax.set_xscale("log"); ax.set_xlim(0.6, EMAX); ax.grid(axis="y", ls=":", color="0.7")
    nt = 13 if completo else 7
    ax.set_xticks(10.0 ** np.arange(nt)); ax.set_xticklabels([f"$10^{{{i}}}$\n({uni[i]})" for i in range(nt)], fontsize=7)
    ax.set_xlabel("Energía [meV]", fontsize=12); ax.set_ylabel(yl, fontsize=12); ax.set_title(tit, fontsize=11, pad=4)
axs[1].legend(fontsize=9, frameon=True, edgecolor="0.2", **({"loc": "center left", "bbox_to_anchor": (0.0, 0.62)} if completo else {"loc": "upper right", "bbox_to_anchor": (1, 0.9)}))
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig17_transmision_otros_wcd.{e}"), dpi=170)
plt.close(fig)

# --- figura: ganancia relativa de captura con el esquema de la figura 4.27 de la tesis ---
# η_rel = η_Cap(NaCl)/η_Cap(agua pura); corridas independientes: σ_rel = η_rel·sqrt((σ_a/η_a)² + (σ_b/η_b)²)
P = {(x[0], x[3]): x for x in D["Agua-pura"]}; REL = {}
fig, ax = plt.subplots(figsize=(13 if completo else 10.5, 6.2))
for n, lo, hi, *_ in REGIONES:
    a, b = max(lo * 1e9, 0.6), min(hi * 1e9, EMAX)
    if a >= b: continue
    if lo * 1e9 > 0.6: ax.axvline(lo * 1e9, color="#2b4fb3", ls="--", lw=1.1)
    ax.text(np.sqrt(a * b), 0.985, n, ha="center", va="top", fontsize=9.5 if completo else 11, fontweight="bold",
            transform=ax.get_xaxis_transform())
for (m, nom, col, _, _), mk in zip(MEDIOS[:0:-1], "Dso"):
    q = []
    for E, N, v, f in D[m]:
        b = P.get((E, f))
        if not b: continue
        if v[0] * N >= 20 and b[2][0] * b[1] >= 20:                   # con menos de 20 capturas el cociente no es útil
            r_ = v[0] / b[2][0]; q.append((E, r_, r_ * np.sqrt(err(v[0], N) ** 2 / v[0] ** 2 + err(b[2][0], b[1]) ** 2 / b[2][0] ** 2), f))
        else: q.append((E, float("nan"), float("nan"), f))
    REL[m] = q
    for f in ("Campaña 1", "barrido rápido"):
        qq = [x for x in q if x[3] == f]
        if qq: ax.errorbar([x[0] for x in qq], [x[1] for x in qq], yerr=[x[2] for x in qq], fmt=mk, color=col, ms=7, capsize=2,
                           mec="k" if f == "Campaña 1" else col, mew=0.6 if f == "Campaña 1" else 1.4, elinewidth=1,
                           label=nom if f == "Campaña 1" else None, mfc=col if f == "Campaña 1" else "white")
ax.axhline(1, color="0.5", lw=0.8)
ax.set_xscale("log"); ax.set_xlim(0.6, EMAX); ax.grid(ls="-", color="0.9")
vals = [x[1] for q in REL.values() for x in q if x[1] == x[1]]; ax.set_ylim(min(0.95, np.floor((min(vals) - 0.05) * 20) / 20), np.ceil((max(vals) + 0.08) * 20) / 20)
nt = 13 if completo else 7
ax.set_xticks(10.0 ** np.arange(nt)); ax.set_xticklabels(uni[:nt], fontsize=10)
ax.set_xlabel("Energía del neutrón incidente", fontsize=12)
ax.set_ylabel(r"$\eta_{\rm capt\text{-}rel} = N_{\rm capt}({\rm agua+NaCl})\,/\,N_{\rm capt}({\rm agua\ pura})$", fontsize=12)
ax.legend(fontsize=11, loc="upper right", bbox_to_anchor=(1, 0.92), frameon=True, edgecolor="0.2")
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig18_captura_relativa_wcd.{e}"), dpi=170)
plt.close(fig)
with open(os.path.join(TAB, "captura_relativa.tex"), "w") as fo:
    ms = [m for m, *_ in MEDIOS[1:]]
    fo.write("\\begin{tabular}{lr" + "r" * len(ms) + "}\n\\toprule\nRegión & Energía & " +
             " & ".join(n.replace("Agua + ", "").replace("%", "\\%").replace(" de NaCl", "~NaCl") for _, n, *_ in MEDIOS[1:]) + " \\\\\n\\midrule\n")
    prev = None
    for i, (E, _a, _b, f) in enumerate(REL[ms[0]]):
        r = next(n for n, lo, hi, *_ in REGIONES if lo * 1e9 <= E * 1.0001 and E < hi * 1e9 * 0.9999)
        if prev and (r != prev or f != REL[ms[0]][i - 1][3]): fo.write("\\midrule\n")
        fo.write(f"{r if r != prev else ''} & {etq_E(E)} & " + " & ".join(f"${REL[m][i][1]:.3f}\\pm{REL[m][i][2]:.3f}$" if REL[m][i][1] == REL[m][i][1] else "--" for m in ms) + " \\\\\n")
        prev = r
    fo.write("\\bottomrule\n\\end{tabular}\n")
for m in REL: print(m, "rel 1 meV %.3f, máx %.3f, 1 keV %.3f" % (REL[m][0][1], max(x[1] for x in REL[m]), next(x[1] for x in REL[m] if abs(x[0] - 1e6) < 1)))

# --- tablas con el formato de la Tabla 4.8 / C.3--C.5 ---
for m, nom, *_ , corto in MEDIOS:
    with open(os.path.join(TAB, f"balance_{corto}.tex"), "w") as fo:
        fo.write("\\begin{tabular}{crrrrr}\n\\toprule\n$E_n$ & $\\eta_{\\rm Cap}$ (\\%) & $\\eta_{\\rm Refle}$ (\\%) & "
                 "$\\eta_{\\rm Trans}$ (\\%) & $\\eta_{\\rm Otros}$ (\\%) & $\\sum_i \\eta_i$ \\\\\n\\midrule\n")
        for i, (E, N, v, f) in enumerate(D[m]):
            if i and f != D[m][i - 1][3]: fo.write("\\midrule\n")
            fo.write(f"{etq_E(E)} & " + " & ".join(f"${100 * x:.3f}\\pm{100 * err(x, N):.3f}$" for x in v) + f" & ${sum(v):.5f}$ \\\\\n")
        fo.write("\\bottomrule\n\\end{tabular}\n")
with open(os.path.join(TAB, "captura_wcd.tex"), "w") as fo:
    fo.write("\\begin{tabular}{llr" + "r" * len(MEDIOS) + "}\n\\toprule\nRegión & Energía & $N_{\\rm inc}$ & " +
             " & ".join(n.replace("Agua + ", "").replace("%", "\\%").replace(" de NaCl", "~NaCl") for _, n, *_ in MEDIOS) + " \\\\\n\\midrule\n")
    prev = None
    for i, (E, N, _, _) in enumerate(D["Agua-pura"]):
        r = next(n for n, lo, hi, *_ in REGIONES if lo * 1e9 <= E * 1.0001 and E < hi * 1e9 * 0.9999)
        if prev and (r != prev or D["Agua-pura"][i][3] != D["Agua-pura"][i - 1][3]): fo.write("\\midrule\n")
        fo.write(f"{r if r != prev else ''} & {etq_E(E)} & " + f"{N:,}".replace(",", "\\,") + " & " +
                 " & ".join(f"${100 * D[m][i][2][0]:.2f}\\pm{100 * err(D[m][i][2][0], D[m][i][1]):.2f}$" for m, *_ in MEDIOS) + " \\\\\n")
        prev = r
    fo.write("\\bottomrule\n\\end{tabular}\n")
with open(os.path.join(BASE, "informe", "cifras_captura.tex"), "w") as fo:
    fo.write("% generado por scripts/captura_wcd.py; no editar a mano\n\\newif\\ifbalancerapido\\balancerapido" + ("true" if completo else "false") + "\n")
print("energías por medio:", {m: len(D[m]) for m in D}, "| hasta 1 GeV:", completo)
for m, nom, *_ in MEDIOS:
    i = int(np.argmax([x[2][0] for x in D[m]])); print(f"{nom:22s} η_Cap máx {100 * D[m][i][2][0]:.2f} % en {D[m][i][0]:g} meV")
