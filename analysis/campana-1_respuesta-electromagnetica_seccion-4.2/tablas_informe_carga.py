#!/usr/bin/env python3
"""Tablas LaTeX del informe técnico de la respuesta electromagnética (etapa de la carga y la eficiencia).

Lee resultados_carga/ (procesar_carga.py) y escribe en <salida> las filas de cada tabla. La última fila de cada
archivo no termina en \\\\: el documento maestro la cierra tras \\input.

Uso: python3 tablas_informe_carga.py <resultados_carga> <salida>
"""
import csv
import sys
from pathlib import Path

ENERGIAS = ["1meV", "2.5meV", "5meV", "7meV", "10meV", "25meV", "50meV", "80meV", "100meV",
            "300meV", "500meV", "700meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
ROT = dict(zip(ENERGIAS, ["1 meV", "2.5 meV", "5 meV", "7 meV", "10 meV", "25 meV", "50 meV", "80 meV", "100 meV",
                          "300 meV", "500 meV", "700 meV", "1 eV", "10 eV", "100 eV", "1 keV"]))
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
NOM = dict(zip(MEDIOS, ["Agua pura", "2.5~\\% NaCl", "5~\\% NaCl", "10~\\% NaCl"]))
FIN = " \\\\\n"


def leer(ruta):
    with open(ruta) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main(res, salida):
    res, salida = Path(res), Path(salida)
    salida.mkdir(parents=True, exist_ok=True)

    # Resumen: un bloque por energía separado por \midrule
    filas = {(r["energia"], r["medio"]): r for r in leer(res / "resumen_carga_campana.tsv")}
    lineas = []
    for e in ENERGIAS:
        for i, m in enumerate(MEDIOS):
            r = filas[(e, m)]
            f = lambda k: float(r[k])
            lineas.append(f"{ROT[e] if i == 0 else ''} & {NOM[m]} & {int(r['eventos_senal'])} & {100 * f('eps'):.2f} & "
                          f"{100 * f('eta_cap'):.2f} & {f('P_senal_captura'):.3f} & "
                          f"{f('profundidad_captura_media_mm') / 10:.2f} & "
                          f"{f('Q_media_pe'):.2f}\\,$\\pm$\\,{f('u_Q_media_pe'):.2f} & {f('Q_std_pe'):.2f} & "
                          f"{int(r['Q_mediana_pe'])} & {100 * f('f_Q20'):.2f}"
                          + (" \\\\ \\midrule" if i == len(MEDIOS) - 1 and e != ENERGIAS[-1] else ""))
    with open(salida / "tabla_resumen_carga.tex", "w") as fh:
        for i, l in enumerate(lineas):
            fh.write(l + ("" if i == len(lineas) - 1 else ("\n" if l.endswith("\\midrule") else FIN)))
        fh.write("\n")

    lineas = []
    for r in leer(res / "planitud_carga.tsv"):
        f = lambda k: float(r[k])
        lineas.append(f"{NOM[r['medio']]} & {f('Q_ponderada_pe'):.3f}\\,$\\pm$\\,{f('u_Q_ponderada_pe'):.3f} & "
                      f"{f('Q_min_pe'):.2f}--{f('Q_max_pe'):.2f} & {f('chi2_media'):.1f}/{int(r['ndf_media'])} & "
                      f"{f('p_media'):.3f} & {f('chi2_forma'):.0f}/{int(r['ndf_forma'])} & {f('p_forma'):.3f} & "
                      f"{f('dQ_baja_alta_pe'):+.2f}\\,$\\pm$\\,{f('u_dQ_baja_alta_pe'):.2f} ({f('dQ_sigma'):+.1f}$\\sigma$)")
    (salida / "tabla_planitud_carga.tex").write_text(FIN.join(lineas) + "\n")

    lineas = [f"{ROT[r['energia']]} & {NOM[r['medio']]} & "
              + " & ".join(f"{float(r[f'G_Q{u}']):.2f}" for u in [1, 5, 10, 20])
              for r in leer(res / "ganancia_eficiencia_carga.tsv")]
    (salida / "tabla_ganancia_eficiencia.tex").write_text(FIN.join(lineas) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
