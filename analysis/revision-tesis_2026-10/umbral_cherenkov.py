#!/usr/bin/env python3
"""Máximo del espectro de electrones Cherenkov (Tabla 4.18) y conteos en la ventana (Tabla 4.19).

Hallazgos de la revisión: (1) los archivos Cerenkov-A{25,5,10}NaCl-*.txt usados en el notebook
Ajuste-cherenkov-AP-1me-1keV.ipynb se obtuvieron restando una constante a las energías de Geant4
(0.0056128, 0.0093931 y 0.0153931 MeV); con los datos sin desplazar, el máximo está en 0.2641 MeV en los
cuatro medios. (2) En la Tabla 4.19 la fila de 10 meV de 5 y 10 % de NaCl repetía la de 100 meV porque
el notebook cargó el archivo de 100 meV dos veces; los conteos correctos son 168 296 y 229 272.

Uso: python3 umbral_cherenkov.py <carpeta imagenes-resultados/Cherenkov>
"""
import os
import sys

import numpy as np
from scipy.optimize import curve_fit

base = sys.argv[1]
ENERGIAS = ["1meV", "10meV", "100meV", "1000meV", "1000000meV"]
MEDIOS = {"Agua pura": (["Agua-pura"], 0.0, (0.2596, 0.2686)),
          "2.5 % NaCl": (["Agua+25NaCl", "Agua+2.5NaCl"], 0.0056128, (0.25396, 0.26296)),
          "5 % NaCl": (["Agua+5NaCl"], 0.0093931, (0.2502, 0.2592)),
          "10 % NaCl": (["Agua+10NaCl"], 0.0153931, (0.2442, 0.2532))}


def gauss(x, A, m, s, b0, b1):
    return A * np.exp(-0.5 * ((x - m) / s) ** 2) + b0 + b1 * (x - m)


for medio, (carpetas, delta, (a, b)) in MEDIOS.items():
    for e in ENERGIAS:
        ruta = next((f"{base}/{e}/{c}/procesos_filtrados/Cerenkov/Cerenkov.txt" for c in carpetas
                     if os.path.exists(f"{base}/{e}/{c}/procesos_filtrados/Cerenkov/Cerenkov.txt")), None)
        if ruta is None:
            continue
        x = np.loadtxt(ruta, usecols=-1)
        h, ed = np.histogram(x, bins=3000, range=(0.20, 0.32))
        c = 0.5 * (ed[1:] + ed[:-1])
        i = h.argmax()
        sel = (c > c[i] - 0.0045) & (c < c[i] + 0.0045)
        p, _ = curve_fit(gauss, c[sel], h[sel], p0=[h[i], c[i], 1e-4, h[sel].min(), 0])
        hd, _ = np.histogram(x - delta, bins=3000, range=(0.20, 0.32))
        n = hd[(c >= a) & (c <= b)].sum()
        print(f"{medio:11s} {e:11s} pico sin desplazar {p[1]:.5f} MeV; electrones en la ventana {n}")
