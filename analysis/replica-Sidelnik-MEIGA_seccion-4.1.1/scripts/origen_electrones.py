#!/usr/bin/env python3
"""Descompone el espectro de electrones producidos por gammas en el agua (Fig. 5 de Sidelnik) segun el origen del gamma
padre: captura en H, captura en Cl, otras capturas, dispersion inelastica de neutrones, bremsstrahlung, aniquilacion,
decaimiento radiactivo y otros procesos hadronicos; y separa los eventos con produccion de piones.
Encadena: electron (secundarias-interaccion-gamma) -> gamma padre (pasos-gamma, primer paso: creator_process, parent_id)
-> neutron capturado (capturas-neutrones: target_Z). Histogramas de 20 keV, 0-10 MeV, solo e- creados en el agua.
Uso: origen_electrones.py <carpeta corrida> <medio>   -> resultados/<medio>_origen_electrones.npz"""
import sys, os
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.csv as pcsv
C, m = sys.argv[1], sys.argv[2]
DS = os.path.join(C, "Datos-simulacion") if os.path.isdir(os.path.join(C, "Datos-simulacion")) else C
NMAX = sum(1 for l in open(os.path.join(DS, "Carga-total.txt")) if len(l.split()) >= 2 and l.endswith("\n"))
EB = np.arange(0, 10.0001, 0.02)
def hdr(f):
    return open(os.path.join(DS, f)).readline().lstrip("# ").rstrip("\n").split("\t")
def leer(f, cols, filtro=None):
    dic = pa.dictionary(pa.int32(), pa.string())
    rd = pcsv.open_csv(os.path.join(DS, f), read_options=pcsv.ReadOptions(column_names=hdr(f), skip_rows=1, block_size=256 << 20),
                       parse_options=pcsv.ParseOptions(delimiter="\t", invalid_row_handler=lambda r: "skip"),
                       convert_options=pcsv.ConvertOptions(include_columns=cols, column_types={c: dic for c in cols if c in ("creator_process", "material", "particle", "category")}))
    out = []
    for b in rd:
        d = b.to_pandas(); d = d[d.run_id < NMAX]
        out.append(filtro(d) if filtro else d)
    return pd.concat(out, ignore_index=True)
K = lambda run, trk: run.to_numpy().astype(np.int64) * 10**7 + trk.to_numpy().astype(np.int64)
# gammas: creador y padre (primer paso)
g = leer("pasos-gamma.tsv", ["run_id", "track_id", "parent_id", "step_number", "creator_process"], lambda d: d[d.step_number == 1])
g["k"] = K(g.run_id, g.track_id); g["kp"] = K(g.run_id, g.parent_id); g["cre"] = g.creator_process.astype(str)
# capturas: nucleo
c = pd.read_csv(os.path.join(DS, "capturas-neutrones.tsv"), sep="\t", skiprows=1, header=None, names=hdr("capturas-neutrones.tsv"), on_bad_lines="skip")
c = c[pd.to_numeric(c.run_id, errors="coerce") < NMAX]
zcap = dict(zip(K(c.run_id.astype(int), c.track_id.astype(int)), c.target_Z.astype(int)))
def grupo(r):
    if r.cre == "nCapture":
        z = zcap.get(r.kp, 0)
        return "captura H" if z == 1 else ("captura Cl" if z == 17 else "captura otra")
    return {"neutronInelastic": "inelástica n", "eBrem": "bremsstrahlung", "annihil": "aniquilación",
            "RadioactiveDecayBase": "decaimiento radiactivo"}.get(r.cre, "otros hadrónicos")
cap_mask = g.cre == "nCapture"
g["grupo"] = g.cre.map({"neutronInelastic": "inelástica n", "eBrem": "bremsstrahlung", "annihil": "aniquilación",
                        "RadioactiveDecayBase": "decaimiento radiactivo", "nCapture": "captura"}).fillna("otros hadrónicos")
zc = g.loc[cap_mask, "kp"].map(zcap).fillna(0).astype(int)
g.loc[cap_mask, "grupo"] = np.where(zc == 1, "captura H", np.where(zc == 17, "captura Cl", "captura otra"))
gm = dict(zip(g.k, g.grupo))
# eventos con piones
s = leer("secundarias-inelastica-neutron.tsv", ["run_id", "particle"])
pi = np.zeros(NMAX, bool); pi[s.run_id[s.particle.astype(str).isin(["pi+", "pi-", "pi0"])].unique()] = True
# electrones creados por gammas en el agua
e = leer("secundarias-interaccion-gamma.tsv", ["run_id", "category", "parent_track_id", "particle", "material", "kinetic_energy_MeV"],
         lambda d: d[(d.particle.astype(str) == "e-") & d.material.astype(str).str.startswith(("Water", "SaltyWater"))])
e["grupo"] = pd.Series(K(e.run_id, e.parent_track_id)).map(gm).fillna("sin gamma padre").to_numpy()
e["pion"] = pi[e.run_id.to_numpy()]
out = {"EB": EB, "N": NMAX, "frac_eventos_pion": pi.mean()}
for gr, d in e.groupby("grupo"):
    for tag, dd in (("todos", d), ("sin_piones", d[~d.pion])):
        out[f"h|{gr}|{tag}"] = np.histogram(dd.kinetic_energy_MeV, EB)[0]
np.savez_compressed(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados", f"{m}_origen_electrones.npz"), **out)
print(m, NMAX, "electrones", len(e), e.grupo.value_counts().to_dict())
