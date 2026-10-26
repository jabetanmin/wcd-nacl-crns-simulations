#!/usr/bin/env python3
"""
Respuesta del prototipo aplicada a una corrida MEIGA: convierte la carga simulada (p.e.) en la carga que mediría la
electrónica, con las calibraciones y los efectos medidos en las trazas crudas, y la compara con el exceso medido.

Cadena por evento:
  1. Calibración ADC/p.e. con muones del MISMO detector (misma posición del PMT): pico de la VEM simulada frente al
     pico de muones de las tomas de fondo (ventana del disparo 40 358 ADC, robusto 39 458 ADC; agua pura), corregido
     por la saturación del ADC con el modelo de la forma del pulso (punto 3).
  2. Resolución de un fotoelectrón: Q_ADC = k·Q·(1 + 0.4·g/√Q), g normal.
  3. Pulso: amplitud A = Q_ADC / (Q/A), con el cociente carga/amplitud medido en los pulsos del fondo según la
     amplitud (2.97 muestras para pulsos pequeños a 4.3 para grandes). Si A supera el techo del ADC (8040), la carga
     medida es la suma recortada de la plantilla del pulso (plantilla medida en el fondo de agua pura).
  4. Disparo: se conservan los pulsos con pico > 1200 ADC (PEAK_THRESHOLD de los cuadernos del prototipo).
  5. Normalización: un factor vertical (neutrones incidentes en 300 s) común a todos los medios, ajustado al exceso
     medido (fuente − fondo) entre 4500 y 30 000 ADC.
Uso: respuesta_prototipo.py --muones <corrida muones> --medio pura <corrida> [--medio 2.5 <corrida>] [--medio 10 <corrida>]
     (una corrida = carpeta con parte*/Datos-simulacion/Carga-total.txt, o un .npz con el arreglo Q)
     [--etiqueta texto] [--k-libre]   (--k-libre: además ajusta k común, como el método de los cuadernos)
     [--salida carpeta]   (carpeta con resultados/ y figuras/; por defecto, la de este análisis)
     [--sin-panel-muones]   (con --k-libre: la figura muestra solo el ajuste libre)
-> resultados/respuesta_prototipo_<etiqueta>.json, figuras/fig14_respuesta_prototipo_<etiqueta>
"""
import argparse, glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
PREV = os.path.join(BASE, "..", "Analisis-corridas-AmBe", "resultados")
# --- medidas en las trazas crudas del prototipo (pura_fondo.dat, 8 ns por muestra; ver informe, sec. de saturación) ---
PLANTILLA = np.array([0.08, 0.64, 1.00, 0.77, 0.56, 0.42, 0.22, 0.11, 0.06, 0.02])   # pulso normalizado al pico
TECHO_ADC = 8040.0                                                                   # recorte del ADC
QA_AMPL = np.array([1200, 2000, 3000, 4000, 5000, 6000, 7000, 7990])                 # amplitud [ADC]
QA_VAL = np.array([2.97, 3.23, 3.91, 4.18, 4.29, 4.30, 4.33, 4.29])                  # carga/amplitud [muestras]
PICO_MUONES_EXP = {"ventana_trigger": 40357.6, "robusto": 39458.0}                   # pico de muones, fondo agua pura
UMBRAL_PICO = 1200.0
MED = {"pura": ("Agua pura", "red"), "2.5": ("Agua + 2.5 % NaCl", "green"), "10": ("Agua + 10 % NaCl", "darkorange")}
B = np.arange(0, 60001, 250.); X = 0.5 * (B[1:] + B[:-1]); SEL = (X >= 4500) & (X < 30000)

def cargas(ruta):
    if ruta.endswith(".npz"):
        return np.load(ruta)["Q"].astype(int)
    fs = sorted(glob.glob(os.path.join(ruta, "parte*", "Datos-simulacion", "Carga-total.txt")))
    if not fs: raise SystemExit(f"no hay parte*/Datos-simulacion/Carga-total.txt en {ruta}")
    return np.concatenate([[int(l.split()[1]) for l in open(f) if l.strip()] for f in fs])

def qa(A):                                   # cociente carga/amplitud medido, función de la amplitud
    return np.interp(A, QA_AMPL, QA_VAL, left=QA_VAL[0], right=QA_VAL[-1])

def digitalizar(q_pe, k, rng):
    """carga simulada [p.e.] -> (carga medida [ADC], pasa el disparo)"""
    q = q_pe.astype(float); ok = q > 0
    Q = np.zeros_like(q); Q[ok] = k * q[ok] * (1 + 0.4 * rng.standard_normal(ok.sum()) / np.sqrt(q[ok]))
    Q = np.clip(Q, 0, None)
    A = Q / qa(Q / 4.0)                      # amplitud verdadera (iteración simple: Q/A depende de A)
    A = Q / qa(A)
    sat = A > TECHO_ADC
    Qm = Q.copy()
    if sat.any():                            # pulso recortado: suma de min(A·plantilla, techo), escalada a la carga lineal
        lin = (A[sat, None] * PLANTILLA[None, :]).sum(1)
        rec = np.minimum(A[sat, None] * PLANTILLA[None, :], TECHO_ADC).sum(1)
        Qm[sat] = Q[sat] * rec / lin
    return Qm, np.minimum(A, TECHO_ADC) > UMBRAL_PICO

def pico(x, bins):
    h, e = np.histogram(x, bins=bins); c = 0.5 * (e[1:] + e[:-1])
    hs = np.convolve(h, np.ones(5) / 5, "same"); i = np.argmax(hs); j = slice(max(i - 3, 0), i + 4)
    a, b, _ = np.polyfit(c[j], hs[j], 2)
    return float(-b / (2 * a)) if a < 0 else float(c[i])

ap = argparse.ArgumentParser()
ap.add_argument("--muones", required=True)
ap.add_argument("--medio", nargs=2, action="append", metavar=("MEDIO", "CORRIDA"), required=True)
ap.add_argument("--etiqueta", default="corrida")
ap.add_argument("--k-libre", action="store_true")
ap.add_argument("--salida", default=None)
ap.add_argument("--sin-panel-muones", action="store_true")
a = ap.parse_args()
if a.salida:
    RES, FIG = (os.path.join(os.path.abspath(a.salida), d) for d in ("resultados", "figuras"))
rng = np.random.default_rng(7)

# 1. calibración: k tal que el pico de muones simulado, ya digitalizado (con saturación), caiga en el pico medido
qmu = cargas(a.muones); qmu = qmu[qmu > 0]
cal = {}
for met, objetivo in PICO_MUONES_EXP.items():
    best = None
    for k in np.arange(60, 400, 0.5):
        Qm, _ = digitalizar(qmu, k, np.random.default_rng(3))
        d = abs(pico(Qm, np.arange(15000, 120000, 1000)) - objetivo)
        if best is None or d < best[0]: best = (d, float(k))
    cal[met] = {"ADC_por_pe": best[1], "pe_por_1000ADC": 1000 / best[1], "VEM_sim_pe": pico(qmu, np.arange(0, qmu.max() + 10, 5))}
print("calibración con muones:", json.dumps(cal))

T = json.load(open(os.path.join(PREV, "experimento_tomas.json")))
out = {"etiqueta": a.etiqueta, "calibracion": cal, "corridas": {m: r for m, r in a.medio}, "muones": a.muones, "metodos": {}}
Qs = {m: cargas(r) for m, r in a.medio}
for met, arch in (("ventana_trigger", "experimento_cargas.npz"), ("robusto", "cargas_robustas.npz")):
    Xd = np.load(os.path.join(PREV, arch)); E = {}
    for m in Qs:
        tn, tf = T[f"{m}_neutrones"]["duracion_s"], T[f"{m}_fondo"]["duracion_s"]
        E[m] = (np.histogram(Xd[f"{m}_neutrones"], B)[0] / tn - np.histogram(Xd[f"{m}_fondo"], B)[0] / tf) * 300
    def hist(k):
        H = {}
        for m, q in Qs.items():
            Qm, disp = digitalizar(q, k, np.random.default_rng(11))
            H[m] = np.histogram(Qm[disp], B)[0] / len(q)          # por neutrón incidente
        return H
    def ajuste_N(H):
        r = np.concatenate([np.log(E[m][SEL & (E[m] > 10)] / np.maximum(H[m], 0.5 / len(Qs[m]))[SEL & (E[m] > 10)]) for m in Qs])
        return float(np.exp(r.mean())), float(np.std(r))
    k_mu = cal[met]["ADC_por_pe"]; H = hist(k_mu); N, rms = ajuste_N(H)
    res = {"k_ADC_por_pe": k_mu, "N_inc_300s": N, "rms_ln": rms,
           "fraccion_disparo": {m: float(np.mean(digitalizar(q, k_mu, np.random.default_rng(11))[1])) for m, q in Qs.items()}}
    curvas = {"muones": (k_mu, N, H)}
    if a.k_libre:
        best = None
        for k in np.arange(50, 2001, 25):
            Hk = hist(k); Nk, rk = ajuste_N(Hk)
            if best is None or rk < best[1]: best = (k, rk, Nk, Hk)
        res["k_libre"] = {"k_ADC_por_pe": float(best[0]), "N_inc_300s": best[2], "rms_ln": best[1],
                          "fraccion_disparo": {m: float(np.mean(digitalizar(q, best[0], np.random.default_rng(11))[1])) for m, q in Qs.items()}}
        curvas["libre"] = (best[0], best[2], best[3])
        if a.sin_panel_muones: del curvas["muones"]
    out["metodos"][met] = res
    if met == "ventana_trigger":
        fig, axs = plt.subplots(1, len(curvas), figsize=(7.5 * len(curvas), 5.4), squeeze=False, sharey=True)
        for ax, (nom, (k, N, H)) in zip(axs[0], curvas.items()):
            for m in Qs:
                ax.plot(X, np.clip(E[m], 0.5, None), color=MED[m][1], lw=1, label=f"Exp: {MED[m][0]}")
                ax.plot(X, np.clip(H[m] * N, 1e-3, None), "--", color=MED[m][1], lw=1.6, label=f"Sim: {MED[m][0]}")
            ax.axvline(TECHO_ADC * PLANTILLA.sum(), color="0.5", lw=0.7, ls=":")
            ax.set_yscale("log"); ax.set_ylim(10, 3e5); ax.set_xlim(0, 45000); ax.grid(alpha=0.3, ls="--")
            ax.set_xlabel("Carga [ADC]")
            ax.set_title(("Calibración con muones" if nom == "muones" else "Factor horizontal libre") +
                         f": {k:.0f} ADC/p.e., N = {N:.2g}", fontsize=10)
            ax.legend(fontsize=7.5)
        axs[0][0].set_ylabel("Cuentas en 300 s por 250 ADC (fuente − fondo)")
        fig.suptitle(f"Respuesta del prototipo aplicada a la simulación ({a.etiqueta}): resolución, saturación y disparo", fontsize=11)
        fig.tight_layout()
        for x in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig14_respuesta_prototipo_{a.etiqueta}.{x}"), dpi=170)
json.dump(out, open(os.path.join(RES, f"respuesta_prototipo_{a.etiqueta}.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(out["metodos"], indent=1, ensure_ascii=False))
