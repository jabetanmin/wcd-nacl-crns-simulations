#!/usr/bin/env python3
"""Distancias alternativas para interpretar la Fig. 2 de Sidelnik: captura respecto a
(a) el vertice donde nacio el neutron capturado y (b) la primera inelastica del primario."""
import sys, os, numpy as np, pandas as pd, pyarrow.csv as pcsv
C, OUT = sys.argv[1], sys.argv[2]; DS = os.path.join(C, "Datos-simulacion") if os.path.isdir(os.path.join(C, "Datos-simulacion")) else C
NMAX = sum(1 for l in open(os.path.join(DS, "Carga-total.txt")) if len(l.split()) >= 2 and l.endswith("\n"))
hdr = open(os.path.join(DS, "pasos-neutrones.tsv")).readline().lstrip("# ").rstrip("\n").split("\t")
rd = pcsv.open_csv(os.path.join(DS, "pasos-neutrones.tsv"),
                   read_options=pcsv.ReadOptions(column_names=hdr, skip_rows=1, block_size=256 << 20),
                   parse_options=pcsv.ParseOptions(delimiter="\t", invalid_row_handler=lambda r: "skip"),
                   convert_options=pcsv.ConvertOptions(include_columns=["run_id", "track_id", "step_number", "step_process",
                                                                         "pre_x_cm", "pre_y_cm", "pre_z_cm", "post_x_cm", "post_y_cm", "post_z_cm"]))
v, inel = [], []
for b in rd:
    d = b.to_pandas(); d = d[d.run_id < NMAX]
    v.append(d[d.step_number == 1][["run_id", "track_id", "pre_x_cm", "pre_y_cm", "pre_z_cm"]])
    p = d[(d.track_id == 1) & (d.step_process == "neutronInelastic")]
    inel.append(p[["run_id", "post_x_cm", "post_y_cm", "post_z_cm"]])
v = pd.concat(v).rename(columns={"pre_x_cm": "vx", "pre_y_cm": "vy", "pre_z_cm": "vz"}); inel = pd.concat(inel).drop_duplicates("run_id")
hc = open(os.path.join(DS, "capturas-neutrones.tsv")).readline().lstrip("# ").rstrip("\n").split("\t")
c = pd.read_csv(os.path.join(DS, "capturas-neutrones.tsv"), sep="\t", skiprows=1, header=None, names=hc, on_bad_lines="skip")
c = c[pd.to_numeric(c.run_id, errors="coerce") < NMAX].copy(); c["run_id"] = c.run_id.astype(np.int64)
c = c[c.material.str.startswith(("Water", "SaltyWater"))]
a = c.merge(v, on=["run_id", "track_id"], how="left")
dv = np.sqrt((a.post_x_cm - a.vx) ** 2 + (a.post_y_cm - a.vy) ** 2 + (a.post_z_cm - a.vz) ** 2)
b2 = c.merge(inel, on="run_id", how="left", suffixes=("", "_i"))
di = np.sqrt((b2.post_x_cm - b2.post_x_cm_i) ** 2 + (b2.post_y_cm - b2.post_y_cm_i) ** 2 + (b2.post_z_cm - b2.post_z_cm_i) ** 2)
np.savez_compressed(OUT, d_vertice=dv.to_numpy(), d_inel_primario=di.to_numpy())
print("capturas", len(c), "con vertice", int(np.isfinite(dv).sum()), "con inelastica del primario", int(np.isfinite(di).sum()))
