#!/usr/bin/env python3
"""Tabla 4.2 de la tesis (parametros nucleares y lineas gamma de captura termica) y energia de cada linea en MEIGA:
para cada linea de la tabla se busca, entre los gammas de las capturas en ese isotopo (<medio>.npz), la linea de MEIGA
mas intensa a menos de 3 keV y se da su energia media y su intensidad por 100 capturas.
Escribe resultados/tabla_parametros_nucleares.json"""
import os, json
import numpy as np, pandas as pd
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(R, "resultados")
# isotopo: (Z, A, abundancia %, sigma0 [mb], lineas [(E keV, valor original de la Tabla 4.2 si se corrigio)])
# Energias unificadas con las figuras del informe: 16O de Firestone y Revay (2016) como en la Fig. 4.2 de la tesis;
# 35Cl de la evaluacion ENSDF (Nica et al. 2012) como en el esquema de niveles de 36Cl.
TABLA = {"1H": (1, 1, "99.99", "332.60 \\pm 0.70", [(2223.25, None)]),
         "16O": (8, 16, "99.76", "0.170 \\pm 0.003", [(870.76, None), (1087.89, 1087.86), (2184.49, 2184.44), (3272.02, 3272.15), (4142.60, 4142.73)]),
         "35Cl": (17, 35, "75.78", "43840 \\pm 170", [(517.07, None), (788.42, None), (1164.86, None), (1951.13, 1959.13), (1959.34, "nueva"),
                                                     (6110.98, 6110.84), (8578.70, 8578.21)]),
         "23Na": (11, 23, "100", "527 \\pm 7", [(472.20, None)]),
         "37Cl": (17, 37, "24.22", "553 \\pm 17", [(637.69, None), (755.43, None), (788.42, None), (1692.11, None), (2166.90, None), (4134.13, None)])}
VENTANA = 0.4        # keV: misma transicion. El H es la excepcion: Geant4 emite la linea 1,1 keV por encima (2224,37 keV)
gam, ncap = {}, {}
for m in ["pura", "nacl25", "nacl5", "nacl10"]:
    f = os.path.join(RES, f"{m}.npz")
    if not os.path.exists(f):
        continue
    z = np.load(f)
    cap = pd.DataFrame({"run": z["cap_run_id"], "trk": z["cap_track_id"], "Z": z["cap_target_Z"], "A": z["cap_target_A"], "mat": z["cap_material"]})
    cap = cap[cap.mat.str.startswith(("Water", "SaltyWater"))]
    sc = pd.DataFrame({"run": z["sc_run"], "trk": z["sc_ptrk"], "p": z["sc_part"], "E": z["sc_E"] * 1e3})
    g = sc[sc.p == "gamma"].merge(cap, on=["run", "trk"])
    for (Z, A), d in g.groupby(["Z", "A"]):
        gam.setdefault((Z, A), []).append(d.E.to_numpy())
    for (Z, A), d in cap.groupby(["Z", "A"]):
        ncap[(Z, A)] = ncap.get((Z, A), 0) + len(d)
out = {}
for iso, (Z, A, ab, s0, lineas) in TABLA.items():
    E = np.concatenate(gam.get((Z, A), [np.array([])])); n = ncap.get((Z, A), 0); filas = []
    for El, orig in lineas:
        v_ = 1.5 if iso == "1H" else VENTANA
        cerca = E[np.abs(E - El) < v_]
        if len(cerca) == 0:
            filas.append({"tabla": El, "original": orig, "MEIGA": None, "por_100": 0.0}); continue
        v, c = np.unique(np.round(cerca, 1), return_counts=True); Ep = v[np.argmax(c)]
        sel = cerca[np.abs(cerca - Ep) < 0.3]
        filas.append({"tabla": El, "original": orig, "MEIGA": float(sel.mean()), "por_100": 100 * len(sel) / n})
    # gamma unico con toda la energia de separacion (solo Geant4): linea mas intensa por encima de la ultima de la tabla
    alto = E[E > max(l for l, _ in lineas) + 0.3]
    if len(alto):
        v, c = np.unique(np.round(alto, 1), return_counts=True); Ep = v[np.argmax(c)]
        sel = alto[np.abs(alto - Ep) < 0.3]
        if len(sel) / max(n, 1) > 0.02:
            filas_sn = {"MEIGA": float(sel.mean()), "por_100": 100 * len(sel) / n}
        else:
            filas_sn = None
    else:
        filas_sn = None
    out[iso] = {"abundancia": ab, "sigma0_mb": s0, "capturas_MEIGA": n, "lineas": filas, "gamma_unico_Sn": filas_sn}
json.dump(out, open(os.path.join(RES, "tabla_parametros_nucleares.json"), "w"), indent=1)
for iso, v in out.items():
    print(iso, v["capturas_MEIGA"], [(l["tabla"], round(l["MEIGA"], 2) if l["MEIGA"] else None, round(l["por_100"], 1)) for l in v["lineas"]], "Sn:", v["gamma_unico_Sn"])
