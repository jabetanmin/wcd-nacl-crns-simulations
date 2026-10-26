#!/usr/bin/env python3
"""
Histograma de carga simulado por medio y comparación con el detector prototipo.

Simulación (p.e., bins de 1 p.e.):
  (a) "Corrida AmBe": histograma de las corridas MEIGA (1 637 458 n, inyección por la tapa) —
      es exactamente datos/histogramas_comparados.txt del notebook.
  (b) "Montaje 5 min": histograma esperado en 5 min para los 373 272 neutrones del montaje
      blindado = 130 711·h_haz(ISO) + 167 963·h_halo + 74 598·h_fondo, con h_haz de las corridas
      AmBe reponderadas y h_halo/h_fondo de la Campaña 1 (histograma_carga.tsv) plegados con el
      espectro de cada componente (pesos de interpolación lineal en log E).
Experimento: carga por pulso (procesar_experimento.py), fuente - fondo NORMALIZADO POR TIEMPO
(cada toma dura 300 s salvo 10_neutrones, 240 s) y llevado a 300 s.
Calibración del notebook: p.e. = ADC_suma · 3.95 / 1000 (SHIFT_FACTOR).
-> resultados/histograma_carga_simulado.tsv, comparacion_exp_sim.json, figuras fig07-fig09
"""
import csv, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
FUENTE = os.path.abspath(os.path.join(BASE, "..", "Analisis-fuente-AmBe", "resultados"))
C1H = os.path.join(os.environ.get("REPO_TESIS", os.path.join(os.path.expanduser("~"), "Documentos", "Documetos-Jaime-Betancourt", "Repositorio-Jaime-tesis", "wt-revision-tesis")), "analysis",
                   "campana-1_respuesta-electromagnetica_seccion-4.2", "resultados_carga", "histograma_carga.tsv")
MED = {"pura": ("Agua pura", "Agua-pura", "red", "pura"), "nacl25": ("Agua + 2.5 % NaCl", "Agua+2.5NaCl", "green", "2.5"),
       "nacl10": ("Agua + 10 % NaCl", "Agua+10NaCl", "darkorange", "10")}
N_COMP = {"haz": 130711, "halo": 167963, "fondo": 74598}
PE_POR_ADC = 3.95 / 1000
T_REF = 300.0
QMAX = 200
plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "legend.fontsize": 9})

# ---- pesos ISO (mismo método que analizar_corridas.py)
E1, E2, L = np.loadtxt(os.path.join(FUENTE, "ISO8529_AmBe_digitalizado.txt"), unpack=True)
NORM = np.sum(L * np.log(E2 / E1))
def masa(a, b):
    lo, hi = np.maximum(a, E1), np.minimum(b, E2)
    return float(np.sum(np.where(hi > lo, L * np.log(np.where(hi > lo, hi / lo, 1)), 0)) / NORM)
def pesos(E0):
    u, inv, n = np.unique(np.round(E0, 5), return_inverse=True, return_counts=True)
    bd = np.concatenate([[u[0] - (u[1] - u[0]) / 2], 0.5 * (u[1:] + u[:-1]), [u[-1] + (u[-1] - u[-2]) / 2]])
    P = np.array([masa(bd[j], bd[j + 1]) for j in range(len(u))])
    return (P / (n / len(E0)))[inv]

# ---- histogramas de la Campaña 1 plegados
c1 = {}
with open(C1H) as f:
    for r in csv.DictReader(f, delimiter="\t"):
        c1.setdefault((r["medio"], r["energia"]), np.zeros(QMAX + 1))[min(int(r["carga_pe"]), QMAX)] += float(r["cuentas"])
E_meV = {}
for (m, e) in c1:
    E_meV[e] = float(e.replace("meV", ""))
def pesos_malla(espectro, Emin, Emax, n=4000):
    claves = sorted(E_meV, key=E_meV.get)
    x = np.log10([E_meV[k] * 1e-3 for k in claves])          # eV
    E = np.geomspace(Emin, Emax, n); lx = np.log10(E)
    phi = espectro(E) * E
    w = []
    for i in range(len(x)):                                    # funciones sombrero en log E (planas fuera)
        h = np.zeros_like(lx)
        if i > 0:
            s = (lx >= x[i - 1]) & (lx <= x[i]); h[s] = (lx[s] - x[i - 1]) / (x[i] - x[i - 1])
        else:
            h[lx <= x[0]] = 1
        if i < len(x) - 1:
            s = (lx >= x[i]) & (lx <= x[i + 1]); h[s] = (x[i + 1] - lx[s]) / (x[i + 1] - x[i])
        else:
            h[lx >= x[-1]] = 1
        w.append(np.trapz(h * phi, np.log(E)))
    w = np.array(w); return claves, w / w.sum()
ESP = {"halo": (lambda E: 1 / E, 0.5, 1e5), "fondo": (lambda E: E * np.exp(-E / 0.0253), 1e-4, 0.5)}

H, resumen = {}, {}
for m, (nom, mc1, col, _) in MED.items():
    d = np.load(os.path.join(RES, f"carga_{m}.npz"))
    Q = np.minimum(d["carga"], QMAX); w = pesos(d["E0"])
    h_run = np.bincount(Q, minlength=QMAX + 1).astype(float)            # conteos de la corrida
    h_haz = np.bincount(Q, weights=w, minlength=QMAX + 1) / w.sum()     # por neutrón, ISO
    comp = {"haz": h_haz}
    for c, (esp, a, b) in ESP.items():
        claves, wm = pesos_malla(esp, a, b)
        comp[c] = sum(wi * c1[(mc1, k)] / 1e5 for wi, k in zip(wm, claves))
    h5 = {c: N_COMP[c] * comp[c] for c in comp}
    h5["total"] = sum(h5.values())
    H[m] = {"corrida": h_run, **{f"5min_{c}": v for c, v in h5.items()}}
    resumen[m] = {"sim_5min_Q>=1": float(h5["total"][1:].sum()), "sim_5min_Q>=5": float(h5["total"][5:].sum()),
                  "sim_5min_Q>=10": float(h5["total"][10:].sum()),
                  "sim_corrida_Q>=1": float(h_run[1:].sum())}

with open(os.path.join(RES, "histograma_carga_simulado.tsv"), "w") as f:
    cols = ["corrida", "5min_haz", "5min_halo", "5min_fondo", "5min_total"]
    f.write("carga_pe\t" + "\t".join(f"{c}_{m}" for m in MED for c in cols) + "\n")
    for q in range(QMAX + 1):
        f.write(f"{q}\t" + "\t".join(f"{H[m][c][q]:.4f}" for m in MED for c in cols) + "\n")

# ---- experimento
X = np.load(os.path.join(RES, "experimento_cargas.npz"))
T = json.load(open(os.path.join(RES, "experimento_tomas.json")))
BW = 20; edges = np.arange(1200, 200000 + BW, BW)                       # como el notebook
EXP = {}
for m, (nom, _, _, pref) in MED.items():
    qn, qf = X[f"{pref}_neutrones"], X[f"{pref}_fondo"]
    tn, tf = T[f"{pref}_neutrones"]["duracion_s"], T[f"{pref}_fondo"]["duracion_s"]
    hn, _ = np.histogram(qn, edges); hf, _ = np.histogram(qf, edges)
    neto = (hn / tn - hf / tf) * T_REF                                   # cuentas en 300 s
    bruto_nb = hn - hf                                                   # resta del notebook
    EXP[m] = {"neto": neto, "nb": bruto_nb, "hn": hn, "hf": hf}
    pe = (edges[:-1] + BW / 2) * PE_POR_ADC
    for thr in (5, 10, 20):
        resumen[m][f"exp_5min_neto_Q>={thr}"] = float(neto[pe >= thr].sum())
    resumen[m].update({"t_fuente_s": tn, "t_fondo_s": tf, "exp_pulsos_fuente": int(len(qn)), "exp_pulsos_fondo": int(len(qf)),
                       "exp_tasa_neta_s": float(len(qn) / tn - len(qf) / tf),
                       "exp_carga_mediana_neta_pe": float(np.median(qn) * PE_POR_ADC),
                       "error_resta_notebook_pct": float(100 * (bruto_nb.sum() - neto.sum() * tn / T_REF) / max(neto.sum() * tn / T_REF, 1))})
    resumen[m]["cociente_exp/sim_Q>=5"] = resumen[m]["exp_5min_neto_Q>=5"] / resumen[m]["sim_5min_Q>=5"]
    resumen[m]["cociente_exp/sim_Q>=10"] = resumen[m]["exp_5min_neto_Q>=10"] / resumen[m]["sim_5min_Q>=10"]
json.dump(resumen, open(os.path.join(RES, "comparacion_exp_sim.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(resumen, indent=1, ensure_ascii=False))

# ---- fig07: histogramas simulados de carga (montaje 5 min) por medio y componente
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
q = np.arange(QMAX + 1)
for m, (nom, _, col, _) in MED.items():
    ax[0].plot(q[1:], H[m]["5min_total"][1:], color=col, lw=1.6, label=nom)
    ax[1].plot(q[1:], H[m]["corrida"][1:] / 1637458, color=col, lw=1.6, label=nom)
for c, ls in (("haz", "--"), ("halo", ":"), ("fondo", "-.")):
    ax[0].plot(q[1:], H["nacl10"][f"5min_{c}"][1:], color="darkorange", lw=1, ls=ls, label=f"10 % NaCl: {c}")
ax[0].set_ylabel("Eventos en 5 min por p.e."); ax[0].set_title("Montaje blindado (373 272 n, 5 min)", fontsize=10)
ax[1].set_ylabel("Fracción de neutrones incidentes"); ax[1].set_title("Corridas AmBe (inyección por la tapa)", fontsize=10)
for a in ax:
    a.set_yscale("log"); a.set_xlim(0, 120); a.set_xlabel("Carga [p.e.]"); a.grid(alpha=0.3, ls="--"); a.legend(fontsize=8)
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig07_histograma_carga_simulado.{e}"), dpi=200)
plt.close(fig)

# ---- fig08: experimento vs simulación por medio, en p.e., 5 min, normalizado por tiempo
fig, ax = plt.subplots(1, 3, figsize=(16, 4.8), sharey=True)
pe_c = (edges[:-1] + BW / 2) * PE_POR_ADC; dpe = BW * PE_POR_ADC
for a, (m, (nom, _, col, _)) in zip(ax, MED.items()):
    hn = EXP[m]["hn"] / T[f"{MED[m][3]}_neutrones"]["duracion_s"] * T_REF
    hf = EXP[m]["hf"] / T[f"{MED[m][3]}_fondo"]["duracion_s"] * T_REF
    # rebin experimental a 1 p.e. para comparar con la simulación
    b1 = np.arange(0, 201, 1)
    def reb(h): return np.histogram(pe_c, bins=b1, weights=h)[0]
    a.step(b1[:-1] + 0.5, reb(hn), where="mid", color="0.55", lw=1, label="Exp: fuente + fondo")
    a.step(b1[:-1] + 0.5, reb(hf), where="mid", color="0.3", lw=1, ls=":", label="Exp: fondo")
    a.step(b1[:-1] + 0.5, reb(EXP[m]["neto"]), where="mid", color=col, lw=1.6, label="Exp: fuente − fondo")
    a.plot(q[1:], H[m]["5min_total"][1:], "k--", lw=1.5, label="Sim: montaje 5 min")
    a.axvline(1200 * PE_POR_ADC, color="0.5", lw=0.7); a.set_title(nom, fontsize=11)
    a.set_yscale("log"); a.set_xlim(0, 120); a.set_ylim(1, 3e5); a.set_xlabel("Carga [p.e.]  (ADC·3.95/1000)")
    a.grid(alpha=0.3, ls="--"); a.legend(fontsize=8)
ax[0].set_ylabel("Cuentas en 300 s por p.e.")
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig08_experimento_vs_simulacion.{e}"), dpi=200)
plt.close(fig)

# ---- fig09: reproducción de la figura del notebook (ADC; sim ×0.3; agua pura desplazada -1500 ADC)
fig, ax = plt.subplots(figsize=(11, 7))
for m, (nom, _, col, _) in MED.items():
    c = edges[:-1] + BW / 2 - (1500 if m == "pura" else 0)
    ax.step(c, EXP[m]["nb"], where="mid", color=col, lw=1.1, label=f"Exp: {nom} (resta del notebook)")
    ax.plot(q * 1000 / 3.95, H[m]["corrida"] * 0.3, "--", color=col, lw=2, label=f"Sim: {nom} (corrida ×0.3)")
ax.set_yscale("log"); ax.set_ylim(10, 1e5); ax.set_xlim(0, 40000); ax.set_xlabel("ADC [u.a.]"); ax.set_ylabel("Cuentas [u.a.]")
ax.grid(alpha=0.3, ls="--"); ax.legend(fontsize=9)
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig09_reproduccion_notebook.{e}"), dpi=200)
plt.close(fig)

# ---- calibración relativa con la joroba de muones del fondo y número efectivo de neutrones
for m, (nom, _, _, pref) in MED.items():
    qf = X[f"{pref}_fondo"]
    h, e = np.histogram(qf, bins=np.arange(0, 200000, 2000)); c = 0.5 * (e[1:] + e[:-1])
    s = c > 20000; hs = np.convolve(h, np.ones(5) / 5, "same")
    resumen[m]["muones_pico_ADC"] = float(c[s][np.argmax(hs[s])])
    resumen[m]["muones_pico_pe"] = resumen[m]["muones_pico_ADC"] * PE_POR_ADC
    for thr in (10, 20):
        sim_n = H[m]["5min_total"][thr:].sum() / sum(N_COMP.values())
        resumen[m][f"N_efectivo_Q>={thr}"] = resumen[m][f"exp_5min_neto_Q>={thr}"] / sim_n
        resumen[m][f"N_efectivo_Q>={thr}_pct_emitidos"] = 100 * resumen[m][f"N_efectivo_Q>={thr}"] / 6.66e8
json.dump(resumen, open(os.path.join(RES, "comparacion_exp_sim.json"), "w"), indent=2, ensure_ascii=False)

# ---- fig10: comparación de FORMA (simulación normalizada al experimento en Q >= 20 p.e.)
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
b1 = np.arange(0, 201, 1)
for m, (nom, _, col, _) in MED.items():
    ne = np.histogram(pe_c, bins=b1, weights=EXP[m]["neto"])[0]
    hs = H[m]["5min_total"][:200]
    k = slice(20, 120)
    f = ne[k].sum() / hs[k].sum()
    ax[0].step(b1[:-1] + 0.5, ne, where="mid", color=col, lw=1.3, label=f"Exp: {nom}")
    ax[0].plot(b1[:-1] + 0.5, hs * f, "--", color=col, lw=1.5, label=f"Sim ×{f:.0f}")
    ax[1].plot(b1[:-1] + 0.5, ne / max(ne[k].sum(), 1), color=col, lw=1.3, label=f"Exp: {nom}")
    ax[1].plot(b1[:-1] + 0.5, H[m]["corrida"][:200] / H[m]["corrida"][k].sum(), ":", color=col, lw=1.5, label=f"Sim corrida AmBe: {nom}")
    resumen[m]["factor_forma_Q20_120"] = float(f)
for a in ax:
    a.set_yscale("log"); a.set_xlim(0, 120); a.set_xlabel("Carga [p.e.]"); a.grid(alpha=0.3, ls="--"); a.legend(fontsize=7.5)
ax[0].set_ylabel("Cuentas en 300 s por p.e."); ax[0].set_title("Simulación (montaje 5 min) escalada al experimento en 20–120 p.e.", fontsize=10)
ax[0].set_ylim(1, 3e5); ax[1].set_ylim(1e-5, 1); ax[1].set_ylabel("Normalizado a 1 en 20–120 p.e.")
ax[1].set_title("Forma: experimento vs corridas AmBe", fontsize=10)
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig10_forma_exp_vs_sim.{e}"), dpi=200)
plt.close(fig)
json.dump(resumen, open(os.path.join(RES, "comparacion_exp_sim.json"), "w"), indent=2, ensure_ascii=False)
print({m: {k: round(v, 3) for k, v in resumen[m].items() if k.startswith(("muones", "N_efectivo", "factor"))} for m in resumen})
