#!/usr/bin/env python3
"""Estimacion de la carga del PMT para otras reflectividades del Tyvek, con un modelo de rebotes
ajustado a los datos de la corrida (por intervalo de energia del foton):
  en cada 'encuentro' con la pared el foton cae en el PMT con prob. s, o en el Tyvek con prob. 1-s,
  donde se absorbe con prob. a; entre encuentros se absorbe en el agua con prob. w.
  P(PMT) = s / (s + (1-s) a + w)   (cadena de Markov con tres absorbentes)
s, a y w se miden en los datos; luego se recalcula P(PMT) con a' = (1 - R') + exceso, donde
'exceso' = a_medido - (1 - R_codigo) es la perdida extra del modelo groundbackpainted."""
import json, os, sys
import numpy as np
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
m = sys.argv[1] if len(sys.argv) > 1 else "pura"
z = np.load(os.path.join(R, "resultados", f"{m}_fotones.npz"))
d, reb, E, run = z["dest"], z["rebotes"].astype(np.int64), z["E"], z["run"]
N = int(run.max()) + 1
Eg = np.array([2.08,2.16,2.19,2.23,2.27,2.32,2.36,2.41,2.46,2.50,2.56,2.61,2.67,2.72,2.79,2.85,2.92,2.99,3.06,3.14,3.22,3.31,3.40,3.49,3.59,3.70,3.81,3.94,4.07,4.20])
Rt = np.array([0.9957,0.9953,0.9948,0.9942,0.9939,0.9937,0.9937,0.9940,0.9945,0.9954,0.9964,0.9975,0.9985,0.9993,1.0,1.0,0.9993,0.9977,0.9948,0.9903,0.9840,0.9753,0.9642,0.9500,0.9334,0.9108,0.8849,0.8541,0.8178,0.7755])
# longitud de absorcion del agua en MEIGA (water2PhotonEnergy / waterAbsLen de Materials.cc), en m
Ew = np.array([2.034,2.068,2.103,2.139,2.177,2.216,2.256,2.298,2.341,2.386,2.433,2.481,2.532,2.585,2.640,2.697,
               2.757,2.820,2.885,2.954,3.026,3.102,3.181,3.265,3.353,3.446,3.545,3.649,3.760,3.877,4.002,4.136])
Lw = np.array([3.448,4.082,6.329,9.174,12.346,13.889,15.152,17.241,18.868,20.0,26.316,35.714,45.455,47.619,52.632,52.632,
               55.556,52.632,52.632,47.619,45.455,41.667,37.037,33.333,30.0,28.5,27.0,24.5,22.0,19.5,17.5,14.5])
eb = np.linspace(2.0, 4.2, 23)
ESC = {"MEIGA actual (tabla x 0,94)": ("escala", 0.94, None), "Auger por defecto R = 0,940": ("cte", 0.940, None),
       "Auger alternativo R = 0,973": ("cte", 0.973, None), "LHAASO R = 0,985": ("cte", 0.985, None),
       "tabla sin factor (x 1,00)": ("escala", 1.00, None),
       "MEIGA actual + agua de 100 m": ("escala", 0.94, 100.0),
       "Auger por defecto: R = 0,940 + 100 m": ("cte", 0.940, 100.0),
       "LHAASO: R = 0,985 + 100 m": ("cte", 0.985, 100.0),
       "tabla sin factor + 100 m": ("escala", 1.00, 100.0)}
tot = {k: 0.0 for k in ESC}; filas = []
for lo, hi in zip(eb[:-1], eb[1:]):
    sel = (E >= lo) & (E < hi); n = sel.sum()
    if n < 1000:
        continue
    npmt = (sel & (d == 0)).sum(); nw = (sel & (d == 1)).sum(); npar = (sel & ((d == 2) | (d == 3))).sum()
    hits_tyv = reb[sel].sum() + npar                 # choques con el Tyvek
    enc = hits_tyv + npmt                            # encuentros con la pared (Tyvek o PMT)
    s = npmt / enc; a = npar / hits_tyv; w = nw / (enc + nw)
    Rc = 0.94 * np.interp(0.5 * (lo + hi), Eg, Rt); exceso = a - (1 - Rc)
    P0 = s / (s + (1 - s) * a + w)
    fila = {"E": 0.5 * (lo + hi), "n": int(n), "P_medido": npmt / n, "P_modelo": P0, "a": a, "exceso": exceso}
    for k, (tipo, v, lam) in ESC.items():
        Rn = v * np.interp(0.5 * (lo + hi), Eg, Rt) if tipo == "escala" else v
        an = min(max(1 - Rn + exceso, 0), 1)
        wn = w if lam is None else w * np.interp(0.5 * (lo + hi), Ew, Lw) / lam
        P = s / (s + (1 - s) * an + wn)
        tot[k] += P * n; fila[k] = P
    filas.append(fila)
res = {"carga_media_estimada": {k: v / N for k, v in tot.items()}, "carga_media_medida": float((d == 0).sum() / N),
       "por_energia": filas}
json.dump(res, open(os.path.join(R, "resultados", f"sensibilidad_tyvek_{m}.json"), "w"), indent=1, ensure_ascii=False, default=float)
print("carga media medida:", round(res["carga_media_medida"], 2), "p.e./neutron")
for k, v in res["carga_media_estimada"].items():
    print(f"  {k:32s} -> {v:6.2f} p.e./neutron  (x{v/res['carga_media_medida']:.2f})")
print("\nverificacion del modelo por energia (P medido vs modelo con a medido):")
for f in filas[::3]:
    print(f"  {f['E']:.2f} eV  medido {100*f['P_medido']:.2f} %  modelo {100*f['P_modelo']:.2f} %  exceso de perdida {100*f['exceso']:.2f} pp")
