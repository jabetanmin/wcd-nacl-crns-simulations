#!/usr/bin/env python3
"""Destino de cada foton optico seguido (pasos-particulas.tsv) en una corrida tipo Sidelnik.

Para cada foton: numero de rebotes en el Tyvek (pasos de longitud cero con material Tyvek),
camino recorrido en el medio, energia, y como termina:
  PMT              entra al Pyrex (lo cuenta G4MPMTAction o se absorbe alli)
  absorcion_agua   OpAbsorption en el medio
  pared            muere en la frontera agua/Tyvek sin reflejarse (REFLECTIVITY < 1)
  tyvek            muere dentro del Tyvek / acero
  otro
Tambien cuenta, por evento (run_id), fotones seguidos y fotones que llegan al PMT.
Uso: destino_fotones.py <carpeta corrida> <salida.npz>
"""
import sys, os, time
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pcsv
import pyarrow.compute as pcomp

C, OUT = sys.argv[1], sys.argv[2]
F = os.path.join(os.path.join(C, "Datos-simulacion") if os.path.isdir(os.path.join(C, "Datos-simulacion")) else C, "pasos-particulas.tsv")
NMAX = sum(1 for l in open(os.path.join(os.path.dirname(F), "Carga-total.txt")) if len(l.split()) >= 2 and l.endswith("\n"))  # neutrones terminados
hdr = open(F).readline().lstrip("# ").rstrip("\n").split("\t")
cols = ["run_id", "particle", "track_id", "step_number", "step_process", "material",
        "pre_x_cm", "pre_y_cm", "pre_z_cm", "post_x_cm", "post_y_cm", "post_z_cm", "pre_energy_MeV", "global_time_ns"]
dic = pa.dictionary(pa.int32(), pa.string())
rd = pcsv.open_csv(F, read_options=pcsv.ReadOptions(column_names=hdr, skip_rows=1, block_size=512 << 20),
                   parse_options=pcsv.ParseOptions(delimiter="\t", invalid_row_handler=lambda r: "skip"),
                   convert_options=pcsv.ConvertOptions(include_columns=cols,
                                                       column_types={"particle": dic, "step_process": dic, "material": dic}))
t0 = time.time()
DEST = ["PMT", "absorcion_agua", "pared", "tyvek", "otro"]
res = {k: [] for k in ["run", "dest", "rebotes", "L", "E", "t"]}
carry = None
nfil = 0


def procesar(d, final=False):
    """d: filas de fotones opticos ordenadas como en el archivo; devuelve las filas del ultimo foton si no es final"""
    key = d.run_id.to_numpy().astype(np.int64) * 100_000_000 + d.track_id.to_numpy()
    ini = np.r_[0, np.flatnonzero(np.diff(key) != 0) + 1]
    fin = np.r_[ini[1:], len(d)]
    resto = None
    if not final:
        resto = d.iloc[ini[-1]:]
        ini, fin = ini[:-1], fin[:-1]
        if len(ini) == 0:
            return resto
    mat = d.material.astype(str).to_numpy(); proc = d.step_process.astype(str).to_numpy()
    x0, y0, z0 = d.pre_x_cm.to_numpy(), d.pre_y_cm.to_numpy(), d.pre_z_cm.to_numpy()
    x1, y1, z1 = d.post_x_cm.to_numpy(), d.post_y_cm.to_numpy(), d.post_z_cm.to_numpy()
    seg = np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2 + (z1 - z0) ** 2)
    enmedio = np.char.startswith(mat.astype("U32"), ("Water")) | np.char.startswith(mat.astype("U32"), "SaltyWater")
    tyv = mat == "Tyvek_HDPE"
    pyr = mat == "Pyrex"
    cs = lambda a: np.add.reduceat(a.astype(np.int64), ini)
    reb = cs(tyv & (seg < 1e-6)); L = np.add.reduceat(seg * enmedio, ini)
    llega = cs(pyr) > 0
    last = fin - 1
    lp, lm = proc[last], mat[last]
    r1 = np.hypot(x1[last], y1[last])
    dest = np.full(len(ini), 4, np.int8)
    dest[llega] = 0
    m = ~llega & (lp == "OpAbsorption") & enmedio[last]; dest[m] = 1
    m = ~llega & (dest == 4) & enmedio[last] & (lp == "Transportation"); dest[m] = 2
    m = ~llega & (dest == 4) & tyv[last]; dest[m] = 3
    res["run"].append(d.run_id.to_numpy()[ini].astype(np.int32)); res["dest"].append(dest)
    res["rebotes"].append(reb.astype(np.int32)); res["L"].append(L.astype(np.float32))
    res["E"].append((d.pre_energy_MeV.to_numpy()[ini] * 1e6).astype(np.float32))
    res["t"].append(d.global_time_ns.to_numpy()[last].astype(np.float64))
    return resto


for b in rd:
    nfil += b.num_rows
    part = b.column("particle")
    m = pcomp.equal(part.cast(pa.string()), "opticalphoton")
    d = b.filter(m).to_pandas(); d = d[d.run_id < NMAX]
    if carry is not None and len(carry):
        d = pd.concat([carry, d], ignore_index=True)
    if len(d):
        carry = procesar(d)
    print(f"{nfil/1e6:8.0f} M filas  {time.time()-t0:5.0f}s", flush=True)
if carry is not None and len(carry):
    procesar(carry, final=True)
out = {k: np.concatenate(v) for k, v in res.items()}
out["DEST"] = np.array(DEST)
np.savez_compressed(OUT, **out)
print("LISTO", len(out["run"]), "fotones", f"{time.time()-t0:.0f}s")
