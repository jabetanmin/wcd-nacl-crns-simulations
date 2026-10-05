#!/usr/bin/env python3
"""Procesa una corrida de la Campaña 1 (neutrones monoenergéticos, QGSP_BERT_HP sin S(alpha,beta)).

Lee solo las salidas crudas del simulador de una carpeta <energía>/<medio>:

  interaccion-completa-neutrones.txt  un paso del neutrón primario por línea:
      paso, partícula, track, padre, E_pre [MeV], x0, y0, z0, x1, y1, z1 [mm], E_post [MeV], proceso
      (una historia empieza cuando paso = 1)
  Carga_Total_*.txt                   fotoelectrones por evento con señal (opcional)

y escribe, en una sola pasada y sin archivos intermedios:

  historias.tsv.gz una fila por historia: conteos por proceso, destino final por cara del volumen
                  activo, posición y energía de captura, y N y xi según la definición de la tesis;
  resumen.json    medias, coeficientes de destino con incertidumbre binomial y estadística de carga.

Definición de N (la del notebook original Analisis-procesos-neutrones-*.ipynb, usada en la tesis):
  1. se conservan los pasos con la posición previa o la posterior dentro de la caja
     |x|, |y| <= 478 mm, 0 <= z <= 1330.05 mm (previa) o 0 <= z <= 1330 mm (posterior);
  2. sobre esa secuencia se busca una cadena que empiece en un hadElastic con número de paso entre 3 y 49,
     continúe solo con hadElastic con pasos consecutivos y termine en nCapture (paso > 3); una captura
     con paso entre 3 y 49 sin cadena previa abierta cuenta como cadena de una sola línea (N = 0);
     cualquier salto en el número de paso u otro proceso descarta la cadena;
  3. N = paso de la captura - paso del primer hadElastic, es decir, el número de dispersiones elásticas;
     xi_historia_inicial = ln(E_pre del primer hadElastic / E_pre de la captura) / N (indefinido si N = 0).
     Esta fue la definición inicial de xi en el estudio; se conserva solo por trazabilidad.
  Como verificación se guarda también N_total, el número de hadElastic de toda la historia capturada.

xi por colisión (DEFINICIÓN DE LA TESIS; reemplazó a la definición inicial por historia):
xi = ln(E_pre/E_post) de cada dispersión elástica. Por historia se guarda suma_ln_E = suma de ln(E_pre/E_post)
sobre sus pasos hadElastic; <xi> = suma de suma_ln_E / suma de n_hadElastic sobre las historias capturadas
(xi_colision_capturadas en resumen.json).

Destino final (última frontera del volumen activo |x|,|y| <= 480 mm, 0 <= z <= 1330 mm, como en
analysis/revision-tesis_2026-10/balance_caras_tanque.py): cap_dentro, cap_fuera, arriba, abajo, lateral,
no_entra, inel_dentro, inel_fuera, otro.

Uso:
  python3 procesar_corrida.py <carpeta de la corrida> <carpeta de salida>
"""
import glob
import gzip
import json
import math
import sys
from pathlib import Path

PROCESOS = ("Transportation", "hadElastic", "neutronInelastic", "nCapture")

# caja del notebook original para N
CAJA_PRE = (478.0, 0.0, 1330.05)
CAJA_POST = (478.0, 0.0, 1330.0)
# volumen activo para el destino final
VOL = (480.0, 0.0, 1330.0)


# Geometría cilíndrica (opcional): radio del tanque de la Campaña 1, tankRadius = 48 cm.
RADIO = 480.0
GEOMETRIA = "caja"   # "caja" (definición de la tesis) o "cilindro" (r = sqrt(x^2 + y^2) <= RADIO)


def en_caja(x, y, z, caja):
    if GEOMETRIA == "cilindro":
        _, zmin, zmax = caja
        return x * x + y * y <= RADIO * RADIO and zmin <= z <= zmax
    lado, zmin, zmax = caja
    return -lado <= x <= lado and -lado <= y <= lado and zmin <= z <= zmax


class CadenaTesis:
    """Máquina de estados que reproduce la extracción de secuencias del notebook original.

    Recibe la secuencia global de pasos filtrados (todas las historias seguidas, como el archivo
    interaccion-neutrones-interior-tanque-*.txt) y entrega (historia, N, E0, E_cap) por cadena válida.
    """

    def __init__(self):
        self.grabando = False
        self.prev = None
        self.inicio = None   # (historia, paso, E_pre)

    def paso(self, hist, paso, e_pre, proceso):
        if not self.grabando and 3 <= paso < 50 and proceso == "nCapture":
            return (hist, 0, e_pre, e_pre)
        if not self.grabando and proceso == "hadElastic" and 3 <= paso < 50:
            self.grabando, self.prev, self.inicio = True, paso, (hist, paso, e_pre)
            return None
        if self.grabando:
            if paso != self.prev + 1:
                self.grabando = False
                return None
            self.prev = paso
            if proceso == "hadElastic":
                return None
            self.grabando = False
            if proceso == "nCapture" and paso > 3:
                h0, p0, e0 = self.inicio
                return (h0, paso - p0, e0, e_pre)
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
    n_tesis = {}
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
        suma_ln = sum(math.log(s[1] / s[9]) for s in pasos if s[8] == "hadElastic" and s[1] > 0 and s[9] > 0)
        filas[historia] = {
            "historia": historia, "n_pasos": len(pasos),
            **{f"n_{p}": conteo[p] for p in PROCESOS},
            "ultimo_proceso": ult[8], "destino": destino(pasos),
            "x_cap": ult[5] if cap else "", "y_cap": ult[6] if cap else "",
            "z_cap": ult[7] if cap else "", "E_cap": ult[1] if cap else "",
            "N_total": conteo["hadElastic"] if cap else "",
            "suma_ln_E": suma_ln,
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
            e_pre = float(c[4])
            x0, y0, z0, x1, y1, z1 = map(float, c[5:11])
            proceso = c[12]
            pasos.append((paso, e_pre, x0, y0, z0, x1, y1, z1, proceso, float(c[11])))
            if en_caja(x0, y0, z0, CAJA_PRE) or en_caja(x1, y1, z1, CAJA_POST):
                r = cadena.paso(historia, paso, e_pre, proceso)
                if r:
                    h, n, e0, ecap = r
                    xi = math.log(e0 / ecap) / n if n > 0 and ecap > 0 else float("nan")
                    n_tesis[h] = (n, xi)
    cerrar()

    columnas = ["historia", "n_pasos"] + [f"n_{p}" for p in PROCESOS] + [
        "ultimo_proceso", "destino", "x_cap", "y_cap", "z_cap", "E_cap", "N_total", "N_tesis", "xi_historia_inicial",
        "suma_ln_E"]
    with gzip.open(salida / "historias.tsv.gz", "wt", compresslevel=9) as f:
        f.write("\t".join(columnas) + "\n")
        for h in sorted(filas):
            fila = filas[h]
            n, xi = n_tesis.get(h, ("", ""))
            fila["N_tesis"] = n
            fila["xi_historia_inicial"] = "" if xi == "" or math.isnan(xi) else f"{xi:.6e}"
            fila["suma_ln_E"] = f"{fila['suma_ln_E']:.6e}"
            f.write("\t".join(str(fila[k]) for k in columnas) + "\n")

    # resumen
    n_hist = len(filas)
    medias = {p: sum(r[f"n_{p}"] for r in filas.values()) / n_hist for p in PROCESOS}
    dest = {}
    for r in filas.values():
        dest[r["destino"]] = dest.get(r["destino"], 0) + 1
    def coef(*claves):
        k = sum(dest.get(c, 0) for c in claves)
        p = k / n_hist
        return {"valor": p, "incertidumbre": math.sqrt(p * (1 - p) / n_hist)}
    capturadas = [r for r in filas.values() if r["ultimo_proceso"] == "nCapture"]
    ns = [v[0] for v in n_tesis.values()]
    xis = [v[1] for v in n_tesis.values() if not math.isnan(v[1])]
    resumen = {
        "corrida": f"{carpeta.parent.name}/{carpeta.name}",
        "historias": n_hist,
        "media_pasos_por_historia": medias,
        "destinos": dest,
        "eta_cap": coef("cap_dentro", "cap_fuera"),
        "eta_refle": coef("arriba"),
        "eta_trans": coef("abajo", "lateral"),
        "eta_otros": coef("no_entra", "inel_dentro", "inel_fuera", "otro"),
        "capturas": len(capturadas),
        "N_tesis": {"cadenas": len(ns), "media": sum(ns) / len(ns) if ns else None},
        "N_total_media": (sum(r["N_total"] for r in capturadas) / len(capturadas)) if capturadas else None,
        "xi_historia_inicial": {"n": len(xis), "media": sum(xis) / len(xis) if xis else None},
        "xi_colision_capturadas": (sum(float(r["suma_ln_E"]) for r in capturadas)
                                   / max(sum(r["n_hadElastic"] for r in capturadas), 1)),
        "xi_colision_todas": (sum(float(r["suma_ln_E"]) for r in filas.values())
                              / max(sum(r["n_hadElastic"] for r in filas.values()), 1)),
    }
    cargas = sorted(glob.glob(str(carpeta / "Carga_Total*.txt")))
    if cargas:
        q = [float(x) for x in open(cargas[0]) if x.strip()]
        resumen["carga"] = {"archivo": Path(cargas[0]).name, "eventos": len(q),
                            "media_pe": sum(q) / len(q) if q else None}
    (salida / "resumen.json").write_text(json.dumps(resumen, indent=1, ensure_ascii=False))
    return resumen


if __name__ == "__main__":
    r = procesar(sys.argv[1], sys.argv[2])
    print(json.dumps({k: r[k] for k in ("corrida", "historias", "capturas", "N_tesis", "xi_colision_capturadas")},
                     ensure_ascii=False))
