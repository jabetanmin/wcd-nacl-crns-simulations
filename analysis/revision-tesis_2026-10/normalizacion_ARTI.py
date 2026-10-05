#!/usr/bin/env python3
"""Normalización temporal de los flujos de ARTI y del flujo completo en la superficie (Sec. 4.3-4.4).

Esquema de simulación: ARTI calcula el flujo en lo alto de un bloque atmosférico de MEIGA de 2000 m
(10 capas de 200 m) sobre el suelo; el flujo completo se registra en la superficie (z = -1000 m).
  * S3_bga_003600_neutrons.shw: salida de ARTI para 1 m2 y t = 3600 s (opción -t; Sarmiento-Cano et al.
    2022), en el nivel de inyección. 317 537 neutrones entre 20 MeV y 135 GeV: 8.82e-3 n cm-2 s-1.
  * all_bga_neutron_35.shw: flujo completo en la superficie, normalizado a 12 h. Sus neutrones
    descendentes de más de 20 MeV equivalen al 17 % de los que entran por arriba, es decir, a una longitud
    de atenuación de unos 115 g/cm2 para unos 200 g/cm2 de aire, compatible con la atenuación del componente
    nucleónico; con Lambda = 115-140 g/cm2 el tiempo compatible es de 9 a 12 h.

Uso: python3 normalizacion_ARTI.py <S3_bga_003600_neutrons.shw> <all_bga_neutron_35.shw> [salida_bga_30.shw]
"""
import math
import sys

M = 939.565


def energia(px, py, pz):
    return math.sqrt(px * px + py * py + pz * pz + M * M) - M


s3, completo = sys.argv[1], sys.argv[2]
E3 = []
for linea in open(s3):
    p = linea.split()
    if p and not p[0].startswith("#"):
        try:
            E3.append(energia(*(float(v) * 1000 for v in p[1:4])))   # GeV/c -> MeV
        except ValueError:
            pass
tasa_arriba = len(E3) / 3600.0
print(f"ARTI (1 h, 1 m2): {len(E3)} neutrones, {min(E3):.2f}-{max(E3):.4g} MeV, "
      f"{tasa_arriba:.1f} n m-2 s-1 = {len(E3)/(1e4*3600):.3e} n cm-2 s-1")

baja20 = 0
for linea in open(completo):
    p = linea.split()
    if len(p) > 6 and p[0] == "neutron":
        px, py, pz = map(float, p[1:4])          # MeV/c; pz < 0 desciende
        baja20 += pz < 0 and energia(px, py, pz) > 20
tasa_suelo = baja20 / 43200.0
f = tasa_suelo / tasa_arriba
print(f"Flujo completo (12 h): {baja20} neutrones descendentes > 20 MeV = {tasa_suelo:.1f} n m-2 s-1")


def profundidad(h):                              # atmósfera estándar, g/cm2
    return 1013.25 * (1 - 2.25577e-5 * h) ** 5.25588 * 1.0197


dX = profundidad(956) - profundidad(2956)
print(f"Fracción que llega al suelo: {f:.3f}; aire = {dX:.0f} g/cm2 -> Lambda = {dX/math.log(1/f):.0f} g/cm2")
for L in (115, 120, 130, 140):
    print(f"  Lambda = {L}: tiempo compatible {baja20/(tasa_arriba*math.exp(-dX/L))/3600:.1f} h")

if len(sys.argv) > 3:
    n = n20 = 0
    for linea in open(sys.argv[3]):
        if linea.startswith("#"):
            continue
        p = linea.split()
        if len(p) < 4:
            continue
        n += 1
        if int(p[0]) == 13 and energia(*(float(v) * 1000 for v in p[1:4])) > 20:
            n20 += 1
    print(f"Muestra de ARTI a 956 m: {n} partículas, {n20} neutrones > 20 MeV; "
          f"cociente nivel de inyección / suelo = {tasa_arriba/(n20/30):.1f} (si es de 30 s)")
