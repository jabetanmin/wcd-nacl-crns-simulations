#!/usr/bin/env python3
"""Carga total por evento y eficiencia de detección del WCD (Campaña 1, 16 energías × 4 medios).

Uso: python3 procesar_carga.py <resultados_neutrones> <salida>
     (p. ej. ../campana-1_neutrones-monoenergeticos_seccion-4.2/resultados resultados_carga)

Entradas, por corrida <energía>/<medio>/ (las produce procesar_corrida.py de la parte neutrónica):
  resumen.json       historias, capturas y el histograma de carga de Carga_Total_*.txt
                     (fotoelectrones por evento; el archivo solo contiene eventos con señal, Q >= 1)
  historias.tsv.gz   posición de cada captura (z_cap): profundidad bajo la superficie del agua (z = 1330 mm)
                     y capturas fuera del agua (z_cap > 1330 mm). Si falta, esas columnas quedan vacías.

Salidas en <salida>/:
  resumen_carga_campana.tsv       una fila por corrida (ver el README)
  histograma_carga.tsv            cuentas por carga entera (formato largo, solo valores no nulos)
  planitud_carga.tsv              pruebas de independencia de la carga respecto de la energía, por medio
  ganancia_eficiencia_carga.tsv   eficiencia del agua con NaCl / agua pura, por umbral de carga
"""
import csv
import gzip
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ENERGIAS = ["1meV", "2.5meV", "5meV", "7meV", "10meV", "25meV", "50meV", "80meV", "100meV",
            "300meV", "500meV", "700meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
E_MEV = {e: float(e[:-3]) for e in ENERGIAS}       # la carpeta 1000000meV se rotula "1 keV", como en la tesis
Z_SUPERFICIE = 1330.0                               # superficie del agua [mm]
UMBRALES = [1, 3, 5, 10, 20]
# Intervalos de carga de la prueba de homogeneidad (agrupados para que las celdas esperadas no queden vacías)
BORDES_HOMOGENEIDAD = [1, 2, 3, 4, 5, 6, 8, 10, 13, 16, 20, 25, 30, 40, 50, 70, 10**6]
ENERGIAS_GANANCIA = ["1meV", "25meV", "1000meV", "1000000meV"]


def capturas_por_profundidad(archivo):
    """Capturas fuera del agua y profundidad media [mm] de las capturas en el agua."""
    fuera, prof = 0, []
    with gzip.open(archivo, "rt") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["ultimo_proceso"] != "nCapture":
                continue
            z = float(r["z_cap"])
            if z > Z_SUPERFICIE:
                fuera += 1
            else:
                prof.append(Z_SUPERFICIE - z)
    return fuera, float(np.mean(prof))


def estadistica(hist, historias, capturas):
    """Estadística de la carga a partir del histograma de cuentas por carga entera."""
    q = np.arange(len(hist))
    h = np.asarray(hist, dtype=float)
    h[0] = 0                                         # Q = 0 no se registra
    n = h.sum()
    media = (q * h).sum() / n
    std = np.sqrt((h * (q - media) ** 2).sum() / (n - 1))
    acum = np.cumsum(h)
    fila = {"eventos_senal": int(n),
            "eps": n / historias, "u_eps": np.sqrt(n / historias * (1 - n / historias) / historias),
            "eta_cap": capturas / historias, "P_senal_captura": n / capturas,
            "Q_media_pe": media, "u_Q_media_pe": std / np.sqrt(n), "Q_std_pe": std,
            "Q_mediana_pe": int(np.searchsorted(acum, n / 2)), "Q_max_pe": int(q[h > 0].max()),
            "f_Q20": h[20:].sum() / n}
    for u in UMBRALES:
        fila[f"eps_Q{u}"] = h[u:].sum() / historias
    return fila


def main(base, salida):
    base, salida = Path(base), Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    filas, hist = [], {}
    for e in ENERGIAS:
        for m in MEDIOS:
            res = json.loads((base / e / m / "resumen.json").read_text())
            h = res["carga"]["histograma_pe"]
            assert sum(h) == res["carga"]["eventos"] and h[0] == 0, f"{e}/{m}: histograma inconsistente"
            hist[(e, m)] = np.asarray(h)
            fila = {"energia": e, "medio": m, "E_meV": E_MEV[e], "historias": res["historias"],
                    "capturas": res["capturas"]}
            fila.update(estadistica(h, res["historias"], res["capturas"]))
            hgz = base / e / m / "historias.tsv.gz"
            if hgz.exists():
                fuera, prof = capturas_por_profundidad(hgz)
                fila["capturas_fuera_agua"], fila["profundidad_captura_media_mm"] = fuera, prof
            else:
                fila["capturas_fuera_agua"], fila["profundidad_captura_media_mm"] = "", ""
            filas.append(fila)
            print(f"{e}/{m}: {fila['eventos_senal']} eventos, <Q> = {fila['Q_media_pe']:.3f} pe", flush=True)

    largo = max(len(h) for h in hist.values())          # mismo largo para sumar histogramas
    hist = {k: np.pad(h, (0, largo - len(h))) for k, h in hist.items()}
    escribir(salida / "resumen_carga_campana.tsv", filas)
    escribir(salida / "histograma_carga.tsv",
             [{"energia": e, "medio": m, "carga_pe": q, "cuentas": int(c)}
              for (e, m), h in hist.items() for q, c in enumerate(h) if c])

    # Independencia de la energía, por medio
    plan = []
    for m in MEDIOS:
        s = [f for f in filas if f["medio"] == m]
        qm, u = np.array([f["Q_media_pe"] for f in s]), np.array([f["u_Q_media_pe"] for f in s])
        w = 1 / u ** 2
        qp = (w * qm).sum() / w.sum()
        chi2 = (((qm - qp) / u) ** 2).sum()
        tabla = np.array([[hist[(e, m)][a:b].sum() for a, b in zip(BORDES_HOMOGENEIDAD[:-1], BORDES_HOMOGENEIDAD[1:])]
                          for e in ENERGIAS])
        tabla = tabla[:, tabla.sum(0) > 0]
        chi2_h, p_h, ndf_h, _ = stats.chi2_contingency(tabla)
        # Energías bajas (<= 10 meV) frente a altas (>= 25 meV): media y error de los eventos agrupados
        grupos = []
        for sel in (lambda x: x <= 10, lambda x: x >= 25):
            h = sum(hist[(e, m)] for e in ENERGIAS if sel(E_MEV[e])).astype(float)
            q = np.arange(len(h))
            n = h.sum()
            mu = (q * h).sum() / n
            grupos.append((mu, np.sqrt((h * (q - mu) ** 2).sum() / (n - 1) / n)))
        d, ud = grupos[0][0] - grupos[1][0], np.hypot(grupos[0][1], grupos[1][1])
        plan.append({"medio": m, "Q_ponderada_pe": qp, "u_Q_ponderada_pe": 1 / np.sqrt(w.sum()),
                     "Q_min_pe": qm.min(), "Q_max_pe": qm.max(),
                     "chi2_media": chi2, "ndf_media": len(s) - 1, "p_media": stats.chi2.sf(chi2, len(s) - 1),
                     "chi2_forma": chi2_h, "ndf_forma": ndf_h, "p_forma": p_h,
                     "dQ_baja_alta_pe": d, "u_dQ_baja_alta_pe": ud, "dQ_sigma": d / ud})
    escribir(salida / "planitud_carga.tsv", plan)

    # Ganancia de eficiencia del NaCl respecto al agua pura
    idx = {(f["energia"], f["medio"]): f for f in filas}
    gan = []
    for e in ENERGIAS_GANANCIA:
        for m in MEDIOS[1:]:
            gan.append({"energia": e, "medio": m,
                        **{f"G_Q{u}": idx[(e, m)][f"eps_Q{u}"] / idx[(e, "Agua-pura")][f"eps_Q{u}"]
                           for u in [1, 5, 10, 20]}})
    escribir(salida / "ganancia_eficiencia_carga.tsv", gan)


def escribir(ruta, filas):
    with open(ruta, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in filas:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, (float, np.floating)) else v) for k, v in r.items()})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
