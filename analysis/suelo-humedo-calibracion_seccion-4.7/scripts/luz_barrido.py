#!/usr/bin/env python3
"""
Fotones Cherenkov aceptados y fotoelectrones por neutrón en el barrido rápido (1 keV a 1 GeV, cuatro medios).
- Fotones: MEIGA corre en modo eFast, que aplica la eficiencia cuántica al crear cada fotón óptico; el ejecucion.log de
  cada corrida registra el inicio de cada traza ("Inicio del rastreo: Particula: opticalphoton"), separada por evento
  ("### Run k starts"). Se cuentan por evento: son los fotones Cherenkov ACEPTADOS por la QE (la magnitud de la fig. 6
  de Sidelnik et al. 2020), no todos los creados.
- Fotoelectrones: Datos-simulacion/Carga-total.txt (segunda columna, en el orden de los eventos).
Se guarda un resumen por corrida en resultados/luz_barrido/<corrida>.npz (fotones y carga por evento), que basta para
rehacer tablas y figuras sin el disco.
Uso: luz_barrido.py [<carpeta del barrido> ...]
-> resultados/luz_barrido.json, informe/tablas/luz_barrido.tex, figuras/fig22_histogramas_fotones,
   fig23_histogramas_fotoelectrones, fig24_luz_vs_energia
"""
import json, os, re, subprocess, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from regiones import REGIONES

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG, TAB = (os.path.join(BASE, d) for d in ("resultados", "figuras", os.path.join("informe", "tablas")))
CACHE = os.path.join(RES, "luz_barrido"); os.makedirs(CACHE, exist_ok=True)
UNID = {"keV": 1e-3, "MeV": 1.0, "GeV": 1e3}
MEDIOS = [("AguaPura", "Agua pura", "red", "o"), ("Agua25NaCl", "Agua + 2.5 % de NaCl", "green", "s"),
          ("Agua5NaCl", "Agua + 5 % de NaCl", "purple", "D"), ("Agua10NaCl", "Agua + 10 % de NaCl", "darkorange", "^")]
AWK = r'''/^### Run [0-9]+ starts/ { if (r != "") print n; r = $3; n = 0; next }
/Inicio del rastreo: Particula: opticalphoton/ { n++ } END { if (r != "") print n }'''

for raiz in sys.argv[1:]:
    for d in sorted(os.listdir(raiz)):
        m = re.fullmatch(r"([0-9.]+)(keV|MeV|GeV)-(\w+)-(\d+)N", d)
        if not m or int(m.group(4)) < 1000: continue
        npz = os.path.join(CACHE, f"{d}.npz")
        if os.path.exists(npz): continue
        log, q = os.path.join(raiz, d, "ejecucion.log"), os.path.join(raiz, d, "Datos-simulacion", "Carga-total.txt")
        fot = np.array(subprocess.run(["mawk", AWK, log], capture_output=True, text=True, check=True,
                                      env={"LC_ALL": "C", "PATH": os.environ["PATH"]}).stdout.split(), dtype=int)
        Q = np.loadtxt(q, usecols=1, ndmin=1).astype(int)
        N = int(m.group(4))
        assert len(fot) == N == len(Q), f"{d}: {len(fot)} eventos en el log, {len(Q)} cargas, N = {N}"
        assert np.all(Q <= fot), f"{d}: hay eventos con más p.e. que fotones aceptados"
        np.savez_compressed(npz, fotones=fot, carga=Q, E_MeV=float(m.group(1)) * UNID[m.group(2)], medio=m.group(3))
        print(f"{d:28s} fotones/n {fot.mean():8.2f}  p.e./n {Q.mean():7.2f}  P(fot>0) {np.mean(fot > 0):.3f}  P(Q>=1) {np.mean(Q >= 1):.3f}")

# --- lectura de la caché ---
D = {}
for f in sorted(os.listdir(CACHE)):
    z = np.load(os.path.join(CACHE, f)); D[(str(z["medio"]), round(float(z["E_MeV"]), 6))] = (z["fotones"], z["carga"])
ENER = sorted({e for _, e in D})
def etq(E): return f"{E * 1e3:g} keV" if E < 1 else (f"{E:g} MeV" if E < 1e3 else f"{E / 1e3:g} GeV")
def err_media(x): return float(x.std(ddof=1) / np.sqrt(len(x)))
res = {}
for mr, *_ in MEDIOS:
    for E in ENER:
        if (mr, E) not in D: continue
        f, q = D[(mr, E)]
        res[f"{mr}|{E}"] = {"medio": mr, "E_MeV": E, "N": int(len(f)), "fot_media": float(f.mean()), "fot_media_err": err_media(f),
                            "pe_media": float(q.mean()), "pe_media_err": err_media(q), "P_fot": float(np.mean(f > 0)),
                            "P_pe1": float(np.mean(q >= 1)), "fot_mediana_con_luz": float(np.median(f[f > 0])) if np.any(f > 0) else 0.0,
                            "pe_por_fot": float(q.sum() / max(f.sum(), 1)), "fot_p99": float(np.percentile(f, 99))}
json.dump(res, open(os.path.join(RES, "luz_barrido.json"), "w"), indent=1)

# --- tabla ---
with open(os.path.join(TAB, "luz_barrido.tex"), "w") as fo:
    fo.write("\\begin{tabular}{l" + "rrr" * len(MEDIOS) + "}\n\\toprule\n & " +
             " & ".join(f"\\multicolumn{{3}}{{c}}{{{n.replace('Agua + ', '').replace('%', chr(92) + '%').replace(' de NaCl', '~NaCl')}}}" for _, n, *_ in MEDIOS) +
             " \\\\\n" + "".join(f"\\cmidrule(lr){{{2 + 3 * k}-{4 + 3 * k}}}" for k in range(len(MEDIOS))) +
             "\nEnergía" + " & fotones & p.e. & p.e./fot." * len(MEDIOS) + " \\\\\n\\midrule\n")
    for E in ENER:
        cel = []
        for mr, *_ in MEDIOS:
            r = res.get(f"{mr}|{E}")
            cel += [f"{r['fot_media']:.2f}" if r['fot_media'] < 100 else f"{r['fot_media']:.0f}",
                    f"{r['pe_media']:.2f}" if r['pe_media'] < 100 else f"{r['pe_media']:.0f}", f"{r['pe_por_fot']:.3f}"] if r else ["--"] * 3
        fo.write(f"{etq(E).replace(' ', '~')} & " + " & ".join(cel) + " \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")

# --- histogramas: un panel por energía, los cuatro medios superpuestos ---
def histos(clave, nombre, xlabel):
    fig, axs = plt.subplots(2, 4, figsize=(15, 7.4), sharey=True)
    for ax, E in zip(axs.flat, ENER):
        xmax = max(np.percentile(D[(mr, E)][clave], 99.9) for mr, *_ in MEDIOS if (mr, E) in D)
        B = np.unique(np.round(np.logspace(0, np.log10(max(xmax, 10) * 1.2), 31))) - 0.5
        for mr, nom, col, _ in MEDIOS:
            if (mr, E) not in D: continue
            x = D[(mr, E)][clave]; h, _ = np.histogram(x, B)
            ax.stairs(h / len(x) / np.diff(B), B, color=col, lw=1.6,
                      label=f"{nom.replace('Agua + ', '')}: {100 * np.mean(x > 0 if clave == 0 else x >= 1):.0f} %")
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(etq(E), fontsize=11); ax.grid(alpha=0.3, ls=":", which="both")
        ax.legend(fontsize=7, title="eventos con señal", title_fontsize=7, loc="lower left")
    for ax in axs[1]: ax.set_xlabel(xlabel)
    for ax in axs[:, 0]: ax.set_ylabel("Fracción de neutrones por unidad")
    fig.tight_layout()
    for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"{nombre}.{e}"), dpi=170)
    plt.close(fig)
histos(0, "fig22_histogramas_fotones", "Fotones Cherenkov aceptados por neutrón")
histos(1, "fig23_histogramas_fotoelectrones", "Fotoelectrones por neutrón")

# --- resumen frente a la energía, con las regiones de la Tabla 2.2 ---
fig, axs = plt.subplots(1, 3, figsize=(16, 5.2))
for ax in axs:
    for n, lo, hi, *_ in REGIONES:
        a, b = max(lo, 5e-4), min(hi, 2e3)
        if a >= b: continue
        if lo > 5e-4: ax.axvline(lo, color="#2b4fb3", ls="--", lw=1.0)
        ax.text(np.sqrt(a * b), 0.985, n, ha="center", va="top", fontsize=8.5, fontweight="bold", transform=ax.get_xaxis_transform())
    ax.set_xscale("log"); ax.set_xlim(5e-4, 2e3); ax.grid(alpha=0.3, ls=":", which="both"); ax.set_xlabel("Energía del neutrón [MeV]")
for mr, nom, col, mk in MEDIOS:
    E = [e for e in ENER if f"{mr}|{e}" in res]; r = [res[f"{mr}|{e}"] for e in E]
    axs[0].errorbar(E, [x["fot_media"] for x in r], yerr=[x["fot_media_err"] for x in r], fmt=mk + "-", color=col, mec="k", mew=0.5, ms=6, capsize=2, label=nom)
    axs[1].errorbar(E, [x["pe_media"] for x in r], yerr=[x["pe_media_err"] for x in r], fmt=mk + "-", color=col, mec="k", mew=0.5, ms=6, capsize=2, label=nom)
    if mr != "AguaPura":
        p = [res[f"AguaPura|{e}"] for e in E]
        rat = [x["pe_media"] / y["pe_media"] for x, y in zip(r, p)]
        er = [rr * np.sqrt((x["pe_media_err"] / x["pe_media"]) ** 2 + (y["pe_media_err"] / y["pe_media"]) ** 2) for rr, x, y in zip(rat, r, p)]
        axs[2].errorbar(E, rat, yerr=er, fmt=mk + "-", color=col, mec="k", mew=0.5, ms=6, capsize=2, label=nom)
axs[0].set_yscale("log"); axs[1].set_yscale("log")
axs[0].set_ylabel("Fotones Cherenkov aceptados por neutrón"); axs[1].set_ylabel("Fotoelectrones por neutrón")
axs[2].set_ylabel("p.e. por neutrón: NaCl / agua pura"); axs[2].axhline(1, color="0.5", lw=0.8)
for ax in axs[:2]: ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(0, 0.9))
axs[2].legend(fontsize=8, loc="upper right", bbox_to_anchor=(1, 0.9))
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig24_luz_vs_energia.{e}"), dpi=170)
plt.close(fig)
print("energías:", [etq(e) for e in ENER])
