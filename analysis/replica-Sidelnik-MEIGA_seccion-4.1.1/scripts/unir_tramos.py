#!/usr/bin/env python3
"""Une dos tramos de una misma corrida (p. ej. la corrida interrumpida de 42 649 neutrones de 2,5 % NaCl y su complemento
de 107 351 neutrones, lanzado con otra semilla) en un solo conjunto de resultados, como si fuera una corrida continua:
  - arreglos por evento (indexados por neutron): se concatenan;
  - arreglos con numero de run/evento (cap_run_id, sc_run, prim*_run, pe_ev, run de fotones): se suma el N del primer tramo;
  - histogramas y conteos: se suman; ejes de bines: se copian (deben coincidir).
Uso: unir_tramos.py <prefijo_a> <prefijo_b> <prefijo_salida>   (p. ej. nacl25a nacl25b nacl25)"""
import os, sys, json
import numpy as np
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
A, B, S = sys.argv[1:4]
RUNS = {"cap_run_id", "sc_run", "prim1_run", "prim_inel_run", "pe_ev", "run"}
EVENTO = {"inc_E0", "inc_pos", "cher_n_por_run", "Q", "json_Q", "json_Edep"}
EJES = {"EB", "GB", "EPH", "DEST", "int_claves"}


def n_eventos(pref):
    return int(np.load(os.path.join(R, f"{pref}.npz"))["N"])


Na = n_eventos(A); Nb = n_eventos(B)


def unir_npz(sufijo, eventos_por_fila=None):
    fa, fb = (os.path.join(R, f"{p}{sufijo}.npz") for p in (A, B))
    if not (os.path.exists(fa) and os.path.exists(fb)):
        print("  falta", sufijo); return
    za, zb = np.load(fa), np.load(fb); out = {}
    claves = sorted(set(za.files) | set(zb.files))
    for k in claves:
        if k not in za.files or k not in zb.files:
            if k == "json_Q" or k == "json_Edep":       # el tramo interrumpido no tiene output.json.gz
                continue
            out[k] = za[k] if k in za.files else zb[k]; continue
        a, b = za[k], zb[k]
        if k in EJES:
            assert np.array_equal(a, b), k; out[k] = a
        elif k == "N":
            out[k] = np.array(Na + Nb)
        elif k == "nfilas":
            out[k] = a + b
        elif k == "frac_eventos_pion":
            out[k] = (a * Na + b * Nb) / (Na + Nb)
        elif k == "int_n":
            out[k] = a + b
        elif k in RUNS:
            out[k] = np.concatenate([a, b + Na])
        elif a.ndim == 0:
            out[k] = a + b
        elif k in EVENTO or k.startswith(("cap_", "sc_", "prim1_", "prim_inel_", "pe_", "d_")) or (sufijo == "_fotones"):
            out[k] = np.concatenate([a, b])
        else:                                                # histogramas
            assert a.shape == b.shape, (k, a.shape, b.shape); out[k] = a + b
    np.savez_compressed(os.path.join(R, f"{S}{sufijo}.npz"), **out)
    print("  ok", f"{S}{sufijo}.npz")


for suf in ["", "_distancias", "_gamma_pasos", "_gammas_hasta600", "_origen_electrones", "_fotones"]:
    unir_npz(suf)
fa, fb = (os.path.join(R, f"fraccion_captura_{p}.json") for p in (A, B))
if os.path.exists(fa) and os.path.exists(fb):
    a, b = json.load(open(fa)), json.load(open(fb)); c = {}
    for k in ["N_primarios", "neutrones_totales", "neutrones_que_pasan_por_el_agua", "capturas_en_agua", "capturas_totales"]:
        c[k] = a[k] + b[k]
    c["neutrones_por_primario"] = c["neutrones_totales"] / c["N_primarios"]
    c["P_a_capturas_sobre_primarios"] = c["capturas_en_agua"] / c["N_primarios"]
    c["P_b_capturas_sobre_todos_los_neutrones"] = c["capturas_en_agua"] / c["neutrones_totales"]
    c["P_c_capturas_sobre_neutrones_en_agua"] = c["capturas_en_agua"] / c["neutrones_que_pasan_por_el_agua"]
    c["creadores"] = {k: a["creadores"].get(k, 0) + b["creadores"].get(k, 0) for k in set(a["creadores"]) | set(b["creadores"])}
    c["tramos"] = [A, B]
    json.dump(c, open(os.path.join(R, f"fraccion_captura_{S}.json"), "w"), indent=1)
    print("  ok", f"fraccion_captura_{S}.json")
print("N total:", Na + Nb)
