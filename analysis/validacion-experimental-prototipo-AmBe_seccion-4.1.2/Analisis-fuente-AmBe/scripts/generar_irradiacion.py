#!/usr/bin/env python3
"""
Irradiación del tanque (WCD) con una fuente puntual 241Am-Be durante un tiempo dado.

Espectro: ISO 8529 digitalizado (resultados/ISO8529_AmBe_digitalizado.txt), grupos con B_E·E
constante: probabilidad del grupo ∝ (B_E·E)·ln(E2/E1) y, dentro del grupo, E log-uniforme.
Emisión: isótropa desde el punto (x_s, y_s, z_s). Número emitido N ~ Poisson(Q·t), con
Q = A[Bq] · 6e-5 n s^-1 Bq^-1 (ISO 8529-1:2021, Tabla 1, valor indicativo).
Se escriben SOLO los neutrones cuya dirección corta el cilindro exterior del tanque
(radio R_ext, 0 <= z <= H_ext); los demás se cuentan pero no se simulan (se desprecia
el retorno por dispersión en suelo y aire).

Formato MEIGA/ARTI, 12 columnas, una línea por neutrón:
  13 px py pz x y z 0 0 0 0 0      (p en GeV/c, posición en cm)
Para usarlo, DetectorList.xml debe tener  <injectionMode type="eFromFile">.
OJO: ParticleFiller de MEIGA invierte pz (momento = (px, py, -pz)), así que aquí se escribe
pz_archivo = -pz_real. px y py no se invierten.

Geometría por defecto = la de la réplica de Sidelnik (SaltyWCD): agua R = 48 cm, H = 133 cm,
Tyvek 0.12 mm + acero 0.5 mm -> R_ext = 48.062 cm; fondo exterior en z = 0, centro del agua en
z = 66.562 cm, tapa exterior en z = 133.124 cm. Eje del tanque en x = y = 0.
"""
import argparse
import json
import os
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(AQUI, "..", "resultados"))
M_N = 939.565            # MeV/c^2
BQ_POR_CI = 3.7e10
RENDIMIENTO_ISO = 6e-5   # n s^-1 Bq^-1


def cargar_espectro():
    E1, E2, L = np.loadtxt(os.path.join(RES, "ISO8529_AmBe_digitalizado.txt"), unpack=True)
    w = L * np.log(E2 / E1)
    return E1, E2, w / w.sum()


def muestrear_E(n, rng, E1, E2, p):
    k = rng.choice(len(p), size=n, p=p)
    return E1[k] * (E2[k] / E1[k]) ** rng.random(n)


def direcciones_iso(n, rng):
    cz = 2 * rng.random(n) - 1
    ph = 2 * np.pi * rng.random(n)
    st = np.sqrt(1 - cz ** 2)
    return np.column_stack([st * np.cos(ph), st * np.sin(ph), cz])


def corta_tanque(S, u, R, H):
    """True si el rayo S + t u (t > 0) entra al cilindro r <= R, 0 <= z <= H por la pared lateral.
    Válido para una fuente fuera del cilindro y con 0 <= z_s <= H (no puede entrar por las tapas
    sin cruzar antes la pared lateral)."""
    a = u[:, 0] ** 2 + u[:, 1] ** 2
    b = 2 * (S[0] * u[:, 0] + S[1] * u[:, 1])
    c = S[0] ** 2 + S[1] ** 2 - R ** 2
    disc = b ** 2 - 4 * a * c
    ok = (disc >= 0) & (a > 0)
    t1 = np.full(len(u), -1.0)
    t1[ok] = (-b[ok] - np.sqrt(disc[ok])) / (2 * a[ok])
    z = S[2] + t1 * u[:, 2]
    return ok & (t1 > 0) & (z >= 0) & (z <= H)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--actividad-Ci", type=float, default=1.0)
    ap.add_argument("--rendimiento", type=float, default=RENDIMIENTO_ISO, help="n s^-1 Bq^-1")
    ap.add_argument("--tiempo", type=float, default=300.0, help="s")
    ap.add_argument("--d", type=float, default=10.0, help="distancia fuente-pared exterior [cm]")
    ap.add_argument("--z", type=float, default=66.562, help="altura de la fuente [cm]")
    ap.add_argument("--R-ext", type=float, default=48.062)
    ap.add_argument("--H-ext", type=float, default=133.124)
    ap.add_argument("--por-archivo", type=int, default=1_000_000)
    ap.add_argument("--lote", type=int, default=10_000_000, help="direcciones muestreadas por lote")
    ap.add_argument("--semilla", type=int, default=20261019)
    ap.add_argument("--salida", default=None)
    ap.add_argument("--solo-contar", action="store_true", help="no escribe archivos")
    a = ap.parse_args()

    rng = np.random.default_rng(a.semilla)
    Q = a.actividad_Ci * BQ_POR_CI * a.rendimiento
    N_emit = int(rng.poisson(Q * a.tiempo))
    S = np.array([-(a.R_ext + a.d), 0.0, a.z])
    E1, E2, p = cargar_espectro()

    nombre = f"Irradiacion-AmBe-{a.actividad_Ci:g}Ci-{a.tiempo:g}s-d{a.d:g}cm"
    dir_sal = a.salida or os.path.join(RES, nombre)
    os.makedirs(dir_sal, exist_ok=True)

    t0 = time.time()
    restantes, n_dentro, parte, buf = N_emit, 0, 0, []
    sumE, sumE2 = 0.0, 0.0
    hist_E = np.zeros(110)            # bins de 0.1 MeV (control)
    hist_cos = np.zeros(20)           # coseno respecto al eje +x (hacia el tanque)

    def volcar(bloque, final=False):
        """Escribe archivos completos de a.por_archivo líneas (y el resto si final)."""
        nonlocal parte
        while bloque is not None and (len(bloque) >= a.por_archivo or (final and len(bloque) > 0)):
            parte += 1
            ruta = os.path.join(dir_sal, f"{nombre}_parte{parte:04d}.txt")
            np.savetxt(ruta, bloque[:a.por_archivo], fmt="13 %.6e %.6e %.6e %.4f %.4f %.4f 0 0 0 0 0")
            bloque = bloque[a.por_archivo:]
        return bloque

    pendiente = None
    while restantes > 0:
        n = min(a.lote, restantes)
        restantes -= n
        u = direcciones_iso(n, rng)
        m = corta_tanque(S, u, a.R_ext, a.H_ext)
        u = u[m]
        k = len(u)
        n_dentro += k
        if k == 0:
            continue
        E = muestrear_E(k, rng, E1, E2, p)
        sumE += E.sum(); sumE2 += (E ** 2).sum()
        hist_E += np.histogram(E, bins=110, range=(0, 11))[0]
        hist_cos += np.histogram(u[:, 0], bins=20, range=(-1, 1))[0]
        if a.solo_contar:
            continue
        pmag = np.sqrt((E + M_N) ** 2 - M_N ** 2) / 1000.0       # GeV/c
        bloque = np.column_stack([pmag * u[:, 0], pmag * u[:, 1], -pmag * u[:, 2],   # -pz: convención MEIGA
                                  np.full(k, S[0]), np.full(k, S[1]), np.full(k, S[2])])
        pendiente = bloque if pendiente is None else np.vstack([pendiente, bloque])
        pendiente = volcar(pendiente)
        print(f"  emitidos {N_emit - restantes:>12d} / {N_emit}, al tanque {n_dentro:>11d}, "
              f"archivos {parte}, {time.time() - t0:7.1f} s", flush=True)
    if not a.solo_contar:
        volcar(pendiente, final=True)

    f = n_dentro / N_emit
    resumen = {
        "actividad_Ci": a.actividad_Ci, "actividad_Bq": a.actividad_Ci * BQ_POR_CI,
        "rendimiento_n_por_s_Bq": a.rendimiento, "Q_n_por_s": Q, "tiempo_s": a.tiempo,
        "neutrones_emitidos_4pi": N_emit, "neutrones_hacia_el_tanque": n_dentro,
        "fraccion_geometrica": f, "error_fraccion": float(np.sqrt(f * (1 - f) / N_emit)),
        "tasa_al_tanque_n_por_s": n_dentro / a.tiempo,
        "fuente_cm": S.tolist(), "d_pared_cm": a.d, "R_ext_cm": a.R_ext, "H_ext_cm": a.H_ext,
        "E_media_MeV": sumE / max(n_dentro, 1),
        "E_rms_MeV": float(np.sqrt(sumE2 / max(n_dentro, 1))),
        "archivos": parte, "neutrones_por_archivo": a.por_archivo, "semilla": a.semilla,
        "formato": "13 px py pz x y z 0 0 0 0 0 (GeV/c, cm); pz escrito con signo invertido (MEIGA usa -pz)",
        "injectionMode": "eFromFile",
        "hist_E_0.1MeV": hist_E.astype(int).tolist(), "hist_cos_x": hist_cos.astype(int).tolist(),
        "tiempo_generacion_s": round(time.time() - t0, 1),
    }
    with open(os.path.join(dir_sal, "resumen.json"), "w") as fo:
        json.dump(resumen, fo, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in resumen.items() if not k.startswith("hist")}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
