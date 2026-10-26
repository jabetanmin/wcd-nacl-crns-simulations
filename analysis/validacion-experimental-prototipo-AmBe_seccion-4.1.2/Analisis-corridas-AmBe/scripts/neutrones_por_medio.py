#!/usr/bin/env python3
"""
Neutrones detectados en el prototipo por medio y neutrones incidentes que implican según la simulación.

Detectados: pulsos netos (fuente − fondo, normalizado por tiempo) con carga >= umbral, en la duración real
de la toma y llevados a 300 s, con incertidumbre de Poisson.
Incidentes: N_inc = detectados / eficiencia simulada por neutrón incidente para el mismo umbral, con dos
modelos de respuesta: (a) montaje blindado (haz+halo+fondo, 373 272 n) y (b) solo corridas AmBe (rápidos).
Si la simulación es correcta y la fuente/geometría no cambió entre tomas, N_inc debe coincidir en los tres
medios y no depender del umbral. -> resultados/neutrones_por_medio.json/.tsv
"""
import json, os
import numpy as np

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES = os.path.join(BASE, "resultados")
X = np.load(os.path.join(RES, "experimento_cargas.npz"))
T = json.load(open(os.path.join(RES, "experimento_tomas.json")))
cab = open(os.path.join(RES, "histograma_carga_simulado.tsv")).readline().split()
S = np.loadtxt(os.path.join(RES, "histograma_carga_simulado.tsv"), skiprows=1)
col = lambda n: S[:, cab.index(n)]
MED = {"pura": "pura", "nacl25": "2.5", "nacl10": "10"}
PE = 3.95 / 1000
UMBRALES = [12, 15, 20, 30, 40]
N_MODELO, N_CORRIDA = 373272, 1637458
out, filas = {}, []
for m, pref in MED.items():
    qn, qf = X[f"{pref}_neutrones"] * PE, X[f"{pref}_fondo"] * PE
    tn, tf = T[f"{pref}_neutrones"]["duracion_s"], T[f"{pref}_fondo"]["duracion_s"]
    out[m] = {"duracion_fuente_s": tn, "duracion_fondo_s": tf,
              "pulsos_fuente": int(len(qn)), "pulsos_fondo": int(len(qf)),
              "netos_toma": float(len(qn) - len(qf) * tn / tf), "netos_300s": float((len(qn) / tn - len(qf) / tf) * 300),
              "tasa_neta_s": float(len(qn) / tn - len(qf) / tf), "umbrales": {}}
    h5, hr = col(f"5min_total_{m}"), col(f"corrida_{m}")
    for u in UMBRALES:
        an, af = np.sum(qn >= u), np.sum(qf >= u)
        net = (an / tn - af / tf) * 300
        unet = np.sqrt(an / tn ** 2 + af / tf ** 2) * 300
        eff_mod = h5[u:].sum() / N_MODELO
        eff_run = hr[u:].sum() / N_CORRIDA
        r = {"netos_300s": float(net), "u_netos": float(unet),
             "eff_sim_montaje": float(eff_mod), "N_inc_montaje": float(net / eff_mod), "u_N_inc_montaje": float(unet / eff_mod),
             "eff_sim_rapidos": float(eff_run), "N_inc_rapidos": float(net / eff_run),
             "carga_media_exp_netos_pe": float((qn[qn >= u].sum() / tn - qf[qf >= u].sum() / tf) / (an / tn - af / tf)),
             "carga_media_sim_pe": float((np.arange(len(h5))[u:] * h5[u:]).sum() / h5[u:].sum())}
        out[m]["umbrales"][u] = r
        filas.append([m, u, net, unet, eff_mod, net / eff_mod, eff_run, net / eff_run, r["carga_media_exp_netos_pe"], r["carga_media_sim_pe"]])
# consistencia entre medios: dispersión de N_inc por umbral
cons = {}
for u in UMBRALES:
    v = np.array([out[m]["umbrales"][u]["N_inc_montaje"] for m in MED])
    w = np.array([out[m]["umbrales"][u]["N_inc_rapidos"] for m in MED])
    cons[u] = {"N_inc_montaje_max/min": float(v.max() / v.min()), "N_inc_rapidos_max/min": float(w.max() / w.min())}
out["consistencia_entre_medios"] = cons
json.dump(out, open(os.path.join(RES, "neutrones_por_medio.json"), "w"), indent=2, ensure_ascii=False)
with open(os.path.join(RES, "neutrones_por_medio.tsv"), "w") as f:
    f.write("medio\tumbral_pe\tnetos_300s\tu_netos\teff_sim_montaje\tN_inc_montaje\teff_sim_rapidos\tN_inc_rapidos\tQmedia_exp\tQmedia_sim\n")
    for r in filas:
        f.write("\t".join([r[0], str(r[1])] + [f"{x:.6g}" for x in r[2:]]) + "\n")
print(json.dumps({m: {k: v for k, v in out[m].items() if k != "umbrales"} for m in MED}, indent=1))
print(open(os.path.join(RES, "neutrones_por_medio.tsv")).read())
print(json.dumps(cons, indent=1))
