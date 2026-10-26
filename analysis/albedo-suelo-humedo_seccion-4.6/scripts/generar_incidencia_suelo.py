#!/usr/bin/env python3
"""
Neutrones incidentes sobre el suelo para MEIGA (con el parche Parche-suelo-SoilBS), a partir del flujo de la tesis.

Entrada: all_bga_neutron_35.shw (tesis, flujo en la superficie de Bucaramanga; "neutron px py pz x y z ...",
p en MeV/c, x, y en mm; pz < 0 = baja hacia el suelo, pz > 0 = sube = albedo del suelo seco). Se toman los que BAJAN.
Salida: N neutrones (muestreados al azar sin reemplazo) con su energía y su dirección originales, en posiciones
uniformes sobre la región de inyección, 1 cm por encima del plano contador (z_plano + 1 cm), formato ARTI de MEIGA
"13 px py pz x y z C 0 0 0 0" (GeV/c, cm, pz invertido: pz > 0 en el archivo = hacia abajo en MEIGA).
Región de inyección: x, y en [-8.5, 8.5] m (uniforme), a 1.5 m de los bordes de un suelo de 20 x 20 x 1 m, sin tanque
(MEIGA_SIN_TANQUE=1). Con --con-tanque, x en [2.0, 8.5] m (lejos del tanque en x = y = 0).
Uso: generar_incidencia_suelo.py <all_bga_neutron_35.shw> [--N 200000] [--z-plano 5] [--salida carpeta]
"""
import argparse, json, os
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("shw")
ap.add_argument("--N", type=int, default=200000)
ap.add_argument("--z-plano", type=float, default=5.0, help="cm sobre la superficie del suelo")
ap.add_argument("--semilla", type=int, default=20261023)
ap.add_argument("--salida", default=None)
ap.add_argument("--con-tanque", action="store_true")
a = ap.parse_args()
rng = np.random.default_rng(a.semilla)
M_N = 939.565

d = np.loadtxt(a.shw, usecols=(1, 2, 3), dtype=float)           # MeV/c
idx_baja = np.nonzero(d[:, 2] < 0)[0]
sel = np.sort(rng.choice(idx_baja, size=min(a.N, len(idx_baja)), replace=False))
P = d[sel] / 1000.0                                               # GeV/c
p = np.linalg.norm(d[sel], axis=1)
E = np.sqrt(p ** 2 + M_N ** 2) - M_N                              # MeV (para p pequeño: p^2/2m)
E = np.where(p < 1e-2, p ** 2 / (2 * M_N), E)
n = len(sel)
x = rng.uniform(200.0 if a.con_tanque else -850.0, 850.0, n); y = rng.uniform(-850.0, 850.0, n); z = np.full(n, a.z_plano + 1.0)
Pf = P.copy(); Pf[:, 2] *= -1                                     # convención de MEIGA

nombre = f"{n}N-Bga-baja-sobre-suelo"
dsal = a.salida or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "flujos")
os.makedirs(os.path.join(dsal, "prueba"), exist_ok=True)
ruta = os.path.join(dsal, nombre + ".txt")
np.savetxt(ruta, np.column_stack([Pf, x, y, z, np.full(n, 5)]), fmt="13 %.6e %.6e %.6e %.4f %.4f %.4f %d 0 0 0 0")
np.savetxt(ruta.replace(".txt", "-componentes.txt"), np.column_stack([sel, E * 1e6]), fmt="%d %.6e",
           header="linea_en_all_bga  E[eV]   (linea k = run_id k)")
for suf in (".txt", "-componentes.txt"):
    lin = open(ruta.replace(".txt", suf)).read().splitlines()
    cab = [l for l in lin if l.startswith("#")]; dat = [l for l in lin if not l.startswith("#")]
    # prueba: 30 neutrones que cubren el rango de energía (los 10 de menor, 10 intermedios y 10 de mayor energía)
    if suf == ".txt":
        orden = np.argsort(E); elegidos = np.concatenate([orden[:10], orden[n // 2 - 5:n // 2 + 5], orden[-10:]])
    open(os.path.join(dsal, "prueba", os.path.basename(ruta.replace(".txt", suf)).replace(f"{n}N", "30N")), "w").write(
        "\n".join(cab + [dat[i] for i in sorted(elegidos)]) + "\n")
fr = lambda a_, b_: float(np.mean((E >= a_) & (E < b_)))
res = {"archivo": os.path.basename(ruta), "N": n, "de_los_que_bajan": int(len(idx_baja)), "semilla": a.semilla,
       "z_plano_cm": a.z_plano, "z_inyeccion_cm": a.z_plano + 1.0, "region_inyeccion_cm": ("x 200..850" if a.con_tanque else "x -850..850") + ", y -850..850", "tanque": bool(a.con_tanque),
       "E_min_MeV": float(E.min()), "E_max_MeV": float(E.max()),
       "fracciones": {"termico <0.5 eV": fr(0, 5e-7), "epitermico 0.5 eV-0.1 MeV": fr(5e-7, 0.1),
                      "evaporacion 0.1-20 MeV": fr(0.1, 20), "cascada >20 MeV": fr(20, 1e9)},
       "cos_theta_medio": float(np.mean(-d[sel, 2] / p))}
json.dump(res, open(os.path.join(dsal, "resumen.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
