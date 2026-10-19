#!/usr/bin/env python3
"""Genera el archivo de entrada (formato ARTI que lee MEIGA/ParticleFiller) para la
replica de Sidelnik et al. (2020): neutrones monoenergeticos de 500 MeV que entran
horizontalmente al WCD a media altura, desde 1 cm fuera del borde exterior del tanque.

Formato de cada linea (12 columnas, unidades CORSIKA):
  id  px  py  pz  x  y  z  id_lluvia  id_primario  E_primario  theta  phi
  id 13 = neutron;  p en GeV/c;  x, y, z en cm.
ParticleFiller guarda el momento como (px, py, -pz), asi que px > 0 y pz = 0 da la
direccion +x (horizontal, hacia el centro del tanque).  Con injectionMode = eCircle
y radio 0, la POSICION la fija DetectorList.xml y la DIRECCION la toma de este archivo;
x, y, z de aqui se escriben solo como referencia.

Uso:  python3 generar_flujo.py            (crea los archivos de 150000 y de 10 neutrones)
"""
import math

M_N = 0.93956542          # masa del neutron [GeV]
T = 0.500                 # energia cinetica [GeV]
p = math.sqrt(T * T + 2 * T * M_N)       # = 1.09067 GeV/c

# Geometria de MEIGA actual (SaltyWCD.cc integrado), con los valores de DetectorList.xml:
#   agua: radio 48 cm, altura 133 cm; Tyvek 0,12 mm; acero 0,5 mm; fondo del tanque en z = 0.
#   capas desde el agua: agua -> Tyvek -> acero (lados, tapa y fondo).
R_AGUA, H_AGUA, TYVEK, ACERO = 48.0, 133.0, 0.012, 0.05      # cm
R_EXT = R_AGUA + TYVEK + ACERO                                # 48,062 cm
X0 = -(R_EXT + 1.0)                                           # 1 cm fuera del borde exterior
Z0 = ACERO + TYVEK + H_AGUA / 2                               # media altura (= centro del agua) = 66,562 cm

for n, nombre in [(150000, "150000N-500MeV-Sidelnik.txt"), (10, "10N-500MeV-Sidelnik.txt")]:
    linea = f"13 {p:.5f} 0 0 {X0:.3f} 0 {Z0:.3f} 0 0 0 0 0\n"
    with open(nombre, "w") as f:
        f.write(linea * n)
    print(f"{nombre}: {n} neutrones, p = {p:.5f} GeV/c, fuente en x = {X0:.3f} cm, z = {Z0:.3f} cm, direccion +x")
