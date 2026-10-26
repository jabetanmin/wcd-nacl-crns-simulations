#!/usr/bin/env python3
"""
Reproduce el método de comparación de los cuadernos del prototipo (Detector-prototipo/Nuevo-analisis/
Comparacion-datos-simulado.ipynb y analisis-datos-AmBe-horizontal.ipynb) y lo aplica a las corridas del montaje.

Método del cuaderno:
  experimento: carga por pulso = suma de la ventana positiva que contiene la muestra 8 de la traza (32 muestras),
               solo pulsos con pico > 1200 ADC; histogramas de 20 ADC desde 1200; neto = fuente − fondo en cuentas
               (sin normalizar por duración); agua pura desplazada −1500 ADC;
  simulación:  histograma de p.e. por evento (bins de 1 p.e.); eje x × 1000/3.95 = 253 ADC por p.e. (calibración
               antigua; el cuaderno AmBe-horizontal usa × 3000/3.95); eje y × 10 (HEIGHT_FACTOR).
Paneles: (a) cuaderno con su simulación (counts-number-photons.txt, 207 969 neutrones térmicos por medio);
         (b) mismos factores con el montaje (10^6 n, y normalizada por neutrón como en (a));
         (c) montaje con el factor común ajustado (ajuste_factor_comun.json), sin desplazar el agua pura.
-> figuras/fig11_metodo_cuaderno, resultados/metodo_cuaderno.json
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
PREV = os.path.join(BASE, "..", "Analisis-corridas-AmBe", "resultados")
SIM_CUADERNO = os.environ.get("SIM_CUADERNO", os.path.join(os.path.expanduser("~"), "Documentos", "Documetos-Jaime-Betancourt",
                              "Detector-prototipo", "Nuevo-analisis", "datos", "counts-number-photons.txt"))
X = np.load(os.path.join(PREV, "experimento_cargas.npz"))          # mismo algoritmo del cuaderno (conteos idénticos)
MED = [("pura", "pura", "Agua pura", "red", 1), ("2.5", "nacl25", "Agua + 2.5 % NaCl", "green", 2),
       ("10", "nacl10", "Agua + 10 % NaCl", "darkorange", 4)]       # última columna: columna del archivo del cuaderno
ADC_PE_CUADERNO, ALTURA, DESPLAZ = 1000 / 3.95, 10.0, 1500.0
N_CUADERNO = 207969
F = json.load(open(os.path.join(RES, "ajuste_factor_comun.json")))["ventana_trigger"]
plt.rcParams.update({"font.size": 11})

B = np.arange(1200, 60001, 20.); C = B[:-1] + 10
def exp_neto(p):
    return np.histogram(X[f"{p}_neutrones"], B)[0] - np.histogram(X[f"{p}_fondo"], B)[0]

S = np.loadtxt(SIM_CUADERNO, comments="#") if os.path.exists(SIM_CUADERNO) else None
fig, ax = plt.subplots(1, 3, figsize=(18, 5.6), sharey=True)
out = {"factores_cuaderno": {"ADC_por_pe": ADC_PE_CUADERNO, "altura": ALTURA, "desplazamiento_pura_ADC": DESPLAZ}}
for p, m, nom, col, jc in MED:
    e = exp_neto(p); c = C - (DESPLAZ if p == "pura" else 0)
    for a in ax[:2]: a.step(c, np.clip(e, 0.5, None), where="mid", color=col, lw=1, label=f"Exp: {nom}")
    ax[2].step(C, np.clip(e, 0.5, None), where="mid", color=col, lw=1, label=f"Exp: {nom}")
    if S is not None:
        ax[0].plot(S[:, 0] * ADC_PE_CUADERNO, S[:, jc] * ALTURA, "--", color=col, lw=1.8, label=f"Sim térmica: {nom}")
    q = np.load(os.path.join(RES, f"eventos_{m}.npz"))["Q"]
    h = np.bincount(q, minlength=200)[:200]
    ax[1].plot((np.arange(200) + 0.5) * ADC_PE_CUADERNO, h * ALTURA * N_CUADERNO / len(q), "--", color=col, lw=1.8, label=f"Sim montaje: {nom}")
    # (c) factor común: misma escala que la figura (bins de 20 ADC): N·h(pe)/k·20
    k, N = F["k_ADC_por_pe"], F["N_inc_300s"]
    ax[2].plot((np.arange(200) + 0.5) * k, h / len(q) * N * 20 / k, "--", color=col, lw=1.8, label=f"Sim montaje: {nom}")
    out[p] = {"exp_neto_total_cuentas": int(e.sum()), "sim_montaje_Qmedia": float(q[q >= 1].mean())}
tit = ["(a) Cuaderno: simulación térmica, 253 ADC/p.e., ×10, pura −1500 ADC",
       "(b) Mismos factores con el montaje Am-Be (entrada lateral)",
       f"(c) Montaje con factor común: {F['k_ADC_por_pe']:.0f} ADC/p.e., {F['N_inc_300s']:.2g} n, sin desplazar"]
for a, t in zip(ax, tit):
    a.set_yscale("log"); a.set_ylim(10, 1e5); a.set_xlim(0, 40000); a.grid(alpha=0.35, ls="--")
    a.set_xlabel("ADC [u.a.]"); a.set_title(t, fontsize=10); a.legend(fontsize=7.5)
ax[0].set_ylabel("Cuentas por 20 ADC (fuente − fondo)")
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig11_metodo_cuaderno.{e}"), dpi=180)
if S is not None:
    xs = S[:, 0]
    out["sim_cuaderno"] = {nom: {"N_Q_ge_1": float(S[:, jc].sum()), "Q_media": float(np.sum(xs * S[:, jc]) / S[:, jc].sum())} for _, _, nom, _, jc in MED}
json.dump(out, open(os.path.join(RES, "metodo_cuaderno.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
