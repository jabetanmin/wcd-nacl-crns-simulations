#!/usr/bin/env python3
"""Valida el archivo compuesto (haz/halo/fondo): relee el archivo de MEIGA, deshace la inversión
de pz, comprueba que todos entran al tanque y dibuja espectros, ángulos y puntos de entrada por
componente. -> figuras/fig12_irradiacion_compuesta, <dir>/validacion.json"""
import glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
D = os.path.join(BASE, "resultados", "Irradiacion-AmBe-blindada-1Ci-300s")
FIG = os.path.join(BASE, "figuras")
M_N, R, H = 939.565, 48.062, 133.124
f = [x for x in glob.glob(os.path.join(D, "*N-*.txt")) if not x.endswith("-componentes.txt")][0]
A = np.loadtxt(f)
C = A[:, 7].astype(int); P = A[:, 1:4].copy(); P[:, 2] *= -1; X = A[:, 4:7]
p = 1000 * np.linalg.norm(P, axis=1); E = p ** 2 / (np.sqrt(p ** 2 + M_N ** 2) + M_N) * 1e6   # eV, sin cancelación
u = P / np.linalg.norm(P, axis=1)[:, None]
comp = np.loadtxt(f.replace(".txt", "-componentes.txt"))
a = u[:, 0] ** 2 + u[:, 1] ** 2; b = 2 * (X[:, 0] * u[:, 0] + X[:, 1] * u[:, 1]); c = X[:, 0] ** 2 + X[:, 1] ** 2 - R ** 2
disc = b * b - 4 * a * c; t1 = (-b - np.sqrt(np.clip(disc, 0, None))) / (2 * a); ent = X + t1[:, None] * u
ok = (disc >= 0) & (t1 > 0) & (ent[:, 2] >= 0) & (ent[:, 2] <= H)
nom = {1: "haz (ISO 8529)", 2: "halo (0.5 eV–100 keV)", 3: "fondo (1e-4–0.5 eV)"}
col = {1: "crimson", 2: "darkorange", 3: "royalblue"}
V = {"archivo": os.path.basename(f), "neutrones": int(len(E)), "todos_entran": bool(ok.all()),
     "componentes_coinciden": bool(np.all(comp[:, 0].astype(int) == C)),
     "energia_coincide_rel": float(np.max(np.abs(comp[:, 1] - E) / comp[:, 1]))}
for k in (1, 2, 3):
    m = C == k
    V[nom[k]] = {"n": int(m.sum()), "pct": float(100 * m.mean()), "E_media_eV": float(E[m].mean()),
                 "E_min_eV": float(E[m].min()), "E_max_eV": float(E[m].max()),
                 "angulo_medio_eje_x_deg": float(np.degrees(np.arccos(u[m, 0])).mean())}
json.dump(V, open(os.path.join(D, "validacion.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(V, indent=1, ensure_ascii=False))

plt.rcParams.update({"font.size": 11, "axes.labelsize": 12})
fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
B = np.geomspace(1e-4, 2e7, 241)
for k in (1, 2, 3):
    m = C == k
    h, _ = np.histogram(E[m], bins=B)
    ax[0].stairs(h / np.diff(np.log(B)) / len(E), B, color=col[k], lw=1.5, label=f"{nom[k]}: {100*m.mean():.0f} %")
ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].set_ylim(1e-4, 1)
ax[0].set_xlabel("$E_n$ [eV]"); ax[0].set_ylabel(r"$E\,dN/dE$ / N$_{total}$")
ax[0].legend(fontsize=8.5); ax[0].grid(alpha=0.3, ls="--", which="both")
for k in (1, 2, 3):
    m = C == k
    ax[1].hist(np.degrees(np.arccos(u[m, 0])), bins=90, range=(0, 90), histtype="step", lw=1.5,
               color=col[k], density=True, label=nom[k])
ax[1].set_yscale("log"); ax[1].set_xlabel(r"Ángulo respecto a la dirección fuente→tanque (+x) [°]")
ax[1].set_ylabel("densidad"); ax[1].legend(fontsize=8.5); ax[1].grid(alpha=0.3, ls="--")
phi = np.degrees(np.arctan2(ent[:, 1], ent[:, 0])) % 360
for k, s in ((3, 0.3), (2, 0.3), (1, 0.6)):
    m = C == k
    sel = np.where(m)[0][:15000]
    ax[2].scatter(phi[sel], ent[sel, 2], s=s, color=col[k], alpha=0.5, rasterized=True)
ax[2].set_xlim(90, 270); ax[2].set_ylim(0, H)
ax[2].set_xlabel(r"Azimut del punto de entrada $\varphi$ [°] (fuente en 180°)"); ax[2].set_ylabel("z de entrada [cm]")
ax[2].set_title("Puntos de entrada (muestra)", fontsize=10)
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig12_irradiacion_compuesta.{ext}"), dpi=200)
