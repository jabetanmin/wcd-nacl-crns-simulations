#!/usr/bin/env python3
"""
Haz colimado de la fuente 241Am-Be: ángulo del cono, área irradiada sobre la pared del tanque y
fracción del flujo emitido, para un canal cilíndrico (diámetro D, largo L) con la fuente puntual
en el fondo del canal y sobre su eje, apuntando al centro del tanque a media altura.

Escenarios:
  A: D = 5 cm, L = 30 cm, salida del canal a 10 cm de la pared (fuente a 40 cm de la pared).
  B: D = 3 cm, L = 30 cm, salida a 10 cm (fuente a 40 cm).
  C: D = 5 cm, L = 30 cm, fuente a 10 cm de la pared (lectura literal "la fuente a 10 cm").
Se comprueba con Monte Carlo sobre la pared cilíndrica (R_ext = 48.062 cm) y se compara con la
emisión sin blindaje. -> resultados/colimador_area.json
"""
import json, os
import numpy as np

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES = os.path.join(BASE, "resultados")
Q = 3.7e10 * 6e-5          # n/s para 1 Ci (ISO 8529-1:2021)
T = 300.0                  # s
R, H, ZC = 48.062, 133.124, 66.562
N_TANQUE_SIN_BLINDAJE = 202_363_865          # archivo de irradiación sin colimar (d = 10 cm)
N_EMITIDOS = 665_980_683

def escenario(D, L, d_fuente_pared, n_mc=4_000_000, semilla=1):
    th = np.arctan((D / 2) / L)                       # semiángulo del cono
    f = (1 - np.cos(th)) / 2                          # fracción de 4π
    r_plano = d_fuente_pared * np.tan(th)             # radio de la mancha en un plano tangente
    # Monte Carlo: direcciones uniformes dentro del cono (eje +x), intersección con el cilindro
    rng = np.random.default_rng(semilla)
    cz = 1 - rng.random(n_mc) * (1 - np.cos(th))      # cos respecto al eje del cono
    ph = 2 * np.pi * rng.random(n_mc)
    st = np.sqrt(1 - cz ** 2)
    u = np.column_stack([cz, st * np.cos(ph), st * np.sin(ph)])
    S = np.array([-(R + d_fuente_pared), 0.0, ZC])
    a = u[:, 0] ** 2 + u[:, 1] ** 2; b = 2 * S[0] * u[:, 0]; c = S[0] ** 2 - R ** 2
    disc = b ** 2 - 4 * a * c
    t1 = (-b - np.sqrt(np.clip(disc, 0, None))) / (2 * a)
    P = S + t1[:, None] * u
    entra = (disc >= 0) & (t1 > 0) & (P[:, 2] >= 0) & (P[:, 2] <= H)
    # área de la mancha sobre la pared curva: extensión en arco (R·Δφ) y en z
    phi = np.arctan2(P[entra, 1], -P[entra, 0])
    ancho = R * (phi.max() - phi.min()); alto = P[entra, 2].max() - P[entra, 2].min()
    area_curva = np.pi * ancho * alto / 4             # elipse con esos ejes
    tasa = Q * f * entra.mean()
    return {
        "D_cm": D, "L_cm": L, "fuente_a_pared_cm": d_fuente_pared,
        "semiangulo_deg": float(np.degrees(th)), "angulo_total_deg": float(2 * np.degrees(th)),
        "fraccion_4pi": float(f), "fraccion_4pi_pct": float(100 * f),
        "radio_mancha_plano_cm": float(r_plano), "area_mancha_plano_cm2": float(np.pi * r_plano ** 2),
        "mancha_pared_ancho_cm": float(ancho), "mancha_pared_alto_cm": float(alto),
        "area_mancha_pared_cm2": float(area_curva),
        "fraccion_del_cono_que_entra": float(entra.mean()),
        "neutrones_por_s_al_tanque": float(tasa),
        "neutrones_5min_al_tanque": float(tasa * T),
        "flujo_medio_en_mancha_n_cm2_s": float(tasa / area_curva),
        "pct_del_flujo_sin_blindaje_al_tanque": float(100 * tasa * T / N_TANQUE_SIN_BLINDAJE),
        "pct_de_la_silueta_del_tanque": float(100 * area_curva / (2 * R * H)),
    }

out = {"Q_n_s": Q, "tiempo_s": T, "emitidos_5min": N_EMITIDOS,
       "A_D5_L30_salida10cm": escenario(5, 30, 40),
       "B_D3_L30_salida10cm": escenario(3, 30, 40),
       "C_D5_L30_fuente10cm": escenario(5, 30, 10)}
# Fuga a través de 10 cm de plomo (orden de magnitud): neutrones emitidos hacia el tanque desde
# 40 cm, fuera del cono, atenuados por exp(-Sigma*10 cm). Sigma_t(Pb, ~4 MeV) ~ 0.25 cm^-1
# (solo no colisionados, cota inferior); Sigma_R ~ 0.116 cm^-1 (sección de remoción, más realista).
rng = np.random.default_rng(3); n = 4_000_000
cz = 2 * rng.random(n) - 1; ph = 2 * np.pi * rng.random(n); st = np.sqrt(1 - cz ** 2)
u = np.column_stack([st * np.cos(ph), st * np.sin(ph), cz]); Sx = -(R + 40.0)
a = u[:, 0] ** 2 + u[:, 1] ** 2; b = 2 * Sx * u[:, 0]; c = Sx ** 2 - R ** 2; disc = b * b - 4 * a * c
t = (-b - np.sqrt(np.clip(disc, 0, None))) / (2 * a); z = ZC + t * u[:, 2]
f40 = float(((disc >= 0) & (t > 0) & (z >= 0) & (z <= H)).mean())
f_fuera = f40 - out["A_D5_L30_salida10cm"]["fraccion_4pi"]
out["fuga_plomo_10cm"] = {"fraccion_geom_hacia_tanque_desde_40cm": f40,
    "T_no_colisionados": float(np.exp(-0.25 * 10)), "T_remocion": float(np.exp(-0.116 * 10)),
    "n_5min_no_colisionados": float(Q * f_fuera * np.exp(-0.25 * 10) * T),
    "n_5min_remocion": float(Q * f_fuera * np.exp(-0.116 * 10) * T)}
json.dump(out, open(os.path.join(RES, "colimador_area.json"), "w"), indent=2, ensure_ascii=False)
for k, v in out.items():
    if isinstance(v, dict):
        print(f"\n{k}")
        for kk, vv in v.items():
            print(f"  {kk:38s} {vv:.6g}")
