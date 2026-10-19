#!/usr/bin/env python3
"""Espectro gamma a partir de pasos-gamma.tsv para comparar con la Fig. 3 de Sidelnik.
Histograma (bins de 1 keV, 0-20 MeV) de la energia previa de: (1) cada paso de gamma, (2) cada paso en el medio,
(3) el primer paso de cada gamma (= energia de creacion), (4) cada interaccion fisica (sin Transportation).
Por creador. Uso: espectro_gamma_pasos.py <carpeta corrida> <salida.npz>"""
import sys, os, time
import numpy as np
import pyarrow as pa, pyarrow.csv as pcsv
C, OUT = sys.argv[1], sys.argv[2]
F = os.path.join(os.path.join(C, "Datos-simulacion") if os.path.isdir(os.path.join(C, "Datos-simulacion")) else C, "pasos-gamma.tsv")
NMAX = sum(1 for l in open(os.path.join(os.path.dirname(F), "Carga-total.txt")) if len(l.split()) >= 2 and l.endswith("\n"))  # neutrones terminados
hdr = open(F).readline().lstrip("# ").rstrip("\n").split("\t")
cols = ["run_id", "step_number", "creator_process", "step_process", "material", "pre_energy_MeV"]
dic = pa.dictionary(pa.int32(), pa.string())
rd = pcsv.open_csv(F, read_options=pcsv.ReadOptions(column_names=hdr, skip_rows=1, block_size=256 << 20),
                   parse_options=pcsv.ParseOptions(delimiter="\t", invalid_row_handler=lambda r: "skip"),
                   convert_options=pcsv.ConvertOptions(include_columns=cols, column_types={"creator_process": dic, "step_process": dic, "material": dic}))
GB = np.arange(0, 20.0001, 0.001); H = {}; t0 = time.time(); n = 0   # 1 keV; se reagrupa al graficar
def add(k, e):
    H[k] = H.get(k, 0) + np.histogram(e, GB)[0]
for b in rd:
    d = b.to_pandas(); d = d[d.run_id < NMAX]; n += len(d)
    e = d.pre_energy_MeV.to_numpy(); mat = d.material.astype(str).to_numpy()
    agua = np.char.startswith(mat.astype("U32"), "Water") | np.char.startswith(mat.astype("U32"), "SaltyWater")
    proc = d.step_process.astype(str).to_numpy(); cre = d.creator_process.astype(str).to_numpy()
    primero = d.step_number.to_numpy() == 1
    add("pasos_todos", e); add("pasos_agua", e[agua]); add("primer_paso", e[primero]); add("primer_paso_agua", e[primero & agua])
    add("interacciones_agua", e[agua & (proc != "Transportation")])
    for c in np.unique(cre[primero]):
        add(f"primer|{c}", e[primero & (cre == c)])
        add(f"pasosagua|{c}", e[agua & (cre == c)])
    print(f"{n/1e6:6.1f} M filas {time.time()-t0:4.0f}s", flush=True)
np.savez_compressed(OUT, GB=GB, nfilas=n, **H)
print("LISTO", n)
