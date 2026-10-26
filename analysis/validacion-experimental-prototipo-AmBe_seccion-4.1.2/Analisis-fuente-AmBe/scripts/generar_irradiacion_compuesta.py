#!/usr/bin/env python3
"""
Irradiación del tanque con el montaje blindado (caja de polietileno con canal de 3 cm x 30 cm,
10 cm de plomo pegado al tanque), modelada con tres componentes (configuración del usuario,
2026-10-20) en lugar de simular el transporte por el blindaje:

  1. Haz directo (rápido)      35 %  espectro ISO 8529; cono del canal (semiángulo
                                      atan(1.5/30) = 2.86°) desde la fuente puntual, 40 cm de la pared.
  2. Halo difuso               45 %  térmicos/epitérmicos 0.5 eV – 100 keV, espectro 1/E
                                      (log-uniforme); emitido desde la cara del plomo (120 x 40 cm)
                                      con ángulos de 0 a 90° respecto a la normal, ley del coseno.
  3. Fondo hemisférico         20 %  térmicos 1e-4 – 0.5 eV, espectro de flujo maxwelliano
                                      (kT = 25.3 meV) truncado; cubre los dos tramos indicados
                                      (0.0001–0.025 eV y 0.025–0.5 eV). Emitido desde un plano frente
                                      a la mitad del tanque que mira a la fuente (96 x 133 cm),
                                      isótropo en el hemisferio hacia el tanque (0–180° de abertura).

Los porcentajes son fracciones de los neutrones que ENTRAN al tanque. La normalización
absoluta se ancla en el haz directo: neutrones que salen por el canal (Q · Ω/4π) por la
transmisión de 10 cm de plomo (remoción, exp(-0.116·10) = 0.313 por defecto) y en 5 min.
Total = haz / 0.35.

Formato MEIGA (eFromFile): 13 px py pz x y z C 0 0 0 0  (GeV/c, cm; pz con signo invertido
porque ParticleFiller.cc usa -pz). La columna 8 (C = 1 haz, 2 halo, 3 fondo) la lee MEIGA pero
no la usa; además se escribe <archivo>-componentes.txt con la componente y la energía por línea
(la línea k es el run_id k en MEIGA). Las líneas están barajadas.
"""
import argparse, json, os
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(AQUI, "..", "resultados"))
M_N = 939.565
R, H, ZC = 48.062, 133.124, 66.562
KT = 0.0253e-6          # MeV


def corta(S, u):
    """S: (n,3) puntos fuera del cilindro con 0<=z<=H; u: (n,3). True si el rayo entra por la pared."""
    a = u[:, 0] ** 2 + u[:, 1] ** 2
    b = 2 * (S[:, 0] * u[:, 0] + S[:, 1] * u[:, 1])
    c = S[:, 0] ** 2 + S[:, 1] ** 2 - R ** 2
    disc = b * b - 4 * a * c
    ok = (disc >= 0) & (a > 0)
    t1 = np.where(ok, (-b - np.sqrt(np.clip(disc, 0, None))) / (2 * np.where(a > 0, a, 1)), -1)
    z = S[:, 2] + t1 * u[:, 2]
    return ok & (t1 > 0) & (z >= 0) & (z <= H)


def espectro_iso(n, rng):
    E1, E2, L = np.loadtxt(os.path.join(RES, "ISO8529_AmBe_digitalizado.txt"), unpack=True)
    w = L * np.log(E2 / E1); w /= w.sum()
    k = rng.choice(len(w), size=n, p=w)
    return E1[k] * (E2[k] / E1[k]) ** rng.random(n)


def espectro_1_E(n, rng, a=0.5e-6, b=0.1):
    return a * (b / a) ** rng.random(n)


def espectro_maxwell(n, rng, a=1e-10, b=0.5e-6):
    """Flujo maxwelliano φ(E) ∝ E exp(-E/kT), truncado a [a, b] (inversión numérica)."""
    E = np.geomspace(a, b, 20001)
    f = E * np.exp(-E / KT)
    cdf = np.concatenate([[0], np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(E))]); cdf /= cdf[-1]
    return np.interp(rng.random(n), cdf, E)


def generar(n, rng, origen, direccion, energia):
    """Genera n neutrones que entran al tanque (rechazo de los que no lo cortan)."""
    Ss, us, intentos, aceptados = [], [], 0, 0
    falta = n
    while falta > 0:
        m = max(4 * falta, 10000)
        S = origen(m, rng); u = direccion(m, rng)
        ok = corta(S, u)
        intentos += m; aceptados += int(ok.sum())
        S, u = S[ok][:falta], u[ok][:falta]
        Ss.append(S); us.append(u); falta -= len(S)
    S, u = np.vstack(Ss), np.vstack(us)
    return S, u, energia(n, rng), aceptados / intentos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--actividad-Ci", type=float, default=1.0)
    ap.add_argument("--rendimiento", type=float, default=6e-5)
    ap.add_argument("--tiempo", type=float, default=300.0)
    ap.add_argument("--T-plomo", type=float, default=float(np.exp(-0.116 * 10)),
                    help="transmisión del haz por 10 cm de plomo (remoción: 0.313; sin choque: 0.082)")
    ap.add_argument("--fracciones", type=float, nargs=3, default=[0.35, 0.45, 0.20],
                    metavar=("HAZ", "HALO", "FONDO"))
    ap.add_argument("--semilla", type=int, default=20261020)
    ap.add_argument("--salida", default=None)
    ap.add_argument("--N-total", type=int, default=None,
                    help="número total de neutrones a generar (mismas fracciones); por defecto, la normalización de 5 min")
    a = ap.parse_args()
    assert abs(sum(a.fracciones) - 1) < 1e-9, "las fracciones deben sumar 1"
    rng = np.random.default_rng(a.semilla)

    Q = a.actividad_Ci * 3.7e10 * a.rendimiento
    th = np.arctan(1.5 / 30.0)
    omega = (1 - np.cos(th)) / 2
    n_haz_esp = Q * omega * a.T_plomo * a.tiempo
    N_tot = int(round(n_haz_esp / a.fracciones[0]))
    if a.N_total:
        N_tot = a.N_total
        n = [int(round(N_tot * f)) for f in a.fracciones]        # número exacto pedido
        n[-1] = N_tot - sum(n[:-1])
    else:
        n = [int(rng.poisson(N_tot * f)) for f in a.fracciones]

    S0 = np.array([-(R + 40.0), 0.0, ZC])
    X_CARA = -R - 0.1                                   # justo fuera del tanque (aire)

    def org_fuente(m, rng): return np.tile(S0, (m, 1))
    def dir_cono(m, rng):
        c = 1 - rng.random(m) * (1 - np.cos(th)); p = 2 * np.pi * rng.random(m); s = np.sqrt(1 - c * c)
        return np.column_stack([c, s * np.cos(p), s * np.sin(p)])
    def org_cara_plomo(m, rng):
        return np.column_stack([np.full(m, X_CARA), rng.uniform(-60, 60, m), ZC + rng.uniform(-20, 20, m)])
    def dir_coseno(m, rng):                              # Lambert: cos θ = sqrt(U)
        c = np.sqrt(rng.random(m)); p = 2 * np.pi * rng.random(m); s = np.sqrt(1 - c * c)
        return np.column_stack([c, s * np.cos(p), s * np.sin(p)])
    def org_silueta(m, rng):
        return np.column_stack([np.full(m, X_CARA), rng.uniform(-R, R, m), rng.uniform(0, H, m)])
    def dir_hemisferio(m, rng):                          # isótropo en el hemisferio +x
        c = rng.random(m); p = 2 * np.pi * rng.random(m); s = np.sqrt(1 - c * c)
        return np.column_stack([c, s * np.cos(p), s * np.sin(p)])

    comps = [("haz", org_fuente, dir_cono, espectro_iso),
             ("halo", org_cara_plomo, dir_coseno, espectro_1_E),
             ("fondo", org_silueta, dir_hemisferio, espectro_maxwell)]
    bloques, info = [], {}
    for k, ((nombre, org, dr, esp), nk) in enumerate(zip(comps, n), start=1):
        S, u, E, acept = generar(nk, rng, org, dr, esp)
        bloques.append((np.full(nk, k), S, u, E))
        info[nombre] = {"neutrones": nk, "fraccion": nk / sum(n),
                        "aceptacion_geometrica": acept,
                        "E_media_MeV": float(E.mean()), "E_mediana_MeV": float(np.median(E)),
                        "E_min_MeV": float(E.min()), "E_max_MeV": float(E.max())}
    C = np.concatenate([b[0] for b in bloques]); S = np.vstack([b[1] for b in bloques])
    u = np.vstack([b[2] for b in bloques]); E = np.concatenate([b[3] for b in bloques])
    perm = rng.permutation(len(E)); C, S, u, E = C[perm], S[perm], u[perm], E[perm]
    p = np.sqrt(E * (E + 2 * M_N)) / 1000.0             # sin cancelación a energías térmicas
    P = p[:, None] * u
    P[:, 2] *= -1                                        # convención de MEIGA

    nombre = (f"Irradiacion-AmBe-blindada-{a.actividad_Ci:g}Ci-{a.tiempo:g}s" if not a.N_total
              else "AmBe-montaje-haz-halo-fondo")
    d = a.salida or os.path.join(RES, nombre)
    os.makedirs(d, exist_ok=True)
    ruta = os.path.join(d, f"{sum(n)}N-{nombre}.txt")
    np.savetxt(ruta, np.column_stack([P, S, C]), fmt="13 %.6e %.6e %.6e %.4f %.4f %.4f %d 0 0 0 0")
    np.savetxt(ruta.replace(".txt", "-componentes.txt"), np.column_stack([C, E * 1e6]), fmt="%d %.6e",
               header="componente (1 haz, 2 halo, 3 fondo)  E[eV]   (línea k = run_id k)")
    E_f = E[C == 3]
    res = {"Q_n_s": Q, "tiempo_s": a.tiempo, "emitidos_4pi": Q * a.tiempo,
           "semiangulo_canal_deg": float(np.degrees(th)), "fraccion_4pi_canal": omega,
           "T_plomo_haz": a.T_plomo, "haz_esperado": n_haz_esp, "N_total_esperado": N_tot,
           "N_total_generado": int(sum(n)), "pct_de_lo_emitido": 100 * sum(n) / (Q * a.tiempo),
           "tasa_al_tanque_n_s": sum(n) / a.tiempo, "componentes": info,
           "fondo_fraccion_1e-4_a_0.025eV": float(np.mean(E_f < 0.025e-6)),
           "fondo_fraccion_0.025_a_0.5eV": float(np.mean(E_f >= 0.025e-6)),
           "archivo": os.path.basename(ruta), "semilla": a.semilla,
           "injectionMode": "eFromFile",
           "geometria": {"fuente_cm": S0.tolist(), "cara_plomo": "x=-48.162, |y|<=60, |z-66.562|<=20",
                         "plano_fondo": "x=-48.162, |y|<=48.062, 0<=z<=133.124"}}
    json.dump(res, open(os.path.join(d, "resumen.json"), "w"), indent=2, ensure_ascii=False)
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
