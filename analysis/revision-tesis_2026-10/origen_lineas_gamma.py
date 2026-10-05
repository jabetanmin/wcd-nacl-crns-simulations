#!/usr/bin/env python3
"""Origen de las líneas gamma del Na (Cap. 4) y de los fotones de 6-7 MeV (Apéndice E).

Lee los archivos gamma-completo-*.txt de la Campaña 1 (columnas: partícula, track, padre, paso,
proceso, x, y, z, E [MeV]) y toma la energía de cada fotón en su primer paso cuando ese paso no
modifica la energía (Transportation o Rayl). Si el padre es el track 1 (el neutrón primario), el fotón
procede de la captura; en otro caso, de un decaimiento posterior.

Resultados de la revisión: 1.3686 y 2.7541 MeV proceden del decaimiento beta del 24Na (padre distinto
del neutrón); las líneas de captura del Na son 0.4722 y 3.9823 MeV. Entre 6 y 7 MeV, el 9-12.5 % de
los fotones en los medios con NaCl procede de la captura en 35Cl (6.111, 6.620, 6.628, 6.978 MeV),
frente a menos del 0.1 % en agua pura; no aparece 16O(n,n'gamma).

Uso: python3 origen_lineas_gamma.py <carpeta Gammas de la Campaña 1>
"""
import collections
import glob
import sys

base = sys.argv[1]
LINEAS = {"Na 0.4722 (captura)": 0.4722, "Na 3.9823 (captura)": 3.9823,
          "24Mg 1.3686 (decaimiento 24Na)": 1.3686, "24Mg 2.7541 (decaimiento 24Na)": 2.7541,
          "H 2.2232": 2.2232, "Cl 6.1109": 6.1109}
for medio in ("Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"):
    madres = {k: collections.Counter() for k in LINEAS}
    total = rango67 = 0
    for f in glob.glob(f"{base}/*/{medio}/gamma-completo-*.txt"):
        for linea in open(f):
            p = linea.split()
            if len(p) < 9 or p[3] != "1" or p[4] not in ("Transportation", "Rayl"):
                continue
            e = float(p[8])
            total += 1
            rango67 += 6 <= e <= 7
            for k, v in LINEAS.items():
                if abs(e - v) < 0.0015:
                    madres[k]["neutrón" if p[2] == "1" else "otra"] += 1
    print(f"{medio}: {total} fotones iniciales; entre 6 y 7 MeV {100*rango67/max(total,1):.2f} %")
    for k in LINEAS:
        if madres[k]:
            print(f"   {k:32s} {dict(madres[k])}")
