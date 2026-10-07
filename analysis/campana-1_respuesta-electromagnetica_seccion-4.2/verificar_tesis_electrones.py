#!/usr/bin/env python3
"""Recalcula las cifras de electrones de la tesis (Sección 4.2 y Apéndice E) y las compara.

Definiciones reconstruidas de los notebooks originales (Imagenes-radiacion-EM/imagenes-resultados/Cherenkov):
  - Tabla E.1 (conteo de procesos de los e±): filas del archivo rastreo-electron con el proceso indicado y
    posición en la caja |x|,|y| <= 480 mm, 0 <= z <= 1330 mm (tanque estricto).
  - Tabla 4.19 (electrones en el máximo Cherenkov): filas `Cerenkov` del tanque estricto con energía en la
    ventana [a, b]. En agua pura, [0.2596, 0.2686] MeV sobre los datos crudos. En los medios con NaCl el
    notebook restó a todas las energías una constante (5.6128, 9.3931 y 15.3931 keV para 2.5, 5 y 10 %)
    y contó en la ventana desplazada que da la nota de la tabla; equivale a contar en [a + c, b + c] sobre
    los datos crudos.
  - Fracción en la ventana: conteo de la Tabla 4.19 / filas `Cerenkov` del tanque estricto (agua pura).
  - Fig. 4.46 (espectro de ionización): filas `eIoni` del tanque estricto con E != 0, histograma de 100
    intervalos en 0-1.6 MeV; el máximo es el centro del intervalo con más cuentas.
  - Tabla 4.18 y Fig. 4.47: máximo del espectro de las filas `Cerenkov` (sin desplazar), ajuste gaussiano con
    fondo lineal en +-4.5 keV sobre intervalos de 0.04 keV.
  - Tabla 4.17: umbral E = mc^2 (1/sqrt(1 - 1/n^2) - 1) con los n de la literatura.

Uso:
  python3 verificar_tesis_electrones.py <carpeta Electrones> <resultados_electrones> <salida.tsv>
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from procesar_electrones import (MEDIOS, MEC2, Z_MAX_ESTRICTO, ajuste_pico_cherenkov, archivo_crudo,  # noqa: E402
                                 dentro, umbral_cherenkov)

PROC_TABLA = ["eIoni", "Scintillation", "Cerenkov", "msc", "eBrem", "Transportation"]
TABLA_E1 = {   # Apéndice E, Tabla E.1: energía -> proceso -> [AP, 2.5, 5, 10]
    "1meV": {"eIoni": [104415, 219435, 288335, 394546], "Scintillation": [91041, 192940, 254074, 347387],
             "Cerenkov": [68740, 161906, 219636, 307946], "msc": [2132, 4091, 5911, 11728],
             "eBrem": [1329, 5415, 7652, 8858], "Transportation": [87, 240, 338, 523]},
    "100meV": {"eIoni": [209524, 422441, 549511, 728838], "Scintillation": [182662, 371480, 483640, 641841],
               "Cerenkov": [136634, 310438, 410596, 559205], "msc": [2132, 7023, 8804, 12226],
               "eBrem": [3668, 7893, 11126, 8858], "Transportation": [168, 240, 624, 983]},
    "1000meV": {"eIoni": [233776, 456494, 598031, 775607], "Scintillation": [203711, 401768, 527083, 683269],
                "Cerenkov": [151900, 330520, 446025, 591381], "msc": [4038, 6908, 9197, 12096],
                "eBrem": [2920, 8415, 11789, 17019], "Transportation": [164, 560, 710, 927]},
    "1000000meV": {"eIoni": [233665, 447464, 579771, 739300], "Scintillation": [204394, 394211, 511984, 652533],
                   "Cerenkov": [150130, 320817, 424867, 553076], "msc": [3538, 5756, 7594, 10830],
                   "eBrem": [2835, 8093, 11463, 15849], "Transportation": [160, 481, 673, 1007]},
}
TABLA_419 = {   # Tabla 4.19: energía -> [AP, 2.5, 5, 10]
    "1meV": [40753, 87566, 117309, 162482], "10meV": [59850, 126775, 168296, 229272],
    "100meV": [81179, 168669, 218690, 293107], "1000meV": [90012, 178672, 237762, 309196],
    "1000000meV": [89030, 172851, 225306, 289149],
}
VENTANA = {"Agua-pura": (0.2596, 0.2686, 0.0), "Agua+2.5NaCl": (0.253960, 0.262960, 0.0056128),
           "Agua+5NaCl": (0.250200, 0.259200, 0.0093931), "Agua+10NaCl": (0.244200, 0.253200, 0.0153931)}
FRACCION_TESIS = (59.257, 59.419)      # % en la ventana, agua pura, cinco energías
PICO_IONI_TESIS = {"Agua-pura": 0.472, "Agua+2.5NaCl": 0.492}
TABLA_417 = {"Agua-pura": (1.3330, 0.26181), "Agua+2.5NaCl": (1.3397, 0.25689),
             "Agua+5NaCl": (1.3436, 0.25411), "Agua+10NaCl": (1.3594, 0.24336)}
TABLA_418 = {m: {e: 0.26411 for e in ("1meV", "10meV", "100meV", "1000meV", "1000000meV")} for m in MEDIOS}
TABLA_418["Agua-pura"].update({"1meV": 0.26410, "10meV": 0.26410, "100meV": 0.26410, "1000meV": 0.26410})


def conteo_ventana(base, energia, medio):
    a, b, c = VENTANA[medio]
    n = tot = 0
    with open(archivo_crudo(base, energia, medio)) as fh:
        for linea in fh:
            if "\tCerenkov\t" not in linea:
                continue
            p = linea.split()
            x, y, z, e = float(p[5]), float(p[6]), float(p[7]), float(p[8])
            if not dentro(x, y, z, Z_MAX_ESTRICTO):
                continue
            tot += 1
            if a <= round(e - c, 8) <= b:      # el notebook guardó los datos desplazados con %.8f
                n += 1
    return n, tot


def pico_ionizacion(r):
    h = r["histogramas"]["eIoni_E_no_nula_estricto"]
    c = h["conteos"][:1600]                         # 0-1.6 MeV en intervalos de 1 keV
    g = [sum(c[i:i + 16]) for i in range(0, 1600, 16)]
    i = g.index(max(g))
    return round(0.016 * (i + 0.5), 3)


def main():
    base, res, salida = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    R = {}
    for e in set(TABLA_E1) | set(TABLA_419) | {"10000meV"}:
        for m in MEDIOS:
            R[e, m] = json.loads((res / e / m / "resumen_electrones.json").read_text())
    filas = []

    def agregar(mag, e, m, tesis, rep, defin, decimales=None, tolerancia=None):
        """`decimales`: cifras con que la tesis da el valor; `tolerancia`: diferencia admitida como compatible."""
        if tesis is None:
            estado = "sin valor en la tesis"
        elif decimales is not None:
            estado = "igual" if round(rep, decimales) == round(tesis, decimales) else "difiere"
        else:
            estado = "igual" if tesis == rep else "difiere"
        if estado == "difiere" and tolerancia is not None and abs(tesis - rep) <= tolerancia:
            estado = "compatible"
        filas.append((mag, e, m, tesis, rep, defin, estado))

    for e, t in TABLA_E1.items():
        for p in PROC_TABLA:
            for j, m in enumerate(MEDIOS):
                agregar(f"Tabla E.1 {p}", e, m, t[p][j], R[e, m]["procesos"][p]["tanque_estricto"],
                        "filas del proceso en el tanque estricto (z <= 1330 mm)")
    fr = []
    for e, t in TABLA_419.items():
        for j, m in enumerate(MEDIOS):
            n, tot = conteo_ventana(base, e, m)
            a, b, c = VENTANA[m]
            agregar("Tabla 4.19 N_e en la ventana", e, m, t[j], n,
                    f"filas Cerenkov del tanque estricto con {a + c:.7f} <= E <= {b + c:.7f} MeV")
            if m == "Agua-pura":
                fr.append(100 * n / tot)
                agregar("fracción en la ventana (%)", e, m, None, round(100 * n / tot, 3),
                        "Tabla 4.19 / filas Cerenkov del tanque estricto")
    agregar("fracción en la ventana: mínimo (%)", "5 energías", "Agua-pura", FRACCION_TESIS[0], round(min(fr), 3),
            "mínimo de las cinco energías", 3)
    agregar("fracción en la ventana: máximo (%)", "5 energías", "Agua-pura", FRACCION_TESIS[1], round(max(fr), 3),
            "máximo de las cinco energías", 3)
    for e in ("1meV", "10meV", "100meV", "1000meV", "10000meV"):     # energías de la Fig. 4.46
        for m in ("Agua-pura", "Agua+2.5NaCl"):
            agregar("Fig. 4.46 máximo del espectro eIoni (MeV)", e, m, PICO_IONI_TESIS[m], pico_ionizacion(R[e, m]),
                    "centro del intervalo máximo, 100 intervalos en 0-1.6 MeV, eIoni con E != 0", 3)
    for m, (n, eu) in TABLA_417.items():
        agregar("Tabla 4.17 umbral Cherenkov (MeV)", "", m, eu, round(umbral_cherenkov(n), 5),
                f"mc^2 (1/sqrt(1-1/n^2) - 1), n = {n}, mc^2 = {MEC2} MeV", 5)
    agregar("umbral con el n de la simulación (MeV)", "", "4 medios", None, round(umbral_cherenkov(1.33), 5),
            "n = 1.33 (waterPT1, igual en los cuatro medios)")
    agregar("umbral en el Pyrex del PMT (MeV)", "", "", None, round(umbral_cherenkov(1.47), 5), "n = 1.47 (pmtRefIndex)")
    for m in MEDIOS:
        for e, t in TABLA_418[m].items():
            mu, _, _ = ajuste_pico_cherenkov(R[e, m]["histogramas"]["Cerenkov_umbral_estricto"])
            agregar("Tabla 4.18 / Fig. 4.47 máximo Cherenkov ajustado (MeV)", e, m, t, round(mu, 6),
                    "gaussiana + fondo lineal en +-4.5 keV, intervalos de 0.04 keV, filas Cerenkov del tanque estricto",
                    decimales=5, tolerancia=0.00004)
    with open(salida, "w") as fh:
        fh.write("magnitud\tenergia\tmedio\ttesis\treproducido\tdefinicion\testado\n")
        for f in filas:
            fh.write("\t".join("" if v is None else str(v) for v in f) + "\n")
    n_ig = sum(f[6] == "igual" for f in filas)
    n_c = sum(f[6] == "compatible" for f in filas)
    n_t = sum(f[6] != "sin valor en la tesis" for f in filas)
    print(f"{n_ig} de {n_t} cifras de la tesis reproducidas exactamente y {n_c} compatibles (Tabla 4.18: a menos de un intervalo de 0.04 keV)")
    for f in filas:
        if f[6] == "difiere":
            print("  difiere:", f[0], f[1], f[2], "tesis", f[3], "reproducido", f[4])


if __name__ == "__main__":
    main()
