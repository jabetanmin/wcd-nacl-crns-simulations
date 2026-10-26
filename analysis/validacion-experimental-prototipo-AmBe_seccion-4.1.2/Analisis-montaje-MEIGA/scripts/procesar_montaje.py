#!/usr/bin/env python3
"""
Procesa una corrida MEIGA del montaje Am-Be (1 000 000 de neutrones por el costado, 4 partes) y deja un
resumen por evento: componente (haz/halo/fondo), energía inicial, carga, capturas (total, en el medio,
núcleo de la primera captura en el medio), tiempo de la primera captura.
Uso: procesar_montaje.py <carpeta 1000000N-...> <etiqueta medio: pura|nacl25|nacl10> [carpeta de salida]
-> <salida, por defecto resultados/>/eventos_<medio>.npz, verificacion_<medio>.json
"""
import json, os, sys
import numpy as np

D, M = sys.argv[1], sys.argv[2]
RES = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
os.makedirs(RES, exist_ok=True)
M_N = 939.565
comp_f = [f for f in os.listdir(D) if f.endswith("-componentes.txt")][0]
CE = np.loadtxt(os.path.join(D, comp_f))                       # componente, E[eV] por línea global
FL = np.loadtxt(os.path.join(D, comp_f.replace("-componentes", "")), usecols=(1, 2, 3))
partes = sorted(p for p in os.listdir(D) if p.startswith("parte"))
Q, NCAP, NCAP_M, NUC, TCAP, ZCAP, XCAP, E_IN, MAT_IN = [], [], [], [], [], [], [], [], []
ver = {"partes": {}}
off = 0
for p in partes:
    dp = os.path.join(D, p); ds = os.path.join(dp, "Datos-simulacion")
    n = sum(1 for _ in open(os.path.join(dp, f"{p}.txt")))
    q = np.array([int(l.split()[1]) for l in open(os.path.join(ds, "Carga-total.txt")) if l.strip()])
    assert len(q) == n, (p, len(q), n)
    # neutrones incidentes: energía del primer paso (comprueba el orden de las líneas)
    ein = np.full(n, np.nan); mat = np.empty(n, dtype=object)
    for l in open(os.path.join(ds, "neutrones-incidentes.tsv")):
        if l[0] == "#": continue
        c = l.split("\t"); r = int(c[0])
        if c[3] == "1" and c[5] == "1": ein[r] = float(c[15]); mat[r] = c[8]
    ncap = np.zeros(n, int); ncap_m = np.zeros(n, int)
    nuc = np.zeros(n, int); tcap = np.full(n, np.nan); zcap = np.full(n, np.nan); xcap = np.full(n, np.nan)
    for l in open(os.path.join(ds, "capturas-neutrones.tsv")):
        if l[0] == "#": continue
        c = l.split("\t"); r = int(c[0])
        ncap[r] += 1
        if c[7].startswith(("Water", "SaltyWater")):
            ncap_m[r] += 1
            if nuc[r] == 0:
                nuc[r] = int(c[8]) * 1000 + int(c[9]); tcap[r] = float(c[18]); zcap[r] = float(c[15]); xcap[r] = float(c[13])
        elif nuc[r] == 0 and ncap_m[r] == 0:
            pass
    Q.append(q); NCAP.append(ncap); NCAP_M.append(ncap_m); NUC.append(nuc); TCAP.append(tcap); ZCAP.append(zcap)
    XCAP.append(xcap); E_IN.append(ein); MAT_IN.append(mat)
    # comprobación: energía del primer paso = energía del archivo
    p_f = np.linalg.norm(FL[off:off + n], axis=1) * 1000
    e_f = p_f ** 2 / (np.sqrt(p_f ** 2 + M_N ** 2) + M_N)
    ok = np.isfinite(ein)
    ver["partes"][p] = {"eventos": int(n), "desde_linea": off, "con_paso_1": int(ok.sum()),
                        "max_dif_rel_energia": float(np.max(np.abs(ein[ok] - e_f[ok]) / e_f[ok]))}
    off += n
Q = np.concatenate(Q); NCAP = np.concatenate(NCAP); NCAP_M = np.concatenate(NCAP_M); NUC = np.concatenate(NUC)
TCAP = np.concatenate(TCAP); ZCAP = np.concatenate(ZCAP); XCAP = np.concatenate(XCAP); E_IN = np.concatenate(E_IN)
ver["eventos_total"] = int(len(Q)); ver["lineas_archivo"] = int(len(CE))
assert len(Q) == len(CE)
np.savez_compressed(os.path.join(RES, f"eventos_{M}.npz"), comp=CE[:, 0].astype(int), E0_eV=CE[:, 1], Q=Q,
                    ncap=NCAP, ncap_medio=NCAP_M, nucleo=NUC, t_cap_ns=TCAP, z_cap_cm=ZCAP, x_cap_cm=XCAP)
json.dump(ver, open(os.path.join(RES, f"verificacion_{M}.json"), "w"), indent=2)
print(json.dumps(ver, indent=1))
