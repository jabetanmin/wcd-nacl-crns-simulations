#!/usr/bin/env python3
"""
Tiempo de exposición del campo de neutrones de Bucaramanga (Sec. 4.3 de la tesis).

all_bga_neutron_35.shw (campo en superficie, ARTI + suelo; formato MEIGA "neutron px py pz x y z", p en MeV/c,
pz < 0 = baja) no registra su tiempo. Se fija comparándolo con una corrida de ARTI de referencia en el mismo sitio:
Salida_BGA_300.shw del repositorio público github.com/csarmiento03/ReunionLAGO2025_ARTI (commit 9ad4c23), ARTI v1r9,
nivel de observación 956 m, ΔS = 1 m², Δt = 300 s (el número del nombre es el argumento -t en segundos; Asorey et
al. 2018, ecs. 13-14). Formato ARTI: CorsikaId px py pz x y z ... con p en GeV/c; neutrón = 13; pz > 0 = baja.

CORSIKA corta los neutrones por debajo de ~50 MeV, así que se comparan las tasas de neutrones que bajan por encima
de un umbral (50 MeV, 100 MeV y 1 GeV): T = N(all_bga, > E) / [N(ARTI, > E) / 300 s].
Uso: verificar_tiempo_exposicion.py <all_bga_neutron_35.shw> <Salida_BGA_300.shw>
"""
import sys
import numpy as np

M_N = 939.565                                     # MeV
T_ARTI = 300.0                                    # s
UMBRALES = (50.0, 100.0, 1000.0)                  # MeV

def ek(p):                                        # |p| en MeV/c -> energía cinética en MeV
    return np.sqrt(p ** 2 + M_N ** 2) - M_N

def leer_meiga(f):
    p = np.loadtxt(f, usecols=(1, 2, 3))
    return ek(np.linalg.norm(p, axis=1))[p[:, 2] < 0]          # solo los que bajan

def leer_arti(f):
    filas = [l.split() for l in open(f) if not l.startswith("#")]
    p = np.array([[float(x) for x in r[1:4]] for r in filas if int(r[0]) == 13]) * 1e3   # GeV/c -> MeV/c
    return ek(np.linalg.norm(p, axis=1))[p[:, 2] > 0]

if len(sys.argv) != 3: sys.exit(__doc__)
Eb, Ea = leer_meiga(sys.argv[1]), leer_arti(sys.argv[2])
print(f"ARTI 300 s, 1 m²: {len(Ea)} neutrones que bajan; all_bga: {len(Eb)} neutrones que bajan")
for u in UMBRALES:
    na, nb = int(np.sum(Ea > u)), int(np.sum(Eb > u))
    tasa = na / T_ARTI
    T = nb / tasa
    print(f"E > {u:6.0f} MeV: ARTI {na:5d} ({tasa:6.2f} n m⁻² s⁻¹, ±{100 / np.sqrt(na):.1f} %), all_bga {nb:7d}"
          f"  ->  T = {T:8.0f} s = {T / 3600:5.2f} h")
