#!/usr/bin/env python3
"""Verifica la Tabla 4.9 de la versión anterior de la tesis (longitud de captura por ajuste gaussiano).

Los valores anteriores provenían de los notebooks de la carpeta Distancia-captura: un histograma de 1000
intervalos de cada archivo Distancias_promedio_captura_*_exterior_TA.txt y un ajuste gaussiano (curve_fit,
pesos sqrt(N)) en un intervalo introducido a mano con input(). Este script toma los valores introducidos que
quedaron registrados en las salidas de esos notebooks, repite cada ajuste y lo compara con la tabla; además
comprueba si cada archivo de distancias coincide con los datos crudos de la Campaña 1.

Uso:
  python3 verificar_tabla_4_9_original.py <carpeta Distancia-captura> <carpeta Neutrones-termicos>
"""
import glob
import json
import math
import os
import re
import sys

import numpy as np
from scipy.optimize import curve_fit

CARPETA = {"1KeV": "1000000meV", "100eV": "100000meV", "10eV": "10000meV", "1eV": "1000meV", "0.7eV": "700meV",
           "0.3eV": "300meV", "100meV": "100meV", "80meV": "80meV", "25meV": "25meV", "10meV": "10meV",
           "5meV": "5meV"}
MEDIO = {"pura": "Agua-pura", "Pura": "Agua-pura", "25NaCl": "Agua+2.5NaCl", "5NaCl": "Agua+5NaCl",
         "10NaCl": "Agua+10NaCl"}
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
# Tabla 4.9 de la versión anterior: (posición, ancho) en cm
TABLA = {"1000000meV": [(6.43, 2.69), (5.98, 3.10), (5.81, 3.21), (5.59, 2.94)],
         "100000meV": [(5.87, 3.06), (4.61, 2.47), (4.53, 2.53), (4.43, 2.36)],
         "10000meV": [(4.38, 2.74), (4.08, 2.84), (4.04, 2.48), (3.96, 2.78)],
         "1000meV": [(3.58, 3.43), (3.40, 2.43), (3.29, 2.56), (3.14, 2.05)],
         "700meV": [(3.55, 2.67), (3.42, 2.40), (3.29, 2.25), (2.98, 2.55)],
         "300meV": [(3.29, 3.15), (3.07, 2.58), (2.85, 2.49), (2.56, 1.73)],
         "100meV": [(2.88, 2.97), (2.83, 2.25), (2.58, 2.53), (2.35, 2.54)],
         "80meV": [(2.76, 2.32), (2.48, 2.02), (2.28, 1.70), (2.01, 1.42)],
         "25meV": [(2.16, 2.91), (1.81, 2.70), (1.67, 2.53), (1.53, 1.43)],
         "10meV": [(1.14, 1.62), (1.01, 1.92), (0.89, 2.11), (0.67, 2.58)],
         "5meV": [(1.03, 1.23), (0.91, 0.82), (0.70, 0.44), (0.61, 0.43)]}


def gauss(x, a, mu, s):
    return a * np.exp(-((x - mu) ** 2) / (2 * s ** 2))


def distancias_crudas(base, e, m):
    """Misma selección que los notebooks: paso 3 hadElastic en z = 1330.05 mm sin pérdida previa, captura final."""
    out, cur = [], []

    def cerrar():
        if (len(cur) >= 3 and cur[2][0] == "3" and cur[2][12] == "hadElastic" and cur[2][7] == "1330.05"
                and cur[-1][12] == "nCapture" and float(cur[2][4]) == float(cur[0][4])):
            out.append(math.dist(tuple(map(float, cur[2][5:8])), tuple(map(float, cur[-1][8:11]))))

    with open(os.path.join(base, e, m, "interaccion-completa-neutrones.txt")) as f:
        for linea in f:
            c = linea.split()
            if c[0] == "1" and cur:
                cerrar()
                cur = []
            cur.append(c)
    cerrar()
    return np.array(out) / 10


def main():
    dist, base = sys.argv[1], sys.argv[2]
    iguales = 0
    total = 0
    for nb_ruta in sorted(glob.glob(os.path.join(dist, "**", "*.ipynb"), recursive=True)):
        rel = os.path.relpath(nb_ruta, dist)
        if "checkpoint" in rel or rel.endswith("Distancias-capturas-neutrones-50meV.ipynb"):
            continue
        e = CARPETA.get(rel.split(os.sep)[0])
        if e not in TABLA:
            continue
        nb = json.load(open(nb_ruta))
        for celda in nb["cells"]:
            src = "".join(celda["source"])
            if "curve_fit" not in src or "input(" not in src:
                continue
            archivo = re.search(r'archivo\s*=\s*"([^"]+)"', src).group(1)
            salida = " ".join("".join(o.get("text", "")) for o in celda.get("outputs", []))
            lo, hi, a0 = [float(x) for x in re.findall(r":\s+([-\d.eE+]+)", salida)[:3]]
            m = MEDIO[re.search(r"captura_Agua_(\w+?)_exterior", archivo).group(1)]
            crudas = distancias_crudas(base, e, m)
            ruta = os.path.join(os.path.dirname(nb_ruta), archivo)
            if os.path.exists(ruta):
                datos = np.array([float(x) / 10 for x in open(ruta) if x.strip()])
                origen = ("crudos C1" if len(datos) == len(crudas)
                          and np.allclose(np.sort(datos), np.sort(crudas), atol=1e-6) else "OTRO ORIGEN")
            else:
                datos, origen = crudas, "archivo ausente (se usan los crudos)"
            h, b = np.histogram(datos, bins=1000)
            c = 0.5 * (b[:-1] + b[1:])
            err = np.where(h > 0, np.sqrt(h), 0)
            k = (c >= lo) & (c <= hi)
            try:
                p, _ = curve_fit(gauss, c[k], h[k], p0=[a0, c[k].mean(), c[k].std()], sigma=err[k],
                                 absolute_sigma=True, maxfev=20000)
                mu, s = p[1], abs(p[2])
            except RuntimeError:
                mu = s = float("nan")
            ref = TABLA[e][MEDIOS.index(m)]
            ok = round(mu, 2) == ref[0] and round(s, 2) == ref[1]
            iguales += ok
            total += 1
            print(f"{e:11s} {m:13s} ajuste [{lo:5.2f},{hi:5.2f}] cm: {mu:6.2f} ± {s:5.2f}   tabla {ref[0]:.2f} ± {ref[1]:.2f}"
                  f"   {'coincide' if ok else 'NO coincide'}   datos: {origen}")
    print(f"\n{iguales} de {total} valores de la tabla se reproducen con los intervalos registrados")


if __name__ == "__main__":
    main()
