#!/usr/bin/env python3
"""
Esquemas del montaje simulado en Geant4/MEIGA (vista lateral x-z, sin escala en los neutrones):
  fig19: el mundo de aire y el suelo SoilBS seco (20 x 20 x 1 m) con su composición másica;
  fig20: el mismo montaje con 30 % de agua (composición de la mezcla) y los espectros que bajan y suben;
  fig21: el WCD sobre el suelo húmedo, con los neutrones que entran por la tapa, la base y el costado.
Dimensiones: parche agregar_suelo.py y ejecutar_suelo.sh (MEIGA_SUELO_XY=20, MEIGA_SUELO_Z=1, mundo 20.5 x 20.5 x 6 m);
entrada y plano contador de generar_incidencia_suelo.py; tasas al tanque de flujos/entrada_tanque.json y
curva_calibracion_tanque.json. Colores: el flujo que baja en gris y el que sube con 30 % en oliva, como en las figuras
de espectros; ninguno de los colores de los medios.
"""
import csv, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
REPO = os.environ.get("REPO_TESIS", os.path.abspath(os.path.join(BASE, "..", "..")))
SOIL = [("O", 0.4900), ("Si", 0.3300), ("Al", 0.0713), ("Fe", 0.0380), ("C", 0.0200), ("Ca", 0.0137), ("K", 0.0136),
        ("Na", 0.0063), ("Mg", 0.0060), ("Ti", 0.0046), ("H", 0.0038), ("N", 0.0010), ("P", 0.0009), ("S", 0.0008)]
W = 0.30
H_AGUA, O_AGUA = 2 * 1.008 / 18.015, 15.999 / 18.015
RHO = lambda w: 1 / (w / 1.0 + (1 - w) / 2.7)
AIRE, SECO, HUMEDO, AGUA_T = "#e9f2fa", "#d9b98c", "#8c6d4f", "#bfe0f5"
BAJA_C, SUBE_C = "#6b6a66", "#bcbd22"

def mezcla(w):
    m = {e: (1 - w) * f for e, f in SOIL}
    m["H"] += w * H_AGUA; m["O"] += w * O_AGUA
    return sorted(m.items(), key=lambda t: -t[1])

def barras(ax, comp, titulo, resaltar=("H", "O")):
    nom = [e for e, _ in comp]; v = [100 * f for _, f in comp]
    col = ["#1f77d4" if e in resaltar else "#8c8c8c" for e in nom]
    y = np.arange(len(nom))[::-1]
    ax.barh(y, v, color=col, height=0.7)
    for yi, vi in zip(y, v): ax.text(vi + 0.6, yi, f"{vi:.2f} %" if vi >= 0.1 else f"{vi:.3f} %", va="center", fontsize=8)
    ax.set_yticks(y); ax.set_yticklabels(nom, fontsize=9); ax.set_xlim(0, 75); ax.set_xlabel("Fracción másica [%]", fontsize=9)
    ax.set_title(titulo, fontsize=10); ax.tick_params(axis="x", labelsize=8)
    for s_ in ("top", "right"): ax.spines[s_].set_visible(False)

def flecha(ax, x0, y0, x1, y1, c, lw=1.6, ms=12):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms, color=c, lw=lw))

def mundo(ax, suelo_col, etq_suelo):
    """Vista lateral del mundo de Geant4: aire 20.5 m x 6 m (z de -3 a 3 m) y suelo de 20 m x 1 m bajo z = 0."""
    ax.add_patch(Rectangle((-10.25, -3), 20.5, 6, fc=AIRE, ec="k", lw=1.2))
    ax.add_patch(Rectangle((-10, -1), 20, 1, fc=suelo_col, ec="k", lw=1.0))
    ax.text(0, -0.5, etq_suelo, ha="center", va="center", fontsize=9.5, color="white" if suelo_col == HUMEDO else "k", weight="bold")
    ax.text(-10.0, 2.75, "Mundo de Geant4 (aire, G4_AIR): 20.5 × 20.5 × 6 m", fontsize=9, va="top")
    ax.text(-10.0, -2.75, "aire", fontsize=8.5, color="0.35", va="bottom")
    # región de inyección y plano contador (exagerados en altura para que se vean)
    ax.plot([-8.5, 8.5], [0.32, 0.32], color="#1b2a6b", lw=2.2)
    caja = dict(fc="white", ec="none", alpha=0.85, pad=1.5)
    ax.text(-9.9, 1.0, "inyección: 200 000 neutrones que bajan,\nuniformes en 17 × 17 m, a 6 cm del suelo", fontsize=8,
            color="#1b2a6b", va="center", bbox=caja)
    ax.plot([-10, 10], [0.16, 0.16], color="#17becf", lw=1.4, ls="--")
    ax.text(9.9, 0.62, "plano contador a 5 cm\n(cruces hacia abajo y hacia arriba)", ha="right", va="center", fontsize=8,
            color="#0f7f8a", bbox=caja)
    # cotas
    ax.annotate("", (-10, -1.25), (10, -1.25), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(0, -1.33, "20 m", ha="center", va="top", fontsize=8)
    ax.annotate("", (10.45, 0), (10.45, -1), arrowprops=dict(arrowstyle="<->", lw=0.8)); ax.text(10.55, -0.5, "1 m", va="center", fontsize=8)
    ax.text(-10.4, 0, "z = 0", ha="right", va="center", fontsize=8)
    ax.set_xlim(-11.2, 11.6); ax.set_ylim(-3.1, 3.1); ax.set_aspect("auto"); ax.axis("off")

def guardar(fig, nombre):
    for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"{nombre}.{e}"), dpi=170, bbox_inches="tight")
    plt.close(fig)

# --- esquema 1: suelo seco ---
fig = plt.figure(figsize=(13.5, 5.2)); gs = fig.add_gridspec(1, 2, width_ratios=[3.1, 1])
ax = fig.add_subplot(gs[0]); mundo(ax, SECO, "Suelo SoilBS seco, ρ = 2.70 g/cm³ (14 elementos)")
rng = np.random.default_rng(3)
for x in np.linspace(-7.5, 7.5, 7):
    dx = rng.uniform(-0.9, 0.9); flecha(ax, x - dx, 2.2, x, 0.36, BAJA_C)
ax.text(-4.2, 2.35, "neutrones atmosféricos que bajan (all_bga_neutron_35.shw)", fontsize=8.5, color=BAJA_C)
for x in (-6, -2.5, 1.5, 5.5): flecha(ax, x, 0.02, x + rng.uniform(-1, 1), 1.5, "k", lw=1.2, ms=10)
ax.text(7.9, 1.55, "neutrones que suben\n(reflejados o creados\nen el suelo)", fontsize=8, va="center", bbox=dict(fc="white", ec="none", alpha=0.85))
ax.set_title("Esquema 1. Montaje de MEIGA para el albedo: aire y suelo seco", fontsize=11)
barras(fig.add_subplot(gs[1]), sorted(SOIL, key=lambda t: -t[1]), "Composición del suelo seco (SoilBS)")
fig.tight_layout(); guardar(fig, "fig19_esquema_suelo_seco")

# --- esquema 2: suelo con 30 % de agua y espectros ---
f = list(csv.reader(open(os.path.join(RES, "espectros_albedo.tsv")), delimiter="\t")); cab, dat = f[0], np.array(f[1:], float)
B = np.concatenate([dat[:, 0], dat[-1:, 1]]); col = {c: dat[:, i] for i, c in enumerate(cab) if i >= 2}
baja = next(c for c in col if c.startswith("Baja")); sube30 = next(c for c in col if "humedo-30" in c)
seco_m = next(c for c in col if "seco" in c and "MEIGA" in c)
J = json.load(open(os.path.join(RES, "albedo_suelo.json")))
J30 = next(v["J_sube_n_m2_s"] for k, v in J["corridas"].items() if "humedo-30" in k)
J0 = next(v["J_sube_n_m2_s"] for k, v in J["corridas"].items() if k.startswith("seco"))
fig = plt.figure(figsize=(13.5, 9.2)); gs = fig.add_gridspec(2, 2, width_ratios=[3.1, 1], height_ratios=[1.05, 1])
ax = fig.add_subplot(gs[0, 0])
mundo(ax, HUMEDO, f"SoilBS + 30 % de agua en masa, ρ = {RHO(W):.2f} g/cm³ (θ$_g$ = {W / (1 - W):.2f}, θ$_v$ = {W * RHO(W):.2f})")
for x in np.linspace(-7.5, 7.5, 7):
    dx = rng.uniform(-0.9, 0.9); flecha(ax, x - dx, 2.2, x, 0.36, BAJA_C)
ax.text(-4.2, 2.35, f"bajan: J$_\\downarrow$ = {J['J_baja_tesis_n_m2_s']:.1f} n m$^{{-2}}$ s$^{{-1}}$", fontsize=9, color=BAJA_C)
for x in (-6, -2.5, 1.5, 5.5): flecha(ax, x, 0.02, x + rng.uniform(-1, 1), 1.5, SUBE_C, lw=1.6, ms=11)
ax.text(7.3, 1.55, f"suben: J$_\\uparrow$ = {J30:.0f} n m$^{{-2}}$ s$^{{-1}}$\n(seco: {J0:.0f})", fontsize=9, va="center", color="#7a7b10", bbox=dict(fc="white", ec="none", alpha=0.85))
ax.set_title("Esquema 2. El mismo montaje con 30 % de humedad", fontsize=11)
barras(fig.add_subplot(gs[0, 1]), mezcla(W), "Composición del suelo con 30 % de agua")
ax = fig.add_subplot(gs[1, :])
REG = [("Fríos", 2e-10, 1e-8), ("Térmicos", 1e-8, 1e-7), ("Epitérmicos", 1e-7, 1e-6), ("Intermedios", 1e-6, 1e-2),
       ("Rápidos", 1e-2, 20), ("Alta energía", 20, 1e4)]
for k, (n, a, b) in enumerate(REG):
    ax.axvspan(max(a, 1e-10), b, color=("#f4f4f4" if k % 2 else "#ffffff"), zorder=0)
    ax.text(np.sqrt(max(a, 1e-10) * b), 0.97, n, ha="center", va="top", fontsize=8.5, color="0.35", transform=ax.get_xaxis_transform())
    if k: ax.axvline(a, color="0.75", lw=0.8, ls=":")
ax.stairs(np.clip(col[baja], 1e-4, None), B, color=BAJA_C, lw=1.8, label="bajan al suelo (entrada, tesis)")
ax.stairs(np.clip(col[seco_m], 1e-4, None), B, color="k", lw=1.4, ls="--", label="suben del suelo seco (MEIGA)")
ax.stairs(np.clip(col[sube30], 1e-4, None), B, color=SUBE_C, lw=2.2, label="suben del suelo con 30 % de agua (MEIGA)")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1e-10, 1e4); ax.set_ylim(1e-1, 2e3)
ax.set_xlabel("Energía cinética $E_n$ [MeV]"); ax.set_ylabel(r"$E\,d\Phi/dE$ [n m$^{-2}$ s$^{-1}$]")
ax.set_title("Espectros en el plano contador (5 cm sobre el suelo)", fontsize=10); ax.grid(alpha=0.25, ls=":", which="both")
ax.legend(fontsize=9, loc="lower center", ncol=3)
fig.tight_layout(); guardar(fig, "fig20_esquema_suelo_humedo_espectros")

# --- esquema 3: el WCD sobre el suelo húmedo ---
e = json.load(open(os.path.join(REPO, "simulations", "tanque-albedo", "flujos", "entrada_tanque.json")))["suelos"]
from normalizacion import J_BAJA_ANTES_N_M2_S
ESC = json.load(open(os.path.join(RES, "albedo_suelo.json")))["J_baja_tesis_n_m2_s"] / J_BAJA_ANTES_N_M2_S
for _v in e.values():
    for _k in ("tasa_base_n_s", "tasa_costado_n_s", "tasa_al_tanque_n_s"): _v[_k] *= ESC
T = json.load(open(os.path.join(RES, "curva_calibracion_tanque.json")))
tb, tc = T["tasa_baja_tapa_n_s"], T["tasa_baja_costado_n_s_por_corte"]["85"]
s30, s0 = e["agua30"], e["seco"]
fig = plt.figure(figsize=(13.5, 7.6)); ax = fig.add_axes([0.02, 0.03, 0.96, 0.9])
ax.add_patch(Rectangle((-5.2, -1.1), 10.4, 6.2, fc=AIRE, ec="k", lw=1.2))
ax.add_patch(Rectangle((-5.0, -1.0), 10.0, 1.0, fc=HUMEDO, ec="k"))
ax.text(-4.85, -0.5, "suelo SoilBS con 30 % de agua", color="white", fontsize=9.5, va="center", weight="bold")
# tanque (unidades: m; radio 0.48 m, agua 1.33 m, base 2 m sobre el suelo)
R, Hw, z0 = 0.48, 1.33, 2.0
ax.add_patch(Rectangle((-R - 0.012, z0 - 0.012), 2 * R + 0.024, Hw + 0.024, fc="#9aa3ad", ec="k", lw=1.2))   # acero (exagerado)
ax.add_patch(Rectangle((-R, z0), 2 * R, Hw, fc=AGUA_T, ec="#3b6ea8", lw=0.8))
zp = z0 + Hw / 2 + 0.3 * Hw / 2
ax.add_patch(matplotlib.patches.Wedge((0, zp), 0.12, 180, 360, fc="#f2c94c", ec="k", lw=0.8))
ax.plot([-0.12, 0.12], [zp, zp], color="k", lw=0.8)
ax.annotate("PMT de Sidelnik a 0.3·H/2, mirando hacia abajo\n(46.55 cm bajo la tapa)", (0.1, zp - 0.06), (1.05, zp + 0.55), fontsize=8.5,
            arrowprops=dict(arrowstyle="-", lw=0.7))
ax.annotate("agua pura o con NaCl\nR = 48 cm, H = 133 cm\nTyvek 0.12 mm, acero 0.5 mm", (-0.2, z0 + 0.35), (-3.6, z0 + 0.1),
            fontsize=8.5, arrowprops=dict(arrowstyle="-", lw=0.7))
ax.annotate("", (-1.0, 0), (-1.0, z0), arrowprops=dict(arrowstyle="<->", lw=0.8)); ax.text(-1.08, z0 / 2, "2 m de aire\n(≈ 0.24 g/cm²)", fontsize=8.5, va="center", ha="right")
# neutrones que bajan: tapa y costado
for x in (-0.3, 0.0, 0.3): flecha(ax, x - 0.15, 4.75, x, z0 + Hw + 0.05, BAJA_C)
for zz in (2.5, 3.1): flecha(ax, -1.7, zz + 0.7, -R - 0.03, zz, BAJA_C)
ax.text(-2.4, 4.85, f"bajan: por la tapa {tb:.0f} n/s, por el costado {tc:.0f} n/s", fontsize=9, color=BAJA_C)
# neutrones que suben: base y costado
for x in (-0.3, 0.05, 0.35): flecha(ax, x + 0.2, 0.08, x, z0 - 0.04, SUBE_C, ms=11)
for zz in (2.3, 2.9, 3.0): flecha(ax, 1.6 + 0.3 * (zz - 2.3), zz - 0.9, R + 0.03, zz, SUBE_C, ms=11)
ax.text(0.7, 0.3, f"suben (30 %): por la base {s30['tasa_base_n_s']:.0f} n/s, por el costado {s30['tasa_costado_n_s']:.0f} n/s\n"
        f"(suelo seco: {s0['tasa_base_n_s']:.0f} y {s0['tasa_costado_n_s']:.0f} n/s; el 71 % entra por el costado)", fontsize=8.5, color="#7a7b10")
ax.text(-5.05, 5.0, "Mundo de Geant4 (aire)", fontsize=9, va="top")
ax.text(2.25, 4.75, "En la simulación directa el suelo no está en la\ngeometría: los neutrones que suben se toman de\n"
        "las corridas del suelo (energía y dirección) y\nse inyectan 1 mm fuera de la base y del costado.\n"
        "Los rasantes (θ > 85°) se cortan.", fontsize=8.2, va="top", color="0.25",
        bbox=dict(fc="white", ec="0.7", boxstyle="round,pad=0.4"))
ax.set_xlim(-5.4, 5.4); ax.set_ylim(-1.2, 5.2); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Esquema 3. El WCD sobre el suelo húmedo: neutrones que entran por la tapa, la base y el costado", fontsize=11)
guardar(fig, "fig21_esquema_tanque_suelo")
print("esquemas 19-21 listos; suelo húmedo:", ", ".join(f"{e_} {100 * f_:.2f}" for e_, f_ in mezcla(W)[:5]))
