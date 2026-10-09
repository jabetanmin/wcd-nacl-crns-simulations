#!/usr/bin/env python3
"""Validación numérica (Sec. 4.1.1): verificación de las cifras de carga de la tesis y pruebas de robustez.

Uso: python3 analizar_validacion.py <resultados> <datos>
  <resultados>  salida de procesar_500MeV.py (se escriben aquí los nuevos archivos)
  <datos>       carpeta con digitalizacion_histograma_carga_referencia_700pts.csv (Fig. 6 de Sidelnik et al. 2020)

Escribe en <resultados>/:
  metricas_reproduccion.tsv  Tabla de métricas de la tesis recalculada con el método original
  metricas_variantes.tsv     las mismas métricas con bins nativos, sin suavizar, a 25 pe y con la referencia limpia
  control_pearson.tsv        r de cada simulación (0.5-10 % NaCl) frente a cada curva de referencia
  razon_25pe.tsv             razones NaCl/agua pura a 25 pe con error de Poisson (simulación) y referencia cruda y limpia
  ajustes_tramos.tsv         Tabla de ajustes por tramos de la tesis: valores, origen y ajuste de Poisson recomendado
  referencia_limpia.tsv      digitalización de la referencia sin los artefactos de la leyenda
"""
import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import pearsonr, spearmanr

SALES = {"Agua+2.5NaCl": "NaCl_2p5", "Agua+5NaCl": "NaCl_5", "Agua+10NaCl": "NaCl_10"}
SIM = ["Agua+0.5NaCl", "Agua+1NaCl", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
VENTANA = (100, 400)                      # intervalo de las métricas de la tesis
# Tabla de métricas de la tesis (tab:metricas_validacion): r, p, rho, RMSE, MAE
TESIS_METRICAS = {"Agua+2.5NaCl": (0.825, 3.5e-175, 0.760, 0.252, 0.200),
                  "Agua+5NaCl": (0.789, 4.1e-150, 0.729, 0.593, 0.432),
                  "Agua+10NaCl": (0.625, 5.2e-77, 0.590, 0.756, 0.582)}
# Tabla de ajustes de la tesis (tab:ajustes): (pendiente, error, intercepto, error) por medio y tramo
TESIS_AJUSTES = {
    "Agua-pura": {(0, 100): (-0.491, 0.015, 4.971, 0.025), (100, 500): (-2.480, 0.121, 9.021, 0.297),
                  (500, 1000): (-1.779, 0.064, 7.374, 0.185), (1000, 1500): (-0.249, 0.127, 3.096, 0.393),
                  (1500, 3500): (-5.472, 0.178, 19.922, 0.605)},
    "Agua+2.5NaCl": {(0, 100): (-0.377, 0.013, 4.729, 0.022), (100, 500): (-2.471, 0.102, 9.115, 0.250),
                     (500, 1000): (-1.732, 0.094, 7.258, 0.269), (1000, 1500): (-0.149, 0.161, 2.793, 0.499),
                     (1500, 3500): (-5.581, 0.213, 20.309, 0.722)},
    "Agua+5NaCl": {(0, 100): (-0.327, 0.012, 4.619, 0.020), (100, 500): (-2.379, 0.106, 8.951, 0.258),
                   (500, 1000): (-1.826, 0.096, 7.530, 0.274), (1000, 1500): (-0.181, 0.178, 2.866, 0.550),
                   (1500, 3500): (-5.403, 0.204, 19.728, 0.690)},
    "Agua+10NaCl": {(0, 100): (-0.272, 0.010, 4.488, 0.018), (100, 500): (-2.271, 0.122, 8.746, 0.299),
                    (500, 1000): (-1.716, 0.052, 7.233, 0.149), (1000, 1500): (-0.316, 0.155, 3.301, 0.479),
                    (1500, 3500): (-5.710, 0.225, 20.762, 0.762)}}
BINNING_A = (400, 0, 6000)               # reproduce los valores de 0-100, 100-500 y 500-1000
BINNING_B = (200, 0, 6000)               # reproduce valores y errores de 1000-1500 y 1500-3500 (celda 34)


def escribir(ruta, filas):
    with open(ruta, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in filas:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, (float, np.floating)) else v) for k, v in r.items()})


def media_movil(y, w=5):
    return np.convolve(y, np.ones(w) / w, mode="same")


class Referencia:
    """Curvas digitalizadas de la Fig. 6 de Sidelnik et al. (cuentas en una malla de 700 puntos, 0-2500)."""

    def __init__(self, ruta):
        self.df = pd.read_csv(ruta)
        self.x = self.df["Numero_de_fotones"].to_numpy()

    def cuentas(self, col, limpia):
        y = self.df[f"{col}_counts_digitized"].to_numpy().copy()
        if limpia:
            # Artefactos: líneas de la leyenda capturadas como curva (1550-1850 fotones, hasta ~5000 cuentas)
            # y el primer punto de la malla. Se sustituyen por interpolación lineal de los vecinos.
            malo = ((self.x > 1550) & (self.x < 1850)) | (self.x < 5)
            y[malo] = np.interp(self.x[malo], self.x[~malo], y[~malo])
        return y

    def razon(self, medio, limpia=False):
        y = self.cuentas(SALES[medio], limpia)
        y0 = self.cuentas("Pure_H2O", limpia)
        return (y / np.trapz(y, self.x)) / (y0 / np.trapz(y0, self.x))


def histograma(q, bordes):
    return np.histogram(q, bordes)[0].astype(float)


def razon_sim(D, medio, bordes, suavizar):
    c, c0 = histograma(D[medio], bordes), histograma(D["Agua-pura"], bordes)
    f, f0 = c / c.sum(), c0 / c0.sum()
    if suavizar:
        f, f0 = media_movil(f), media_movil(f0)
    R = f / (f0 + 1e-12)
    eR = R * np.sqrt(1 / np.maximum(c, 1) + 1 / np.maximum(c0, 1))
    return 0.5 * (bordes[1:] + bordes[:-1]), R, eR


def metricas(a, b):
    r, p = pearsonr(b, a)
    rho, _ = spearmanr(b, a)
    return r, p, rho, float(np.sqrt(np.mean((a - b) ** 2))), float(np.mean(np.abs(a - b)))


def ajuste_loglog(q, nb, a, b, x0, x1):
    """Ajuste original: recta por mínimos cuadrados a (log10 x, log10 N) de los bins no vacíos."""
    c, e = np.histogram(q, bins=nb, range=(a, b))
    x = 0.5 * (e[1:] + e[:-1])
    s = (x >= x0) & (x <= x1) & (c > 0)
    co, cv = np.polyfit(np.log10(x[s]), np.log10(c[s]), 1, cov=True)
    return co[0], np.sqrt(cv[0, 0]), co[1], np.sqrt(cv[1, 1]), int(s.sum())


def ajuste_poisson(q, x0, x1, ancho=10):
    """Ley de potencias dN/dQ ∝ Q^a por máxima verosimilitud de Poisson en bins de `ancho` pe (incluye bins vacíos)."""
    bordes = np.arange(max(x0, 1), x1 + ancho, ancho)
    c = histograma(q, bordes)
    x = 0.5 * (bordes[1:] + bordes[:-1])

    def nll(p):
        mu = np.exp(p[1] + p[0] * np.log(x / x[0]))
        return np.sum(mu - c * np.log(mu))
    r = minimize(nll, [-1.0, np.log(max(c[0], 1))], method="Nelder-Mead",
                 options={"xatol": 1e-8, "fatol": 1e-8, "maxiter": 20000})
    # Error por la información de Fisher: I = sum mu_i [l_i^2, l_i; l_i, 1], con l_i = ln(x_i/x_0)
    l = np.log(x / x[0])
    mu = np.exp(r.x[1] + r.x[0] * l)
    cov = np.linalg.inv(np.array([[np.sum(mu * l * l), np.sum(mu * l)], [np.sum(mu * l), np.sum(mu)]]))
    return r.x[0], np.sqrt(cov[0, 0]), len(c), int(c.sum())


def main(res, datos):
    res, datos = Path(res), Path(datos)
    h = pd.read_csv(res / "histograma_carga.tsv", sep="\t")
    D = {m: np.repeat(g.carga_pe.to_numpy(), g.cuentas.to_numpy()) for m, g in h.groupby("medio")}
    ref = Referencia(datos / "digitalizacion_histograma_carga_referencia_700pts.csv")

    # 1) Métricas con el método original: 300 bins en 0-2500, normalización por área, media móvil de 5 bins,
    #    700 puntos interpolados en 100-400 fotones.
    bordes_t = np.linspace(0, 2500, 301)
    xc = np.linspace(*VENTANA, 700)
    filas = []
    for m, t in TESIS_METRICAS.items():
        x, R, _ = razon_sim(D, m, bordes_t, True)
        v = metricas(np.interp(xc, x, R), np.interp(xc, ref.x, ref.razon(m)))
        filas.append({"medio": m, **{f"{k}_tesis": a for k, a in zip(["r", "p", "rho", "RMSE", "MAE"], t)},
                      **{f"{k}_reproducido": a for k, a in zip(["r", "p", "rho", "RMSE", "MAE"], v)}})
    escribir(res / "metricas_reproduccion.tsv", filas)

    # 2) Variantes
    variantes = {"original_700_puntos": (bordes_t, True, False, True),
                 "bins_nativos_8.3pe_suavizado": (bordes_t, True, False, False),
                 "bins_nativos_8.3pe_sin_suavizar": (bordes_t, False, False, False),
                 "25pe_sin_suavizar": (np.arange(0, 2501, 25), False, False, False),
                 "25pe_sin_suavizar_referencia_limpia": (np.arange(0, 2501, 25), False, True, False)}
    filas = []
    for nombre, (bordes, suav, limpia, interp) in variantes.items():
        for m in SALES:
            x, R, eR = razon_sim(D, m, bordes, suav)
            if interp:
                a, b, e = np.interp(xc, x, R), np.interp(xc, ref.x, ref.razon(m, limpia)), None
            else:
                s = (x >= VENTANA[0]) & (x <= VENTANA[1])
                a, b, e = R[s], np.interp(x[s], ref.x, ref.razon(m, limpia)), eR[s]
            r, p, rho, rmse, mae = metricas(a, b)
            filas.append({"variante": nombre, "medio": m, "n_puntos": len(a), "r": r, "p": p, "rho": rho,
                          "RMSE": rmse, "MAE": mae, "R_sim_media": a.mean(), "R_ref_media": b.mean(),
                          "chi2_por_punto": np.mean(((a - b) / e) ** 2) if e is not None else ""})
    escribir(res / "metricas_variantes.tsv", filas)

    # 3) Control: ¿distingue r la concentración?
    b25 = np.arange(0, 2501, 25)
    filas = []
    for m in SIM:
        x, R, _ = razon_sim(D, m, b25, False)
        s = (x >= VENTANA[0]) & (x <= VENTANA[1])
        for mr in SALES:
            for limpia in (False, True):
                rr = np.interp(x[s], ref.x, ref.razon(mr, limpia))
                filas.append({"simulacion": m, "referencia": mr, "referencia_limpia": int(limpia),
                              "r": pearsonr(rr, R[s])[0], "RMSE": float(np.sqrt(np.mean((R[s] - rr) ** 2))),
                              "R_sim_media": R[s].mean(), "R_ref_media": rr.mean()})
    escribir(res / "control_pearson.tsv", filas)

    # 4) Razones a 25 pe
    filas = []
    x = 0.5 * (b25[1:] + b25[:-1])
    curvas = {m: razon_sim(D, m, b25, False) for m in SIM}
    refs = {(m, l): np.interp(x, ref.x, ref.razon(m, l)) for m in SALES for l in (False, True)}
    for i, xi in enumerate(x):
        fila = {"Q_pe": xi}
        for m in SIM:
            fila[f"R_{m}"], fila[f"err_{m}"] = curvas[m][1][i], curvas[m][2][i]
        for m in SALES:
            fila[f"Rref_{m}"], fila[f"Rref_limpia_{m}"] = refs[(m, False)][i], refs[(m, True)][i]
        filas.append(fila)
    escribir(res / "razon_25pe.tsv", filas)

    # 5) Ajustes por tramos
    filas = []
    for m, tramos in TESIS_AJUSTES.items():
        for (x0, x1), (a_t, da_t, b_t, db_t) in tramos.items():
            A = ajuste_loglog(D[m], *BINNING_A, max(x0, 10), x1)
            B = ajuste_loglog(D[m], *BINNING_B, max(x0, 10), x1)
            P = ajuste_poisson(D[m], max(x0, 10), x1)          # mismo intervalo que el ajuste original
            igual = lambda u, v: abs(u - v) < 6e-4
            origen_v = "A" if igual(A[0], a_t) and igual(A[2], b_t) else ("B" if igual(B[0], a_t) and igual(B[2], b_t) else "?")
            origen_e = "A" if igual(A[1], da_t) and igual(A[3], db_t) else ("B" if igual(B[1], da_t) and igual(B[3], db_t) else "?")
            filas.append({"medio": m, "tramo": f"{x0}-{x1}", "pendiente_tesis": a_t, "err_pend_tesis": da_t,
                          "intercepto_tesis": b_t, "err_int_tesis": db_t, "origen_valores": origen_v,
                          "origen_errores": origen_e, "pend_A": A[0], "err_pend_A": A[1], "n_bins_A": A[4],
                          "pend_B": B[0], "err_pend_B": B[1], "n_bins_B": B[4],
                          "pend_poisson_10pe": P[0], "err_pend_poisson": P[1], "eventos_tramo": P[3]})
    escribir(res / "ajustes_tramos.tsv", filas)

    # 6) Referencia limpia
    escribir(res / "referencia_limpia.tsv",
             [{"Numero_de_fotones": xi, **{f"Rref_{m}": ref.razon(m)[i] for m in SALES},
               **{f"Rref_limpia_{m}": ref.razon(m, True)[i] for m in SALES}} for i, xi in enumerate(ref.x)])
    print("Escrito en", res)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
