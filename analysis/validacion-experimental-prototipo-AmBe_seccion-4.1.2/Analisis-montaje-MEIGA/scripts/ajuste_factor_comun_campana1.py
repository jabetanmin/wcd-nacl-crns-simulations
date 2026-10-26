#!/usr/bin/env python3
"""
Método de factores comunes aplicado a las corridas monoenergéticas de la Campaña 1 (neutrones inyectados por la tapa,
16 energías de 1 meV a 1 keV, 100 000 neutrones por corrida; Carga/<E>/Carga_Total_*.txt, una carga
por evento con señal).
Para cada energía: un factor horizontal k (ADC por p.e.) y un factor vertical N (neutrones incidentes en 300 s),
comunes a agua pura, 2.5 % y 10 % NaCl, ajustados al exceso medido (fuente − fondo, 300 s) entre 4500 y 30 000 ADC (bins sin eventos simulados = 0.5 eventos).
Además: ajuste global con un solo k para todas las energías (la ganancia del PMT es una sola) y N por energía.
-> resultados/ajuste_factor_comun_campana1.json, figuras/fig12_campana1_factor_comun (16 paneles),
   figuras/fig13_campana1_factores (k, N y rms frente a la energía)
"""
import json, os, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
PREV = os.path.join(BASE, "..", "Analisis-corridas-AmBe", "resultados")
CARGA = os.environ.get("CARGA_CAMPANA1", os.path.join(BASE, "..", "..", "Carga"))
T = json.load(open(os.path.join(PREV, "experimento_tomas.json")))
X0 = np.load(os.path.join(PREV, "experimento_cargas.npz"))
N_SIM = 100000
ENERGIAS = [1, 2.5, 5, 7, 10, 25, 50, 80, 100, 300, 500, 700, 1000, 10000, 100000, 1000000]   # meV
def etiqueta(e):
    if e >= 1e6: return "1 keV"          # convención del proyecto para la carpeta 1000000meV
    if e >= 1000: return f"{e/1000:g} eV"
    return f"{e:g} meV"
MED = [("pura", {"AP", "Pura"}, "Agua pura", "red"), ("2.5", {"A25NaCl", "25NaCl"}, "Agua + 2.5 % NaCl", "green"),
       ("10", {"A10NaCl", "10NaCl"}, "Agua + 10 % NaCl", "darkorange")]
B = np.arange(0, 40001, 250.); X = 0.5 * (B[1:] + B[:-1]); SEL = (X >= 4500) & (X < 30000)

E_EXP = {}
for p, _, _, _ in MED:
    tn, tf = T[f"{p}_neutrones"]["duracion_s"], T[f"{p}_fondo"]["duracion_s"]
    E_EXP[p] = (np.histogram(X0[f"{p}_neutrones"], B)[0] / tn - np.histogram(X0[f"{p}_fondo"], B)[0] / tf) * 300

def cargar(e):
    d = os.path.join(CARGA, (f"{e:g}" if e < 1e5 else str(int(e))) + "meV"); out = {}
    for f in os.listdir(d):
        tok = set(re.split(r"[_.]", f))
        for p, claves, _, _ in MED:
            if tok & claves:
                q = np.loadtxt(os.path.join(d, f), dtype=int, ndmin=1); out[p] = q[q > 0]
    return out

def sim_h(q, k):
    q = q.astype(float)
    adc = k * q * (1 + 0.4 * np.random.default_rng(1).standard_normal(len(q)) / np.sqrt(q))
    return np.histogram(adc, B)[0] / N_SIM                    # por neutrón incidente

def residuos(S, k):
    r = []
    for p in S:
        h = np.maximum(sim_h(S[p], k), 0.5 / N_SIM); ok = SEL & (E_EXP[p] > 10); r.append(np.log(E_EXP[p][ok] / h[ok]))   # bins sin simulación = 0.5 eventos
    return np.concatenate(r)

KS = np.arange(25, 2001, 25)
SIMS = {e: cargar(e) for e in ENERGIAS}
out = {"energias_meV": ENERGIAS, "por_energia": {}}
for e in ENERGIAS:
    best = None
    for k in KS:
        r = residuos(SIMS[e], k); lA = r.mean(); rms = float(np.sqrt(np.mean((r - lA) ** 2)))
        if best is None or rms < best[0]: best = (rms, float(k), float(np.exp(lA)))
    out["por_energia"][etiqueta(e)] = {"k_ADC_por_pe": best[1], "N_inc_300s": best[2], "rms_ln": best[0],
                                       "Q_media": {p: float(SIMS[e][p].mean()) for p in SIMS[e]}}
# ajuste global: un k para todas las energías, N libre por energía
best = None
for k in KS:
    tot = 0.0; Ns = {}
    for e in ENERGIAS:
        r = residuos(SIMS[e], k); lA = r.mean(); tot += np.sum((r - lA) ** 2) / len(r); Ns[etiqueta(e)] = float(np.exp(lA))
    if best is None or tot < best[0]: best = (tot, float(k), Ns)
kg, Ng = best[1], best[2]
out["global"] = {"k_ADC_por_pe": kg, "pe_por_1000ADC": 1000 / kg, "N_inc_300s": Ng,
                 "rms_ln": {etiqueta(e): float(np.std(residuos(SIMS[e], kg))) for e in ENERGIAS}}
json.dump(out, open(os.path.join(RES, "ajuste_factor_comun_campana1.json"), "w"), indent=2, ensure_ascii=False)

# fig12: 16 paneles con el k global y el N de cada energía
fig, axs = plt.subplots(4, 4, figsize=(18, 15), sharex=True, sharey=True)
for a, e in zip(axs.flat, ENERGIAS):
    lab = etiqueta(e)
    for p, _, nom, col in MED:
        a.plot(X, np.clip(E_EXP[p], 0.5, None), color=col, lw=0.9)
        a.plot(X, np.clip(sim_h(SIMS[e][p], kg) * Ng[lab], 1e-3, None), "--", color=col, lw=1.4)
    a.set_yscale("log"); a.set_ylim(10, 3e5); a.set_xlim(0, 40000); a.grid(alpha=0.3, ls="--")
    a.set_title(f"{lab}: N = {Ng[lab]:.2g}, rms = {out['global']['rms_ln'][lab]:.2f}", fontsize=10)
for a in axs[-1]: a.set_xlabel("ADC [u.a.]")
for a in axs[:, 0]: a.set_ylabel("Cuentas / 250 ADC (300 s)")
from matplotlib.lines import Line2D
h = [Line2D([], [], color=c, lw=1.2, ls=s) for _, _, _, c in MED for s in ("-", "--")]
l = [f"{t}: {n}" for _, _, n, _ in MED for t in ("Exp", "Sim")]
fig.legend(h, l, loc="upper center", ncol=6, fontsize=10, frameon=False)
fig.suptitle(f"Campaña 1 (inyección por la tapa) con factor común: k = {kg:.0f} ADC/p.e. para todas las energías", y=0.975, fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.955))
for x in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig12_campana1_factor_comun.{x}"), dpi=130)
plt.close(fig)

# fig13: factores frente a la energía
E_eV = np.array(ENERGIAS) / 1000; labs = [etiqueta(e) for e in ENERGIAS]
fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
ax[0].semilogx(E_eV, [out["por_energia"][x]["k_ADC_por_pe"] for x in labs], "o-", color="k", label="ajuste por energía")
ax[0].axhline(kg, color="royalblue", ls="--", label=f"global {kg:.0f}"); ax[0].axhline(126.5, color="crimson", ls=":", label="muones 126")
ax[0].set_ylabel("k [ADC por p.e.]"); ax[0].legend(fontsize=8)
ax[1].loglog(E_eV, [Ng[x] for x in labs], "o-", color="royalblue", label="N con k global")
ax[1].loglog(E_eV, [out["por_energia"][x]["N_inc_300s"] for x in labs], "s--", color="k", ms=4, label="N con k por energía")
ax[1].set_ylabel("Neutrones incidentes en 300 s"); ax[1].legend(fontsize=8)
ax[2].semilogx(E_eV, [out["global"]["rms_ln"][x] for x in labs], "o-", color="royalblue", label="k global")
ax[2].semilogx(E_eV, [out["por_energia"][x]["rms_ln"] for x in labs], "s--", color="k", ms=4, label="k por energía")
ax[2].set_ylabel("rms de ln(exp/sim)"); ax[2].legend(fontsize=8)
for a in ax: a.set_xlabel("Energía del neutrón [eV]"); a.grid(alpha=0.3, ls="--", which="both")
fig.tight_layout()
for x in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig13_campana1_factores.{x}"), dpi=150)
print(f"k global = {kg} ADC/p.e.")
for x in labs:
    r = out["por_energia"][x]
    print(f"{x:>8s}: k={r['k_ADC_por_pe']:6.0f}  N={r['N_inc_300s']:.3g}  rms={r['rms_ln']:.2f} | global: N={Ng[x]:.3g} rms={out['global']['rms_ln'][x]:.2f} | <Q> " +
          " ".join(f"{p}={v:.2f}" for p, v in r["Q_media"].items()))
