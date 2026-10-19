#!/usr/bin/env python3
"""Reconstruccion de los vertices de dispersion elastica de neutrones (hadElastic) en las corridas tipo Sidelnik:
  n(E_in, d_in) + blanco en reposo -> n(E_out, d_out) + nucleo de retroceso(T_rec, d_rec)
- neutron entrante/saliente: pasos-neutrones.tsv (el vertice es el punto final del paso hadElastic; d_out sale del paso siguiente);
- retroceso: pasos-particulas.tsv (creator_process = hadElastic, primer paso), enlazado por (run, traza madre, posicion);
- conservacion: energia E_in - E_out - T_rec, impulso |p_in - p_out - p_rec| / p_in, carga, numero barionico y leptonico;
- masa del blanco reconstruida solo con el neutron: M = (|q|^2 - T^2) / (2 T), q = p_in - p_out, T = E_in - E_out;
- estadistica: blanco segun la energia, fraccion de energia perdida, angulo de dispersion, decremento logaritmico medio xi.
Uso: elasticas_vertices.py <medio> <carpeta corrida> [<carpeta 2> ...]   -> resultados/elasticas_<medio>.npz y .json"""
import os, sys, re, json, time
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.csv as pcsv, pyarrow.compute as pc
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
m, carpetas = sys.argv[1], sys.argv[2:]
MN = 939.56542; U = 931.49410
MASA = {"proton": 938.27209, "deuteron": 1875.61294, "O16": 14895.0796, "O17": 15834.5912, "O18": 16767.1103}
SIM = ["", "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
       "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni"]


def AZ(p):
    if p == "proton": return 1, 1
    if p == "deuteron": return 2, 1
    if p == "triton": return 3, 1
    if p == "alpha": return 4, 2
    mm = re.match(r"([A-Z][a-z]?)(\d+)", p)
    return (int(mm.group(2)), SIM.index(mm.group(1))) if mm and mm.group(1) in SIM else (0, 0)


def masa(p):
    return MASA.get(p, AZ(p)[0] * U)


def ds(c):
    return os.path.join(c, "Datos-simulacion") if os.path.isdir(os.path.join(c, "Datos-simulacion")) else c


def lector(f, cols, bs=512 << 20):
    h = open(f).readline().lstrip("# ").rstrip("\n").split("\t"); dic = pa.dictionary(pa.int32(), pa.string())
    return pcsv.open_csv(f, read_options=pcsv.ReadOptions(column_names=h, skip_rows=1, block_size=bs),
                         parse_options=pcsv.ParseOptions(delimiter="\t", invalid_row_handler=lambda r: "skip"),
                         convert_options=pcsv.ConvertOptions(include_columns=cols, column_types={c: dic for c in cols if c in ("particle", "material", "step_process", "creator_process")}))


t0 = time.time(); V, RC, NT = [], [], 0
P = ["pre_x_cm", "pre_y_cm", "pre_z_cm", "post_x_cm", "post_y_cm", "post_z_cm"]
for c in carpetas:
    d = ds(c); NM = sum(1 for l in open(os.path.join(d, "Carga-total.txt")) if len(l.split()) >= 2 and l.endswith("\n"))
    # ---- neutrones: todas las filas (para tener el paso siguiente)
    tb = []
    for b in lector(os.path.join(d, "pasos-neutrones.tsv"), ["run_id", "track_id", "step_number", "step_process", "material"] + P + ["pre_energy_MeV", "post_energy_MeV"]):
        b = b.filter(pc.less(b["run_id"], NM)); tb.append(b)
    n = pa.concat_tables([pa.Table.from_batches([x]) for x in tb]).to_pandas()
    n["step_process"] = n.step_process.astype(str); n["material"] = n.material.astype(str)
    n = n.sort_values(["run_id", "track_id", "step_number"], kind="stable").reset_index(drop=True)
    el = np.flatnonzero(n.step_process.to_numpy() == "hadElastic")
    sig = el + 1; ok = sig < len(n)
    ok[ok] = (n.run_id.to_numpy()[sig[ok]] == n.run_id.to_numpy()[el[ok]]) & (n.track_id.to_numpy()[sig[ok]] == n.track_id.to_numpy()[el[ok]])
    A = lambda col, idx: n[col].to_numpy()[idx]
    din = np.stack([A("post_x_cm", el) - A("pre_x_cm", el), A("post_y_cm", el) - A("pre_y_cm", el), A("post_z_cm", el) - A("pre_z_cm", el)], 1)
    dout = np.full_like(din, np.nan); s2 = sig[ok]
    dout[ok] = np.stack([A("post_x_cm", s2) - A("pre_x_cm", s2), A("post_y_cm", s2) - A("pre_y_cm", s2), A("post_z_cm", s2) - A("pre_z_cm", s2)], 1)
    v = pd.DataFrame({"run": A("run_id", el) + NT, "trk": A("track_id", el), "mat": A("material", el),
                      "x": A("post_x_cm", el), "y": A("post_y_cm", el), "z": A("post_z_cm", el),
                      "Ein": A("pre_energy_MeV", el), "Eout": A("post_energy_MeV", el)})
    for k, D_ in (("in", din), ("out", dout)):
        nn = np.linalg.norm(D_, axis=1); nn[nn == 0] = np.nan
        for j, ax in enumerate("xyz"):
            v[f"d{k}{ax}"] = D_[:, j] / nn
    V.append(v); del n
    print(c[-40:], "vertices elasticos", len(v), f"{time.time()-t0:.0f}s", flush=True)
    # ---- retrocesos
    rr = []
    for b in lector(os.path.join(d, "pasos-particulas.tsv"), ["run_id", "particle", "parent_id", "step_number", "creator_process"] + P + ["pre_energy_MeV"]):
        msk = pc.and_(pc.equal(pc.cast(b["creator_process"], pa.string()), "hadElastic"), pc.equal(b["step_number"], 1))
        msk = pc.and_(msk, pc.less(b["run_id"], NM))
        x = b.filter(msk)
        if x.num_rows:
            x = x.to_pandas(); x["particle"] = x.particle.astype(str); rr.append(x)
    r = pd.concat(rr, ignore_index=True); r["run_id"] += NT; RC.append(r); NT += NM
    print(c[-40:], "retrocesos", len(r), f"{time.time()-t0:.0f}s", flush=True)
v = pd.concat(V, ignore_index=True); r = pd.concat(RC, ignore_index=True)
# ---- enlace vertice <-> retroceso: misma corrida, traza madre y posicion (redondeada a 1e-4 cm)
kv = lambda a, b_, x, y, z: pd.Series(list(zip(a, b_, np.round(x, 4), np.round(y, 4), np.round(z, 4))))
v["key"] = kv(v.run, v.trk, v.x, v.y, v.z); r["key"] = kv(r.run_id, r.parent_id, r.pre_x_cm, r.pre_y_cm, r.pre_z_cm)
r = r.drop_duplicates("key")
d_r = np.stack([r.post_x_cm - r.pre_x_cm, r.post_y_cm - r.pre_y_cm, r.post_z_cm - r.pre_z_cm], 1); nr = np.linalg.norm(d_r, axis=1); nr[nr == 0] = np.nan
r["drx"], r["dry"], r["drz"] = (d_r / nr[:, None]).T
v = v.merge(r[["key", "particle", "pre_energy_MeV", "drx", "dry", "drz"]].rename(columns={"particle": "rec", "pre_energy_MeV": "Trec"}), on="key", how="left").drop(columns="key")
v["rec"] = v.rec.fillna("sin retroceso")
# ---- cinematica
p = lambda T, M: np.sqrt(T * T + 2 * T * M)
pin, pout = p(v.Ein, MN), p(v.Eout, MN)
q = np.stack([pin * v.dinx - pout * v.doutx, pin * v.diny - pout * v.douty, pin * v.dinz - pout * v.doutz], 1)
T = v.Ein - v.Eout; q2 = (q ** 2).sum(1)
v["M_rec_cin"] = np.where(T > 0, (q2 - T * T) / (2 * T), np.nan)        # masa del blanco deducida del neutron
v["cos_lab"] = v.dinx * v.doutx + v.diny * v.douty + v.dinz * v.doutz
v["dE_cons"] = v.Ein - v.Eout - v.Trec                                   # balance de energia (MeV)
Mr = v.rec.map(lambda s: masa(s) if s != "sin retroceso" else np.nan)
prec = p(v.Trec, Mr)
pr = np.stack([prec * v.drx, prec * v.dry, prec * v.drz], 1)
v["dp_rel"] = np.linalg.norm(q - pr, axis=1) / pin                       # balance de impulso relativo
v["prim"] = v.trk == 1
# blanco deducido solo de la cinematica del neutron (valido si el blanco esta en reposo: E_in >~ 1 eV)
v["A_cin"] = np.where((v.Ein > 1e-6) & (T / v.Ein > 1e-3), np.round(v.M_rec_cin / U), np.nan)   # dispersiones muy rasantes: masa mal condicionada
v["blanco_cin"] = np.select([v.A_cin == 1, v.A_cin.between(15, 19), v.A_cin.between(20, 26), v.A_cin.between(33, 39)],
                            ["H", "O", "Na", "Cl"], default="?")
v.loc[v.A_cin.isna(), "blanco_cin"] = "no reconstruible"
v["xi"] = np.log(v.Ein / v.Eout.where(v.Eout > 0))
# ---- resumen
EBk = [1e-8, 1e-6, 1e-3, 1, 20, 1000]; ETQ = ["< 1 eV", "1 eV - 1 keV", "1 keV - 1 MeV", "1 - 20 MeV", "> 20 MeV"]
v["rango"] = pd.cut(v.Ein, EBk, labels=ETQ, right=False)
out = {"N": NT, "vertices": int(len(v)), "vertices_primario": int(v.prim.sum()), "elasticas_por_neutron_primario": float(len(v) / NT),
       "retroceso": {k: float(c_) for k, c_ in v.rec.value_counts(normalize=True).head(12).items()},
       "retroceso_primario": {k: float(c_) for k, c_ in v[v.prim].rec.value_counts(normalize=True).head(8).items()}}
con = v[v.rec != "sin retroceso"]
out["conservacion"] = {"energia_|dE|<1e-6_MeV": float((con.dE_cons.abs() < 1e-6).mean()), "energia_|dE|/Ein<1e-3": float((con.dE_cons.abs() / con.Ein < 1e-3).mean()),
                       "impulso_|dp|/p<1e-2": float((con.dp_rel < 1e-2).mean()), "impulso_mediana": float(con.dp_rel.median()),
                       "carga_barionico_leptonico": "n + (A,Z) -> n + (A,Z): se conservan por construcción; 0 leptones en el estado inicial y final",
                       "frac_sin_retroceso": float((v.rec == "sin retroceso").mean())}
por_rango = {}
for et in ETQ:
    s = v[v.rango == et]
    if len(s) == 0:
        continue
    s2 = s[s.rec != "sin retroceso"]
    bc = s.blanco_cin.value_counts(normalize=True)
    sH, sO = s[s.blanco_cin == "H"], s[s.blanco_cin == "O"]
    por_rango[et] = {"vertices": int(len(s)), "blanco_cin": {k: float(x) for k, x in bc.items()},
                     "xi_H_cin": float(sH.xi.mean()) if len(sH) else None, "xi_O_cin": float(sO.xi.mean()) if len(sO) else None,
                     "acuerdo_cin_retroceso": float(((s.blanco_cin == "H") == (s.rec == "proton"))[s.rec != "sin retroceso"].mean()) if (s.rec != "sin retroceso").any() else None, "frac_H": float((s.rec == "proton").mean()), "frac_O": float(s.rec.str.match(r"O1[678]").mean()),
                     "frac_sin_retroceso": float((s.rec == "sin retroceso").mean()),
                     "xi_H": float(s[s.rec == "proton"].xi.mean()), "xi_O16": float(s[s.rec == "O16"].xi.mean()),
                     "dE_rel_mediana_H": float((s[s.rec == "proton"].Ein.sub(s[s.rec == "proton"].Eout) / s[s.rec == "proton"].Ein).median()),
                     "dE_rel_max_O16": float((s[s.rec == "O16"].Ein.sub(s[s.rec == "O16"].Eout) / s[s.rec == "O16"].Ein).max()),
                     "frac_ganan_energia": float((s.Eout > s.Ein).mean()),
                     "M_cin_mediana_H": float(s2[s2.rec == "proton"].M_rec_cin.median()), "M_cin_mediana_O16": float(s2[s2.rec == "O16"].M_rec_cin.median()),
                     "dp_rel_mediana": float(s2.dp_rel.median()) if len(s2) else None}
out["por_rango"] = por_rango
out["xi_global"] = {"H_cin": float(v[v.blanco_cin == "H"].xi.mean()), "O_cin": float(v[v.blanco_cin == "O"].xi.mean()),
                    "H_con_retroceso": float(v[v.rec == "proton"].xi.mean()), "O16_con_retroceso": float(v[v.rec == "O16"].xi.mean())}
out["blanco_cin_global"] = {k: float(x) for k, x in v.blanco_cin.value_counts(normalize=True).items()}
json.dump(out, open(os.path.join(R, f"elasticas_{m}.json"), "w"), indent=1, ensure_ascii=False)
cols = ["Ein", "Eout", "Trec", "cos_lab", "M_rec_cin", "A_cin", "dE_cons", "dp_rel", "xi", "x", "y", "z"]
np.savez_compressed(os.path.join(R, f"elasticas_{m}.npz"), rec=v.rec.to_numpy().astype(str), blanco_cin=v.blanco_cin.to_numpy().astype(str), prim=v.prim.to_numpy(), mat=v.mat.to_numpy().astype(str),
                    **{k: v[k].to_numpy().astype(np.float32) for k in cols})
print(json.dumps(out, indent=1, ensure_ascii=False)[:4000]); print(f"{time.time()-t0:.0f}s")
