#!/usr/bin/env python3
"""
Genera una fuente de neutrones 241Am-Be para MEIGA muestreando el espectro limpio
(resultados/espectro_AmBe_limpio.txt) por inversión de la función acumulada.

Diferencias con Espectro-completo-neutrones-fuente-AmBe241.txt:
  * cada neutrón tiene una energía continua (no 437 energías discretas);
  * el número de neutrones por intervalo de energía es proporcional a S(E)*dE
    (no a la cantidad de puntos digitalizados);
  * los neutrones salen en orden aleatorio (cualquier subconjunto inicial
    del archivo tiene el espectro completo);
  * sin puntos espurios ni valores negativos.

Formato de salida (igual al original, momento en GeV/c):
  13 px py pz x y z 0 0 0 0 0

Uso:
  python3 generar_fuente.py [-n 1637458] [--semilla 2026] [--direccion +z|-z|+x|iso]
                            [-o ../resultados/Fuente-AmBe241-corregida-<N>n.txt]
"""
import argparse
import os

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(AQUI, "..", "resultados"))
M_N = 939.565  # MeV/c^2 (mismo valor que el notebook original)


def muestrear(n, rng):
    E, S = np.loadtxt(os.path.join(RES, "espectro_AmBe_limpio.txt"), unpack=True)
    # CDF exacta de la interpolación lineal por tramos
    area = 0.5 * (S[1:] + S[:-1]) * np.diff(E)
    cdf = np.concatenate([[0.0], np.cumsum(area)])
    cdf /= cdf[-1]
    u = rng.random(n)
    k = np.clip(np.searchsorted(cdf, u, side="right") - 1, 0, len(E) - 2)
    # inversión exacta dentro del tramo (densidad lineal)
    e0, e1, s0, s1 = E[k], E[k + 1], S[k], S[k + 1]
    du = (u - cdf[k]) * cdf_total(area)        # área a recorrer dentro del tramo
    m = (s1 - s0) / (e1 - e0)
    with np.errstate(invalid="ignore", divide="ignore"):
        x = np.where(np.abs(m) > 1e-12,
                     (-s0 + np.sqrt(np.maximum(s0 ** 2 + 2 * m * du, 0))) / m,
                     du / np.where(s0 > 0, s0, 1))
    return e0 + np.clip(x, 0, e1 - e0)


def cdf_total(area):
    return float(np.sum(area))


def direcciones(n, modo, rng):
    if modo == "+z":
        return np.tile([0.0, 0.0, 1.0], (n, 1))
    if modo == "-z":
        return np.tile([0.0, 0.0, -1.0], (n, 1))
    if modo == "+x":
        return np.tile([1.0, 0.0, 0.0], (n, 1))
    cz = 2 * rng.random(n) - 1
    ph = 2 * np.pi * rng.random(n)
    st = np.sqrt(1 - cz ** 2)
    return np.column_stack([st * np.cos(ph), st * np.sin(ph), cz])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", type=int, default=1637458, help="número de neutrones")
    ap.add_argument("--semilla", type=int, default=2026)
    ap.add_argument("--direccion", choices=["+z", "-z", "+x", "iso"], default="+z",
                    help="+z reproduce la fuente original (px = py = 0)")
    ap.add_argument("-o", "--salida", default=None)
    a = ap.parse_args()

    rng = np.random.default_rng(a.semilla)
    T = muestrear(a.n, rng)                                   # MeV
    p = np.sqrt((T + M_N) ** 2 - M_N ** 2) / 1000.0           # GeV/c
    u = direcciones(a.n, a.direccion, rng)
    P = p[:, None] * u

    tag = {"+z": "", "-z": "-menosz", "+x": "-x", "iso": "-iso"}[a.direccion]
    salida = a.salida or os.path.join(RES, f"Fuente-AmBe241-corregida-{a.n}n{tag}.txt")
    ceros = "0 0 0 0 0 0 0 0"
    with open(salida, "w") as f:
        for px, py, pz in P:
            f.write(f"13 {px:.6e} {py:.6e} {pz:.6e} {ceros}\n" if a.direccion != "+z"
                    else f"13 0 0 {pz:.6e} {ceros}\n")
    np.savetxt(salida.replace(".txt", "-energias.txt"), T, fmt="%.6f")
    print(f"{salida}: {a.n} neutrones, <E> = {T.mean():.4f} MeV, "
          f"E en [{T.min():.4f}, {T.max():.4f}] MeV, dirección {a.direccion}, semilla {a.semilla}")


if __name__ == "__main__":
    main()
