#!/usr/bin/env python3
"""Canales de las reacciones inelasticas de neutrones (todos los neutrones: primario y secundarios) y gammas de
desexcitacion de cada nucleo residual. Para cada inelastica (secundarias-inelastica-neutron.tsv):
  blanco (A,Z) por conservacion de carga y numero barionico; canal X(n,x)Y con x = particulas ligeras salientes;
  valor Q del estado fundamental con los excesos de masa (AME2020); energia del neutron incidente (interacciones-neutrones.tsv);
  lineas gamma emitidas en el vertice (energia redondeada a 1 keV).
Uso: canales_reaccion.py <medio> <carpeta corrida> [<carpeta 2> ...] -> resultados/canales_<medio>.json"""
import os, sys, re, json, collections
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.csv as pcsv
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
m, carpetas = sys.argv[1], sys.argv[2:]
SIM = ["n", "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
       "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni"]
# excesos de masa (MeV), AME2020
DM = {"n1": 8.0713, "H1": 7.2890, "H2": 13.1357, "H3": 14.9498, "He3": 14.9312, "He4": 2.4249, "He6": 17.5921,
      "Li6": 14.0869, "Li7": 14.9071, "Li8": 20.9458, "Be7": 15.7690, "Be8": 4.9416, "Be9": 11.3484, "Be10": 12.6074,
      "B8": 22.9216, "B10": 12.0506, "B11": 8.6677, "B12": 13.3689, "C10": 15.6986, "C11": 10.6503, "C12": 0.0, "C13": 3.1250,
      "C14": 3.0199, "C15": 9.8732, "N12": 17.3381, "N13": 5.3455, "N14": 2.8634, "N15": 0.1014, "N16": 5.6837, "N17": 7.8710,
      "O13": 23.115, "O14": 8.0070, "O15": 2.8556, "O16": -4.7370, "O17": -0.8087, "O18": -0.7828, "O19": 3.3329,
      "F17": 1.9517, "F18": 0.8733, "Ne20": -7.0419, "Na22": -5.1824, "Na23": -9.5299, "Na24": -8.4182, "Ne22": -8.0247,
      "Ne23": -5.1540, "Mg23": -5.4735, "Mg24": -13.9336, "F19": -1.4874, "F20": -0.0174, "Ne21": -5.7317, "Na21": -2.1844,
      "Cl34": -24.4401, "Cl35": -29.0135, "Cl36": -29.5218, "Cl37": -31.7615, "Cl38": -29.7980, "S32": -26.0157, "S33": -26.5859,
      "S34": -29.9318, "S35": -28.8464, "S36": -30.6641, "S37": -26.8962, "P31": -24.4410, "P32": -24.3050, "P33": -26.3375,
      "P34": -24.5481, "P35": -24.8577, "Ar36": -30.2316, "Ar37": -30.9476, "Si28": -21.4928, "Si30": -24.4329, "Al27": -17.1967}
MPI = {"pi+": 139.570, "pi-": 139.570, "pi0": 134.977}
LIG = {"neutron": ("n", 1, 0), "proton": ("p", 1, 1), "deuteron": ("d", 2, 1), "triton": ("t", 3, 1), "He3": ("³He", 3, 2),
       "alpha": ("α", 4, 2), "pi+": ("π⁺", 0, 1), "pi-": ("π⁻", 0, -1), "pi0": ("π⁰", 0, 0)}
ORD = ["n", "p", "d", "t", "³He", "α", "π⁺", "π⁻", "π⁰"]
DMLIG = {"n": "n1", "p": "H1", "d": "H2", "t": "H3", "³He": "He3", "α": "He4"}


def nucl(p):
    mm = re.match(r"([A-Z][a-z]?)(\d+)", p)
    return (mm.group(1) + mm.group(2), int(mm.group(2)), SIM.index(mm.group(1))) if mm and mm.group(1) in SIM else None


PLAUS = {"H1", "H2", "O16", "O17", "O18", "Na23", "Cl35", "Cl37", "C12", "C13", "N14", "N15", "Ar40", "Fe54", "Fe56", "Fe57", "Fe58",
         "Cr50", "Cr52", "Cr53", "Cr54", "Ni58", "Ni60", "Ni61", "Ni62", "Ni64", "Mn55", "Si28", "Si29", "Si30"}
# lineas de desexcitacion conocidas (keV) por nucleo emisor
LINEAS = {"C12": [4438.9], "N15": [5269.2, 5297.8, 6323.8, 7300.9], "O15": [5183.0, 5240.9, 6176.3], "O16": [6129.9, 6917.1, 7116.9, 2741.1],
          "N14": [1635.0, 2312.6, 5105.9], "C13": [3684.5, 3853.8], "B11": [2124.7, 4444.0], "C14": [6094.0, 7012.0], "B10": [718.4, 1740.0],
          "O17": [870.8, 3055.4], "Be9": [], "N13": [2365.3], "Cl35": [1219.3, 1763.2], "Na23": [439.9, 2076.0], "Cl36": [788.4, 1164.9]}


def ds(c):
    return os.path.join(c, "Datos-simulacion") if os.path.isdir(os.path.join(c, "Datos-simulacion")) else c


def lector(f, cols, NM):
    h = open(f).readline().lstrip("# ").rstrip("\n").split("\t"); dic = pa.dictionary(pa.int32(), pa.string()); out = []
    for b in pcsv.open_csv(f, read_options=pcsv.ReadOptions(column_names=h, skip_rows=1, block_size=256 << 20),
                           parse_options=pcsv.ParseOptions(delimiter="\t", invalid_row_handler=lambda r: "skip"),
                           convert_options=pcsv.ConvertOptions(include_columns=cols, column_types={c: dic for c in cols if c in ("particle", "material", "step_process", "parent_particle")})):
        d = b.to_pandas(); out.append(d[d.run_id < NM])
    d = pd.concat(out, ignore_index=True)
    for c in ("particle", "material", "step_process", "parent_particle"):
        if c in d:
            d[c] = d[c].astype(str)
    return d


S_, I_, NT = [], [], 0
for c in carpetas:
    d = ds(c); NM = sum(1 for l in open(os.path.join(d, "Carga-total.txt")) if len(l.split()) >= 2 and l.endswith("\n"))
    s = lector(os.path.join(d, "secundarias-inelastica-neutron.tsv"), ["run_id", "parent_particle", "parent_track_id", "parent_step_number", "particle", "material", "kinetic_energy_MeV"], NM)
    s = s[s.parent_particle == "neutron"]
    i = lector(os.path.join(d, "interacciones-neutrones.tsv"), ["run_id", "track_id", "step_number", "step_process", "pre_energy_MeV"], NM)
    i = i[i.step_process == "neutronInelastic"]
    s["run_id"] += NT; i["run_id"] += NT; NT += NM; S_.append(s); I_.append(i)
    print(c[-45:], NM, len(s), len(i), flush=True)
s = pd.concat(S_, ignore_index=True); it = pd.concat(I_, ignore_index=True).rename(columns={"track_id": "parent_track_id", "step_number": "parent_step_number"})
K = ["run_id", "parent_track_id", "parent_step_number"]
reac = []
for k, g in s.groupby(K, sort=False):
    cnt = collections.Counter(); A = Z = 0; res = []; gam = []; Ek = 0.0
    for p, e in zip(g.particle, g.kinetic_energy_MeV):
        if p in LIG:
            sm, a, z = LIG[p]; cnt[sm] += 1; A += a; Z += z; Ek += e
        elif p == "gamma":
            gam.append(e)
        else:
            nu = nucl(p.split("[")[0])
            if nu:
                res.append(nu[0]); A += nu[1]; Z += nu[2]
    At, Zt = A - 1, Z
    blanco = f"{SIM[Zt]}{At}" if 0 < Zt < len(SIM) and At > 0 else "?"
    if blanco not in PLAUS:                 # faltan productos en el archivo (p. ej. el nucleo residual no se registro)
        blanco = "incompleto"
    if not res and cnt.get("n", 0) >= 1 and blanco == f"{SIM[Zt]}{At}":
        pass
    sal = list(cnt.elements())
    # canal: si queda un nucleo residual, X(n, ligeras)Y; las n salientes incluyen la dispersada
    xs = "".join((f"{cnt[t]}{t}" if cnt[t] > 1 else t) for t in ORD if cnt[t])
    if len(res) == 1 and res[0] == blanco and xs == "n":
        xs = "n'"
    if blanco == "incompleto" and not res and xs == "nα" and Zt == 2 and At == 4:
        blanco, res = "O16", ["C12"]           # 16O(n,n alpha)12C con el 12C no registrado (lo delata la linea de 4439 keV)
    canal = f"{blanco}(n,{xs if xs else 'γ'}){'+'.join(res) if res else ''}"
    # Q del estado fundamental
    try:
        Q = DM["n1"] + DM[blanco] - sum(DM[DMLIG[t]] * cnt[t] for t in cnt if t in DMLIG) - sum(DM[r] for r in res) - sum(MPI[p] for p in g.particle if p in MPI)
    except KeyError:
        Q = np.nan
    reac.append((k, blanco, canal, Q, gam, g.material.iloc[0], res[0] if len(res) == 1 else ("+".join(res) if res else "—")))
rdf = pd.DataFrame([dict(zip(K, k), blanco=b, canal=c, Q=q, ng=len(gm), Eg=sum(gm), mat=mt, residual=rs) for k, b, c, q, gm, mt, rs in reac])
rdf = rdf.merge(it.drop_duplicates(K)[K + ["pre_energy_MeV"]], on=K, how="left")
gl = [(c, r, b, round(e * 1e3, 1)) for (k, b, c, q, gm, mt, r) in reac for e in gm]
G = pd.DataFrame(gl, columns=["canal", "residual", "blanco", "E_keV"])
G = G.merge(rdf[["canal"]].drop_duplicates(), on="canal") if False else G
TODAS = sorted({(e, nu) for nu, ls in LINEAS.items() for e in ls})


def linea(E, res, bl):
    """linea discreta solo si pertenece al nucleo residual o al blanco de esa reaccion"""
    for e, nu in TODAS:
        if abs(E - e) <= 10 and (nu == res or nu == bl or nu in str(res).split("+")):
            return f"{e:.0f} ({nu})"
    return None


G["linea"] = [linea(e, r, b) for e, r, b in zip(G.E_keV, G.residual, G.blanco)]
out_lin = None
NR = len(rdf); out = {"N": NT, "inelasticas": NR, "inelasticas_por_neutron_incidente": NR / NT,
                      "material": {k: v / NR for k, v in rdf.mat.value_counts().items()},
                      "blanco": {k: v / NR for k, v in rdf.blanco.value_counts().head(12).items()}}
rango = pd.cut(rdf.pre_energy_MeV, [0, 20, 100, 1000], labels=["< 20 MeV", "20-100 MeV", "> 100 MeV"])
out["por_energia"] = {k: v / NR for k, v in rango.value_counts().sort_index().items()}
canales = []
for c, g in rdf.groupby("canal"):
    if len(g) / NR < 0.002:
        continue
    gg = G[G.canal == c]; lines = gg.E_keV.value_counts()
    canales.append({"canal": c, "frac": len(g) / NR, "Q_MeV": float(g.Q.iloc[0]) if np.isfinite(g.Q.iloc[0]) else None,
                    "E_n_mediana_MeV": float(g.pre_energy_MeV.median()), "frac_E_menor_20MeV": float((g.pre_energy_MeV < 20).mean()),
                    "gammas_por_reaccion": float(g.ng.mean()), "E_gamma_por_reaccion_MeV": float(g.Eg.mean()),
                    "lineas": [(l_, float(n_ / len(g))) for l_, n_ in gg.linea.value_counts().head(4).items() if n_ / len(g) > 0.02]})
out["canales"] = sorted(canales, key=lambda x: -x["frac"])
# origen de los gammas de 4-7 MeV
g47 = G[(G.E_keV >= 4000) & (G.E_keV <= 7000)]
out["gammas_4_7_MeV_por_inelastica"] = len(g47) / NR
out["gammas_4_7_MeV_por_residual"] = {k: v / len(g47) for k, v in g47.residual.value_counts().head(10).items()}
out["gammas_4_7_MeV_lineas"] = {k: float(v / len(g47)) for k, v in g47.linea.fillna("continuo / otras").value_counts().head(14).items()}
out["gammas_4_7_MeV_por_canal"] = {k: float(v / len(g47)) for k, v in g47.canal.value_counts().head(10).items()}
# gammas de 4-7 MeV segun la energia del neutron incidente: HP (< 20 MeV, lineas de ENDF) frente a cascada (> 20 MeV)
Gk = pd.DataFrame([(c, e, k) for (k, b, c, q, gm, mt, r) in reac for e in gm], columns=["canal", "E", "k"])
Ek = dict(zip(map(tuple, rdf[K].to_numpy()), rdf.pre_energy_MeV))
Gk["En"] = [Ek.get(tuple(k), np.nan) for k in Gk.k]
s47 = ((G.E_keV >= 4000) & (G.E_keV <= 7000)).to_numpy()      # misma seleccion que g47 (G y Gk tienen el mismo orden)
out["gammas_4_7_MeV_frac_de_n_menor_20MeV"] = float((Gk.En[s47] < 20).mean())
g47["En"] = Gk.En[s47].to_numpy()
out["gammas_4_7_MeV_frac_lineas_si_En_menor_20"] = float(g47[g47.En < 20].linea.notna().mean())
out["gammas_4_7_MeV_frac_lineas_si_En_mayor_20"] = float(g47[g47.En >= 20].linea.notna().mean())
json.dump(out, open(os.path.join(R, f"canales_{m}.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: out[k] for k in ["inelasticas", "inelasticas_por_neutron_incidente", "blanco", "por_energia", "gammas_4_7_MeV_por_residual", "gammas_4_7_MeV_lineas"]}, indent=1, ensure_ascii=False))
print(json.dumps(out["gammas_4_7_MeV_por_canal"], indent=1, ensure_ascii=False))
print("4-7 MeV: de n<20 MeV", out["gammas_4_7_MeV_frac_de_n_menor_20MeV"], "lineas si <20", out["gammas_4_7_MeV_frac_lineas_si_En_menor_20"], "si >20", out["gammas_4_7_MeV_frac_lineas_si_En_mayor_20"])
for c in out["canales"][:25]:
    print(f"{c['canal']:22s} {100*c['frac']:5.1f}%  Q={c['Q_MeV'] if c['Q_MeV'] is None else round(c['Q_MeV'],2)}  En={c['E_n_mediana_MeV']:.0f}  <20:{100*c['frac_E_menor_20MeV']:.0f}%  ng={c['gammas_por_reaccion']:.2f}  lineas={c['lineas']}")
