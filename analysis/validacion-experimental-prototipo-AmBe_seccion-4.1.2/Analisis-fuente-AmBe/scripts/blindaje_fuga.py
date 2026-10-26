#!/usr/bin/env python3
"""
Estimación (atenuación exponencial, sin transporte) de cuántos neutrones de una fuente 241Am-Be
de 1 Ci llegan al tanque en 5 min con el montaje descrito por el usuario (2026-10-20):

  * Fuente puntual dentro de una caja de polietileno/parafina, al fondo de un canal cilíndrico
    de 3 cm de diámetro y 30 cm de largo que apunta al tanque.
  * Entre la cara exterior de la caja y el tanque hay 10 cm, ocupados por bloques de plomo de
    10 cm de espesor, 40 cm de alto y 120 cm de largo (plomo pegado al tanque, centrado a la
    altura de la fuente). El canal NO atraviesa el plomo: el haz cruza los 10 cm de plomo.
  * Caja a media altura del tanque (z = 66.562 cm). Mesa debajo (no se modela).
  * Supuesto: la caja es un cubo de polietileno de 60 cm de lado con la fuente en el centro
    (30 cm hasta cada cara, igual al largo del canal); no se conocen sus medidas exteriores.

Tanque: R_ext = 48.062 cm, H_ext = 133.124 cm, eje en x = y = 0. Fuente en x = -(R + 40).
Para cada dirección isótropa que corta el tanque se calcula el recorrido en polietileno
(30 cm salvo dentro del canal) y en plomo (losa x ∈ [-R-10, -R], |y| <= 60, |z - zc| <= 20),
y se aplica exp(-Σ_PE L_PE - Σ_Pb L_Pb) con dos juegos de Σ:
  - "no colisionados" (Σ total a ~4 MeV): PE 0.22 cm^-1, Pb 0.25 cm^-1   -> cota inferior
  - "remoción" (Σ_R de blindaje de neutrones rápidos): PE 0.123, Pb 0.116 -> estimación habitual
No incluye los neutrones moderados que salen de la caja como térmicos/epitérmicos (pueden ser
importantes para las capturas en el tanque) ni la dispersión en la mesa, el suelo o el aire.
-> resultados/blindaje_fuga.json
"""
import json, os
import numpy as np

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES = os.path.join(BASE, "resultados")
Q, T = 3.7e10 * 6e-5, 300.0
R, H, ZC = 48.062, 133.124, 66.562
L_CANAL, R_CANAL, PE = 30.0, 1.5, 30.0
D_PB, Y_PB, Z_PB = 10.0, 60.0, 20.0
S = np.array([-(R + D_PB + L_CANAL), 0.0, ZC])
SIG = {"no_colisionados": (0.22, 0.25), "remocion": (0.123, 0.116)}

rng = np.random.default_rng(11)
N = 40_000_000
acc = {k: {"canal": 0.0, "PE+Pb": 0.0, "solo_PE": 0.0} for k in SIG}
n_dir = {"canal": 0, "PE+Pb": 0, "solo_PE": 0}
n_tanque = 0
for _ in range(N // 4_000_000):
    n = 4_000_000
    cz = 2 * rng.random(n) - 1; ph = 2 * np.pi * rng.random(n); st = np.sqrt(1 - cz ** 2)
    u = np.column_stack([st * np.cos(ph), st * np.sin(ph), cz])
    a = u[:, 0] ** 2 + u[:, 1] ** 2; b = 2 * S[0] * u[:, 0]; c = S[0] ** 2 - R ** 2
    disc = b * b - 4 * a * c
    t1 = (-b - np.sqrt(np.clip(disc, 0, None))) / (2 * a)
    z = S[2] + t1 * u[:, 2]
    m = (disc >= 0) & (t1 > 0) & (z >= 0) & (z <= H)
    u, t1 = u[m], t1[m]
    n_tanque += len(u)
    # canal: semiángulo atan(R_CANAL / L_CANAL) alrededor de +x
    en_canal = u[:, 0] >= np.cos(np.arctan(R_CANAL / L_CANAL))
    # recorrido en la losa de plomo: x entre -R-D_PB y -R (hasta la entrada al tanque)
    tx0 = (-R - D_PB - S[0]) / u[:, 0]
    tx1 = np.minimum((-R - S[0]) / u[:, 0], t1)
    ts = np.linspace(0, 1, 41)[None, :]
    tt = tx0[:, None] + ts * np.clip(tx1 - tx0, 0, None)[:, None]
    yy = S[1] + tt * u[:, 1:2]; zz = S[2] + tt * u[:, 2:3]
    dentro = (np.abs(yy) <= Y_PB) & (np.abs(zz - ZC) <= Z_PB)
    L_pb = np.clip(tx1 - tx0, 0, None) * dentro.mean(axis=1)
    L_pe = np.where(en_canal, 0.0, PE / np.abs(u).max(axis=1))     # salida del cubo de semilado 30 cm
    grupos = {"canal": en_canal, "PE+Pb": (~en_canal) & (L_pb > 0), "solo_PE": (~en_canal) & (L_pb == 0)}
    for g, sel in grupos.items():
        n_dir[g] += int(sel.sum())
        for k, (spe, spb) in SIG.items():
            acc[k][g] += float(np.exp(-spe * L_pe[sel] - spb * L_pb[sel]).sum())

out = {"supuestos": __doc__.strip().split("\n\n")[1], "Q_n_s": Q, "tiempo_s": T,
       "fraccion_geom_hacia_tanque": n_tanque / N,
       "fraccion_4pi_por_camino": {g: v / N for g, v in n_dir.items()}}
for k in SIG:
    out[k] = {g: {"n_por_s": Q * v / N, "n_5min": Q * v / N * T} for g, v in acc[k].items()}
    out[k]["total_n_5min"] = sum(x["n_5min"] for x in out[k].values() if isinstance(x, dict))
json.dump(out, open(os.path.join(RES, "blindaje_fuga.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps({k: v for k, v in out.items() if k != "supuestos"}, indent=1))
