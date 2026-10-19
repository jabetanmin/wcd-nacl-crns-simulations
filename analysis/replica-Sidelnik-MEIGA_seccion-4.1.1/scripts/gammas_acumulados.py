#!/usr/bin/env python3
"""Gammas creados en el medio con energia hasta 600 MeV (bines de 0,01 MeV), por proceso creador y separando
los eventos con piones, para la Fig. 4 de Sidelnik (cuentas acumuladas de derecha a izquierda).
Uso: gammas_acumulados.py <carpeta corrida> <medio>  ->  resultados/<medio>_gammas_hasta600.npz"""
import sys, os
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.csv as pcsv
C, m = sys.argv[1], sys.argv[2]
DS = os.path.join(C, "Datos-simulacion") if os.path.isdir(os.path.join(C, "Datos-simulacion")) else C
NMAX = sum(1 for l in open(os.path.join(DS, "Carga-total.txt")) if len(l.split()) >= 2 and l.endswith("\n"))
hdr = lambda f: open(os.path.join(DS, f)).readline().lstrip("# ").rstrip("\n").split("\t")
dic = pa.dictionary(pa.int32(), pa.string())
s = pd.read_csv(os.path.join(DS, "secundarias-inelastica-neutron.tsv"), sep="\t", skiprows=1, header=None, usecols=[0, 7], names=["run", "p"], on_bad_lines="skip")
s = s[pd.to_numeric(s.run, errors="coerce") < NMAX]
pi = np.zeros(NMAX, bool); pi[s.run[s.p.isin(["pi+", "pi-", "pi0"])].astype(int).unique()] = True
EB = np.arange(0, 600.0001, 0.01); H = {}
rd = pcsv.open_csv(os.path.join(DS, "pasos-gamma.tsv"), read_options=pcsv.ReadOptions(column_names=hdr("pasos-gamma.tsv"), skip_rows=1, block_size=256 << 20),
                   parse_options=pcsv.ParseOptions(delimiter="\t", invalid_row_handler=lambda r: "skip"),
                   convert_options=pcsv.ConvertOptions(include_columns=["run_id", "step_number", "creator_process", "material", "pre_energy_MeV"],
                                                       column_types={"creator_process": dic, "material": dic}))
def add(k, e):
    H[k] = H.get(k, 0) + np.histogram(e, EB)[0]
for b in rd:
    d = b.to_pandas(); d = d[(d.run_id < NMAX) & (d.step_number == 1)]
    d = d[d.material.astype(str).str.startswith(("Water", "SaltyWater"))]
    e = d.pre_energy_MeV.to_numpy(); p = pi[d.run_id.to_numpy()]; cre = d.creator_process.astype(str).to_numpy()
    add("todos", e); add("sin_piones", e[~p])
    for c in np.unique(cre):
        add(f"cre|{c}", e[cre == c])
np.savez_compressed(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados", f"{m}_gammas_hasta600.npz"), EB=EB, N=NMAX, **H)
print(m, NMAX, int(H["todos"].sum()), "gammas; >600 MeV no incluidos")
