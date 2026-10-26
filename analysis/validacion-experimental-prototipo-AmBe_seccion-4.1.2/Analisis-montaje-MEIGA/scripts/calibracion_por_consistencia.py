#!/usr/bin/env python3
"""
Calibración p.e./ADC por consistencia entre medios: con la misma fuente y geometría, el número de neutrones
incidentes N_inc = detectados(Q_ADC >= U) / eps_sim(Q_pe >= U·c) debe ser igual en agua pura y en 2.5 % NaCl.
Se barre la calibración c (p.e. por ADC) y el umbral U (ADC) y se busca dónde coinciden.
-> resultados/calibracion_consistencia.json, figuras/fig06_calibracion_consistencia
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
out = {}
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
PARES = [("nacl25", "2.5", "green", "2.5 % NaCl"), ("nacl10", "10", "darkorange", "10 % NaCl")]
for metodo, arch in (("ventana_trigger", "experimento_cargas.npz"), ("robusto", "cargas_robustas.npz")):
    X = np.load(os.path.join(PREV, arch))
    a = ax[0 if metodo == "ventana_trigger" else 1]
    Q = {m: np.load(os.path.join(RES, f"eventos_{m}.npz"))["Q"] for m in ["pura"] + [p[0] for p in PARES]
         if os.path.exists(os.path.join(RES, f"eventos_{m}.npz"))}
    pref = {"pura": "pura", "nacl25": "2.5", "nacl10": "10"}
    def det(m, U):
        qn, qf = X[f"{pref[m]}_neutrones"], X[f"{pref[m]}_fondo"]
        tn, tf = T[f"{pref[m]}_neutrones"]["duracion_s"], T[f"{pref[m]}_fondo"]["duracion_s"]
        return (np.sum(qn >= U) / tn - np.sum(qf >= U) / tf) * 300
    cs = np.linspace(2, 14, 241) / 1000            # p.e. por ADC
    out[metodo] = {}
    for m2, p2, col, nom in PARES:
        if m2 not in Q: continue
        res = {}
        for U in (3000, 4000, 5000, 6000):
            d = {m: det(m, U) for m in ("pura", m2)}
            razon = []
            for c in cs:
                e = {m: np.mean(Q[m] >= U * c) for m in ("pura", m2)}
                razon.append((d["pura"] / e["pura"]) / (d[m2] / e[m2]) if min(e.values()) > 0 else np.nan)
            razon = np.array(razon)
            ok = np.isfinite(razon)
            lr = np.log(razon[ok]); cc = cs[ok]
            cruce = None
            for i in range(len(lr) - 1):
                if lr[i] * lr[i + 1] <= 0:
                    cruce = cc[i] - lr[i] * (cc[i + 1] - cc[i]) / (lr[i + 1] - lr[i]); break
            Ninc = None
            if cruce:
                e = {m: np.mean(Q[m] >= U * cruce) for m in ("pura", m2)}
                Ninc = {m: float(det(m, U) / e[m]) for m in ("pura", m2)}
            res[U] = {"pe_por_1000ADC_consistente": (1000 * cruce if cruce else None), "N_inc_300s": Ninc,
                      "razon_con_3.95": float(razon[np.argmin(abs(cs - 3.95e-3))]),
                      "razon_con_7.9": float(razon[np.argmin(abs(cs - 7.9e-3))])}
            if U == 4000:
                a.semilogy(cs * 1000, razon, color=col, lw=1.6, label=f"pura / {nom}, U = {U} ADC")
            else:
                a.semilogy(cs * 1000, razon, color=col, lw=0.7, alpha=0.4, label=(f"pura / {nom}, U = 3000-6000 ADC" if U == 3000 else None))
        out[metodo][f"pura/{p2}"] = res
    a.axhline(1, color="0.4", lw=0.8); a.axvline(3.95, color="crimson", ls=":", label="3.95 (antigua)")
    a.axvline(7.9, color="royalblue", ls="--", lw=0.9, label="7.9 (muones)")
    a.set_xlabel("Calibración [p.e. por 1000 ADC]"); a.set_ylabel("N_inc(agua pura) / N_inc(medio con NaCl)")
    a.set_title(f"Método de carga: {metodo}", fontsize=10); a.grid(alpha=0.3, ls="--", which="both"); a.legend(fontsize=7)
json.dump(out, open(os.path.join(RES, "calibracion_consistencia.json"), "w"), indent=2)
fig.tight_layout()
for x in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig06_calibracion_consistencia.{x}"), dpi=200)
print(json.dumps({m: {p: {U: (v['pe_por_1000ADC_consistente'], v['razon_con_7.9'], v['N_inc_300s']) for U, v in r.items()} for p, r in x.items()} for m, x in out.items()}, indent=1))
