#!/usr/bin/env python3
"""Interacciones del neutron primario de 500 MeV (traza 1) en las corridas tipo Sidelnik:
  - tipo de proceso y secuencia (interacciones-neutrones.tsv, traza 1): elasticas, inelastica, captura;
  - donde: material y profundidad a lo largo del haz de la inelastica del primario;
  - con quien: nucleo blanco, deducido por conservacion de carga y numero barionico de los productos
    (A_blanco = sum A_productos - 1, Z_blanco = sum Z_productos);
  - resultados: multiplicidad y espectro de energia de cada tipo de producto, nucleo residual y fraccion de la
    energia que se lleva el neutron mas energetico.
Uso: inelasticas_primario.py <medio> <carpeta corrida> [<carpeta corrida 2> ...]   (varias carpetas = tramos)
Escribe resultados/inelasticas_primario_<medio>.json y resultados/inelasticas_primario_<medio>.npz"""
import sys, os, re, json, collections
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.csv as pcsv
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
m, carpetas = sys.argv[1], sys.argv[2:]
SIM = ["", "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
       "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"]
LIGERAS = {"neutron": (1, 0), "proton": (1, 1), "deuteron": (2, 1), "triton": (3, 1), "He3": (3, 2), "alpha": (4, 2),
           "pi+": (0, 1), "pi-": (0, -1), "pi0": (0, 0), "gamma": (0, 0), "e-": (0, -1), "e+": (0, 1),
           "kaon+": (0, 1), "kaon-": (0, -1), "kaon0L": (0, 0), "kaon0S": (0, 0), "lambda": (1, 0), "sigma+": (1, 1), "sigma-": (1, -1)}


def AZ(p):
    if p in LIGERAS:
        return LIGERAS[p]
    mm = re.match(r"([A-Z][a-z]?)(\d+)", p)
    if mm and mm.group(1) in SIM:
        return int(mm.group(2)), SIM.index(mm.group(1))
    return None


def ds(c):
    return os.path.join(c, "Datos-simulacion") if os.path.isdir(os.path.join(c, "Datos-simulacion")) else c


def nmax(d):
    return sum(1 for l in open(os.path.join(d, "Carga-total.txt")) if len(l.split()) >= 2 and l.endswith("\n"))


def leer(f, cols, filtro, NM):
    h = open(f).readline().lstrip("# ").rstrip("\n").split("\t"); dic = pa.dictionary(pa.int32(), pa.string()); out = []
    rd = pcsv.open_csv(f, read_options=pcsv.ReadOptions(column_names=h, skip_rows=1, block_size=256 << 20),
                       parse_options=pcsv.ParseOptions(delimiter="\t", invalid_row_handler=lambda r: "skip"),
                       convert_options=pcsv.ConvertOptions(include_columns=cols, column_types={c: dic for c in cols if c in ("particle", "material", "step_process", "category")}))
    for b in rd:
        d = b.to_pandas(); d = d[(d.run_id < NM)]; d = filtro(d)
        for c in ("particle", "material", "step_process", "category"):
            if c in d:
                d[c] = d[c].astype(str)
        out.append(d)
    return pd.concat(out, ignore_index=True)


SEC, INT, NT = [], [], 0
for c in carpetas:
    d = ds(c); NM = nmax(d)
    s = leer(os.path.join(d, "secundarias-inelastica-neutron.tsv"),
             ["run_id", "category", "parent_track_id", "parent_step_number", "particle", "material", "x_cm", "y_cm", "z_cm", "kinetic_energy_MeV"],
             lambda d: d[d.parent_track_id == 1], NM)
    i = leer(os.path.join(d, "interacciones-neutrones.tsv"),
             ["run_id", "track_id", "step_number", "step_process", "material", "post_x_cm", "pre_energy_MeV", "post_energy_MeV"],
             lambda d: d[d.track_id == 1], NM)
    s["run_id"] += NT; i["run_id"] += NT; NT += NM
    SEC.append(s); INT.append(i)
    print(c, NM, "secundarias del primario", len(s), "interacciones del primario", len(i), flush=True)
s = pd.concat(SEC, ignore_index=True); it = pd.concat(INT, ignore_index=True)
X0 = -48.062                                             # cara exterior del acero (entrada del haz)
out = {"N": NT}
# ---- secuencia de procesos del primario
seq = it.sort_values(["run_id", "step_number"]).groupby("run_id").step_process.apply(list)
cnt = collections.Counter()
nel_antes = []
for r, l in seq.items():
    fin = "neutronInelastic" if "neutronInelastic" in l else ("nCapture" if "nCapture" in l else "solo elásticas")
    cnt[fin] += 1
    k = l.index("neutronInelastic") if "neutronInelastic" in l else len(l)
    nel_antes.append(sum(1 for p in l[:k] if p == "hadElastic"))
cnt["sin interacción"] = NT - len(seq)
out["destino_primario"] = {k: v / NT for k, v in cnt.items()}
out["elasticas_antes_de_la_inelastica"] = dict(collections.Counter(min(x, 5) for x in nel_antes))
out["procesos_del_primario"] = {k: int(v) for k, v in it.step_process.value_counts().items()}
# ---- inelasticas del primario: una por (run, paso)
g = s.groupby(["run_id", "parent_step_number"])
ev = g.agg(material=("material", "first"), x=("x_cm", "first"), y=("y_cm", "first"), z=("z_cm", "first")).reset_index()
ev["prof_cm"] = ev.x - X0
az = s.particle.map(AZ)
s["A"] = az.map(lambda t: t[0] if t else np.nan); s["Z"] = az.map(lambda t: t[1] if t else np.nan)
sumA = s.groupby(["run_id", "parent_step_number"]).A.sum(); sumZ = s.groupby(["run_id", "parent_step_number"]).Z.sum()
ev = ev.merge((sumA - 1).rename("A_blanco"), on=["run_id", "parent_step_number"]).merge(sumZ.rename("Z_blanco"), on=["run_id", "parent_step_number"])
ev["blanco"] = [f"{SIM[int(z)]}{int(a)}" if 0 < z < len(SIM) and a > 0 else "?" for a, z in zip(ev.A_blanco, ev.Z_blanco)]
# energia del primario en la inelastica
ie = it[it.step_process == "neutronInelastic"][["run_id", "pre_energy_MeV"]].drop_duplicates("run_id")
ev = ev.merge(ie, on="run_id", how="left")
out["inelasticas"] = int(len(ev))
out["material"] = {k: v / len(ev) for k, v in ev.material.value_counts().items()}
out["blanco"] = {k: v / len(ev) for k, v in ev.blanco.value_counts().head(15).items()}
out["blanco_en_medio"] = {k: v / ev.material.str.startswith(("Water", "SaltyWater")).sum()
                          for k, v in ev[ev.material.str.startswith(("Water", "SaltyWater"))].blanco.value_counts().head(10).items()}
out["prof_media_cm"] = float(ev.prof_cm.mean()); out["prof_mediana_cm"] = float(ev.prof_cm.median())
out["E_primario_mediana_MeV"] = float(ev.pre_energy_MeV.median())
# ---- productos
TIPOS = ["neutron", "proton", "deuteron", "triton", "He3", "alpha", "pi+", "pi-", "pi0", "gamma"]
s["tipo"] = np.where(s.particle.isin(TIPOS), s.particle, np.where(s.A.fillna(0) > 4, "núcleo residual", "otro"))
mult = s.groupby(["run_id", "parent_step_number", "tipo"]).size().unstack(fill_value=0)
out["multiplicidad_media"] = {k: float(mult[k].mean()) if k in mult else 0.0 for k in TIPOS + ["núcleo residual"]}
out["frac_con"] = {k: float((mult[k] > 0).mean()) if k in mult else 0.0 for k in ["pi+", "pi-", "pi0", "alpha", "deuteron"]}
out["energia_media_MeV"] = {k: float(s[s.tipo == k].kinetic_energy_MeV.mean()) for k in TIPOS if (s.tipo == k).any()}
out["energia_total_media_MeV"] = {k: float(s[s.tipo == k].groupby(["run_id", "parent_step_number"]).kinetic_energy_MeV.sum().sum() / len(ev)) for k in TIPOS + ["núcleo residual"] if (s.tipo == k).any()}
res = s[s.tipo == "núcleo residual"].particle.str.replace(r"\[.*\]", "", regex=True)
out["nucleos_residuales"] = {k: v / len(ev) for k, v in res.value_counts().head(15).items()}
nn = s[s.tipo == "neutron"].groupby(["run_id", "parent_step_number"]).kinetic_energy_MeV
lead = nn.max(); tot = s.groupby(["run_id", "parent_step_number"]).kinetic_energy_MeV.sum()
fl = (lead / ev.set_index(["run_id", "parent_step_number"]).pre_energy_MeV.reindex(lead.index)).dropna()
out["neutron_lider_frac_E_mediana"] = float(fl.median())
out["frac_sin_neutron_saliente"] = float(1 - len(lead) / len(ev))
out["energia_visible_vs_primario"] = float((tot / ev.set_index(["run_id", "parent_step_number"]).pre_energy_MeV.reindex(tot.index)).median())
json.dump(out, open(os.path.join(R, f"inelasticas_primario_{m}.json"), "w"), indent=1, ensure_ascii=False)
EB = np.logspace(-2, np.log10(600), 81)
np.savez_compressed(os.path.join(R, f"inelasticas_primario_{m}.npz"), EB=EB, prof=ev.prof_cm.to_numpy(), mat=ev.material.to_numpy().astype(str),
                    blanco=ev.blanco.to_numpy().astype(str), lider=fl.to_numpy(),
                    **{f"E|{k}": np.histogram(s[s.tipo == k].kinetic_energy_MeV, EB)[0] for k in TIPOS + ["núcleo residual"]},
                    **{f"mult|{k}": np.bincount(mult[k].to_numpy(), minlength=12)[:12] if k in mult else np.zeros(12, int) for k in TIPOS})
print(json.dumps(out, indent=1, ensure_ascii=False))
