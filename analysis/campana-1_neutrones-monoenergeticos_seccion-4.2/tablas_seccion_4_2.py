#!/usr/bin/env python3
"""Tablas LaTeX de la Sección 4.2 para el informe técnico "Respuesta del WCD a flujos
monocromáticos de neutrones".

Lee solo resultados/resumen_campana.tsv y escribe en <salida>:
  tabla_pasos.tex              pasos Transportation y hadElastic por neutrón incidente (Figs. 4.17 y 4.18)
  tabla_xi_<regimen>.tex       <xi> y sigma(xi) por régimen de energía y medio (Figs. 4.20-4.23, D.4-D.6)
  tabla_eficiencia.tex         eficiencia de detección epsilon con incertidumbre binomial (Fig. 4.51)
  tabla_senal_captura.tex      epsilon/eta_Cap, <k> y ganancia de eficiencia respecto al agua pura

Uso: python3 tablas_seccion_4_2.py <carpeta resultados> <carpeta de salida>
"""
import csv
import math
import sys
from pathlib import Path

from procesar_campana import ENERGIAS, MEDIOS

ROTULO = ["1 meV", "2.5 meV", "5 meV", "7 meV", "10 meV", "25 meV", "50 meV", "80 meV", "100 meV",
          "300 meV", "500 meV", "700 meV", "1 eV", "10 eV", "100 eV", "1 keV"]
# Regímenes de la tesis (Tabla 2.2); los extremos se comparten como en las Figuras 4.20-4.23.
REGIMENES = {
    "fria": ["1meV", "2.5meV", "5meV", "7meV", "10meV"],
    "termica": ["10meV", "25meV", "50meV", "80meV", "100meV"],
    "epitermica": ["100meV", "300meV", "500meV", "700meV", "1000meV"],
    "intermedia": ["1000meV", "10000meV", "100000meV", "1000000meV"],
}
N_INC = 100_000


def main():
    res, sal = Path(sys.argv[1]), Path(sys.argv[2])
    sal.mkdir(parents=True, exist_ok=True)
    R = {(r["energia"], r["medio"]): r
         for r in csv.DictReader(open(res / "resumen_campana.tsv"), delimiter="\t")}
    rot = dict(zip(ENERGIAS, ROTULO))
    f = lambda e, m, k: float(R[(e, m)][k])

    # Pasos por neutrón incidente
    filas = []
    for e in ENERGIAS:
        c = [f"{f(e, m, 'media_Transportation'):.2f}" for m in MEDIOS]
        c += [f"{f(e, m, 'media_hadElastic'):.2f}" for m in MEDIOS]
        filas.append(f"{rot[e]} & " + " & ".join(c) + r" \\")
    (sal / "tabla_pasos.tex").write_text("\n".join(filas) + "\n")

    # Letargía por régimen
    for reg, es in REGIMENES.items():
        filas = []
        for e in es:
            c = [f"${f(e, m, 'xi_media'):+.4f}$ & {f(e, m, 'xi_sigma'):.3f}" for m in MEDIOS]
            filas.append(f"{rot[e]} & " + " & ".join(c) + r" \\")
        (sal / f"tabla_xi_{reg}.tex").write_text("\n".join(filas) + "\n")

    # Eficiencia de detección y señal por captura
    filas_ef, filas_sc = [], []
    for e in ENERGIAS:
        ef = [int(R[(e, m)]["carga_eventos"]) / N_INC for m in MEDIOS]
        u = [math.sqrt(x * (1 - x) / N_INC) for x in ef]
        filas_ef.append(f"{rot[e]} & " + " & ".join(
            f"${100 * x:.2f}\\pm{100 * s:.2f}$" for x, s in zip(ef, u)) + r" \\")
        cap = [f(e, m, "eta_cap") for m in MEDIOS]
        k = [f(e, m, "carga_media_pe") for m in MEDIOS]
        c = [f"{x / y:.3f}" for x, y in zip(ef, cap)]
        c += [f"{x:.2f}" for x in k]
        c += [f"{x / ef[0]:.2f}" for x in ef[1:]]
        filas_sc.append(f"{rot[e]} & " + " & ".join(c) + r" \\")
    (sal / "tabla_eficiencia.tex").write_text("\n".join(filas_ef) + "\n")
    (sal / "tabla_senal_captura.tex").write_text("\n".join(filas_sc) + "\n")


if __name__ == "__main__":
    main()
