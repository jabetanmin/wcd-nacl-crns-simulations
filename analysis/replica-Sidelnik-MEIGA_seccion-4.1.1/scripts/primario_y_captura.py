#!/usr/bin/env python3
"""Relacion entre el destino del neutron primario y las capturas (de resultados/<medio>.npz):
eventos con captura, fraccion de ellos en que el primario tuvo una inelastica, primario capturado como la misma traza
y capturas por evento con captura. Escribe resultados/primario_y_captura_<medio>.json"""
import os, json
import numpy as np
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
for m in ["pura", "nacl25", "nacl5", "nacl10"]:
    f = os.path.join(RES, f"{m}.npz")
    if not os.path.exists(f):
        continue
    z = np.load(f); N = int(z["N"]); inel = np.unique(z["prim_inel_run"]); mat = z["cap_material"]
    ag = np.char.startswith(mat, "Water") | np.char.startswith(mat, "SaltyWater")
    cr = np.unique(z["cap_run_id"][ag]); capP = np.unique(z["cap_run_id"][(z["cap_track_id"] == 1) & ag])
    out = {"eventos_con_captura": len(cr) / N, "frac_eventos_captura_con_inel_primario": float(np.isin(cr, inel).mean()),
           "primario_capturado": len(capP) / N, "capturas_por_evento_con_captura": float(ag.sum() / len(cr))}
    json.dump(out, open(os.path.join(RES, f"primario_y_captura_{m}.json"), "w"), indent=1); print(m, out)
