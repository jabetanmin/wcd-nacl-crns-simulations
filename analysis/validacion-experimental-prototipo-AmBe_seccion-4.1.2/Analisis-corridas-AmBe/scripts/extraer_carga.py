#!/usr/bin/env python3
"""Lee output.json de cada corrida AmBe (MEIGA) y guarda por evento: energía inicial E0 (MeV, desde
el momento del primario), carga (p.e.), energía depositada y posición de inyección.
-> resultados/carga_<medio>.npz"""
import json, os, re
import numpy as np

BASE = os.path.join(os.environ.get("ADATA", os.path.join("/media", os.environ.get("USER", "ubuntu"), "ADATA HD330")), "Simulacion-fuente-241AmBe", "Tipos-medios")   # disco: variable ADATA
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
M_N = 939.565
ARCH = {"pura": f"{BASE}/Agua-pura/output.json",
        "nacl25": f"{BASE}/Agua+2.5NaCl/Datos-simulacion/output.json",
        "nacl10": f"{BASE}/Agua+10NaCl/output.json"}
pat = re.compile(r'"Event_(\d+)":\{"InputFlux":\{"ID":(\d+),"Position":\[([^\]]+)\],"Momentum":\[([^\]]+)\]\},'
                 r'"Detector_0":\{"EnergyDeposit":([^,]+),"OptDevice_0":\{"Charge":(\d+)\}\}\}')
for m, f in ARCH.items():
    t = open(f).read()
    filas = pat.findall(t)
    n_ev = len(re.findall(r'"Event_\d+"', t))
    assert len(filas) == n_ev, (m, len(filas), n_ev)
    idx = np.array([int(r[0]) for r in filas])
    pos = np.array([[float(v) for v in r[2].split(",")] for r in filas])
    mom = np.array([[float(v) for v in r[3].split(",")] for r in filas])   # MeV/c
    p = np.linalg.norm(mom, axis=1)
    E0 = p ** 2 / (np.sqrt(p ** 2 + M_N ** 2) + M_N)
    o = np.argsort(idx)
    np.savez_compressed(os.path.join(RES, f"carga_{m}.npz"), evento=idx[o], E0=E0[o],
                        carga=np.array([int(r[5]) for r in filas])[o],
                        edep=np.array([float(r[4]) for r in filas])[o], pos=pos[o])
    print(m, "eventos", n_ev, "indices 0..", idx.max(), "contiguos", bool(np.all(np.sort(idx) == np.arange(n_ev))),
          "Q>0", int((np.array([int(r[5]) for r in filas]) > 0).sum()), flush=True)
