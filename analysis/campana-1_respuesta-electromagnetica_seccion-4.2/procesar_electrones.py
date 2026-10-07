#!/usr/bin/env python3
"""Procesa los electrones y positrones de las 64 corridas de la Campaña 1 (Sección 4.2 de la tesis).

Lee, para cada energía y medio, el archivo crudo rastreo-electron-*.txt escrito por
G4WCDSteppingAction (etiqueta campana-1-QGSP_BERT_HP): una fila por paso de cada e- o e+,

    partícula  proceso  trackID  parentID  paso  x  y  z  E

con `proceso` el que limitó el paso (GetProcessDefinedStep), (x, y, z) [mm] la posición posterior del
paso y E [MeV] la energía cinética posterior (track->GetKineticEnergy()). El archivo no tiene
identificador de evento. A diferencia de los fotones, los pasos de una traza NO son siempre
consecutivos: G4Cerenkov suspende el electrón para seguir primero sus fotones ópticos, de modo que
las trazas de un mismo evento se intercalan. Cada traza empieza en el paso 1 y se sigue por su
trackID (único dentro de un evento; un nuevo paso 1 con el mismo trackID abre otra traza).

Particularidades del registro:
  - `Scintillation`: cuando el electrón se detiene, Geant4 añade un paso de longitud cero con E = 0
    limitado por G4Scintillation. Cuenta electrones detenidos, no luz de centelleo (el material no
    tiene rendimiento de centelleo).
  - `Cerenkov`: el paso lo limitó G4Cerenkov, que acorta el paso para que el electrón no baje del
    umbral de emisión del material (n = 1.33 constante en el agua de los cuatro medios, tabla
    waterPT1; n = 1.47 en el Pyrex del PMT). Por eso la energía posterior de esos pasos se acumula
    en el umbral: 264.06 keV en el agua y 186.2 keV en el Pyrex.

Definiciones:
  - tanque: |x|,|y| <= 480 mm y 0 <= z <= 1330.05 mm (criterio de la tesis para los gamma);
    tanque estricto: z <= 1330 mm (criterio de los notebooks de electrones de la tesis).
  - energía inicial aproximada de una traza: energía posterior al paso 1.
  - traza emisora: la que tiene al menos un paso `Cerenkov` en el tanque.
  - longitud registrada: suma de las distancias entre posiciones posteriores consecutivas de una traza
    (desde el paso 1; el primer paso no se incluye porque falta el vértice); `sobre umbral` cuando la
    energía al inicio del tramo supera el umbral del agua.

Uso:
  python3 procesar_electrones.py <carpeta Electrones> <carpeta de salida> [procesos] [caja|cilindro]
Salida: <salida>/<energía>/<medio>/resumen_electrones.json y <salida>/resumen_electrones_campana.tsv.
"""
import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

ENERGIAS = ["1meV", "2.5meV", "5meV", "7meV", "10meV", "25meV", "50meV", "80meV", "100meV",
            "300meV", "500meV", "700meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
ETIQUETA_MEDIO = {"Agua-pura": "AP", "Agua+2.5NaCl": "A-25NaCl", "Agua+5NaCl": "A-5NaCl",
                  "Agua+10NaCl": "A-10NaCl"}
PROCESOS = ["eIoni", "Cerenkov", "Scintillation", "msc", "eBrem", "Transportation", "annihil"]

XY_MAX, Z_MIN, Z_MAX, Z_MAX_ESTRICTO = 480.0, 0.0, 1330.05, 1330.0

MEC2 = 0.51099895                       # MeV


def umbral_cherenkov(n):
    return MEC2 * (1.0 / math.sqrt(1.0 - 1.0 / (n * n)) - 1.0)


N_AGUA_SIM, N_PYREX_SIM = 1.33, 1.47
E_UMBRAL_AGUA = umbral_cherenkov(N_AGUA_SIM)     # 0.26406 MeV
E_UMBRAL_PYREX = umbral_cherenkov(N_PYREX_SIM)   # 0.18617 MeV
VENTANA_TESIS = (0.2596, 0.2686)        # ventana del conteo de la Tabla 4.20 (agua pura, MeV)
VENTANA_PYREX = (0.180, 0.190)

# Histogramas
H_ANCHO, H_MAX = 0.005, 10.0            # espectros completos, 5 keV
F_ANCHO, F_MAX = 0.001, 3.2             # espectros finos, 1 keV (la tesis usa 16 keV en 0-1.6 MeV)
C_ANCHO, C_MIN, C_MAX = 0.00004, 0.15, 0.32   # zona del umbral, 0.04 keV (binning de la tesis)
Z_ANCHO, R_ANCHO, R_MAX = 10.0, 10.0, 700.0   # mm


class Hist:
    def __init__(self, ancho, maximo, minimo=0.0):
        self.ancho, self.minimo, self.maximo = ancho, minimo, maximo
        self.c = [0] * int(round((maximo - minimo) / ancho))
        self.fuera = 0
        self.n = self.s = self.s2 = 0

    def add(self, v):
        self.n += 1
        self.s += v
        self.s2 += v * v
        i = int((v - self.minimo) / self.ancho)
        if 0 <= i < len(self.c) and v >= self.minimo:
            self.c[i] += 1
        else:
            self.fuera += 1

    def dic(self):
        media = self.s / self.n if self.n else None
        sd = math.sqrt(max(self.s2 / self.n - media * media, 0)) if self.n else None
        return {"ancho": self.ancho, "rango": [self.minimo, self.maximo], "conteos": self.c,
                "fuera_de_rango": self.fuera, "n": self.n, "media": media, "std": sd}


GEOMETRIA = {"forma": "caja"}      # "caja" (criterio de la tesis) o "cilindro" (r <= 480 mm)


def dentro(x, y, z, zmax=Z_MAX):
    if not Z_MIN <= z <= zmax:
        return False
    if GEOMETRIA["forma"] == "cilindro":
        return x * x + y * y <= XY_MAX * XY_MAX
    return -XY_MAX <= x <= XY_MAX and -XY_MAX <= y <= XY_MAX


def zona_exterior(x, y, z):
    if z > Z_MAX:
        return "encima"
    if z < Z_MIN:
        return "debajo"
    return "lateral"


def archivo_crudo(base, energia, medio):
    fs = sorted((base / energia).glob(f"rastreo-electron-{ETIQUETA_MEDIO[medio]}-*.txt"))
    if len(fs) != 1:
        raise FileNotFoundError(f"{energia}/{medio}: {len(fs)} archivos rastreo-electron")
    return fs[0]


def cerrar_traza(t, acc):
    """Acumula las magnitudes de una traza terminada."""
    p = t["particula"]
    acc["trazas"][p] += 1
    if t["inicio_tanque"]:
        acc["trazas_tanque"][p] += 1
        acc["E_inicial"][p].add(t["E1"])
        if t["E1"] > E_UMBRAL_AGUA:
            acc["trazas_sobre_umbral_tanque"][p] += 1
    if t["cer"]:
        acc["trazas_emisoras"][p] += 1
        acc["cer_por_traza"].add(t["cer"])
        acc["E_inicial_emisoras"].add(t["E1"])
    acc["longitud_tanque_mm"] += t["L"]
    acc["longitud_sobre_umbral_mm"] += t["Lu"]
    if t["Lu"] > 0:
        acc["longitud_sobre_umbral_traza"].add(t["Lu"])
    acc["pasos_por_traza"].add(t["pasos"])


def procesar(args):
    base, salida, energia, medio = args
    f = archivo_crudo(base, energia, medio)
    filas = {"total": 0, "tanque": 0, "tanque_estricto": 0, "exterior": 0,
             "e-": 0, "e+": 0}
    procesos = {p: {"total": 0, "tanque": 0, "tanque_estricto": 0, "exterior": 0, "E_cero_tanque": 0,
                    "encima": 0, "debajo": 0, "lateral": 0} for p in PROCESOS}
    otros = {}
    acc = {
        "trazas": {"e-": 0, "e+": 0}, "trazas_tanque": {"e-": 0, "e+": 0},
        "trazas_sobre_umbral_tanque": {"e-": 0, "e+": 0}, "trazas_emisoras": {"e-": 0, "e+": 0},
        "E_inicial": {"e-": Hist(H_ANCHO, H_MAX), "e+": Hist(H_ANCHO, H_MAX)},
        "E_inicial_emisoras": Hist(H_ANCHO, H_MAX),
        "cer_por_traza": Hist(1, 200), "pasos_por_traza": Hist(1, 500),
        "longitud_sobre_umbral_traza": Hist(1.0, 100.0),
        "longitud_tanque_mm": 0.0, "longitud_sobre_umbral_mm": 0.0,
    }
    h = {
        "pasos_tanque": Hist(H_ANCHO, H_MAX),
        "eIoni_E_no_nula_estricto": Hist(F_ANCHO, F_MAX),
        "Cerenkov_estricto": Hist(F_ANCHO, F_MAX),
        "Cerenkov_umbral_estricto": Hist(C_ANCHO, C_MAX, C_MIN),
        "eBrem_estricto": Hist(F_ANCHO, F_MAX),
        "msc_estricto": Hist(F_ANCHO, F_MAX),
    }
    pyrex = {"z": Hist(Z_ANCHO, 1400.0), "r": Hist(R_ANCHO, R_MAX)}
    cer_agua = {"z": Hist(Z_ANCHO, 1400.0), "r": Hist(R_ANCHO, R_MAX)}
    ventana = {"tesis_agua": 0, "pyrex": 0, "bajo_umbral_agua": 0, "Cerenkov_estricto": 0}
    abiertas = {}

    with open(f) as fh:
        for linea in fh:
            c = linea.split()
            if len(c) < 9:
                continue
            part, proc = c[0], c[1]
            tid, paso = int(c[2]), int(c[4])
            x, y, z, e = float(c[5]), float(c[6]), float(c[7]), float(c[8])
            filas["total"] += 1
            filas[part] = filas.get(part, 0) + 1
            en = dentro(x, y, z)
            en_e = dentro(x, y, z, Z_MAX_ESTRICTO)
            d = procesos.get(proc)
            if d is None:
                d = otros.setdefault(proc, {"total": 0, "tanque": 0, "tanque_estricto": 0, "exterior": 0,
                                            "E_cero_tanque": 0, "encima": 0, "debajo": 0, "lateral": 0})
            d["total"] += 1
            if en:
                filas["tanque"] += 1
                d["tanque"] += 1
                h["pasos_tanque"].add(e)
                if e == 0:
                    d["E_cero_tanque"] += 1
            else:
                filas["exterior"] += 1
                d["exterior"] += 1
                d[zona_exterior(x, y, z)] += 1
            if en_e:
                filas["tanque_estricto"] += 1
                d["tanque_estricto"] += 1
                if proc == "eIoni" and e != 0:
                    h["eIoni_E_no_nula_estricto"].add(e)
                elif proc == "eBrem":
                    h["eBrem_estricto"].add(e)
                elif proc == "msc":
                    h["msc_estricto"].add(e)
                elif proc == "Cerenkov":
                    ventana["Cerenkov_estricto"] += 1
                    h["Cerenkov_estricto"].add(e)
                    h["Cerenkov_umbral_estricto"].add(e)
                    r = math.hypot(x, y)
                    if VENTANA_TESIS[0] <= e <= VENTANA_TESIS[1]:
                        ventana["tesis_agua"] += 1
                    if VENTANA_PYREX[0] <= e <= VENTANA_PYREX[1]:
                        ventana["pyrex"] += 1
                        pyrex["z"].add(z)
                        pyrex["r"].add(r)
                    else:
                        cer_agua["z"].add(z)
                        cer_agua["r"].add(r)
                    if e < E_UMBRAL_AGUA - 0.0005:
                        ventana["bajo_umbral_agua"] += 1

            # seguimiento por traza
            if paso == 1:
                t = abiertas.get(tid)
                if t is not None:
                    cerrar_traza(t, acc)
                t = {"particula": part, "E1": e, "inicio_tanque": en, "cer": 0, "L": 0.0, "Lu": 0.0,
                     "pasos": 1, "x": x, "y": y, "z": z, "E": e}
                abiertas[tid] = t
            else:
                t = abiertas.get(tid)
                if t is None:
                    continue
                t["pasos"] += 1
                if en:
                    dl = math.sqrt((x - t["x"]) ** 2 + (y - t["y"]) ** 2 + (z - t["z"]) ** 2)
                    t["L"] += dl
                    if t["E"] > E_UMBRAL_AGUA:
                        t["Lu"] += dl
                t["x"], t["y"], t["z"], t["E"] = x, y, z, e
            if proc == "Cerenkov" and en:
                t["cer"] += 1
    for t in abiertas.values():
        cerrar_traza(t, acc)

    res = {
        "energia": energia, "medio": medio, "archivo": f.name, "geometria": GEOMETRIA["forma"],
        "umbral_agua_MeV": E_UMBRAL_AGUA, "umbral_pyrex_MeV": E_UMBRAL_PYREX,
        "filas": filas, "procesos": procesos, "otros_procesos": otros,
        "trazas": acc["trazas"], "trazas_tanque": acc["trazas_tanque"],
        "trazas_sobre_umbral_tanque": acc["trazas_sobre_umbral_tanque"],
        "trazas_emisoras": acc["trazas_emisoras"],
        "longitud_tanque_mm": acc["longitud_tanque_mm"],
        "longitud_sobre_umbral_mm": acc["longitud_sobre_umbral_mm"],
        "ventanas_Cerenkov": ventana,
        "histogramas": {k: v.dic() for k, v in h.items()},
        "E_inicial": {k: v.dic() for k, v in acc["E_inicial"].items()},
        "E_inicial_emisoras": acc["E_inicial_emisoras"].dic(),
        "Cerenkov_por_traza_emisora": acc["cer_por_traza"].dic(),
        "pasos_por_traza": acc["pasos_por_traza"].dic(),
        "longitud_sobre_umbral_traza_mm": acc["longitud_sobre_umbral_traza"].dic(),
        "Cerenkov_pyrex_posicion": {k: v.dic() for k, v in pyrex.items()},
        "Cerenkov_agua_posicion": {k: v.dic() for k, v in cer_agua.items()},
    }
    d = salida / energia / medio
    d.mkdir(parents=True, exist_ok=True)
    (d / "resumen_electrones.json").write_text(json.dumps(res))
    return res


def ajuste_pico_cherenkov(h, semiventana=0.0045, rango=(0.20, 0.32)):
    """Ajuste del máximo Cherenkov como en la tesis: gaussiana más fondo lineal en +-4.5 keV alrededor del
    intervalo más poblado del histograma de 0.04 keV en 0.20-0.32 MeV. Devuelve (mu, u_mu, sigma) en MeV."""
    import numpy as np
    from scipy.optimize import curve_fit

    c = np.array(h["conteos"], float)
    x = h["rango"][0] + (np.arange(len(c)) + 0.5) * h["ancho"]
    s = (x >= rango[0]) & (x <= rango[1])
    x, c = x[s], c[s]
    i = c.argmax()
    w = np.abs(x - x[i]) <= semiventana

    def f(x, a, mu, sg, b0, b1):
        return a * np.exp(-0.5 * ((x - mu) / sg) ** 2) + b0 + b1 * (x - mu)

    p, cov = curve_fit(f, x[w], c[w], p0=[c[i], x[i], 3 * h["ancho"], np.median(c[w]), 0.0], maxfev=20000)
    return p[1], math.sqrt(cov[1, 1]), abs(p[2])


def fila_tsv(r):
    P = r["procesos"]
    hc = r["histogramas"]["Cerenkov_umbral_estricto"]
    c = hc["conteos"]
    i = c.index(max(c))
    fila = {
        "energia": r["energia"], "medio": r["medio"],
        "filas_total": r["filas"]["total"], "filas_tanque": r["filas"]["tanque"],
        "filas_tanque_estricto": r["filas"]["tanque_estricto"], "filas_exterior": r["filas"]["exterior"],
        "trazas_e-": r["trazas"]["e-"], "trazas_e+": r["trazas"]["e+"],
        "trazas_tanque_e-": r["trazas_tanque"]["e-"], "trazas_tanque_e+": r["trazas_tanque"]["e+"],
        "trazas_sobre_umbral_e-": r["trazas_sobre_umbral_tanque"]["e-"],
        "trazas_sobre_umbral_e+": r["trazas_sobre_umbral_tanque"]["e+"],
        "trazas_emisoras_e-": r["trazas_emisoras"]["e-"], "trazas_emisoras_e+": r["trazas_emisoras"]["e+"],
    }
    for p in PROCESOS:
        for z in ("total", "tanque", "tanque_estricto", "exterior"):
            fila[f"{p}_{z}"] = P[p][z]
    fila.update({
        "E_inicial_media_e-": r["E_inicial"]["e-"]["media"],
        "E_inicial_media_e+": r["E_inicial"]["e+"]["media"],
        "longitud_tanque_mm": round(r["longitud_tanque_mm"], 1),
        "longitud_sobre_umbral_mm": round(r["longitud_sobre_umbral_mm"], 1),
        "Cerenkov_ventana_tesis": r["ventanas_Cerenkov"]["tesis_agua"],
        "Cerenkov_ventana_pyrex": r["ventanas_Cerenkov"]["pyrex"],
        "Cerenkov_bajo_umbral_agua": r["ventanas_Cerenkov"]["bajo_umbral_agua"],
        "Cerenkov_pico_MeV": round(hc["rango"][0] + (i + 0.5) * hc["ancho"], 6),
        "eIoni_E_no_nula_media": r["histogramas"]["eIoni_E_no_nula_estricto"]["media"],
    })
    return fila


def main():
    base, salida = Path(sys.argv[1]), Path(sys.argv[2])
    nproc = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    if len(sys.argv) > 4:
        GEOMETRIA["forma"] = sys.argv[4]
    tareas = [(base, salida, e, m) for e in ENERGIAS for m in MEDIOS]
    with Pool(nproc) as pool:
        res = pool.map(procesar, tareas)
    filas = [fila_tsv(r) for r in res]
    cols = list(filas[0])
    with open(salida / "resumen_electrones_campana.tsv", "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for fl in filas:
            fh.write("\t".join("" if fl[k] is None else str(fl[k]) for k in cols) + "\n")
    print(f"{len(res)} corridas procesadas -> {salida}")


if __name__ == "__main__":
    main()
