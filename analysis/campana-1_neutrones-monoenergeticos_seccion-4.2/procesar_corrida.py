#!/usr/bin/env python3
"""Procesa una corrida de la Campaña 1 (neutrones monoenergéticos, QGSP_BERT_HP sin S(alpha,beta)).

Lee solo las salidas crudas del simulador de una carpeta <energía>/<medio>:

  interaccion-completa-neutrones.txt  un paso del neutrón primario por línea:
      paso, partícula, track, padre, E_pre [MeV], x0, y0, z0, x1, y1, z1 [mm], E_post [MeV], proceso
      (una historia empieza cuando paso = 1)
  Carga_Total_*.txt                   fotoelectrones por evento con señal (opcional)

y escribe, en una sola pasada y sin archivos intermedios:

  historias.tsv.gz  una fila por historia: conteos por proceso, destino final por cara del volumen
                    activo, posición y energía de captura, N y xi;
  resumen.json      medias y desviaciones por historia, coeficientes de destino con incertidumbre
                    binomial, <N>, <xi>, y los histogramas de N, xi y carga que usan las figuras.

Cadenas de dispersión (definición de la tesis, la del notebook Analisis-procesos-neutrones-*.ipynb):
  1. se conservan los pasos con la posición previa o la posterior dentro de la caja
     |x|, |y| <= 478 mm, 0 <= z <= 1330.05 mm (previa) o 0 <= z <= 1330 mm (posterior);
  2. sobre esa secuencia se busca una cadena que empiece en un hadElastic con número de paso entre 3 y 49,
     continúe solo con hadElastic con pasos consecutivos y termine en nCapture (paso > 3); una captura
     con paso entre 3 y 49 sin cadena previa abierta cuenta como cadena de una sola línea (N = 0);
     cualquier salto en el número de paso u otro proceso descarta la cadena.

N (tesis): número de dispersiones elásticas de la cadena. N_total (verificación): todos los hadElastic de
la historia capturada.

xi (DEFINICIÓN DE LA TESIS): xi = ln(E_pre/E_post) de cada dispersión elástica de las cadenas válidas,
como en los notebooks Histogramas_cita_*.ipynb. <xi> y sigma(xi) se toman sobre todas esas colisiones;
el histograma usa 300 intervalos entre -2 y 2, como las figuras de la tesis. Por historia se guarda la suma
de xi de su cadena (suma_xi_cadena).

lambda_cap (longitud de captura, definición de la tesis, Sección 4.2.1 y notebooks de Distancia-captura):
  distancia en línea recta entre la posición previa del paso 3 y la posición de captura, para las historias
  capturadas cuyo paso 3 es una dispersión elástica que empieza en la cara interior de la tapa
  (z = 1330.05 mm) sin pérdida previa de energía. Estadística por corrida con un método fijo: mediana
  (valor principal) y cuartiles, moda (máximo de un histograma de intervalos de 0.5 cm refinado con una
  parábola de tres puntos) y media, con incertidumbres por remuestreo (bootstrap, 200 réplicas, semilla fija).

xi_historia_inicial (definición inicial del estudio, reemplazada; solo por trazabilidad):
  ln(E_pre del primer hadElastic / E_pre de la captura) / N, por historia.

Destino final (última frontera del volumen activo |x|,|y| <= 480 mm, 0 <= z <= 1330 mm, como en
analysis/revision-tesis_2026-10/balance_caras_tanque.py): cap_dentro, cap_fuera, arriba, abajo, lateral,
no_entra, inel_dentro, inel_fuera, otro.

Uso:
  python3 procesar_corrida.py <carpeta de la corrida> <carpeta de salida> [caja|cilindro]
"""
import glob
import gzip
import json
import math
import sys
from pathlib import Path

import numpy as np

PROCESOS = ("Transportation", "hadElastic", "neutronInelastic", "nCapture")

# caja del notebook original para las cadenas de dispersión
CAJA_PRE = (478.0, 0.0, 1330.05)
CAJA_POST = (478.0, 0.0, 1330.0)
# volumen activo para el destino final
VOL = (480.0, 0.0, 1330.0)

# Geometría cilíndrica (opcional): radio del tanque de la Campaña 1, tankRadius = 48 cm.
RADIO = 480.0
GEOMETRIA = "caja"   # "caja" (definición de la tesis) o "cilindro" (r = sqrt(x^2 + y^2) <= RADIO)

# histograma de xi de las figuras de la tesis
XI_BINS = 300
XI_RANGO = (-2.0, 2.0)

# longitud de captura
Z_TAPA = 1330.05            # cara interior de la tapa [mm]
LAMBDA_BIN = 2.0            # histograma guardado: 0.2 cm
MODA_BIN = 5.0              # intervalo para la moda: 0.5 cm
LAMBDA_MAX = 1000.0         # histograma guardado hasta 100 cm
BOOTSTRAP = 200
SEMILLA = 20261005


def lambda_cap(pasos):
    """Longitud de captura [mm] según la definición de la tesis, o None."""
    if len(pasos) < 3 or pasos[-1][8] != "nCapture":
        return None
    p3 = pasos[2]
    if p3[0] != 3 or p3[8] != "hadElastic" or p3[4] != Z_TAPA or p3[1] != pasos[0][1]:
        return None
    ult = pasos[-1]
    return math.dist((p3[2], p3[3], p3[4]), (ult[5], ult[6], ult[7]))


def moda_refinada(valores):
    bordes = np.arange(0.0, valores.max() + MODA_BIN, MODA_BIN)
    h, _ = np.histogram(valores, bins=bordes)
    centros = 0.5 * (bordes[:-1] + bordes[1:])
    i = int(np.argmax(h))
    if 0 < i < len(h) - 1:
        a, b, _ = np.polyfit(centros[i - 1:i + 2], h[i - 1:i + 2], 2)
        if a < 0:
            return float(-b / (2 * a))
    return float(centros[i])


def estadistica_lambda(valores):
    v = np.asarray(valores, dtype=float)
    if len(v) == 0:
        return None
    rng = np.random.default_rng(SEMILLA)
    modas, medianas, medias = [], [], []
    for _ in range(BOOTSTRAP):
        m = rng.choice(v, size=len(v), replace=True)
        modas.append(moda_refinada(m))
        medianas.append(np.median(m))
        medias.append(m.mean())
    h, _ = np.histogram(v, bins=np.arange(0.0, LAMBDA_MAX + LAMBDA_BIN, LAMBDA_BIN))
    return {"n": int(len(v)), "unidad": "mm",
            "moda": moda_refinada(v), "u_moda": float(np.std(modas)),
            "mediana": float(np.median(v)), "u_mediana": float(np.std(medianas)),
            "media": float(v.mean()), "u_media": float(np.std(medias)), "std": float(v.std()),
            "p25": float(np.percentile(v, 25)), "p75": float(np.percentile(v, 75)),
            "histograma": {"ancho": LAMBDA_BIN, "rango": [0.0, LAMBDA_MAX], "conteos": h.tolist(),
                           "encima": int((v > LAMBDA_MAX).sum())}}


def en_caja(x, y, z, caja):
    if GEOMETRIA == "cilindro":
        _, zmin, zmax = caja
        return x * x + y * y <= RADIO * RADIO and zmin <= z <= zmax
    lado, zmin, zmax = caja
    return -lado <= x <= lado and -lado <= y <= lado and zmin <= z <= zmax


class CadenaTesis:
    """Máquina de estados que reproduce la extracción de secuencias del notebook original.

    Recibe la secuencia global de pasos filtrados (todas las historias seguidas, como el archivo
    interaccion-neutrones-interior-tanque-*.txt) y entrega (historia, N, E0, E_cap, [xi]) por cadena
    válida, donde [xi] son los ln(E_pre/E_post) de sus dispersiones elásticas.
    """

    def __init__(self):
        self.grabando = False
        self.prev = None
        self.inicio = None   # (historia, paso, E_pre)
        self.xis = []

    def paso(self, hist, paso, e_pre, e_post, proceso):
        if not self.grabando and 3 <= paso < 50 and proceso == "nCapture":
            return (hist, 0, e_pre, e_pre, [])
        if not self.grabando and proceso == "hadElastic" and 3 <= paso < 50:
            self.grabando, self.prev, self.inicio = True, paso, (hist, paso, e_pre)
            self.xis = [math.log(e_pre / e_post)] if e_pre > 0 and e_post > 0 else []
            return None
        if self.grabando:
            if paso != self.prev + 1:
                self.grabando = False
                return None
            self.prev = paso
            if proceso == "hadElastic":
                if e_pre > 0 and e_post > 0:
                    self.xis.append(math.log(e_pre / e_post))
                return None
            self.grabando = False
            if proceso == "nCapture" and paso > 3:
                h0, p0, e0 = self.inicio
                return (h0, paso - p0, e0, e_pre, self.xis)
        return None


def destino(pasos):
    """Clasificación por la última frontera del volumen activo atravesada."""
    entro = False
    salida = None
    for _, _, x0, y0, z0, x1, y1, z1, _, _ in pasos:
        a = en_caja(x0, y0, z0, VOL)
        b = en_caja(x1, y1, z1, VOL)
        if b:
            entro = True
        if a and not b:
            salida = "arriba" if z1 > VOL[2] else ("abajo" if z1 < VOL[1] else "lateral")
        if not a and b:
            salida = None
    ultimo = pasos[-1]
    dentro = en_caja(ultimo[5], ultimo[6], ultimo[7], VOL)
    if ultimo[8] == "nCapture":
        return "cap_dentro" if dentro else "cap_fuera"
    if ultimo[8] == "neutronInelastic":
        return "inel_dentro" if dentro else "inel_fuera"
    if not entro:
        return "no_entra"
    return salida or "otro"


def procesar(carpeta, salida, geometria="caja"):
    """geometria = "caja" (definición de la tesis) o "cilindro" (mismo z, radio RADIO en x-y)."""
    global GEOMETRIA
    GEOMETRIA = geometria
    carpeta, salida = Path(carpeta), Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    cadena = CadenaTesis()
    filas = {}
    cadenas = {}
    xi_todas = []
    historia = 0
    pasos = []

    def cerrar():
        if not pasos:
            return
        conteo = {p: 0 for p in PROCESOS}
        for s in pasos:
            conteo[s[8]] = conteo.get(s[8], 0) + 1
        ult = pasos[-1]
        cap = ult[8] == "nCapture"
        filas[historia] = {
            "historia": historia, "n_pasos": len(pasos),
            **{f"n_{p}": conteo[p] for p in PROCESOS},
            "ultimo_proceso": ult[8], "destino": destino(pasos),
            "x_cap": ult[5] if cap else "", "y_cap": ult[6] if cap else "",
            "z_cap": ult[7] if cap else "", "E_cap": ult[1] if cap else "",
            "N_total": conteo["hadElastic"] if cap else "",
            "lambda_cap": lambda_cap(pasos),
        }

    with open(carpeta / "interaccion-completa-neutrones.txt") as f:
        for linea in f:
            c = linea.split()
            if len(c) < 13:
                continue
            paso = int(c[0])
            if paso == 1 and pasos:
                cerrar()
                pasos = []
            if paso == 1:
                historia += 1
            e_pre, e_post = float(c[4]), float(c[11])
            x0, y0, z0, x1, y1, z1 = map(float, c[5:11])
            proceso = c[12]
            pasos.append((paso, e_pre, x0, y0, z0, x1, y1, z1, proceso, e_post))
            if en_caja(x0, y0, z0, CAJA_PRE) or en_caja(x1, y1, z1, CAJA_POST):
                r = cadena.paso(historia, paso, e_pre, e_post, proceso)
                if r:
                    h, n, e0, ecap, xis = r
                    xi_ini = math.log(e0 / ecap) / n if n > 0 and ecap > 0 else float("nan")
                    cadenas[h] = (n, xi_ini, sum(xis))
                    xi_todas.extend(xis)
    cerrar()

    columnas = ["historia", "n_pasos"] + [f"n_{p}" for p in PROCESOS] + [
        "ultimo_proceso", "destino", "x_cap", "y_cap", "z_cap", "E_cap", "N_total", "N_tesis",
        "suma_xi_cadena", "xi_historia_inicial", "lambda_cap"]
    with gzip.open(salida / "historias.tsv.gz", "wt", compresslevel=9) as f:
        f.write("\t".join(columnas) + "\n")
        for h in sorted(filas):
            fila = filas[h]
            n, xi_ini, sxi = cadenas.get(h, ("", float("nan"), ""))
            fila["N_tesis"] = n
            fila["suma_xi_cadena"] = "" if sxi == "" else f"{sxi:.6e}"
            fila["xi_historia_inicial"] = "" if math.isnan(xi_ini) else f"{xi_ini:.6e}"
            fila["lambda_cap"] = "" if fila["lambda_cap"] is None else f"{fila['lambda_cap']:.6f}"
            f.write("\t".join(str(fila[k]) for k in columnas) + "\n")

    # resumen
    n_hist = len(filas)

    def media_std(clave):
        v = np.array([r[clave] for r in filas.values()], dtype=float)
        return {"media": float(v.mean()), "std": float(v.std())}

    dest = {}
    for r in filas.values():
        dest[r["destino"]] = dest.get(r["destino"], 0) + 1

    def coef(*claves):
        k = sum(dest.get(c, 0) for c in claves)
        p = k / n_hist
        return {"valor": p, "incertidumbre": math.sqrt(p * (1 - p) / n_hist)}

    capturadas = [r for r in filas.values() if r["ultimo_proceso"] == "nCapture"]
    ns = np.array([v[0] for v in cadenas.values()], dtype=int)
    xi_ini = np.array([v[1] for v in cadenas.values() if not math.isnan(v[1])])
    xi = np.array(xi_todas)
    hist_xi, _ = np.histogram(xi, bins=XI_BINS, range=XI_RANGO)
    resumen = {
        "corrida": f"{carpeta.parent.name}/{carpeta.name}",
        "geometria": geometria,
        "historias": n_hist,
        "pasos_por_historia": {p: media_std(f"n_{p}") for p in PROCESOS},
        "destinos": dest,
        "eta_cap": coef("cap_dentro", "cap_fuera"),
        "eta_refle": coef("arriba"),
        "eta_trans": coef("abajo", "lateral"),
        "eta_otros": coef("no_entra", "inel_dentro", "inel_fuera", "otro"),
        "capturas": len(capturadas),
        "N_tesis": {"cadenas": int(len(ns)), "media": float(ns.mean()) if len(ns) else None,
                    "histograma": np.bincount(ns).tolist() if len(ns) else []},
        "N_total_media": float(np.mean([r["N_total"] for r in capturadas])) if capturadas else None,
        "xi_tesis": {"colisiones": int(len(xi)), "media": float(xi.mean()), "sigma": float(xi.std()),
                     "mediana": float(np.median(xi)),
                     "histograma": {"bins": XI_BINS, "rango": list(XI_RANGO), "conteos": hist_xi.tolist(),
                                    "debajo": int((xi < XI_RANGO[0]).sum()),
                                    "encima": int((xi > XI_RANGO[1]).sum())}},
        "xi_historia_inicial": {"n": int(len(xi_ini)), "media": float(xi_ini.mean()) if len(xi_ini) else None},
        "lambda_cap": estadistica_lambda([float(r["lambda_cap"]) for r in filas.values() if r["lambda_cap"] != ""]),
    }
    cargas = sorted(glob.glob(str(carpeta / "Carga_Total*.txt")))
    if cargas:
        q = np.array([float(x) for x in open(cargas[0]) if x.strip()])
        enteros = bool(np.all(q == np.round(q)))
        resumen["carga"] = {"archivo": Path(cargas[0]).name, "eventos": int(len(q)),
                            "media_pe": float(q.mean()), "std_pe": float(q.std()),
                            "histograma_pe": np.bincount(q.astype(int)).tolist() if enteros else None}
    (salida / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False))
    return resumen


if __name__ == "__main__":
    geo = sys.argv[3] if len(sys.argv) > 3 else "caja"
    r = procesar(sys.argv[1], sys.argv[2], geo)
    print(json.dumps({"corrida": r["corrida"], "capturas": r["capturas"],
                      "N_medio": r["N_tesis"]["media"], "colisiones_xi": r["xi_tesis"]["colisiones"],
                      "xi_medio": r["xi_tesis"]["media"], "xi_sigma": r["xi_tesis"]["sigma"]},
                     ensure_ascii=False))
