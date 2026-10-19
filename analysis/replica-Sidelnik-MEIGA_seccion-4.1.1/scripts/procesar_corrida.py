#!/usr/bin/env python3
"""Procesa una corrida tipo Sidelnik (MEIGA, 150000 neutrones de 500 MeV horizontales).

Lee <carpeta>/Datos-simulacion/*.tsv, Carga-total*.txt y <carpeta>/output.json.gz y guarda
en un .npz todo lo necesario para comparar con Sidelnik et al. (2020) y para el analisis
propio. Cada neutron primario es una corrida de MEIGA: el evento se identifica por run_id.

Uso: procesar_corrida.py <carpeta de la corrida> <salida.npz>
Acepta corridas interrumpidas: usa solo los neutrones terminados (ver eventos_completos) y
output.json.gz es opcional (MEIGA lo escribe al final).
"""
import sys, os, time, gzip, json
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pcsv

C, OUT = sys.argv[1], sys.argv[2]
DS = os.path.join(C, "Datos-simulacion") if os.path.isdir(os.path.join(C, "Datos-simulacion")) else C   # docker cp puede dejar los archivos sin subcarpeta
t0 = time.time()
out = {}
EB = np.logspace(-6, np.log10(600), 601)          # MeV, bins logaritmicos
GB = np.arange(0, 20.0001, 0.005)                 # MeV, 5 keV para espectros gamma de lineas
out["EB"] = EB; out["GB"] = GB


def log(msg):
    print(f"[{time.time()-t0:6.0f}s] {msg}", flush=True)


def leer(nombre, cols, dtypes=None):
    if cols is not None and "run_id" not in cols:
        cols = list(cols) + ["run_id"]
    d = pd.read_csv(os.path.join(DS, nombre), sep="\t", comment=None, skiprows=1, header=None,
                    names=HDR[nombre], usecols=cols, dtype=dtypes, on_bad_lines="skip")
    d = d[pd.to_numeric(d.run_id, errors="coerce") < NMAX]
    d["run_id"] = d.run_id.astype(np.int64)
    return d


def eventos_completos(ds):
    """Eventos terminados = lineas completas de Carga-total.txt (una por neutron). En una corrida
    interrumpida el ultimo neutron queda a medias y se descartan sus filas (run_id >= este valor)."""
    n = 0
    for l in open(os.path.join(ds, "Carga-total.txt")):
        if len(l.split()) >= 2 and l.endswith("\n"):
            n += 1
    return n


NMAX = eventos_completos(DS)
HDR = {}
for f in os.listdir(DS):
    if f.endswith(".tsv"):
        with open(os.path.join(DS, f)) as fh:
            HDR[f] = fh.readline().lstrip("# ").rstrip("\n").split("\t")

# ---------------- incidentes ----------------
inc = leer("neutrones-incidentes.tsv", ["run_id", "pre_x_cm", "pre_y_cm", "pre_z_cm", "pre_energy_MeV"])
N = int(inc.run_id.nunique()); out["N"] = N
assert N == NMAX, (N, NMAX)
out["inc_E0"] = inc.pre_energy_MeV.to_numpy()
out["inc_pos"] = inc[["pre_x_cm", "pre_y_cm", "pre_z_cm"]].to_numpy()
log(f"incidentes: {N}")

# ---------------- capturas ----------------
cap = leer("capturas-neutrones.tsv", None)
for k in ["run_id", "track_id", "parent_id", "step_number", "target_Z", "target_A"]:
    out[f"cap_{k}"] = cap[k].to_numpy()
for k in ["post_x_cm", "post_y_cm", "post_z_cm", "pre_energy_MeV", "global_time_ns"]:
    out[f"cap_{k}"] = cap[k].to_numpy()
out["cap_material"] = cap.material.to_numpy().astype(str)
log(f"capturas: {len(cap)}")

# ---------------- productos de captura ----------------
sc = leer("secundarias-captura-neutron.tsv", ["run_id", "parent_track_id", "parent_step_number", "particle",
                                               "material", "kinetic_energy_MeV"])
out["sc_run"] = sc.run_id.to_numpy(); out["sc_ptrk"] = sc.parent_track_id.to_numpy()
out["sc_part"] = sc.particle.to_numpy().astype(str); out["sc_E"] = sc.kinetic_energy_MeV.to_numpy()
out["sc_material"] = sc.material.to_numpy().astype(str)
log(f"productos de captura: {len(sc)}")

# ---------------- primario: primera interaccion e inelasticas ----------------
cols = ["run_id", "track_id", "step_number", "step_process", "material", "post_x_cm", "post_y_cm", "post_z_cm",
        "pre_energy_MeV", "post_energy_MeV", "global_time_ns"]
prim = []
rd = pcsv.open_csv(os.path.join(DS, "interacciones-neutrones.tsv"),
                   read_options=pcsv.ReadOptions(column_names=HDR["interacciones-neutrones.tsv"], skip_rows=1,
                                                 block_size=256 << 20),
                   parse_options=pcsv.ParseOptions(delimiter="\t", invalid_row_handler=lambda r: "skip"),
                   convert_options=pcsv.ConvertOptions(include_columns=cols))
n_int = {}
for b in rd:
    d = b.to_pandas(); d = d[d.run_id < NMAX]
    vc = d.groupby(["step_process", "material"]).size()
    for k, v in vc.items():
        n_int[k] = n_int.get(k, 0) + int(v)
    prim.append(d[d.track_id == 1])
prim = pd.concat(prim)
first = prim.sort_values(["run_id", "step_number"]).groupby("run_id").first()
out["prim1_run"] = first.index.to_numpy(); out["prim1_proc"] = first.step_process.to_numpy().astype(str)
out["prim1_mat"] = first.material.to_numpy().astype(str); out["prim1_x"] = first.post_x_cm.to_numpy()
out["prim1_Epost"] = first.post_energy_MeV.to_numpy()
inel = prim[prim.step_process == "neutronInelastic"]
out["prim_inel_run"] = inel.run_id.to_numpy(); out["prim_inel_x"] = inel.post_x_cm.to_numpy()
out["prim_inel_E"] = inel.pre_energy_MeV.to_numpy()
out["int_claves"] = np.array([f"{a}|{b}" for a, b in n_int]); out["int_n"] = np.array(list(n_int.values()))
log(f"interacciones de neutrones: {sum(n_int.values())}")

# ---------------- gammas: creacion y primera interaccion ----------------
def histos_stream(nombre, cols, fn, bs=256 << 20):
    cols = cols if "run_id" in cols else cols + ["run_id"]
    rd = pcsv.open_csv(os.path.join(DS, nombre),
                       read_options=pcsv.ReadOptions(column_names=HDR[nombre], skip_rows=1, block_size=bs),
                       parse_options=pcsv.ParseOptions(delimiter="\t", invalid_row_handler=lambda r: "skip"),
                       convert_options=pcsv.ConvertOptions(include_columns=cols))
    for b in rd:
        d = b.to_pandas()
        fn(d[d.run_id < NMAX])


acc = {}


def add(key, h):
    acc[key] = acc.get(key, 0) + h


def gam(d):
    s1 = d[d.step_number == 1]
    agua = s1.material.str.startswith(("Water", "SaltyWater"))
    for cp, g in s1[agua].groupby("creator_process"):
        add(f"gcre|{cp}", np.histogram(g.pre_energy_MeV, EB)[0])
        add(f"gcrelin|{cp}", np.histogram(g.pre_energy_MeV, GB)[0])
    add("gcre_fuera", np.histogram(s1.pre_energy_MeV[~agua], EB)[0])
    pr = d.groupby("run_id").size()
    add("g_nfilas", len(d))


histos_stream("pasos-gamma.tsv", ["run_id", "step_number", "creator_process", "material", "pre_energy_MeV"], gam)
log("pasos-gamma")


def gint(d):
    agua = d.material.str.startswith(("Water", "SaltyWater"))
    for p, g in d[agua].groupby("step_process"):
        add(f"gint|{p}", np.histogram(g.pre_energy_MeV, EB)[0])
        add(f"gintlin|{p}", np.histogram(g.pre_energy_MeV, GB)[0])


histos_stream("interacciones-gamma.tsv", ["step_process", "material", "pre_energy_MeV"], gint)
log("interacciones-gamma")

# ---------------- electrones creados por gammas ----------------
def egam(d):
    agua = d.material.str.startswith(("Water", "SaltyWater"))
    for (p, part), g in d[agua].groupby(["category", "particle"]):
        add(f"egam|{p}|{part}", np.histogram(g.kinetic_energy_MeV, EB)[0])
        add(f"egamlin|{p}|{part}", np.histogram(g.kinetic_energy_MeV, GB)[0])


histos_stream("secundarias-interaccion-gamma.tsv", ["category", "particle", "material", "kinetic_energy_MeV"], egam)
log("electrones de gammas")

# ---------------- todos los electrones: creacion ----------------
def ele(d):
    s1 = d[d.step_number == 1]
    agua = s1.material.str.startswith(("Water", "SaltyWater"))
    for (cp, part), g in s1[agua].groupby(["creator_process", "particle"]):
        add(f"ecre|{cp}|{part}", np.histogram(g.pre_energy_MeV, EB)[0])


histos_stream("pasos-electrones.tsv", ["particle", "step_number", "creator_process", "material", "pre_energy_MeV"], ele)
log("pasos-electrones")

# ---------------- fotones Cherenkov ----------------
nch = np.zeros(N + 1, np.int64)
EPH = np.linspace(1.5e-6, 4.5e-6, 301)


def cher(d):
    nch[:] += np.bincount(d.run_id.to_numpy(), minlength=N + 1)[:N + 1]
    for p, g in d.groupby("parent_particle"):
        add(f"cher_padre|{p}", np.array([len(g)]))
    add("cher_E", np.histogram(d.kinetic_energy_MeV, EPH)[0])
    add("cher_mat|agua", np.array([int(d.material.str.startswith(("Water", "SaltyWater")).sum())]))


histos_stream("fotones-cherenkov.tsv", ["run_id", "parent_particle", "material", "kinetic_energy_MeV"], cher, bs=512 << 20)
out["cher_n_por_run"] = nch[:N]; out["EPH"] = EPH
log("fotones Cherenkov")

for k, v in acc.items():
    out["H_" + k] = np.asarray(v)

# ---------------- carga ----------------
q = np.array([int(l.split()[1]) for l in open(os.path.join(DS, "Carga-total.txt")) if len(l.split()) >= 2 and l.endswith("\n")])
d = pd.read_csv(os.path.join(DS, "Carga-total-cada-N.txt"), sep="\t", header=None, names=["Q", "i", "t"], on_bad_lines="skip").dropna()
ev = np.cumsum(d.i.to_numpy() == 0) - 1
d = d[ev < NMAX]; ev = ev[ev < NMAX]
assert ev[-1] + 1 == len(q) == N, (ev[-1] + 1, len(q), N)
pe = d.Q.to_numpy() > 0
out["Q"] = q; out["pe_ev"] = ev[pe].astype(np.int32); out["pe_t_ns"] = d.t.to_numpy()[pe] * 1e9
if os.path.exists(os.path.join(C, "output.json.gz")):
    o = json.load(gzip.open(os.path.join(C, "output.json.gz")))["Output"]
    ks = sorted((k for k in o if k.startswith("Event_")), key=lambda k: int(k.split("_")[1]))
    out["json_Q"] = np.array([o[k]["Detector_0"]["OptDevice_0"]["Charge"] for k in ks])
    out["json_Edep"] = np.array([o[k]["Detector_0"].get("EnergyDeposit", np.nan) for k in ks])
else:
    log("sin output.json.gz (corrida interrumpida): se usa solo Carga-total.txt")
log(f"carga: {len(q)} eventos")

np.savez_compressed(OUT, **out)
log(f"LISTO -> {OUT}")
