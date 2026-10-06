#!/usr/bin/env python3
"""Recalcula desde los archivos crudos las cifras de los fotones gamma de la Sección 4.2 de la tesis,
con las definiciones que usaron los notebooks originales, y las compara con los valores publicados.

Definiciones reconstruidas (notebooks Procesos-gamma-*, Procesos-electrones-*, Compton_diferente_energia,
Rayleigh_diferente_energia e Histogramas-coordenadas-*):
  - Tabla "Tipo de interacciones de los gamma_Cap en el tanque":
      N_Cap ............ capturas de la Campaña 1 (resumen del procesamiento de neutrones);
      N(gamma_Cap) ..... líneas de gamma-primario-*.txt (1 y 10 meV, salvo 1 meV con 5 % de NaCl) o
                         número de trazas gamma = filas con paso 1 (100 meV, 1 eV y 1 keV, y 1 meV con 5 %);
      N_Total-int ...... todas las filas de gamma-completo;
      N_Int(Tanque) .... filas con |x|,|y| <= 480 mm y 0 <= z <= 1330.05 mm;
      N_Int(Ext) ....... el resto;
      N_Int(Com) ....... agua pura: filas compt con E < 3 MeV en cualquier posición;
                         medios con NaCl: filas compt en el tanque (todas las energías).
  - Tabla de FWHM de Compton: filas compt del tanque estricto (z <= 1330 mm), histograma de 1000 intervalos
    en [0, 2.7] MeV; FWHM = distancia entre los centros extremos con cuentas >= máximo/2.
  - Máximo del espectro Rayleigh: intervalos de 3 keV.
  - Tabla de fotoabsorción: filas phot del tanque estricto cuya fila anterior en ese archivo filtrado es
    compt; media y desviación de la energía de esa fila anterior en [0.01, 0.1] MeV.
  - Distribución espacial: el mismo subconjunto (en agua pura a 1 meV, fila anterior compt, Rayl o
    Transportation), dentro del cilindro r <= 46 cm y 0 <= z <= 133 cm.
  - Conversión de pares: 100 * filas conv (en cualquier posición) / N_Int(Tanque).

Uso: python3 verificar_tesis_gamma.py <Gammas-contenido-completo> <resumen_campana.tsv de neutrones> <salida.tsv>
"""
import csv
import math
import sys
from pathlib import Path

CARPETA_ENERGIA = {"2.5meV": "2-5meV"}
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
E5 = ["1meV", "10meV", "100meV", "1000meV", "1000000meV"]

# --- Valores publicados en la tesis -------------------------------------------------------------
T_INTER = {  # (N_Cap, N_gamma, Total, Tanque, Compton, Ext) por energía y medio
    "1meV": [(17418, 17558, 133706, 108898, 80740, 24808), (20642, 35368, 265832, 213878, 154210, 51954),
             (23437, 56620, 345439, 275135, 195348, 70304), (28107, 65001, 460496, 363278, 253350, 97218)],
    "10meV": [(25021, 25115, 194412, 159194, 118791, 35218), (29452, 49316, 377599, 306048, 221630, 71551),
              (32991, 64802, 487960, 392804, 281787, 95156), (39456, 89244, 646280, 514877, 362021, 131403)],
    "100meV": [(33180, 37093, 262414, 216088, 161547, 46326), (38582, 75993, 500696, 409145, 298487, 91551),
               (42412, 100111, 683187, 517145, 372938, 119042), (49580, 136891, 825011, 664137, 470694, 160874)],
    "1000meV": [(35881, 40640, 289431, 239947, 180218, 49484), (40822, 79930, 534570, 440039, 322883, 94531),
                (45105, 106296, 686295, 561933, 407543, 124362), (51378, 142917, 868959, 704066, 501212, 164893)],
    "1000000meV": [(33772, 38253, 283957, 238505, 180263, 45452), (37570, 74769, 513650, 428752, 316772, 84898),
                   (40934, 98141, 651474, 541513, 396436, 109961), (45413, 128026, 807929, 667270, 481180, 140195)],
}
COLS_INTER = ["N_Cap", "N(gamma_Cap)", "N_Total-int", "N_Int(Tanque)", "N_Int(Com)", "N_Int(Ext)"]
T_FWHM = {  # (FWHM, E_max, C_max) para 1, 10, 100 y 1000 meV
    "Agua-pura": [(0.054, 0.050, 1962), (0.054, 0.050, 2760), (0.054, 0.047, 3825), (0.057, 0.047, 4208)],
    "Agua+2.5NaCl": [(0.062, 0.047, 3548), (0.057, 0.050, 5153), (0.059, 0.053, 6743), (0.059, 0.053, 7395)],
    "Agua+5NaCl": [(0.062, 0.050, 4224), (0.065, 0.053, 6200), (0.065, 0.053, 8271), (0.062, 0.053, 9194)],
    "Agua+10NaCl": [(0.070, 0.053, 5262), (0.068, 0.055, 7644), (0.068, 0.055, 9861), (0.065, 0.055, 10723)],
}
T_PHOT = {  # (N, media, sigma) para 1, 100, 1000 meV y 1 keV
    "Agua-pura": [(4175, .0464, .0151), (8464, .0471, .0156), (9433, .0468, .0153), (9397, .0470, .0157)],
    "Agua+2.5NaCl": [(8884, .0488, .0159), (17275, .0488, .0159), (18645, .0487, .0157), (18430, .0488, .0158)],
    "Agua+5NaCl": [(11928, .0506, .0161), (22828, .0507, .0158), (24906, .0504, .0160), (24288, .0501, .0158)],
    "Agua+10NaCl": [(16783, .0534, .0164), (31405, .0534, .0161), (33601, .0534, .0163), (32248, .0531, .0162)],
}
T_ESPACIAL = {  # (N, z_media cm) a 1 meV y 1 keV; r_media: 24.1-24.5 (1 meV) y ~24.2 (1 keV)
    "1meV": [(4802, 109.5), (8750, 110.0), (11761, 109.7), (16598, 110.6)],
    "1000000meV": [(9263, 108.8), (18159, 109.6), (23941, 110.0), (31780, 110.5)],
}
T_PARES = {"1meV": [0.14, 0.40, 0.46, 0.57], "10meV": [0.15, 0.39, 0.48, 0.53], "100meV": [0.13, 0.39, 0.46, 0.54],
           "1000meV": [0.11, 0.37, 0.45, 0.54], "1000000meV": [0.13, 0.37, 0.45, 0.55]}


def en_caja(x, y, z, zmax):
    return -480 <= x <= 480 and -480 <= y <= 480 and 0 <= z <= zmax


def leer(base, e, m):
    carpeta = Path(base) / CARPETA_ENERGIA.get(e, e) / m
    [arch] = sorted(carpeta.glob("gamma-completo-*.txt"))
    prim = sorted(carpeta.glob("gamma-primario-*.txt"))
    r = {"total": 0, "tanque": 0, "paso1": 0, "compt_E3": 0, "compt_tanque": 0, "conv_tanque": 0, "conv_total": 0,
         "compt_estricto": [], "rayl_tanque": [], "phot_prev_compt": [], "pos_prev_compt": [],
         "pos_prev_ext": [], "primario": None}
    prev_est = None
    with open(arch) as f:
        for linea in f:
            c = linea.split()
            if len(c) < 9:
                continue
            p = c[4]
            x, y, z, en = float(c[5]), float(c[6]), float(c[7]), float(c[8])
            ins, est = en_caja(x, y, z, 1330.05), en_caja(x, y, z, 1330.0)
            r["total"] += 1
            r["tanque"] += ins
            r["paso1"] += c[3] == "1"
            if p == "compt":
                r["compt_E3"] += en < 3.0
                r["compt_tanque"] += ins
                if est:
                    r["compt_estricto"].append(en)
            elif p == "Rayl" and ins:
                r["rayl_tanque"].append(en)
            elif p == "conv":
                r["conv_total"] += 1
                r["conv_tanque"] += ins
            if est:
                if p == "phot" and prev_est is not None:
                    if prev_est[0] == "compt":
                        r["phot_prev_compt"].append(prev_est[1])
                        r["pos_prev_compt"].append((x, y, z))
                    if prev_est[0] in ("compt", "Rayl", "Transportation"):
                        r["pos_prev_ext"].append((x, y, z))
                prev_est = (p, en)
    if prim:
        r["primario"] = sum(1 for _ in open(prim[0]))
    return r


def hist(v, n, lo, hi):
    c = [0] * n
    w = (hi - lo) / n
    for a in v:
        i = int((a - lo) / w)
        if 0 <= i < n:
            c[i] += 1
    centros = [lo + (i + 0.5) * w for i in range(n)]
    return c, centros


def fwhm(v):
    c, x = hist(v, 1000, 0.0, 2.7)
    i = max(range(len(c)), key=lambda k: c[k])
    idx = [k for k in range(len(c)) if c[k] >= c[i] / 2]
    return x[idx[-1]] - x[idx[0]], x[i], c[i]


def momentos(v, lo, hi):
    w = [a for a in v if lo <= a <= hi]
    m = sum(w) / len(w)
    return m, math.sqrt(sum((a - m) ** 2 for a in w) / len(w))


def espacial(pos):
    sel = [(x / 10, y / 10, z / 10) for x, y, z in pos if (x / 10) ** 2 + (y / 10) ** 2 <= 46.0 ** 2 and 0 <= z / 10 <= 133]
    n = len(sel)
    return n, sum(z for _, _, z in sel) / n, sum(math.hypot(x, y) for x, y, _ in sel) / n


def estado(t, v, tol):
    if t is None:
        return "sin valor en la tesis"
    return "igual" if abs(t - v) <= tol else "difiere"


def main():
    base, neutr, salida = sys.argv[1], sys.argv[2], sys.argv[3]
    cap = {(r["energia"], r["medio"]): int(r["capturas"]) for r in csv.DictReader(open(neutr), delimiter="\t")}
    filas = []

    def add(mag, e, m, t, v, definicion, tol=0):
        filas.append([mag, e, m, t, v, definicion, estado(t, v, tol)])

    datos = {(e, m): leer(base, e, m) for e in E5 for m in MEDIOS}
    for e in E5:
        for j, m in enumerate(MEDIOS):
            d = datos[(e, m)]
            t = T_INTER[e][j]
            usa_prim = e in ("1meV", "10meV") and not (e == "1meV" and m == "Agua+5NaCl")
            ng = d["primario"] if usa_prim else d["paso1"]
            comp = d["compt_E3"] if m == "Agua-pura" else d["compt_tanque"]
            vals = [cap[(e, m)], ng, d["total"], d["tanque"], comp, d["total"] - d["tanque"]]
            defs = ["capturas de la Campaña 1",
                    "líneas de gamma-primario" if usa_prim else "trazas gamma (filas con paso 1)",
                    "todas las filas", "filas en la caja z<=1330.05 mm", "compt E<3 MeV, todas las posiciones"
                    if m == "Agua-pura" else "compt en la caja", "filas fuera de la caja"]
            for col, tv, v, df in zip(COLS_INTER, t, vals, defs):
                add(col, e, m, tv, v, df)
            add("pares_%", e, m, T_PARES[e][j], round(100 * d["conv_total"] / d["tanque"], 2),
                "100*conv (todas las posiciones)/N_Int(Tanque)", 0.005)
            add("f_Compton", e, m, None, round(comp / d["tanque"], 4), "N_Int(Com)/N_Int(Tanque)")
    for m in MEDIOS:
        for k, e in enumerate(["1meV", "10meV", "100meV", "1000meV"]):
            fw, emax, cmax = fwhm(datos[(e, m)]["compt_estricto"])
            t = T_FWHM[m][k]
            add("FWHM_Compton_MeV", e, m, t[0], round(fw, 3), "1000 intervalos en [0,2.7] MeV", 0.0005)
            add("Emax_Compton_MeV", e, m, t[1], round(emax, 3), "centro del intervalo máximo", 0.0005)
            add("Cmax_Compton", e, m, t[2], cmax, "cuentas del intervalo máximo")
        for e in E5:
            c, x = hist(datos[(e, m)]["rayl_tanque"], 1000, 0.0, 3.0)
            i = max(range(len(c)), key=lambda q: c[q])
            add("Emax_Rayleigh_MeV", e, m, None, round(x[i], 4), "intervalos de 3 keV")
        for k, e in enumerate(["1meV", "100meV", "1000meV", "1000000meV"]):
            v = datos[(e, m)]["phot_prev_compt"]
            mu, sd = momentos(v, 0.01, 0.1)
            t = T_PHOT[m][k]
            add("phot_N", e, m, t[0], len(v), "phot con fila anterior compt (tanque estricto)")
            add("phot_media_MeV", e, m, t[1], round(mu, 4), "en [0.01,0.1] MeV", 0.00005)
            add("phot_sigma_MeV", e, m, t[2], round(sd, 4), "en [0.01,0.1] MeV", 0.00005)
    for e in ("1meV", "1000000meV"):
        for j, m in enumerate(MEDIOS):
            d = datos[(e, m)]
            ext = e == "1meV" and m == "Agua-pura"
            n, zm, rm = espacial(d["pos_prev_ext"] if ext else d["pos_prev_compt"])
            t = T_ESPACIAL[e][j]
            df = "anterior compt/Rayl/Transportation" if ext else "anterior compt"
            add("espacial_N", e, m, t[0], n, df + "; r<=46 cm, 0<=z<=133 cm")
            add("espacial_z_media_cm", e, m, t[1], round(zm, 1), df, 0.05)
            add("espacial_r_media_cm", e, m, None, round(rm, 1), df)
    with open(salida, "w") as f:
        f.write("magnitud\tenergia\tmedio\ttesis\treproducido\tdefinicion\testado\n")
        for r in filas:
            if r[3] is None:
                r[6] = "sin valor en la tesis"
            f.write("\t".join("" if v is None else str(v) for v in r) + "\n")
    n_igual = sum(1 for r in filas if r[6] == "igual")
    n_dif = sum(1 for r in filas if r[6] == "difiere")
    print(f"{n_igual} iguales, {n_dif} difieren, {len(filas) - n_igual - n_dif} sin valor en la tesis")
    for r in filas:
        if r[6] == "difiere":
            print("  DIFIERE:", r[0], r[1], r[2], "tesis", r[3], "reproducido", r[4])


if __name__ == "__main__":
    main()
