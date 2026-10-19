#!/usr/bin/env python3
"""Esquema de la cinematica de la dispersion elastica n + (A,Z) en el laboratorio, para explicar la Fig. 21:
(a) colision con H: el neutron no puede retroceder (theta + phi = 90 grados);
(b) colision con 16O: el neutron puede salir en cualquier direccion y pierde poca energia;
(c) diagrama de velocidades: la velocidad final en el laboratorio es V_CM + u' (u' sobre un circulo);
    para el H el circulo pasa por el origen (theta_lab <= 90 grados), para el O lo encierra (todas las direcciones);
(d) energia final uniforme entre alpha*E y E (dispersion isotropa en el CM);
(e) distribucion de cos(theta_lab) a baja energia: teoria frente a MEIGA;
(f) por encima de 20 MeV la dispersion es frontal (MEIGA).
Lee resultados/elasticas_pura.npz (elasticas_vertices.py) si existe. Escribe figuras/fig23_esquema_cinematica_elastica."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Wedge
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FIG = os.path.join(R, "figuras")
A_H, A_O = 1.0, 15.86                     # masas en unidades de la masa del neutron
CH, CO, CN = "#2a78d6", "#d62728", "#0b0b0b"
alfa = lambda A: ((A - 1) / (A + 1)) ** 2


def flecha(ax, x0, y0, x1, y1, col, lw=2.2, ls="-", ms=16):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms, color=col, lw=lw, ls=ls, shrinkA=0, shrinkB=0))


def final_lab(A, th):
    """velocidad final del neutron (unidades de la inicial) para un angulo de laboratorio th"""
    return (np.cos(th) + np.sqrt(A ** 2 - np.sin(th) ** 2)) / (A + 1)


def colision(ax, A, th_deg, nombre, col, Etxt):
    th = np.radians(th_deg); v1 = final_lab(A, th)
    pn = np.array([v1 * np.cos(th), v1 * np.sin(th)]); pR = np.array([1.0, 0.0]) - pn   # impulso del nucleo (unidades m_n v)
    vR = pR / A
    flecha(ax, -1.25, 0, -0.18, 0, CN); ax.text(-0.75, -0.08, "neutrón\nincidente, $E$", ha="center", va="top", fontsize=11)
    ax.add_patch(Circle((0, 0), 0.07 + 0.025 * np.log(A + 1), color=col, zorder=3))
    flecha(ax, 0, 0, 1.1 * pn[0], 1.1 * pn[1], CN)
    ax.text(1.1 * pn[0] + (0.05 if pn[0] >= 0 else -0.05), 1.1 * pn[1] + 0.06, f"neutrón dispersado\n$E' = {v1 ** 2:.2f}\\,E$".replace(".", ","),
            ha="left" if pn[0] >= 0 else "right", va="bottom", fontsize=11)
    esc = 1.1 if A < 2 else 3.0
    flecha(ax, 0, 0, esc * vR[0], esc * vR[1], col, ls="--")
    ax.text(esc * vR[0] + 0.06, esc * vR[1] - 0.04, "núcleo de\nretroceso" + ("" if A < 2 else "\n(velocidad × 3)"), ha="left", va="top", fontsize=10.5, color=col)
    ax.add_patch(Wedge((0, 0), 0.32, 0, th_deg, color="#8a8984", alpha=0.35)); ax.text(0.36 * np.cos(th / 2), 0.36 * np.sin(th / 2), "θ", fontsize=12)
    ax.axhline(0, color="#c3c2b7", lw=0.8, ls=":")
    ax.set_title(nombre + "\n" + Etxt, fontsize=12.5)
    ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.0, 1.25); ax.set_aspect("equal"); ax.axis("off")


estilo.aplicar()
fig, axs = plt.subplots(2, 3, figsize=(12, 8.8))
# (a) H
a = axs[0, 0]
a.add_patch(Wedge((0, 0), 1.2, 90, 270, color="#e34948", alpha=0.08)); a.text(-1.3, 1.05, "hemisferio prohibido\npara el neutrón", fontsize=10.5, color="#a32826", va="top")
colision(a, A_H, 40, "(a) Colisión con $^{1}$H (masa ≈ neutrón)", CH, "salen perpendiculares; θ ≤ 90°")
# (b) O
colision(axs[0, 1], A_O, 120, "(b) Colisión con $^{16}$O (masa ≈ 16 n)", CO, "puede rebotar; conserva ≥ 78 % de E")
# (c) diagrama de velocidades
a = axs[0, 2]
for A, col, y0, nom in [(A_H, CH, 0.55, "$^{1}$H"), (A_O, CO, -0.75, "$^{16}$O")]:
    V = 1 / (A + 1); u = A / (A + 1)
    a.add_patch(Circle((V, y0), u, fill=False, color=col, lw=1.8))
    flecha(a, 0, y0, V, y0, CN, lw=1.8, ms=12); a.text(V / 2 if A < 2 else 0.12, y0 + 0.04 if A < 2 else y0 - 0.06, "$V_{CM}$", ha="center" if A < 2 else "left", va="bottom" if A < 2 else "top", fontsize=10.5)
    t = np.radians(125); pt = (V + u * np.cos(t), y0 + u * np.sin(t))
    flecha(a, V, y0, *pt, col, lw=1.5, ms=11); flecha(a, 0, y0, *pt, "#555555", lw=1.5, ls=":", ms=11)
    a.plot(0, y0, "o", color=CN, ms=4)
    a.text(V + u + 0.03, y0, nom, color=col, fontsize=12, va="center")
a.text(-0.08, 0.75, "origen sobre\nel círculo:\nθ$_{lab}$ ≤ 90°", fontsize=10.5, color=CH, ha="right", va="center")
a.text(-0.95, -1.85, "origen dentro del círculo:\ncualquier dirección", fontsize=10.5, color=CO, va="center")
a.set_title("(c) Velocidades: $\\vec v\\,'_{lab} = \\vec V_{CM} + \\vec u\\,'$\n($\\vec u\\,'$ isótropa en el CM)", fontsize=12.5)
a.set_xlim(-1.0, 1.3); a.set_ylim(-2.05, 1.15); a.set_aspect("equal"); a.axis("off")
# (d) energia final uniforme
a = axs[1, 0]
for A, col, nom in [(A_H, CH, "$^{1}$H: α = 0"), (A_O, CO, "$^{16}$O: α = 0,777")]:
    al = alfa(A); h = 1 / (1 - al)
    a.fill_between([al, 1], 0, h, color=col, alpha=0.25, step="pre"); a.plot([al, al, 1, 1], [0, h, h, 0], color=col, lw=2, label=nom)
a.set_yscale("log"); a.set_ylim(0.3, 20); a.set_xlim(0, 1.02)
a.set_xlabel("Energía final del neutrón E'/E"); a.set_ylabel("Densidad de probabilidad")
a.annotate("pérdida máxima 22 %", xy=(0.777, 4.48), xytext=(0.22, 5.6), fontsize=10.5, color=CO, arrowprops=dict(arrowstyle="->", color=CO))
a.annotate("puede perder\ntoda su energía", xy=(0.02, 1), xytext=(0.12, 0.45), fontsize=10.5, color=CH, arrowprops=dict(arrowstyle="->", color=CH))
a.legend(loc="upper left"); a.set_title("(d) E' uniforme entre αE y E", fontsize=12.5)
# (e) y (f): cos(theta_lab)
f_ = os.path.join(R, "resultados", "elasticas_pura.npz")
Z = np.load(f_, allow_pickle=True) if os.path.exists(f_) else None
cb = np.linspace(-1, 1, 81); cc = 0.5 * (cb[1:] + cb[:-1])
rng = np.random.default_rng(1)
for A, col, nom in [(A_H, CH, "H"), (A_O, CO, "$^{16}$O")]:
    ccm = rng.uniform(-1, 1, 400000)                     # isotropo en el CM
    cl = (1 + A * ccm) / np.sqrt(A ** 2 + 2 * A * ccm + 1)
    h, _ = np.histogram(cl, cb, density=True)
    axs[1, 1].plot(cc, h, "-", color=col, lw=2, label=f"{nom}: teoría (⟨cos θ⟩ = {2 / (3 * A):.2f})".replace(".", ","))
    if Z is not None:
        for (lo, hi, a) in [(1e-3, 1, axs[1, 1]), (20, 600, axs[1, 2])]:
            s = (Z["Ein"] > lo) & (Z["Ein"] < hi) & (Z["blanco_cin"] == ("H" if A < 2 else "O"))
            hm, _ = np.histogram(Z["cos_lab"][s], cb, density=True)
            a.step(cc, hm, where="mid", color=col, lw=1.2, ls="--", label=f"{nom}: MEIGA" + (" (1 keV–1 MeV)" if hi == 1 else " (> 20 MeV)"))
    axs[1, 2].plot(cc, h, "-", color=col, lw=1.2, alpha=0.5, label=f"{nom}: isótropo en el CM")
a = axs[1, 1]; a.set_xlabel("cos θ$_{lab}$ del neutrón"); a.set_ylabel("Densidad"); a.set_ylim(0, 2.3); a.text(0.5, 2.05, "H: ⟨cos θ⟩ = 0,67", color=CH, ha="center", fontsize=11); a.text(-0.55, 0.62, "$^{16}$O: ⟨cos θ⟩ = 0,04", color=CO, ha="center", fontsize=11)
a.set_title("(e) Ángulo a baja energía\n(isótropo en el CM)", fontsize=12.5)
a = axs[1, 2]; a.set_yscale("log"); a.set_ylim(1e-4, 100); a.set_xlabel("cos θ$_{lab}$ del neutrón"); a.set_ylabel("Densidad")
a.set_title("(f) Por encima de 20 MeV: el $^{16}$O\ndispersa hacia adelante (difracción)", fontsize=12.5)
from matplotlib.lines import Line2D
H_ = [Line2D([], [], color=CH, lw=2, label="$^{1}$H"), Line2D([], [], color=CO, lw=2, label="$^{16}$O"),
      Line2D([], [], color="#555555", lw=2, label="teoría: dispersión isótropa en el CM"),
      Line2D([], [], color="#555555", lw=1.2, ls="--", label="MEIGA: (e) 1 keV–1 MeV; (f) > 20 MeV")]
fig.legend(handles=H_, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.0), columnspacing=1.5)
fig.tight_layout(rect=(0, 0.05, 1, 1))
for e in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig23_esquema_cinematica_elastica.{e}"))
print("ok")
