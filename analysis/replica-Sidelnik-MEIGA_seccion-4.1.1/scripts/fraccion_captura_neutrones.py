#!/usr/bin/env python3
"""Interpretaciones de la 'probabilidad de captura' de la Tabla 2 de Sidelnik:
capturas en el agua divididas por (a) neutrones primarios, (b) todos los neutrones del evento
(primario + los producidos en la cascada), (c) neutrones que entran o nacen en el agua.
Uso: fraccion_captura_neutrones.py <carpeta corrida> <medio>"""
import sys, os, json
import numpy as np, pandas as pd, pyarrow.csv as pcsv
C, m = sys.argv[1], sys.argv[2]
DS = os.path.join(C, "Datos-simulacion") if os.path.isdir(os.path.join(C, "Datos-simulacion")) else C
NMAX = sum(1 for l in open(os.path.join(DS, "Carga-total.txt")) if len(l.split()) >= 2 and l.endswith("\n"))
F = os.path.join(DS, "pasos-neutrones.tsv")
hdr = open(F).readline().lstrip("# ").rstrip("\n").split("\t")
rd = pcsv.open_csv(F, read_options=pcsv.ReadOptions(column_names=hdr, skip_rows=1, block_size=256 << 20),
                   parse_options=pcsv.ParseOptions(delimiter="\t", invalid_row_handler=lambda r: "skip"),
                   convert_options=pcsv.ConvertOptions(include_columns=["run_id", "track_id", "step_number", "creator_process", "material", "pre_energy_MeV"]))
tr, agua_tr = set(), set(); crea = {}; n1 = 0; E1 = []
for b in rd:
    d = b.to_pandas(); d = d[d.run_id < NMAX]
    k = d.run_id.to_numpy().astype(np.int64) * 10**7 + d.track_id.to_numpy()
    tr.update(np.unique(k).tolist())
    ag = d.material.astype(str).str.startswith(("Water", "SaltyWater")).to_numpy()
    agua_tr.update(np.unique(k[ag]).tolist())
    s1 = d[d.step_number == 1]
    for c_, v in s1.creator_process.astype(str).value_counts().items():
        crea[c_] = crea.get(c_, 0) + int(v)
    E1.append(s1.pre_energy_MeV.to_numpy())
c = pd.read_csv(os.path.join(DS, "capturas-neutrones.tsv"), sep="\t", skiprows=1, header=None,
                names=open(os.path.join(DS, "capturas-neutrones.tsv")).readline().lstrip("# ").rstrip("\n").split("\t"), on_bad_lines="skip")
c = c[pd.to_numeric(c.run_id, errors="coerce") < NMAX]
cap_agua = int(c.material.astype(str).str.startswith(("Water", "SaltyWater")).sum())
E1 = np.concatenate(E1)
out = {"N_primarios": NMAX, "neutrones_totales": len(tr), "neutrones_por_primario": len(tr) / NMAX,
       "neutrones_que_pasan_por_el_agua": len(agua_tr), "capturas_en_agua": cap_agua, "capturas_totales": int(len(c)),
       "P_a_capturas_sobre_primarios": cap_agua / NMAX,
       "P_b_capturas_sobre_todos_los_neutrones": cap_agua / len(tr),
       "P_c_capturas_sobre_neutrones_en_agua": cap_agua / len(agua_tr),
       "creadores": crea, "E_nacimiento_mediana_MeV": float(np.median(E1))}
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados", f"fraccion_captura_{m}.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "creadores"}, indent=1)); print(sorted(crea.items(), key=lambda x: -x[1])[:8])
