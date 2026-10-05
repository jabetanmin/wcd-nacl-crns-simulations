#!/usr/bin/env python3
"""Procesa las 64 corridas de la Campaña 1 (16 energías x 4 medios) con procesar_corrida.py.

Uso:
  python3 procesar_campana.py <carpeta Neutrones-termicos> <carpeta de salida> [procesos]
Salida: <salida>/<energía>/<medio>/{historias.tsv.gz,resumen.json} y <salida>/resumen_campana.tsv.
"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

from procesar_corrida import procesar

ENERGIAS = ["1meV", "2.5meV", "5meV", "7meV", "10meV", "25meV", "50meV", "80meV", "100meV",
            "300meV", "500meV", "700meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]


def tarea(args):
    base, salida, e, m = args
    return procesar(Path(base) / e / m, Path(salida) / e / m)


def main():
    base, salida = sys.argv[1], sys.argv[2]
    procesos = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    trabajos = [(base, salida, e, m) for e in ENERGIAS for m in MEDIOS]
    with Pool(procesos) as pool:
        resumenes = pool.map(tarea, trabajos)
    cols = ["energia", "medio", "historias", "capturas", "eta_cap", "u_eta_cap", "eta_refle", "u_eta_refle",
            "eta_trans", "u_eta_trans", "eta_otros", "u_eta_otros",
            "media_Transportation", "std_Transportation", "media_hadElastic", "std_hadElastic",
            "media_neutronInelastic", "cadenas_N", "N_tesis_media", "N_total_media",
            "xi_colisiones", "xi_media", "xi_sigma", "xi_mediana",
            "xi_historia_inicial_n", "xi_historia_inicial_media", "carga_eventos", "carga_media_pe"]
    with open(Path(salida) / "resumen_campana.tsv", "w") as f:
        f.write("\t".join(cols) + "\n")
        for (_, _, e, m), r in zip(trabajos, resumenes):
            pp = r["pasos_por_historia"]
            fila = [e, m, r["historias"], r["capturas"]]
            for k in ("eta_cap", "eta_refle", "eta_trans", "eta_otros"):
                fila += [f"{r[k]['valor']:.6f}", f"{r[k]['incertidumbre']:.6f}"]
            fila += [f"{pp['Transportation']['media']:.5f}", f"{pp['Transportation']['std']:.5f}",
                     f"{pp['hadElastic']['media']:.5f}", f"{pp['hadElastic']['std']:.5f}",
                     f"{pp['neutronInelastic']['media']:.5f}",
                     r["N_tesis"]["cadenas"], f"{r['N_tesis']['media']:.4f}", f"{r['N_total_media']:.4f}",
                     r["xi_tesis"]["colisiones"], f"{r['xi_tesis']['media']:.6f}",
                     f"{r['xi_tesis']['sigma']:.6f}", f"{r['xi_tesis']['mediana']:.6f}",
                     r["xi_historia_inicial"]["n"], f"{r['xi_historia_inicial']['media']:.6f}",
                     r.get("carga", {}).get("eventos", ""),
                     f"{r['carga']['media_pe']:.4f}" if r.get("carga") else ""]
            f.write("\t".join(map(str, fila)) + "\n")
    print(f"{len(resumenes)} corridas -> {Path(salida) / 'resumen_campana.tsv'}")


if __name__ == "__main__":
    main()
