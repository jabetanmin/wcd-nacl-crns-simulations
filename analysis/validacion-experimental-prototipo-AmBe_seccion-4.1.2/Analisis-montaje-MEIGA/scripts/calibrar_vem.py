#!/usr/bin/env python3
"""
Calibración p.e./ADC del prototipo con muones: compara la carga simulada de muones verticales (VEM) en MEIGA
(mismo detector y PMT que el montaje Am-Be) con el pico de muones del fondo medido en cada toma de fondo.
Uso: calibrar_vem.py <carpeta 2000N-muones-VEM-...> [etiqueta]
-> resultados/calibracion_vem[_etiqueta].json, figuras/fig05_calibracion_vem[_etiqueta]
   (sin etiqueta: la calibración principal, PMT en la tapa; p. ej. etiqueta 'pmtbajo' para el PMT bajado)
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = sys.argv[1]
SUF = f"_{sys.argv[2]}" if len(sys.argv) > 2 else ""
BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
PREV = os.path.join(BASE, "..", "Analisis-corridas-AmBe", "resultados")

import gzip
def cargas(dp):
    f = os.path.join(dp, "Datos-simulacion", "Carga-total.txt")
    if os.path.exists(f):
        return np.array([int(l.split()[1]) for l in open(f) if l.strip()])
    o = json.load(gzip.open(os.path.join(dp, "output.json.gz"), "rt"))["Output"]          # respaldo
    ev = sorted(o, key=lambda k: int(k.split("_")[1]))
    return np.array([o[k]["Detector_0"]["OptDevice_0"]["Charge"] for k in ev])
q = np.concatenate([cargas(os.path.join(D, p)) for p in sorted(os.listdir(D)) if p.startswith("parte")])
def pico(x, bins):
    h, e = np.histogram(x, bins=bins); c = 0.5 * (e[1:] + e[:-1])
    hs = np.convolve(h, np.ones(5) / 5, "same"); i = np.argmax(hs)
    j = slice(max(i - 3, 0), i + 4)                                   # parábola alrededor del máximo suavizado
    a, b, _ = np.polyfit(c[j], hs[j], 2)
    return float(-b / (2 * a)) if a < 0 else float(c[i])
sim = {"muones": int(len(q)), "Q_media": float(q.mean()), "Q_mediana": float(np.median(q)),
       "Q_pico": pico(q, np.arange(0, q.max() + 10, 5)), "Q_p16": float(np.percentile(q, 16)), "Q_p84": float(np.percentile(q, 84))}
# pico de muones del fondo medido (dos métodos de carga), por medio
exp = {}
for met, arch in (("ventana_trigger", "experimento_cargas.npz"), ("robusto", "cargas_robustas.npz")):
    X = np.load(os.path.join(PREV, arch))
    for pref in ("pura", "2.5", "10"):
        x = X[f"{pref}_fondo"]; x = x[x > 15000]
        exp[f"{met}_{pref}"] = {"pico_ADC": pico(x, np.arange(15000, 120000, 1000)), "mediana_ADC": float(np.median(x))}
cal = {k: {"ADC_por_pe": v["pico_ADC"] / sim["Q_pico"], "pe_por_1000ADC": 1000 * sim["Q_pico"] / v["pico_ADC"]} for k, v in exp.items()}
v = [x["pe_por_1000ADC"] for x in cal.values()]
resumen = {"pe_por_1000ADC_media": float(np.mean(v)), "rango": [float(min(v)), float(max(v))], "umbral_disparo_ADC": 3000,
           "umbral_disparo_pe_nueva_cal": round(3 * float(np.mean(v)), 1), "umbral_disparo_pe_cal_3.95": 11.9}
out = {"simulacion": sim, "experimento_fondo": exp, "calibracion": cal, "resumen": resumen, "calibracion_usada_hasta_ahora_pe_por_1000ADC": 3.95,
       "nota": "fondo = muones de todas las direcciones; simulación = verticales (VEM). La diferencia de longitud media de traza da una incertidumbre de ~10 %."}
json.dump(out, open(os.path.join(RES, f"calibracion_vem{SUF}.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
ax[0].hist(q, bins=np.arange(0, q.max() + 10, 5), histtype="step", color="k", lw=1.4)
ax[0].axvline(sim["Q_pico"], color="crimson", ls="--", label=f"pico {sim['Q_pico']:.0f} p.e.")
ax[0].set_xlabel("Carga por muón vertical [p.e.]"); ax[0].set_ylabel("Muones"); ax[0].legend(); ax[0].grid(alpha=0.3, ls="--")
ax[0].set_title("MEIGA: muones verticales de 4 GeV/c (VEM)", fontsize=10)
X = np.load(os.path.join(PREV, "experimento_cargas.npz"))
for pref, col in (("pura", "red"), ("2.5", "green"), ("10", "darkorange")):
    x = X[f"{pref}_fondo"]; f = cal[f"ventana_trigger_{pref}"]["pe_por_1000ADC"] / 1000
    h, e = np.histogram(x * f, bins=np.arange(0, 3 * sim["Q_pico"], 5)); ax[1].stairs(h / h.max(), e, color=col, lw=1.2, label=f"fondo {pref} (×{1000*f:.2f} p.e./kADC)")
hs, e = np.histogram(q, bins=np.arange(0, 3 * sim["Q_pico"], 5)); ax[1].stairs(hs / hs.max(), e, color="k", lw=1.6, ls="--", label="MEIGA VEM")
ax[1].set_xlabel("Carga [p.e.] (calibración por muones)"); ax[1].set_ylabel("normalizado"); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3, ls="--")
fig.tight_layout()
for x_ in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig05_calibracion_vem{SUF}.{x_}"), dpi=200)
