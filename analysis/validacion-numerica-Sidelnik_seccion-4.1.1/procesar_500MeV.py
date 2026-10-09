#!/usr/bin/env python3
"""Validación numérica (Sec. 4.1.1): neutrones de 500 MeV, réplica de Sidelnik et al. (2020).

Uso: python3 procesar_500MeV.py <carpeta Espectros-gamma-500MeV> <salida>

Lee los archivos crudos una sola vez y escribe resúmenes pequeños en <salida>/:
  verificacion_archivos.tsv   MD5, líneas y emparejamiento línea a línea electrón/gamma de cada archivo de espectro
  histograma_carga.tsv        cuentas por carga entera (fotoelectrones), 6 medios (formato largo, solo no nulas)
  resumen_carga.tsv           eventos (reales y normalizados), eficiencia, media, desviación, mediana y máximo de la carga
  espectro_gamma.tsv          histograma de la energía de los fotones (intervalos de 5 keV, 0-20 MeV, y logarítmicos)
  espectro_electrones.tsv     ídem para los archivos de electrones, rotulados por nombre de archivo
  lineas_gamma.tsv            cuentas en ventanas de ±10 keV alrededor de líneas de captura conocidas

Archivos de entrada (subcarpetas de <carpeta>):
  Histograma-total-carga/Carga_Total_Agua_<medio>_Neutrones_500MeV.txt   un entero por evento con señal (Q >= 1)
  Espectro-gamma/Espectro-energia-gamma(s)-<medio>.txt                   una energía [MeV] por fila
  Espectro-electrones/Espectro-energia-electrones-agua-<medio>[...].txt  una energía cinética [MeV] por fila
Normalización: se simularon N_SIMULADOS = 2e5 neutrones por medio; los conteos absolutos se dan también normalizados a
N_NORMALIZACION = 1.5e5 neutrones incidentes (columnas *_norm), para compararlos con Sidelnik et al. (2020). Los errores
estadísticos se calculan siempre con los conteos reales.
Cada fila de los archivos de "gamma" y "electrones" corresponde a una interacción de un fotón que crea un e±
(columnas 9 y 10 de un archivo de partículas secundarias: energía del fotón antes de interactuar y energía del e±).
"""
import csv
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MEDIOS_CARGA = {"Pura": "Agua-pura", "05NACl": "Agua+0.5NaCl", "1NACl": "Agua+1NaCl", "25NACl": "Agua+2.5NaCl",
                "5NACl": "Agua+5NaCl", "10NACl": "Agua+10NaCl"}
GAMMA = {"Agua-pura": "Espectro-energia-gamma-agua-pura.txt", "Agua+2.5NaCl": "Espectro-energia-gammas-25NaCl.txt",
         "Agua+5NaCl": "Espectro-energia-gammas-5NaCl.txt", "Agua+10NaCl": "Espectro-energia-gammas-10NaCl.txt"}
ELECTRONES = ["Espectro-energia-electrones-agua-pura.txt", "Espectro-energia-electrones-agua-25NaCl.txt",
              "Espectro-energia-electrones-agua-5NaCl.txt", "Espectro-energia-electrones-agua-10NaCl.txt",
              "Espectro-energia-electrones-agua-10NaCl-1.txt", "Espectro-energia-electrones-agua-5NaCl-Meiga.txt",
              "Espectro-energia-electrones-agua-10NaCl-Meiga.txt"]
BORDES_LIN = np.round(np.arange(0, 20.0 + 1e-9, 0.005), 6)          # 5 keV
BORDES_LOG = np.logspace(-3, np.log10(600), 121)                     # 1 keV - 600 MeV
LINEAS_KEV = {"H 2223.25": 2223.25, "O 870.76": 870.76, "O 1087.86": 1087.86, "O 2184.44": 2184.44,
              "O 3272.15": 3272.15, "O 4142.73": 4142.73, "Na 472.20": 472.20, "Cl35 517.07": 517.07,
              "Cl35 788.42": 788.42, "Cl35 1164.86": 1164.86, "Cl35 1951.14": 1951.14, "Cl35 1959.35": 1959.35,
              "Cl35 6110.84": 6110.84, "Cl35 8578.6": 8578.6, "Cl37 755.43": 755.43, "Cl37 1692.11": 1692.11,
              "Cl37 4134.13": 4134.13, "aniquilacion 511": 511.0}
N_EMPAREJAMIENTO = 2_000_000
N_SIMULADOS = 200_000          # neutrones de 500 MeV simulados por medio
N_NORMALIZACION = 150_000      # neutrones incidentes a los que se normalizan los conteos
FACTOR_NORM = N_NORMALIZACION / N_SIMULADOS


def md5(ruta):
    h = hashlib.md5()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 22), b""):
            h.update(bloque)
    return h.hexdigest()


def leer(ruta):
    return pd.read_csv(ruta, header=None, dtype=np.float64)[0].to_numpy()


def escribir(ruta, filas):
    with open(ruta, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in filas:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, (float, np.floating)) else v) for k, v in r.items()})


def histogramas(nombre, x):
    filas = []
    n, _ = np.histogram(x, BORDES_LIN)
    filas += [{"serie": nombre, "escala": "lineal_5keV", "E_min_MeV": a, "E_max_MeV": b, "cuentas": int(c)}
              for a, b, c in zip(BORDES_LIN[:-1], BORDES_LIN[1:], n) if c]
    n, _ = np.histogram(x, BORDES_LOG)
    filas += [{"serie": nombre, "escala": "log", "E_min_MeV": a, "E_max_MeV": b, "cuentas": int(c)}
              for a, b, c in zip(BORDES_LOG[:-1], BORDES_LOG[1:], n) if c]
    return filas


def main(base, salida):
    base, salida = Path(base), Path(salida)
    salida.mkdir(parents=True, exist_ok=True)

    # --- Carga
    hist, res = [], []
    for f in sorted((base / "Histograma-total-carga").glob("Carga_Total_Agua_*_Neutrones_500MeV.txt")):
        medio = MEDIOS_CARGA[f.name.split("_")[3]]
        q = leer(f).astype(int)
        c = np.bincount(q)
        hist += [{"medio": medio, "carga_pe": i, "cuentas": int(n)} for i, n in enumerate(c) if n]
        res.append({"medio": medio, "archivo": f.name, "md5": md5(f), "eventos": len(q),
                    "eventos_norm": len(q) * FACTOR_NORM, "eficiencia": len(q) / N_SIMULADOS, "Q_min": q.min(),
                    "Q_max": q.max(), "Q_media": q.mean(), "Q_std": q.std(ddof=1), "Q_mediana": np.median(q)})
        print(f"carga {medio}: {len(q)} eventos", flush=True)
    escribir(salida / "histograma_carga.tsv", hist)
    escribir(salida / "resumen_carga.tsv", res)

    # --- Espectros
    gam = {m: leer(base / "Espectro-gamma" / a) for m, a in GAMMA.items()}
    filas_g, filas_l, verif = [], [], []
    for m, x in gam.items():
        filas_g += histogramas(m, x)
        xk = np.round(x * 1000, 2)                    # el archivo guarda 6 cifras: valores cada 0.01 keV
        for nombre, E in LINEAS_KEV.items():
            # Energía de Geant4: el valor de 0.01 keV más poblado a ±2 keV de la línea tabulada (G4NDL puede
            # diferir de NNDC en ~1 keV); cuentas en ±0.05 keV alrededor de ese valor y fondo a +5 keV.
            v, n = np.unique(xk[np.abs(xk - E) <= 2], return_counts=True)
            Eg = v[n.argmax()] if len(n) else np.nan
            filas_l.append({"medio": m, "linea": nombre, "E_tabla_keV": E, "E_geant4_keV": Eg,
                            "cuentas_linea": int(np.sum(np.abs(xk - Eg) <= 0.05)),
                            "cuentas_linea_norm": np.sum(np.abs(xk - Eg) <= 0.05) * FACTOR_NORM,
                            "fondo_mas5keV": int(np.sum(np.abs(xk - (Eg + 5)) <= 0.05))})
        f = base / "Espectro-gamma" / GAMMA[m]
        verif.append({"archivo": f"Espectro-gamma/{f.name}", "md5": md5(f), "filas": len(x),
                      "rotulo": m, "emparejado_con": "", "fraccion_e_le_gamma": ""})
        print(f"gamma {m}: {len(x)} filas", flush=True)
    filas_e = []
    for a in ELECTRONES:
        f = base / "Espectro-electrones" / a
        e = leer(f)
        filas_e += histogramas(a.replace("Espectro-energia-electrones-", "").replace(".txt", ""), e)
        # Emparejamiento: si el archivo de electrones se extrajo de las mismas filas que uno de gammas, la energía
        # del e± nunca supera la del fotón (Compton, fotoeléctrico, pares).
        mejor, frac = "", 0.0
        for m, x in gam.items():
            k = min(N_EMPAREJAMIENTO, len(e), len(x))
            fr = float(np.mean(e[:k] <= x[:k] + 1e-9))
            if fr > frac:
                mejor, frac = m, fr
        verif.append({"archivo": f"Espectro-electrones/{a}", "md5": md5(f), "filas": len(e), "rotulo": a,
                      "emparejado_con": mejor if frac > 0.999 and len(e) == len(gam[mejor]) else "ninguno",
                      "fraccion_e_le_gamma": frac})
        print(f"electrones {a}: {len(e)} filas -> {mejor} ({frac:.4f})", flush=True)
    escribir(salida / "espectro_gamma.tsv", filas_g)
    escribir(salida / "espectro_electrones.tsv", filas_e)
    escribir(salida / "lineas_gamma.tsv", filas_l)
    escribir(salida / "verificacion_archivos.tsv", verif)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
