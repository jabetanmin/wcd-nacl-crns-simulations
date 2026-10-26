#!/usr/bin/env python3
"""
Comparación experimento–simulación con el método de factores comunes: un solo factor horizontal k (ADC por
p.e., la ganancia del PMT) y un solo factor vertical (neutrones incidentes en 300 s) para los tres medios. Se
ajustan sobre el exceso medido (fuente − fondo) entre 4500 y 30 000 ADC, en escala logarítmica; los bins sin eventos simulados cuentan como 0.5 eventos. La carga
simulada se convierte a ADC con una resolución de 1 p.e. del 40 %.
Se compara con k de la calibración por muones (127 ADC/p.e. con el PMT en la tapa): con ese k se ajusta solo el factor
vertical, y se dan el residuo, la fracción de bins con simulación y la distancia de forma (KS) por medio.
Uso: ajuste_factor_comun.py [--eventos pura nacl25 nacl10] [--calibracion calibracion_vem.json] [--etiqueta texto]
     [--salida carpeta]   (sin argumentos: el montaje con el PMT en la tapa, como antes)
-> <salida>/ajuste_factor_comun[_<etiqueta>].json, figuras fig10_ajuste_factor_comun[_<etiqueta>], fig10b_…
"""
import argparse, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ap = argparse.ArgumentParser()
ap.add_argument("--eventos", nargs=3, default=["pura", "nacl25", "nacl10"], metavar=("PURA", "NACL25", "NACL10"),
                help="etiquetas de resultados/eventos_<etiqueta>.npz")
ap.add_argument("--calibracion", default="calibracion_vem.json")
ap.add_argument("--etiqueta", default="")
ap.add_argument("--salida", default=None, help="carpeta con resultados/ y figuras/ (por defecto, la de este análisis)")
a = ap.parse_args()
SAL = os.path.abspath(a.salida) if a.salida else BASE
RES, FIG = os.path.join(SAL, "resultados"), os.path.join(SAL, "figuras")
SUF = f"_{a.etiqueta}" if a.etiqueta else ""
PREV = os.path.join(BASE, "..", "Analisis-corridas-AmBe", "resultados")
T = json.load(open(os.path.join(PREV, "experimento_tomas.json")))
MED = [("pura", a.eventos[0], "Agua pura", "red"), ("2.5", a.eventos[1], "Agua + 2.5 % NaCl", "green"),
       ("10", a.eventos[2], "Agua + 10 % NaCl", "darkorange")]
B = np.arange(0, 40001, 250.); X = 0.5 * (B[1:] + B[:-1]); SEL = (X >= 4500) & (X < 30000)
K_MUONES = 1000 / json.load(open(os.path.join(RES, a.calibracion)))["resumen"]["pe_por_1000ADC_media"]
N_MODELO = 373272                                            # neutrones al tanque en 5 min, 1 Ci (modelo)

def sim_h(q, k, semilla=1):
    n = len(q); q = q[q > 0].astype(float)
    adc = k * q * (1 + 0.4 * np.random.default_rng(semilla).standard_normal(len(q)) / np.sqrt(q))
    return np.histogram(adc, B)[0] / n                        # por neutrón incidente

def ks_forma(e, h):                                           # distancia KS entre las formas (área 1) en el intervalo
    ok = SEL & (e > 0); e = np.clip(e[ok], 0, None); h = h[ok]
    if h.sum() <= 0 or e.sum() <= 0: return 1.0
    return float(np.max(np.abs(np.cumsum(e) / e.sum() - np.cumsum(h) / h.sum())))

def ajustar(E, S, ks):
    best = None
    for k in ks:
        r = []
        for p in E:
            h = np.maximum(sim_h(S[p], k), 0.5 / len(S[p])); ok = SEL & (E[p] > 10); r.append(np.log(E[p][ok] / h[ok]))   # bins sin simulación = 0.5 eventos
        r = np.concatenate(r); lA = r.mean(); rms = float(np.sqrt(np.mean((r - lA) ** 2)))
        if best is None or rms < best[0]: best = (rms, float(k), float(np.exp(lA)))
    return best

out = {"k_muones_ADC_por_pe": K_MUONES, "N_modelo_5min": N_MODELO}
for met, arch in (("ventana_trigger", "experimento_cargas.npz"), ("robusto", "cargas_robustas.npz")):
    Xd = np.load(os.path.join(PREV, arch)); E, S = {}, {}
    for p, m, _, _ in MED:
        tn, tf = T[f"{p}_neutrones"]["duracion_s"], T[f"{p}_fondo"]["duracion_s"]
        E[p] = (np.histogram(Xd[f"{p}_neutrones"], B)[0] / tn - np.histogram(Xd[f"{p}_fondo"], B)[0] / tf) * 300
        S[p] = np.load(os.path.join(RES, f"eventos_{m}.npz"))["Q"]
    rms, k, N = ajustar(E, S, np.arange(25, 2001, 25))
    propio = {}
    for p in E:
        h = np.maximum(sim_h(S[p], k), 0.5 / len(S[p])); ok = SEL & (E[p] > 10); propio[p] = float(np.exp(np.mean(np.log(E[p][ok] / h[ok]))))
    # con la calibración por muones: mejor factor vertical común y su residuo
    r = []
    for p in E:
        h = sim_h(S[p], K_MUONES); ok = SEL & (E[p] > 10) & (h > 0); r.append(np.log(E[p][ok] / h[ok]) if ok.any() else np.array([]))
    nbins_mu = int(sum(len(x) for x in r))
    nbins_sel = int(sum((SEL & (E[p] > 10)).sum() for p in E))
    rms_mu, _, N_mu = ajustar(E, S, [K_MUONES])               # mismo criterio que el ajuste libre, con k fijo
    frac_mu = {p: float(np.mean(sim_h(S[p], K_MUONES)[SEL & (E[p] > 10)] > 0)) for p in E}
    out[met + "_muones"] = {"k_ADC_por_pe": K_MUONES, "N_inc_300s": N_mu, "rms_ln": rms_mu,
                            "fraccion_bins_con_simulacion": frac_mu,
                            "ks_forma": {p: ks_forma(E[p], sim_h(S[p], K_MUONES)) for p in E}}
    out[met] = {"ks_forma": {p: ks_forma(E[p], sim_h(S[p], k)) for p in E}, "bins_en_intervalo": nbins_sel,
                "k_ADC_por_pe": k, "pe_por_1000ADC": 1000 / k, "N_inc_300s": N, "rms_ln": rms,
                "N_inc_propio_con_k_comun": propio, "N_inc_sobre_modelo_1Ci": N / N_MODELO,
                "bins_con_simulacion_si_k_muones": nbins_mu}
    if met == "ventana_trigger":
        fig, ax = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
        for a_, kk, NN, tit in ((ax[0], K_MUONES, N_mu, f"k = {K_MUONES:.0f} ADC/p.e. (muones), N = {N_mu:.2g}"),
                               (ax[1], k, N, f"k = {k:.0f} ADC/p.e. (ajuste común), N = {N:.2g}")):
            for p, m, nom, col in MED:
                a_.plot(X, np.clip(E[p], 0.5, None), color=col, lw=1, label=f"Exp: {nom}")
                a_.plot(X, np.clip(sim_h(S[p], kk) * NN, 1e-3, None), "--", color=col, lw=1.5, label=f"Sim: {nom}")
            a_.set_yscale("log"); a_.set_ylim(10, 3e5); a_.set_xlim(0, 40000); a_.grid(alpha=0.3, ls="--")
            a_.set_xlabel("ADC"); a_.set_title(tit, fontsize=10)
        ax[0].set_ylabel("Cuentas en 300 s por 250 ADC (fuente − fondo)"); ax[1].legend(fontsize=8)
        fig.tight_layout()
        for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig10_ajuste_factor_comun{SUF}.{e}"), dpi=200)
json.dump(out, open(os.path.join(RES, f"ajuste_factor_comun{SUF}.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))

# fig10b: un solo panel, con el formato de los cuadernos del prototipo (factor común ajustado)
R = out["ventana_trigger"]; k, N = R["k_ADC_por_pe"], R["N_inc_300s"]
Xd = np.load(os.path.join(PREV, "experimento_cargas.npz"))
plt.rcParams.update({"font.size": 15})
fig, ax = plt.subplots(figsize=(12, 8))
for p, m, nom, col in reversed(MED):
    tn, tf = T[f"{p}_neutrones"]["duracion_s"], T[f"{p}_fondo"]["duracion_s"]
    E = (np.histogram(Xd[f"{p}_neutrones"], B)[0] / tn - np.histogram(Xd[f"{p}_fondo"], B)[0] / tf) * 300
    ax.plot(X, np.clip(E, 0.5, None), color=col, lw=1.3, label=f"Exp: {nom}")
for p, m, nom, col in MED:
    q = np.load(os.path.join(RES, f"eventos_{m}.npz"))["Q"]
    ax.plot(X, np.clip(sim_h(q, k) * N, 1e-3, None), "--", color=col, lw=2, label=f"Sim: {nom}")
ax.set_yscale("log"); ax.set_ylim(10, 3e5); ax.set_xlim(0, 40000)
ax.set_xlabel("ADC [u.a.]"); ax.set_ylabel("Cuentas en 300 s por 250 ADC (fuente − fondo)")
ax.set_title(f"MEIGA {a.etiqueta or 'montaje'} con factor común: {k:.0f} ADC/p.e. y {N:.2g} neutrones", fontsize=14)
ax.grid(alpha=0.4, ls="--"); ax.legend(fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(FIG, f"fig10b_histogramas_factor_comun{SUF}.png"), dpi=110); fig.savefig(os.path.join(FIG, f"fig10b_histogramas_factor_comun{SUF}.pdf"))
