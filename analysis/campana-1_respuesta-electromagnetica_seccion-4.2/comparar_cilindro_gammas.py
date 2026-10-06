#!/usr/bin/env python3
"""Compara el procesamiento de los fotones gamma con la caja de la tesis (|x|,|y| <= 480 mm) y con el
cilindro del tanque (r <= 480 mm), con los mismos límites en z.

Uso: python3 comparar_cilindro_gammas.py <resultados caja> <resultados cilindro> <salida.tsv>
Imprime, para cada magnitud, el intervalo de la diferencia relativa (cilindro/caja - 1) en las 64 corridas.
"""
import json
import sys
from pathlib import Path

ENERGIAS = ["1meV", "2.5meV", "5meV", "7meV", "10meV", "25meV", "50meV", "80meV", "100meV",
            "300meV", "500meV", "700meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]


def magnitudes(r):
    P = r["procesos"]
    d = {k: r["destino"]["neutron"].get(k, 0) + r["destino"]["secundarias"].get(k, 0)
         for k in ("phot_tanque", "conv_tanque", "phot_fuera", "conv_fuera", "escapa")}
    fis = sum(P[p]["tanque"] for p in ("compt", "phot", "Rayl", "conv"))
    tp = r["tesis_fotoabsorcion_previa_compt"]
    h = r["histogramas_tesis"]["compt_estricto_2.7MeV_1000"]
    c = h["conteos"]
    i = c.index(max(c))
    sel = [k for k in range(len(c)) if c[k] >= c[i] / 2]
    return {
        "pasos_tanque": r["filas"]["tanque"],
        "pasos_exterior": r["filas"]["exterior"],
        "pasos_tanque_estricto": r["filas"]["tanque_estricto"],
        "compt_tanque": P["compt"]["tanque"],
        "phot_tanque": P["phot"]["tanque"],
        "Rayl_tanque": P["Rayl"]["tanque"],
        "conv_tanque": P["conv"]["tanque"],
        "Transportation_tanque": P["Transportation"]["tanque"],
        "compt_tanque_estricto": P["compt"]["tanque_estricto"],
        "phot_tanque_estricto": P["phot"]["tanque_estricto"],
        "Rayl_tanque_estricto": P["Rayl"]["tanque_estricto"],
        "Transportation_tanque_estricto": P["Transportation"]["tanque_estricto"],
        "fraccion_compton_fisicas": P["compt"]["tanque"] / fis,
        "pares_%_tesis": 100 * P["conv"]["total"] / r["filas"]["tanque"],
        "f_Compton_tesis": P["compt"]["tanque"] / r["filas"]["tanque"],
        "fotones_absorbidos_tanque": d["phot_tanque"] + d["conv_tanque"],
        "fotones_que_escapan": d["escapa"],
        "fotoabs_tesis_N": tp["n"],
        "fotoabs_tesis_media": tp["0.01-0.1MeV"]["media"],
        "fotoabs_tesis_sigma": tp["0.01-0.1MeV"]["std"],
        "FWHM_Compton": (sel[-1] - sel[0]) * h["ancho"],
        "Cmax_Compton": c[i],
        "z_fotoabs_media": r["fotoabsorcion_tanque"]["z_mm"]["media"],
        "r_fotoabs_media": r["fotoabsorcion_tanque"]["r_mm"]["media"],
    }


def main():
    caja, cil, salida = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    filas, rango = [], {}
    for e in ENERGIAS:
        for m in MEDIOS:
            a = magnitudes(json.loads((caja / e / m / "resumen_gammas.json").read_text()))
            b = magnitudes(json.loads((cil / e / m / "resumen_gammas.json").read_text()))
            for k in a:
                rel = (b[k] / a[k] - 1) if a[k] else 0.0
                filas.append((e, m, k, a[k], b[k], rel))
                lo, hi = rango.get(k, (rel, rel))
                rango[k] = (min(lo, rel), max(hi, rel))
    with open(salida, "w") as f:
        f.write("energia\tmedio\tmagnitud\tcaja\tcilindro\tdiferencia_relativa\n")
        for r in filas:
            f.write("\t".join(str(v) for v in r[:5]) + f"\t{r[5]:.6f}\n")
    print(f"{'magnitud':32s} {'cambio relativo (cilindro/caja - 1)':>36s}")
    for k, (lo, hi) in rango.items():
        print(f"{k:32s} {100 * lo:+9.3f} % a {100 * hi:+9.3f} %")


if __name__ == "__main__":
    main()
