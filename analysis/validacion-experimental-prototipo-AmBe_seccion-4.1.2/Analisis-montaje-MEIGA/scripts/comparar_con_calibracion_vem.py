#!/usr/bin/env python3
"""
Experimento vs simulación del montaje con la calibración por muones (calibracion_vem.json):
(a) tasas por banda de carga en la toma con fuente y en la de fondo (la región de muones debe restarse a cero),
(b) espectro del exceso (fuente − fondo, 300 s) frente a la predicción absoluta de MEIGA para 1 Ci en 5 min,
(c) longitud de caída exponencial del exceso (ADC) frente a la simulada (p.e.): calibración "por forma".
-> resultados/comparacion_calibracion_vem.json, figuras fig07_bandas_fuente_fondo, fig08_exceso_vs_meiga
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
PREV = os.path.join(BASE, "..", "Analisis-corridas-AmBe", "resultados")
T = json.load(open(os.path.join(PREV, "experimento_tomas.json")))
V = json.load(open(os.path.join(RES, "calibracion_vem.json")))
C = V["resumen"]["pe_por_1000ADC_media"] / 1000                     # p.e. por ADC
VEM = V["simulacion"]["Q_pico"]
MED = {"pura": ("Agua pura", "red", "pura"), "2.5": ("Agua + 2.5 % NaCl", "green", "nacl25"),
       "10": ("Agua + 10 % NaCl", "darkorange", "nacl10")}
N_MODELO = {1: 130711, 2: 167963, 3: 74598}                          # haz, halo, fondo en 5 min, 1 Ci
BANDAS = [(0, 23), (23, 50), (50, 100), (100, 200), (200, 280), (280, 400), (400, 800)]
plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "legend.fontsize": 9})

def sim_absoluta(m, bins):
    """Histograma de carga de MEIGA esperado en 300 s para el modelo de 1 Ci (haz/halo/fondo)."""
    f = os.path.join(RES, f"eventos_{m}.npz")
    if not os.path.exists(f):
        return None, None
    e = np.load(f); h = np.zeros(len(bins) - 1)
    for k, n in N_MODELO.items():
        s = e["comp"] == k
        h += np.histogram(e["Q"][s], bins)[0] * n / s.sum()
    return h, e["Q"]

def caida(x, h, lo, hi):
    s = (x >= lo) & (x < hi) & (h > 0)
    return float(-1 / np.polyfit(x[s], np.log(h[s]), 1)[0])

out = {"pe_por_ADC": C, "VEM_pe": VEM, "umbral_disparo_pe": 3000 * C, "metodos": {}}
for met, arch in (("ventana_trigger", "experimento_cargas.npz"), ("robusto", "cargas_robustas.npz")):
    X = np.load(os.path.join(PREV, arch)); r = {}
    for p, (nom, col, m) in MED.items():
        qn, qf = X[f"{p}_neutrones"] * C, X[f"{p}_fondo"] * C
        tn, tf = T[f"{p}_neutrones"]["duracion_s"], T[f"{p}_fondo"]["duracion_s"]
        bandas = []
        for a, b in BANDAS:
            rn, rf = np.sum((qn >= a) & (qn < b)) / tn, np.sum((qf >= a) & (qf < b)) / tf
            bandas.append({"pe": [a, b], "fuente_por_s": float(rn), "fondo_por_s": float(rf), "cociente": float(rn / rf) if rf else None})
        B = np.arange(0, 60001, 500); x = 0.5 * (B[1:] + B[:-1])
        h = np.histogram(X[f"{p}_neutrones"], B)[0] / tn - np.histogram(X[f"{p}_fondo"], B)[0] / tf
        r[p] = {"bandas": bandas, "exceso_23_200pe_por_s": float(sum(z["fuente_por_s"] - z["fondo_por_s"] for z in bandas[1:4])),
                "caida_exceso_ADC_4k_10k": caida(x, h, 4000, 10000), "caida_exceso_ADC_10k_20k": caida(x, h, 10000, 20000)}
        hs, q = sim_absoluta(m, np.arange(0, 200))
        if hs is not None:
            xs = np.arange(199).astype(float)
            Ls = caida(xs, hs, 2, 8)
            r[p]["sim"] = {"caida_pe_2_8": Ls, "fraccion_Q_ge_umbral": float(np.mean(q >= 3000 * C)),
                           "eventos_300s_Q_ge_umbral": float(hs[int(np.ceil(3000 * C)):].sum()),
                           "pe_por_1000ADC_por_forma": 1000 * Ls / r[p]["caida_exceso_ADC_4k_10k"]}
            r[p]["exceso_sobre_sim_Q_ge_umbral"] = float((r[p]["exceso_23_200pe_por_s"] * 300) / max(r[p]["sim"]["eventos_300s_Q_ge_umbral"], 1e-9))
    out["metodos"][met] = r
json.dump(out, open(os.path.join(RES, "comparacion_calibracion_vem.json"), "w"), indent=2, ensure_ascii=False)

# fig07: espectros de las tomas con fuente y de fondo en p.e. (calibración por muones)
X = np.load(os.path.join(PREV, "experimento_cargas.npz"))
fig, ax = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
b = np.arange(0, 900, 5)
for a, (p, (nom, col, _)) in zip(ax, MED.items()):
    tn, tf = T[f"{p}_neutrones"]["duracion_s"], T[f"{p}_fondo"]["duracion_s"]
    a.stairs(np.histogram(X[f"{p}_neutrones"] * C, b)[0] / tn, b, color=col, lw=1.4, label="toma con fuente")
    a.stairs(np.histogram(X[f"{p}_fondo"] * C, b)[0] / tf, b, color="k", lw=1.1, ls="--", label="toma de fondo")
    a.axvline(3000 * C, color="0.5", lw=0.8); a.axvline(VEM, color="royalblue", lw=0.8, ls=":", label=f"VEM simulado ({VEM:.0f} p.e.)")
    a.set_yscale("log"); a.set_xlabel(f"Carga [p.e.] (× {1000*C:.2f} p.e./kADC)"); a.set_title(nom, fontsize=10)
    a.grid(alpha=0.3, ls="--"); a.legend(fontsize=8)
    t = a.secondary_xaxis("top", functions=(lambda v: v / VEM, lambda v: v * VEM)); t.set_xlabel("VEM")
ax[0].set_ylabel("Tasa [s$^{-1}$ por 5 p.e.]")
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig07_bandas_fuente_fondo.{e}"), dpi=200)
plt.close(fig)

# fig08: exceso medido vs predicción absoluta de MEIGA (1 Ci, 5 min)
Xr = np.load(os.path.join(PREV, "cargas_robustas.npz"))
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
b = np.arange(0, 200, 1)
for p, (nom, col, m) in MED.items():
    tn, tf = T[f"{p}_neutrones"]["duracion_s"], T[f"{p}_fondo"]["duracion_s"]
    ex = (np.histogram(Xr[f"{p}_neutrones"] * C, b)[0] / tn - np.histogram(Xr[f"{p}_fondo"] * C, b)[0] / tf) * 300
    ax[0].stairs(np.clip(ex, 0.5, None), b, color=col, lw=1.3, label=f"exceso medido, {nom}")
    hs, _ = sim_absoluta(m, b)
    if hs is not None:
        ax[0].stairs(np.clip(hs, 1e-3, None), b, color=col, lw=1.3, ls="--", label=f"MEIGA 1 Ci, {nom}")
ax[0].axvline(3000 * C, color="0.5", lw=0.8)
ax[0].text(3000 * C + 2, 3e5, "disparo\n≈3000 ADC", fontsize=8, color="0.3", va="top")
ax[0].set_yscale("log"); ax[0].set_ylim(1e-2, 1e6); ax[0].set_xlabel("Carga [p.e.] (calibración por muones)")
ax[0].set_ylabel("Eventos en 300 s por p.e."); ax[0].grid(alpha=0.3, ls="--"); ax[0].legend(fontsize=8)
ax[0].set_title("Exceso (fuente − fondo) vs predicción absoluta", fontsize=10)
# forma normalizada: exceso en ADC vs simulación en p.e., cada uno escalado a su longitud de caída
R = out["metodos"]["robusto"]
for p, (nom, col, m) in MED.items():
    tn, tf = T[f"{p}_neutrones"]["duracion_s"], T[f"{p}_fondo"]["duracion_s"]
    B = np.arange(3000, 40001, 500); x = 0.5 * (B[1:] + B[:-1])
    h = np.histogram(Xr[f"{p}_neutrones"], B)[0] / tn - np.histogram(Xr[f"{p}_fondo"], B)[0] / tf
    ax[1].plot(x / 1000, np.clip(h / h.max(), 1e-4, None), color=col, lw=1.3, label=f"{nom}: L = {R[p]['caida_exceso_ADC_4k_10k']:.0f} ADC")
ax[1].set_yscale("log"); ax[1].set_xlabel("Carga [kADC]"); ax[1].set_ylabel("Exceso normalizado")
ax[1].set_title("Forma del exceso medido (cambia poco con el NaCl)", fontsize=10)
ax[1].grid(alpha=0.3, ls="--"); ax[1].legend(fontsize=8)
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig08_exceso_vs_meiga.{e}"), dpi=200)
plt.close(fig)
print(json.dumps({k: {p: {kk: vv for kk, vv in v.items() if kk != "bandas"} for p, v in r.items()} for k, r in out["metodos"].items()}, indent=1, ensure_ascii=False))
