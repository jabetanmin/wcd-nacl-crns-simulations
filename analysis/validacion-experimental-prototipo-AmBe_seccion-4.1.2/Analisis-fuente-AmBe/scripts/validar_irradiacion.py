#!/usr/bin/env python3
"""
Valida los archivos de irradiación: lee algunas partes, reconstruye energía y dirección
(deshaciendo la inversión de pz de MEIGA), comprueba que todos los rayos entran al tanque y
compara el espectro con el ISO 8529 digitalizado. -> figuras/fig11, <dir>/validacion.json
Uso: validar_irradiacion.py [directorio] [n_partes]
"""
import glob, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
args = [x for x in sys.argv[1:] if not x.startswith("-") and not x.endswith(".json")]   # ignora argv de Jupyter
d = args[0] if len(args) > 0 else os.path.join(RES, "Irradiacion-AmBe-1Ci-300s-d10cm")
n_partes = int(args[1]) if len(args) > 1 else 3
M_N = 939.565
res = json.load(open(os.path.join(d, "resumen.json")))
partes = sorted(glob.glob(os.path.join(d, "*_parte*.txt")))
rng = np.random.default_rng(0)
elegidas = sorted(rng.choice(partes, size=min(n_partes, len(partes)), replace=False))
A = np.vstack([np.loadtxt(f) for f in elegidas])
ids, P, X = A[:, 0], A[:, 1:4].copy(), A[:, 4:7]
P[:, 2] *= -1                                    # momento real en Geant4
p = 1000 * np.linalg.norm(P, axis=1)
T = np.sqrt(p ** 2 + M_N ** 2) - M_N
u = P / np.linalg.norm(P, axis=1)[:, None]
S = np.array(res["fuente_cm"]); R, H = res["R_ext_cm"], res["H_ext_cm"]

# punto de entrada en la pared lateral
a = u[:, 0] ** 2 + u[:, 1] ** 2; b = 2 * (S[0] * u[:, 0] + S[1] * u[:, 1]); c = S[0] ** 2 + S[1] ** 2 - R ** 2
disc = b ** 2 - 4 * a * c
t1 = (-b - np.sqrt(np.clip(disc, 0, None))) / (2 * a)
ent = S + t1[:, None] * u
ok = (disc >= 0) & (t1 > 0) & (ent[:, 2] >= 0) & (ent[:, 2] <= H)

E1, E2, L = np.loadtxt(os.path.join(RES, "ISO8529_AmBe_digitalizado.txt"), unpack=True)
w = L * np.log(E2 / E1); w /= w.sum()
B = np.append(E1, E2[-1])
h, _ = np.histogram(T, bins=B)
esp = w * len(T)
m = esp > 20
chi2 = float(np.sum((h[m] - esp[m]) ** 2 / esp[m]))
V = {"partes_leidas": [os.path.basename(f) for f in elegidas], "neutrones_leidos": int(len(T)),
     "ids": sorted({int(i) for i in ids}), "posicion_unica": bool(np.all(np.abs(X - S) < 1e-3)),
     "todos_entran_al_tanque": bool(ok.all()), "fraccion_que_entra": float(ok.mean()),
     "E_media_MeV": float(T.mean()),
     "E_media_esperada_MeV": float(np.sum(L * (E2 - E1)) / np.sum(L * np.log(E2 / E1))),
     "chi2_grupos": chi2, "ndf": int(m.sum()),
     "ux_media": float(u[:, 0].mean()),
     "entrada_z_media_cm": float(ent[ok, 2].mean()),
     "angulo_incidencia_medio_deg": float(np.degrees(np.mean(np.arccos(np.clip(
         -(ent[ok, 0] * u[ok, 0] + ent[ok, 1] * u[ok, 1]) / R, -1, 1)))))}
json.dump(V, open(os.path.join(d, "validacion.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(V, indent=1, ensure_ascii=False))

plt.rcParams.update({"font.size": 11, "axes.labelsize": 12})
fig, ax = plt.subplots(1, 3, figsize=(14, 4.3))
ax[0].stairs(h / len(T) / np.log(E2 / E1), B, color="seagreen", lw=1.5, label="Archivo generado")
ax[0].stairs(w / np.log(E2 / E1), B, color="k", ls="--", lw=1.2, label="ISO 8529 digitalizado")
ax[0].set_xscale("log"); ax[0].set_xlabel("$E_n$ [MeV]"); ax[0].set_ylabel("Fracción por unidad de letargia")
ax[0].legend(fontsize=9); ax[0].grid(alpha=0.3, ls="--", which="both")
ax[0].text(0.03, 0.6, f"$\\chi^2$/ndf = {chi2:.0f}/{int(m.sum())}", transform=ax[0].transAxes)
phi = np.degrees(np.arctan2(ent[ok, 1], ent[ok, 0])) % 360   # la fuente está en phi = 180°
hb = ax[1].hist2d(phi, ent[ok, 2], bins=[90, 67], range=[[90, 270], [0, H]], cmap="viridis")
ax[1].set_xlabel(r"Azimut del punto de entrada $\varphi$ [°]")
ax[1].set_ylabel("z de entrada [cm]"); ax[1].set_title("Puntos de entrada en la pared", fontsize=10)
fig.colorbar(hb[3], ax=ax[1], label="neutrones")
ax[2].hist(np.degrees(np.arccos(np.clip(-(ent[ok, 0] * u[ok, 0] + ent[ok, 1] * u[ok, 1]) / R, -1, 1))),
           bins=45, range=(0, 90), color="slateblue")
ax[2].set_xlabel("Ángulo de incidencia respecto a la normal [°]"); ax[2].set_ylabel("neutrones")
ax[2].grid(alpha=0.3, ls="--")
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig11_validacion_irradiacion.{ext}"), dpi=200)
