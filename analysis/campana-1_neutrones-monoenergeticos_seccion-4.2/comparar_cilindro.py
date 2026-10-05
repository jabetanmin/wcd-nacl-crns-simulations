#!/usr/bin/env python3
"""Compara la selección por caja (definición de la tesis) con la selección por cilindro.

La tesis selecciona los pasos dentro del tanque con una caja cuadrada en x-y (|x|,|y| <= 478 mm para N y xi;
<= 480 mm para el destino final), mientras que el volumen de agua es un cilindro de radio 480 mm
(tankRadius = 48 cm). Este script reprocesa las 64 corridas con el cilindro r = sqrt(x^2 + y^2) <= 480 mm
(mismos límites en z) y compara, corrida por corrida y neutrón por neutrón, con los resultados de la caja.

Uso:
  python3 comparar_cilindro.py <carpeta Neutrones-termicos> <resultados caja> <salida cilindro> [procesos]
Salida: <salida>/<energía>/<medio>/..., <salida>/comparacion_caja_cilindro.tsv
"""
import csv
import gzip
import sys
from multiprocessing import Pool
from pathlib import Path

from procesar_campana import ENERGIAS, MEDIOS
from procesar_corrida import procesar


def tarea(args):
    base, salida, e, m = args
    procesar(Path(base) / e / m, Path(salida) / e / m, geometria="cilindro")
    return e, m


def leer(ruta):
    with gzip.open(ruta, "rt") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def media(v):
    v = [float(x) for x in v if x != ""]
    return sum(v) / len(v) if v else float("nan")


def comparar(caja, cil, e, m):
    a = leer(Path(caja) / e / m / "historias.tsv.gz")
    b = leer(Path(cil) / e / m / "historias.tsv.gz")
    n = len(a)
    cambia_dest = sum(1 for x, y in zip(a, b) if x["destino"] != y["destino"])
    cambia_N = sum(1 for x, y in zip(a, b) if x["N_tesis"] != y["N_tesis"])
    def eta(h, *k):
        return 100 * sum(1 for r in h if r["destino"] in k) / n
    def xi_col(h):
        # xi de la tesis: suma de ln(E_pre/E_post) en las cadenas / número de colisiones de las cadenas
        c = [r for r in h if r["N_tesis"] != ""]
        return sum(float(r["suma_xi_cadena"]) for r in c) / max(sum(int(r["N_tesis"]) for r in c), 1)
    fila = {"energia": e, "medio": m,
            "cambia_destino": cambia_dest, "cambia_N": cambia_N}
    for nombre, claves in [("cap_dentro", ("cap_dentro",)), ("cap_fuera", ("cap_fuera",)),
                           ("refle", ("arriba",)), ("trans", ("abajo", "lateral")),
                           ("otros", ("no_entra", "inel_dentro", "inel_fuera", "otro"))]:
        fila[f"{nombre}_caja"] = eta(a, *claves)
        fila[f"{nombre}_cil"] = eta(b, *claves)
    fila["cadenas_caja"] = sum(1 for r in a if r["N_tesis"] != "")
    fila["cadenas_cil"] = sum(1 for r in b if r["N_tesis"] != "")
    fila["N_caja"] = media(r["N_tesis"] for r in a)
    fila["N_cil"] = media(r["N_tesis"] for r in b)
    fila["xi_hist_inicial_caja"] = media(r["xi_historia_inicial"] for r in a)
    fila["xi_hist_inicial_cil"] = media(r["xi_historia_inicial"] for r in b)
    fila["xi_tesis_caja"] = xi_col(a)
    fila["xi_tesis_cil"] = xi_col(b)
    return fila


def main():
    base, caja, cil = sys.argv[1], sys.argv[2], sys.argv[3]
    procesos = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    trabajos = [(base, cil, e, m) for e in ENERGIAS for m in MEDIOS]
    with Pool(procesos) as pool:
        pool.map(tarea, trabajos)
        filas = pool.starmap(comparar, [(caja, cil, e, m) for e in ENERGIAS for m in MEDIOS])
    cols = list(filas[0].keys())
    with open(Path(cil) / "comparacion_caja_cilindro.tsv", "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in filas:
            f.write("\t".join(f"{r[c]:.6g}" if isinstance(r[c], float) else str(r[c]) for c in cols) + "\n")
    print(f"{len(filas)} corridas -> {Path(cil) / 'comparacion_caja_cilindro.tsv'}")


if __name__ == "__main__":
    main()
