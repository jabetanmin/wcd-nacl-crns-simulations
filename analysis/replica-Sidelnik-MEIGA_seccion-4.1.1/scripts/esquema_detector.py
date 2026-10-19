#!/usr/bin/env python3
"""Esquema del WCD de la replica de Sidelnik (corte lateral y = 0, a escala) con un evento real de MEIGA (agua pura):
trayectorias de los neutrones (primario de 500 MeV y secundarios), captura en H, gamma de captura y electrones del gamma.
Si existe la corrida (CORRIDAS_SIDELNIK) extrae el evento y lo guarda en resultados/evento_ejemplo.json; si no, usa ese archivo.
Escribe figuras/fig00_esquema_detector.{png,pdf}. Uso: esquema_detector.py [medio] [run_id]   (por defecto: nacl25, run 124, captura en 35Cl)"""
import os, sys, json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
MEDIO = sys.argv[1] if len(sys.argv) > 1 else "nacl25"
RUN = int(sys.argv[2]) if len(sys.argv) > 2 else {"pura": 142, "nacl25": 124}[MEDIO]
CORR = {"pura": "150000N-500MeV-Sidelnik-H2O-pura-sinSab-20261012-061022", "nacl25": "42649N-parcial-500MeV-Sidelnik-H2O-2.5NaCl-sinSab-20261013"}
CARP = os.path.join(os.environ.get("CORRIDAS_SIDELNIK", ""), CORR[MEDIO])
CARP = os.path.join(CARP, "Datos-simulacion") if os.path.isdir(os.path.join(CARP, "Datos-simulacion")) else CARP
FJ = os.path.join(RES, f"evento_ejemplo_{MEDIO}.json")
AGUA = {"pura": "agua pura", "nacl25": "agua + 2,5 % NaCl"}[MEDIO]
if os.path.isdir(CARP):
    ev = {"run": RUN, "medio": MEDIO}
    for f, cl in [("pasos-neutrones.tsv", "n"), ("pasos-gamma.tsv", "g"), ("pasos-electrones.tsv", "e")]:
        hdr = open(os.path.join(CARP, f)).readline().lstrip("# ").rstrip("\n").split("\t")
        out = []
        for d in pd.read_csv(os.path.join(CARP, f), sep="\t", skiprows=1, header=None, names=hdr, chunksize=500000,
                             usecols=["run_id", "particle", "track_id", "parent_id", "step_number", "creator_process", "step_process",
                                      "pre_x_cm", "pre_z_cm", "post_x_cm", "post_z_cm", "pre_energy_MeV"]):
            out.append(d[d.run_id == RUN])
            if d.run_id.min() > RUN:
                break
        d = pd.concat(out).sort_values(["track_id", "step_number"])
        if cl == "e":                               # trazas de e+- que nacen sobre el umbral Cherenkov (~0,26 MeV)
            E0 = d[d.step_number == 1].set_index("track_id").pre_energy_MeV
            d = d[d.track_id.isin(E0[E0 > 0.3].index)]
        ev[cl] = [{"trk": int(t), "cre": str(g.creator_process.iloc[0]), "E0": float(g.pre_energy_MeV.iloc[0]), "padre": int(g.parent_id.iloc[0]),
                   "fin": str(g.step_process.iloc[-1]),
                   "x": [float(g.pre_x_cm.iloc[0])] + g.post_x_cm.round(2).tolist(), "z": [float(g.pre_z_cm.iloc[0])] + g.post_z_cm.round(2).tolist()}
                  for t, g in d.groupby("track_id")]
    json.dump(ev, open(FJ, "w"))
if not os.path.exists(FJ):
    raise SystemExit(f"Falta {FJ}: conecte el disco con las corridas (variable CORRIDAS_SIDELNIK) para extraer el evento {RUN} de {MEDIO}.")
ev = json.load(open(FJ))
estilo.aplicar(**{"axes.grid": False})
fig, ax = plt.subplots(figsize=(8, 8.6))
Rw, H, TY, AC = 48.0, 133.0, 0.012, 0.05; E = 1.2        # paredes exageradas x E para que se vean
z0 = AC                                                 # fondo del agua
ax.add_patch(Rectangle((-Rw - (TY + AC) * 20, z0 - AC * 20), 2 * Rw + 2 * (TY + AC) * 20, H + 2 * AC * 20 + TY * 20, fc="#8a8984", ec="none"))
ax.add_patch(Rectangle((-Rw - TY * 40, z0), 2 * Rw + 2 * TY * 40, H + TY * 40, fc="#f2f2ee", ec="none"))
ax.add_patch(Rectangle((-Rw, z0), 2 * Rw, H, fc="#d6eef8" if MEDIO == "pura" else "#d9f0e0", ec="none"))
ax.add_patch(Rectangle((-5.08, z0 + H - 5.0), 10.16, 5.0, fc="#7cc58f", ec="#2e7d32", lw=1))
ax.plot([-60, 60], [z0 - AC * 20 - 0.6] * 2, color="#c75000", lw=5, solid_capstyle="butt")
# evento: capturas clasificadas por los gammas que emiten (un gamma de ~2,224 MeV = H; cascada = Cl)
COLH, COLCL, COLE = "#2a78d6", "#d62728", "#7b1fa2"
gpad = {}
for t in ev["g"]:
    if t["cre"] == "nCapture":
        gpad.setdefault(t["padre"], []).append(t)
capt = []
for t in ev["n"]:
    if t["fin"] == "nCapture":
        gs = gpad.get(t["trk"], []); es = sorted([g["E0"] for g in gs], reverse=True)
        tipo = "H" if len(es) == 1 and abs(es[0] - 2.2244) < 0.01 else "Cl"
        capt.append({"x": t["x"][-1], "z": t["z"][-1], "tipo": tipo, "E": es, "trk": t["trk"]})
colg = {g["trk"]: (COLH if c["tipo"] == "H" else COLCL) for c in capt for g in gpad.get(c["trk"], [])}


def dibujar(a, lw=1.0):
    for t in ev["n"]:
        prim = t["trk"] == 1
        a.plot(t["x"], t["z"], "-", color="#0b0b0b" if prim else "#5b5a57", lw=(1.6 if prim else 0.8) * lw, zorder=4)
    for t in ev["g"]:
        cap = t["cre"] == "nCapture"
        a.plot(t["x"], t["z"], "--" if cap else ":", color=colg.get(t["trk"], "#eda100"), lw=(1.6 if cap else 0.8) * lw, zorder=5)
    for t in ev["e"]:
        a.plot(t["x"], t["z"], "-", color=COLE, lw=2.2 * lw, zorder=5, solid_capstyle="round")
    for c in capt:
        a.plot(c["x"], c["z"], "o", color=COLH if c["tipo"] == "H" else COLCL, ms=8, zorder=6, mec="white", mew=0.8)


dibujar(ax)
x0, zf = ev["n"][0]["x"][0], ev["n"][0]["z"][0]
ax.add_patch(FancyArrowPatch((x0 - 14, zf), (x0 - 0.5, zf), arrowstyle="-|>", mutation_scale=16, color="#0b0b0b", lw=1.8))
fs = 10.5
ax.annotate("Neutrón incidente\n500 MeV (fuente a 1 cm\nde la pared, media altura)", (x0 - 8, zf), (-73, 30), fontsize=fs, ha="center",
            arrowprops=dict(arrowstyle="-", color="#555555", lw=0.8))
ax.annotate("PMT 10,16 × 10,16 × 5 cm\n(en la tapa)", (0, z0 + H - 2.5), (25, 152), fontsize=fs, ha="left", arrowprops=dict(arrowstyle="-", color="#555555", lw=0.8))
ax.annotate("Tyvek 0,12 mm", (Rw + 0.3, 115), (58, 125), fontsize=fs, arrowprops=dict(arrowstyle="-", color="#555555", lw=0.8))
ax.annotate("Acero inoxidable 0,5 mm", (Rw + 1.6, 100), (58, 110), fontsize=fs, arrowprops=dict(arrowstyle="-", color="#555555", lw=0.8))
ax.text(10, 8, f"Volumen activo: {AGUA}\n(R = 48 cm, H = 133 cm)", ha="center", fontsize=fs, color="#1f4e79", bbox=dict(fc="white", ec="none", alpha=0.75, pad=1.5))
for k, c in enumerate(sorted(capt, key=lambda c: c["tipo"])):
    if c["tipo"] == "H":
        txt, col = "Captura n + $^1$H → d + γ\n(2224 keV)", COLH
    else:
        txt = "Captura n + $^{35}$Cl → $^{36}$Cl + cascada γ:\n" + " + ".join(f"{e * 1e3:.0f}" for e in c["E"]) + f" keV = {sum(c['E']):.3f} MeV".replace(".", ",")
        col = COLCL
    ax.annotate(txt, (c["x"], c["z"]), ((-93, 141) if c["tipo"] == "Cl" else (-44, 42)), fontsize=fs, color=col, ha="left", bbox=dict(fc="white", ec="none", alpha=0.8, pad=1.5),
                arrowprops=dict(arrowstyle="-", color=col, lw=0.8))
# ampliacion de la zona de moderacion y capturas
ins = ax.inset_axes([0.58, 0.16, 0.36, 0.36])
dibujar(ins, 1.0)
xs_ = [c["x"] for c in capt] + [x0 + 2]; zs_ = [c["z"] for c in capt]
xm, zm = (min(xs_) + max(xs_)) / 2, (min(zs_) + max(zs_)) / 2; dx = max(max(xs_) - min(xs_), max(zs_) - min(zs_)) / 2 + 5
for c in capt:
    for g in gpad.get(c["trk"], []):
        k = min(len(g["x"]) - 1, 1)
        xe, ze = np.clip(g["x"][k], xm - dx * 0.85, xm + dx * 0.85), np.clip(g["z"][k], zm - dx * 0.85, zm + dx * 0.85)
        ins.text(xe, ze, f"{g['E0'] * 1e3:.0f}", fontsize=9, color=COLH if c["tipo"] == "H" else COLCL, ha="center", va="center",
                 bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.6))
ins.set_xlim(xm - dx, xm + dx); ins.set_ylim(zm - dx, zm + dx); ins.set_aspect("equal")
ins.set_facecolor("#d6eef8" if MEDIO == "pura" else "#d9f0e0"); ins.set_xticks([]); ins.set_yticks([])
ins.set_title(f"ampliación ({2 * dx:.0f} cm de lado; γ en keV)", fontsize=9)
for sp in ins.spines.values():
    sp.set_visible(True); sp.set_color("#555555")
ax.indicate_inset_zoom(ins, edgecolor="#555555", lw=0.8)
from matplotlib.lines import Line2D
h = [Line2D([], [], color="#0b0b0b", lw=1.6, label="neutrón primario"), Line2D([], [], color="#5b5a57", lw=0.8, label="neutrones secundarios (moderación)"),
     Line2D([], [], color=COLH, ls="--", lw=1.6, label="captura en H y su γ"), Line2D([], [], color=COLCL, ls="--", lw=1.6, label="captura en $^{35}$Cl y su cascada γ"), Line2D([], [], color="#eda100", ls=":", lw=1, label="otros γ"),
     Line2D([], [], color=COLE, lw=2, label="e$^\\pm$ sobre el umbral Cherenkov (recorren mm)")]
ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=9.5, frameon=False)
ax.set_xlim(-95, 95); ax.set_ylim(-6, 165); ax.set_aspect("equal"); ax.axis("off")
ax.set_title(f"WCD de la réplica de Sidelnik en MEIGA (corte y = 0, a escala; paredes exageradas)\nevento real de {AGUA}: run {ev['run']}, proyección x–z", fontsize=10.5)
fig.tight_layout()
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig00_esquema_detector{'' if MEDIO == 'nacl25' else '_' + MEDIO}.{e}"))
print("n trazas", len(ev["n"]), "g", len(ev["g"]), "e", len(ev["e"]))
