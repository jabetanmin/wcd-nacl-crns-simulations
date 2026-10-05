#!/usr/bin/env python3
"""Balance de destinos de los neutrones de la Campaña 1 por caras del volumen activo (Tabla 4.8 y Apéndice).

Cada historia de interaccion-completa-neutrones.txt (solo el neutrón primario; una historia empieza en
el paso 1) se clasifica en una de cuatro categorías mutuamente excluyentes:

  Cap    el último paso es nCapture (se separa si ocurre dentro o fuera del volumen activo);
  Refle  el neutrón entra al volumen activo y lo abandona por la cara superior (último cruce);
  Trans  lo abandona por el fondo o por la pared lateral;
  Otros  no llega a entrar al volumen activo, o su historia termina en neutronInelastic.

Volumen activo: |x|, |y| <= 480 mm y 0 <= z <= 1330 mm. La clasificación usa la última frontera del
volumen activo atravesada; la versión anterior de la tesis usaba la cara de la caja del mundo de Geant4
por la que salía el neutrón, lo que contaba como "transmisión" el escape lateral por el mundo.

Columnas del archivo: paso, partícula, track, padre, E_pre, x0, y0, z0, x1, y1, z1, E_post, proceso.

Uso:
  python3 balance_caras_tanque.py <carpeta Neutrones-termicos> <carpeta de salida> [procesos]
Salida: balance_caras_tanque.tsv, dos figuras (PDF) y las cuatro tablas en LaTeX.
"""
import collections
import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

ENERGIAS = ["1meV", "2.5meV", "5meV", "7meV", "10meV", "25meV", "50meV", "80meV", "100meV",
            "300meV", "500meV", "700meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
VALOR_MEV = [1, 2.5, 5, 7, 10, 25, 50, 80, 100, 300, 500, 700, 1e3, 1e4, 1e5, 1e6]
# La carpeta 1000000meV se rotula "1 keV" en la tesis por decisión del autor.
ETIQUETAS = [f"${v:g}\\,\\mathrm{{meV}}$" for v in VALOR_MEV[:12]] + [
    "$1\\,\\mathrm{eV}$", "$10\\,\\mathrm{eV}$", "$100\\,\\mathrm{eV}$", "$1\\,\\mathrm{keV}$"]
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]


def dentro(x, y, z):
    return abs(x) <= 480 and abs(y) <= 480 and 0 <= z <= 1330


def clasificar(historia):
    ultimo = historia[-1]
    proceso = ultimo[12]
    entro = False
    salida = None
    for p in historia:
        a = dentro(float(p[5]), float(p[6]), float(p[7]))
        b = dentro(float(p[8]), float(p[9]), float(p[10]))
        if b:
            entro = True
        if a and not b:
            z = float(p[10])
            salida = "arriba" if z > 1330 else ("abajo" if z < 0 else "lateral")
        if not a and b:
            salida = None
    fin_dentro = dentro(float(ultimo[8]), float(ultimo[9]), float(ultimo[10]))
    if proceso == "nCapture":
        return "cap_dentro" if fin_dentro else "cap_fuera"
    if proceso == "neutronInelastic":
        return "inel_dentro" if fin_dentro else "inel_fuera"
    if not entro:
        return "no_entra"
    return salida or "otro"


def procesar(archivo):
    cuentas = collections.Counter()
    historia = []
    with open(archivo) as f:
        for linea in f:
            p = linea.split()
            if p[0] == "1" and historia:
                cuentas[clasificar(historia)] += 1
                historia = []
            historia.append(p)
    if historia:
        cuentas[clasificar(historia)] += 1
    return f"{archivo.parent.parent.name}/{archivo.parent.name}", dict(cuentas)


def agrupar(c):
    n = sum(c.values())
    g = lambda *k: sum(c.get(x, 0) for x in k) / n
    return {"n": n, "cap": g("cap_dentro", "cap_fuera"), "ref": g("arriba"),
            "tra": g("abajo", "lateral"), "otr": g("no_entra", "inel_dentro", "inel_fuera", "otro")}


def tabla_latex(T, medio):
    filas = []
    for e, etq in zip(ENERGIAS, ETIQUETAS):
        t = T[(e, medio)]
        celdas = [f"${100*t[k]:.3f}\\pm{100*math.sqrt(t[k]*(1-t[k])/t['n']):.3f}$"
                  for k in ("cap", "ref", "tra", "otr")]
        filas.append(f"{etq} & " + " & ".join(celdas)
                     + f" & ${t['cap']+t['ref']+t['tra']+t['otr']:.5f}$ \\\\")
    return "\n".join(filas) + "\n"


def figuras(T, salida):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    etiquetas = ["Agua pura", "Agua + 2.5 % de NaCl", "Agua + 5 % de NaCl", "Agua + 10 % de NaCl"]
    colores = ["red", "green", "purple", "orange"]
    marcas = ["D", "s", "^", "o"]

    def ejes(ax):
        ax.set_xscale("log")
        ax.set_xlim(0.7, 1.5e6)
        for x in (10, 100, 1e3):
            ax.axvline(x, color="b", ls="--", lw=1)
        ax.grid(True, axis="y", ls=":", color="0.7")
        ax.set_xticks([1, 10, 100, 1e3, 1e4, 1e5, 1e6])
        ax.set_xticklabels(["$10^0$\n(1 meV)", "$10^1$\n(10 meV)", "$10^2$\n(100 meV)", "$10^3$\n(1 eV)",
                            "$10^4$\n(10 eV)", "$10^5$\n(100 eV)", "$10^6$\n(1 keV)"])
        ax.set_xlabel("Energía  [meV]", fontsize=13)

    def panel(ax, clave, ylim, ylabel):
        for m, et, col, mk in zip(MEDIOS, etiquetas, colores, marcas):
            p = np.array([T[(e, m)][clave] for e in ENERGIAS])
            n = np.array([T[(e, m)]["n"] for e in ENERGIAS])
            ax.errorbar(VALOR_MEV, 100 * p, yerr=100 * np.sqrt(p * (1 - p) / n), fmt=mk, color=col,
                        mec="k", mew=0.5, ms=7, capsize=2, ecolor="k", label=et)
        ax.set_ylabel(ylabel, fontsize=13)
        ax.set_ylim(*ylim)
        ejes(ax)

    fig, ax = plt.subplots(figsize=(10, 6.6))
    panel(ax, "ref", (40, 82), r"$\eta_{\mathrm{Refle}}=N_{\mathrm{refle}}/N_{\mathrm{inc}}$  [%]")
    for x, txt in [(3.2, "Fríos"), (32, "Térmicos"), (380, "Epitérmicos"), (4e4, "Intermedios")]:
        ax.text(x, 79.5, txt, ha="center", fontsize=12, weight="bold")
    ax.legend(loc="lower right", fontsize=12, framealpha=1, edgecolor="k")
    fig.tight_layout()
    fig.savefig(salida / "Fraccion_neutrones_reflejados_cara_tanque.pdf")

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.6))
    panel(a1, "tra", (0, 0.1), r"$\eta_{\mathrm{Trans}}=N_{\mathrm{trans}}/N_{\mathrm{inc}}$  [%]")
    a1.set_title("(a) Salida por el fondo o los laterales", fontsize=12)
    panel(a2, "otr", (0, 7), r"$\eta_{\mathrm{Otros}}=N_{\mathrm{otros}}/N_{\mathrm{inc}}$  [%]")
    a2.set_title("(b) No ingreso al volumen activo e interacción inelástica", fontsize=12)
    a2.legend(loc="upper right", fontsize=10, framealpha=1, edgecolor="k")
    for a in (a1, a2):
        for t in a.get_xticklabels():
            t.set_fontsize(8)
    fig.tight_layout()
    fig.savefig(salida / "Fraccion_neutrones_transmitidos_otros_cara_tanque.pdf")


def main():
    base = Path(sys.argv[1])
    salida = Path(sys.argv[2])
    procesos = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    salida.mkdir(parents=True, exist_ok=True)
    archivos = [base / e / m / "interaccion-completa-neutrones.txt" for e in ENERGIAS for m in MEDIOS]
    with Pool(procesos) as pool:
        crudos = pool.map(procesar, archivos)
    (salida / "balance_caras_tanque_crudo.json").write_text(json.dumps(crudos, indent=1))

    T = {}
    with open(salida / "balance_caras_tanque.tsv", "w") as f:
        f.write("energia\tmedio\tN\tcap_dentro\tcap_fuera\tarriba\tabajo\tlateral\tno_entra\t"
                "inel_dentro\tinel_fuera\totro\teta_cap\teta_refle\teta_trans\teta_otros\n")
        for (ruta, c), (e, m) in zip(crudos, [(e, m) for e in ENERGIAS for m in MEDIOS]):
            T[(e, m)] = agrupar(c)
            t = T[(e, m)]
            claves = ["cap_dentro", "cap_fuera", "arriba", "abajo", "lateral", "no_entra",
                      "inel_dentro", "inel_fuera", "otro"]
            f.write(f"{e}\t{m}\t{t['n']}\t" + "\t".join(str(c.get(k, 0)) for k in claves)
                    + f"\t{t['cap']:.6f}\t{t['ref']:.6f}\t{t['tra']:.6f}\t{t['otr']:.6f}\n")
    for m in MEDIOS:
        (salida / f"tabla_balance_{m}.tex").write_text(tabla_latex(T, m))
    figuras(T, salida)
    t = T[("1meV", "Agua-pura")]
    print(f"Agua pura, 1 meV: Cap {100*t['cap']:.3f}  Refle {100*t['ref']:.3f}  "
          f"Trans {100*t['tra']:.3f}  Otros {100*t['otr']:.3f}")


if __name__ == "__main__":
    main()
