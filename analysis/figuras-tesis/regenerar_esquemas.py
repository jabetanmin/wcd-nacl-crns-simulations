"""Rehace con Matplotlib los esquemas de la tesis que eran imágenes generadas.

  fig_esquema_arti            cadena de simulación de ARTI (Sarmiento-Cano et al. 2022)
  fig_contador_he3            contador proporcional de 3He: espectro digitalizado, tubo y cadena electrónica
  fig_modelo_suelo            geometría del modelo de suelo en Geant4
  fig_procesos_neutron        clasificación de las interacciones de los neutrones
  fig_trayectorias_tanque     trayectorias simuladas de neutrones en el WCD (datos de la Campaña 1)

Uso: python3 regenerar_esquemas.py <salida>
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch, Rectangle, Circle

SAL = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
AQUI = Path(__file__).resolve().parent
MALLA = Path(os.environ.get("DATOS_NEUTRONES_TERMICOS", "datos/Neutrones-termicos"))
plt.rcParams.update({"font.size": 11, "savefig.bbox": "tight"})


def guardar(fig, nombre):
    fig.savefig(SAL / f"{nombre}.pdf")
    fig.savefig(SAL / f"{nombre}.png", dpi=300)
    plt.close(fig)


def caja(ax, x, y, w, h, texto, fc, ec, fs=10, peso="normal", color="k", r=0.02):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.005,rounding_size={r}", fc=fc, ec=ec, lw=1.3))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=fs, fontweight=peso, color=color,
            wrap=True)


def flecha(ax, a, b, color="0.25", lw=1.4, estilo="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=estilo, mutation_scale=13, color=color, lw=lw, ls=ls))


# ---------------------------------------------------------------- ARTI
def fig_arti():
    etapas = [("1", "Entrada", "Condiciones iniciales:\nintervalo de energía,\nángulos cenital\ny azimutal, campo\ngeomagnético", "Interfaz Bash", "#d9534f"),
              ("2", "Control", "Archivos de\nconfiguración que\nusa CORSIKA para\npreparar la simulación", "Perl", "#2b5f9e"),
              ("3", "CORSIKA", "Cascadas atmosféricas.\nSalida: archivos binarios\ny de preanálisis", "Fortran y C++", "#f0883e"),
              ("4", "MAGCOS", "Usa la salida de\nCORSIKA para producir\nel flujo corregido\ngeomagnéticamente", "ROOT y C++", "#5a4fa2"),
              ("5", "Geant4", "Respuesta del detector.\nSalida: distribución de\nfotoelectrones e\nhistograma de carga", "C++", "#f2b134")]
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    w = 1.86
    for k, (num, nom, desc, leng, c) in enumerate(etapas):
        x = 0.1 + k * 1.98
        punta = 0.22
        pts = [(x, 2.2), (x + w - punta, 2.2), (x + w, 2.55), (x + w - punta, 2.9), (x, 2.9)]
        if k:
            pts.append((x + punta, 2.55))
        ax.add_patch(Polygon(pts, closed=True, fc=c, ec="white", lw=2))
        ax.add_patch(Circle((x + 0.33, 2.55), 0.2, fc="white", ec=c, lw=1.5))
        ax.text(x + 0.33, 2.55, num, ha="center", va="center", fontsize=11, fontweight="bold", color=c)
        ax.text(x + 1.08, 2.55, nom, ha="center", va="center", fontsize=10.5, fontweight="bold", color="white")
        ax.text(x + w / 2 - 0.05, 3.25, leng, ha="center", va="center", fontsize=10, style="italic", color="0.2")
        caja(ax, x - 0.02, 0.3, w - 0.06, 1.55, desc, "#f4f4f4", c, fs=8.4)
        flecha(ax, (x + w / 2 - 0.05, 2.18), (x + w / 2 - 0.05, 1.87), color=c)
    ax.text(5, 3.95, "Cadena de simulación de ARTI", ha="center", fontsize=13, fontweight="bold")
    guardar(fig, "fig_esquema_arti")


# ---------------------------------------------------------------- contador de 3He
def pulso(ax, t, v, color, titulo, texto, umbral=None):
    ax.plot(t, v, color=color, lw=1.8)
    ax.axhline(0, color="k", lw=0.8)
    if umbral is not None:
        ax.axhline(umbral, color="0.4", ls="--", lw=0.9)
        ax.text(t[-1], umbral + 0.05, "umbral", ha="right", va="bottom", fontsize=8, color="0.3")
    ax.set_title(titulo, fontsize=10.5, color=color, fontweight="bold")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.set_xlabel("tiempo", fontsize=9)
    ax.text(0.5, -0.2, texto, transform=ax.transAxes, ha="center", va="top", fontsize=8.6)


def fig_contador():
    d = np.loadtxt(AQUI / "espectro_he3_digitalizado.tsv")
    x, y = d[:, 0], d[:, 1] / d[:, 1].max()
    fig = plt.figure(figsize=(12, 8.2))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.25, 0.8], hspace=0.45, wspace=0.35)

    ax = fig.add_subplot(gs[0, :2])
    ax.plot(x, y, color="#1f4e9c", lw=1.2)
    for xa, ya, txt, dx, dy in [(1490, 1.0, "absorción total\n(764 keV)", -520, -0.12),
                                (1215, 0.21, "efecto de pared\ndel protón (573 keV)", -620, 0.25),
                                (630, 0.05, "efecto de pared\ndel tritón (191 keV)", -200, 0.28)]:
        ax.annotate(txt, (xa, ya), xytext=(xa + dx, ya + dy), fontsize=9, ha="center",
                    arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=1))
    ax.set_xlim(0, 2000)
    ax.set_ylim(0, 1.08)
    ax.set_xlabel("Altura del pulso [canal]")
    ax.set_ylabel("Cuentas relativas")
    ax.set_title("(a) Espectro de altura de pulsos (digitalizado)", fontsize=11, loc="left")
    ax.grid(True, alpha=0.3)

    ax = fig.add_subplot(gs[0, 2:])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("(b) Tubo proporcional de $^3$He", fontsize=11, loc="left")
    ax.add_patch(FancyBboxPatch((1, 1.6), 7.2, 2.6, boxstyle="round,pad=0.02,rounding_size=1.2", fc="#eef3f8",
                                ec="0.25", lw=1.6))
    ax.plot([0.4, 9.2], [2.9, 2.9], color="0.3", lw=1.4)
    ax.text(0.3, 2.9, "ánodo (+HV)", ha="right", va="center", fontsize=9)
    ax.text(4.6, 1.45, "cátodo: carcasa metálica (tierra)", ha="center", va="top", fontsize=9)
    ax.text(4.6, 3.85, "gas $^3$He", ha="center", fontsize=9.5, color="0.3")
    flecha(ax, (1.8, 5.4), (4.2, 3.1), color="#2b5f9e", ls="--")
    ax.text(1.7, 5.5, "neutrón térmico", ha="center", fontsize=9.5, color="#2b5f9e")
    ax.add_patch(Circle((4.35, 2.95), 0.18, fc="#2ca02c", ec="k", lw=0.6))
    flecha(ax, (4.45, 3.05), (6.4, 3.7), color="#c0392b")
    ax.text(6.5, 3.75, "p (573 keV)", fontsize=9.5, color="#c0392b", va="center")
    flecha(ax, (4.25, 2.85), (3.1, 2.05), color="#6a3d9a")
    ax.text(3.0, 1.95, "t (191 keV)", fontsize=9.5, color="#6a3d9a", ha="right", va="center")
    ax.text(4.6, 0.35, "$^3$He + n $\\rightarrow$ p + $^3$H + 764 keV", ha="center", fontsize=10.5,
            bbox=dict(boxstyle="round", fc="white", ec="0.5"))

    t = np.linspace(0, 10, 400)
    pre = np.where(t > 1, (1 - np.exp(-(t - 1) / 0.3)) * np.exp(-(t - 1) / 2.5), 0)
    amp = np.where(t > 1, np.sin((t - 1) / 3.0 * np.pi) * np.exp(-(t - 1) / 2.0), 0)
    amp = np.where(t > 7, 0, amp) / np.max(amp)
    dig = np.where((t > 2.5) & (t < 5.0), 1.0, 0.0)
    cnt = np.zeros_like(t)
    for c in [1.5, 3.8, 5.6, 8.3]:
        cnt[np.abs(t - c) < 0.08] = 1
    datos = [(pre / pre.max(), "#2ca02c", "(c) Preamplificador", "Integra la carga y la\nconvierte en un pulso\nde tensión", None),
             (amp, "#e67e22", "(d) Amplificador", "Da forma al pulso y\nmejora la relación\nseñal/ruido", None),
             (dig, "#8e44ad", "(e) Discriminador", "Genera un pulso lógico\nsi la amplitud supera\nel umbral", 0.35),
             (cnt, "#c0392b", "(f) Contador", "Cada pulso lógico\nsuma un evento\n(neutrón detectado)", None)]
    for k, (v, c, tit, txt, u) in enumerate(datos):
        pulso(fig.add_subplot(gs[1, k]), t, v, c, tit, txt, u)
    guardar(fig, "fig_contador_he3")


# ---------------------------------------------------------------- modelo de suelo
def fig_suelo():
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.add_patch(Rectangle((0.3, 0.3), 9.4, 6.4, fc="#f3f8fc", ec="#2b5f9e", lw=1.5, ls="--"))
    ax.text(0.5, 6.45, "Volumen mundo: aire seco (G4_AIR)", fontsize=11, color="#2b5f9e", va="top")
    ax.add_patch(Rectangle((1.2, 0.8), 7.6, 2.2, fc="#b08968", ec="#6b4f2e", lw=1.5, hatch="..", alpha=0.9))
    ax.text(5.0, 1.9, "Suelo seco", ha="center", va="center",
            fontsize=10.5, color="white", fontweight="bold")
    ax.annotate("", xy=(9.1, 0.8), xytext=(9.1, 3.0), arrowprops=dict(arrowstyle="<->", lw=1.2))
    ax.text(9.2, 1.9, "1 m", va="center", fontsize=11)
    ax.text(1.3, 2.9, "interfaz aire–suelo", ha="left", va="top", fontsize=9.5, color="white")
    for x0 in [1.8, 3.0, 4.2, 5.4]:
        flecha(ax, (x0, 5.2), (x0 + 0.3, 3.1), color="#2b5f9e", lw=1.4)
    ax.text(3.6, 5.35, "neutrones incidentes\n(flujo de la etapa II)", fontsize=10, color="#2b5f9e", ha="center")
    for x0, dx in [(6.6, -0.3), (7.4, 0.3), (8.2, -0.2)]:
        flecha(ax, (x0, 3.1), (x0 + dx, 4.9), color="#8e44ad", lw=1.4, ls="--")
    ax.text(7.4, 5.15, "neutrones de albedo\n(emergen del suelo\nhacia el aire)", fontsize=10, color="#8e44ad", ha="center")
    guardar(fig, "fig_modelo_suelo")


# ---------------------------------------------------------------- interacciones del neutrón
def fig_procesos():
    fig, ax = plt.subplots(figsize=(13, 6.2))
    ax.set_xlim(0, 12.9)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    caja(ax, 4.75, 5.4, 3.4, 0.75, "Interacción neutrón–núcleo", "#1f3b6e", "#1f3b6e", fs=12, peso="bold", color="white")
    caja(ax, 1.0, 3.9, 3.0, 0.8, "Dispersión\n(el neutrón sobrevive)", "#fff3e6", "#e67e22", fs=10.5, peso="bold")
    caja(ax, 7.8, 3.9, 3.6, 0.8, "Absorción\n(el núcleo absorbe el neutrón)", "#fdecea", "#c0392b", fs=10.5, peso="bold")
    flecha(ax, (5.6, 5.4), (2.5, 4.72))
    flecha(ax, (7.3, 5.4), (9.6, 4.72))
    hojas_d = [("Elástica\n$(n,n)$", "El núcleo queda en su\nestado fundamental;\nel neutrón cede energía\ncinética por retroceso", 0.05),
               ("Inelástica\n$(n,n')$", "El núcleo queda excitado\ny se desexcita\nemitiendo rayos $\\gamma$", 2.3)]
    hojas_a = [("Captura radiativa\n$(n,\\gamma)$", "Núcleo compuesto\nexcitado que emite\nrayos $\\gamma$", 4.6),
               ("Partículas cargadas\n$(n,p)$, $(n,\\alpha)$, $(n,d)$", "Emisión de protones,\npartículas $\\alpha$ o\ndeuterones", 6.7),
               ("Emisión de neutrones\n$(n,2n)$, $(n,3n)$, …", "Solo por encima de\nla energía umbral\nde cada reacción", 8.8),
               ("Fisión\n$(n,f)$", "Fragmentos de fisión\ny neutrones\nsecundarios", 10.9)]
    for nom, desc, x in hojas_d:
        caja(ax, x, 1.95, 2.1, 0.95, nom, "#fff3e6", "#e67e22", fs=10, peso="bold")
        caja(ax, x, 0.15, 2.1, 1.55, desc, "white", "#e67e22", fs=9)
        flecha(ax, (2.5, 3.88), (x + 1.05, 2.92))
    for nom, desc, x in hojas_a:
        caja(ax, x, 1.95, 1.95, 0.95, nom, "#fdecea", "#c0392b", fs=8.4, peso="bold")
        caja(ax, x, 0.15, 1.95, 1.55, desc, "white", "#c0392b", fs=8.6)
        flecha(ax, (9.6, 3.88), (x + 0.97, 2.92))
    guardar(fig, "fig_procesos_neutron")


# ---------------------------------------------------------------- trayectorias en el tanque
def leer_eventos(carpeta, medio, n_ev=25):
    """Pasos del neutrón primario de los n_ev primeros eventos (formato de interaccion-completa-neutrones.txt)."""
    filas, ev = [], 0
    with open(MALLA / carpeta / medio / "interaccion-completa-neutrones.txt") as f:
        for linea in f:
            c = linea.split()
            if c[0] == "1":
                ev += 1
                if ev > n_ev:
                    break
            filas.append((ev, *map(float, c[5:11]), c[12]))
    return pd.DataFrame(filas, columns=["ev", "x1", "y1", "z1", "x2", "y2", "z2", "proceso"])


def recortar(p, q, lim):
    """Recorta el segmento p-q a la caja lim (Liang-Barsky)."""
    t0, t1, d = 0.0, 1.0, q - p
    for i, (a, b) in enumerate(lim):
        for num, den in [(p[i] - a, -d[i]), (b - p[i], d[i])]:
            if den == 0:
                if num < 0:
                    return None
            else:
                t = num / den
                if den < 0:
                    t0 = max(t0, t)
                else:
                    t1 = min(t1, t)
    return None if t0 > t1 else (p + t0 * d, p + t1 * d)


LIM = [(-900, 900), (-900, 900), (-100, 1600)]


def fig_trayectorias():
    paneles = [("1000meV", "Agua-pura", "(a) Agua pura, 1 eV"), ("1000000meV", "Agua-pura", "(b) Agua pura, 1 keV"),
               ("1000meV", "Agua+2.5NaCl", "(c) Agua + 2.5 % de NaCl, 1 eV"),
               ("1000000meV", "Agua+2.5NaCl", "(d) Agua + 2.5 % de NaCl, 1 keV")]
    fig = plt.figure(figsize=(11, 10.5))
    R, Hc = 480, 1330                                        # mm, volumen de agua
    for k, (e, m, tit) in enumerate(paneles):
        ax = fig.add_subplot(2, 2, k + 1, projection="3d")
        d = leer_eventos(e, m)
        for ev, g in d.groupby("ev"):
            capt = (g.proceso == "nCapture").any()
            c = "#2ca02c" if capt else "#1f77b4"
            for _, s in g.iterrows():
                seg = recortar(np.array([s.x1, s.y1, s.z1]), np.array([s.x2, s.y2, s.z2]), LIM)
                if seg is not None:
                    ax.plot(*zip(*seg), color=c, lw=0.6, alpha=0.8)
            fin = g.iloc[-1]
            if capt:
                ax.scatter(fin.x2, fin.y2, fin.z2, color="#d62728", s=9, depthshade=False)
        th = np.linspace(0, 2 * np.pi, 80)
        for z in [0, Hc]:
            ax.plot(R * np.cos(th), R * np.sin(th), z, color="0.35", lw=1)
        for a in [0, np.pi / 2, np.pi, 3 * np.pi / 2]:
            ax.plot([R * np.cos(a)] * 2, [R * np.sin(a)] * 2, [0, Hc], color="0.35", lw=0.8)
        ax.set_xlim(-900, 900)
        ax.set_ylim(-900, 900)
        ax.set_zlim(-100, 1600)
        ax.set_box_aspect((1, 1, 0.95))
        ax.view_init(elev=22, azim=-60)
        ax.set_xlabel("x [mm]", fontsize=8)
        ax.set_ylabel("y [mm]", fontsize=8)
        ax.set_zlabel("z [mm]", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.set_title(tit, fontsize=11)
    fig.legend(handles=[plt.Line2D([], [], color="#2ca02c", label="neutrón capturado"),
                        plt.Line2D([], [], color="#1f77b4", label="neutrón que escapa"),
                        plt.Line2D([], [], color="#d62728", marker="o", ls="", label="punto de captura")],
               loc="lower center", ncol=3, fontsize=10, frameon=False)
    fig.subplots_adjust(wspace=0.05, hspace=0.08, bottom=0.05)
    guardar(fig, "fig_trayectorias_tanque")


if __name__ == "__main__":
    SAL.mkdir(parents=True, exist_ok=True)
    fig_arti()
    fig_contador()
    fig_suelo()
    fig_procesos()
    fig_trayectorias()
