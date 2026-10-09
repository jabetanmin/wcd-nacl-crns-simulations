#!/usr/bin/env python3
"""Tablas LaTeX del informe técnico de la validación numérica (Sec. 4.1.1).

Uso: python3 tablas_informe.py <resultados> <salida>
La última fila de cada archivo no termina en \\\\: el documento maestro la cierra tras \\input.
"""
import sys
from pathlib import Path

import pandas as pd

ROT = {"Agua-pura": "Agua pura", "Agua+0.5NaCl": "0.5~\\% NaCl", "Agua+1NaCl": "1~\\% NaCl",
       "Agua+2.5NaCl": "2.5~\\% NaCl", "Agua+5NaCl": "5~\\% NaCl", "Agua+10NaCl": "10~\\% NaCl"}
ORDEN = list(ROT)
FIN = " \\\\\n"


def sci(v):
    m, e = f"{v:.1e}".split("e")
    return f"${m}\\times10^{{{int(e)}}}$"


def main(res, sal):
    res, sal = Path(res), Path(sal)
    sal.mkdir(parents=True, exist_ok=True)
    leer = lambda n: pd.read_csv(res / n, sep="\t")
    w = lambda n, lineas: (sal / n).write_text(FIN.join(lineas) + "\n")

    c = leer("resumen_carga.tsv").set_index("medio").loc[ORDEN]
    w("tabla_carga.tex", [f"{ROT[m]} & {r.eventos_norm:.0f} & {100 * r.eficiencia:.2f} & {r.Q_media:.1f} & {r.Q_std:.1f} & {int(r.Q_mediana)} & "
                          f"{int(r.Q_max)}" for m, r in c.iterrows()])

    t = leer("metricas_reproduccion.tsv")
    w("tabla_metricas.tex", [f"{ROT[r.medio]} & {r.r_tesis:.3f} / {r.r_reproducido:.3f} & "
                             f"{sci(r.p_tesis)} / {sci(r.p_reproducido)} & {r.rho_tesis:.3f} / {r.rho_reproducido:.3f} & "
                             f"{r.RMSE_tesis:.3f} / {r.RMSE_reproducido:.3f} & {r.MAE_tesis:.3f} / {r.MAE_reproducido:.3f}"
                             for r in t.itertuples()])

    v = leer("metricas_variantes.tsv")
    nombres = {"original_700_puntos": "Tesis: 700 puntos interpolados",
               "bins_nativos_8.3pe_suavizado": "Bins de 8.3 pe, suavizado",
               "bins_nativos_8.3pe_sin_suavizar": "Bins de 8.3 pe, sin suavizar",
               "25pe_sin_suavizar": "Bins de 25 pe, sin suavizar",
               "25pe_sin_suavizar_referencia_limpia": "25 pe, referencia sin artefactos"}
    filas = []
    for nombre, g in v.groupby("variante", sort=False):
        for i, r in enumerate(g.itertuples()):
            filas.append(f"{nombres[nombre] if i == 0 else ''} & {ROT[r.medio]} & {int(r.n_puntos)} & {r.r:.3f} & "
                         f"{sci(r.p)} & {r.RMSE:.3f} & {r.R_sim_media:.2f} & {r.R_ref_media:.2f}"
                         + (" \\\\ \\midrule" if i == len(g) - 1 and nombre != list(nombres)[-1] else ""))
    (sal / "tabla_variantes.tex").write_text(
        "".join(l + ("\n" if l.endswith("\\midrule") else (FIN if k < len(filas) - 1 else "\n"))
                for k, l in enumerate(filas)))

    a = leer("ajustes_tramos.tsv")
    nom_or = {"A": "A", "B": "B", "?": "---"}
    filas = []
    tramos = list(dict.fromkeys(a.tramo))
    for t_ in tramos:
        g = a[a.tramo == t_]
        for i, r in enumerate(g.itertuples()):
            filas.append(f"{t_ if i == 0 else ''} & {ROT[r.medio]} & ${r.pendiente_tesis:.3f}\\pm{r.err_pend_tesis:.3f}$ & "
                         f"{nom_or[r.origen_valores]}/{nom_or[r.origen_errores]} & ${r.pend_A:.3f}\\pm{r.err_pend_A:.3f}$ & "
                         f"${r.pend_B:.3f}\\pm{r.err_pend_B:.3f}$ & ${r.pend_poisson_10pe:.3f}\\pm{r.err_pend_poisson:.3f}$"
                         + (" \\\\ \\midrule" if i == len(g) - 1 and t_ != tramos[-1] else ""))
    (sal / "tabla_ajustes.tex").write_text(
        "".join(l + ("\n" if l.endswith("\\midrule") else (FIN if k < len(filas) - 1 else "\n"))
                for k, l in enumerate(filas)))

    l = leer("lineas_gamma.tsv")
    p = l.pivot(index="linea", columns="medio", values="cuentas_linea_norm")       # por 1.5e5 neutrones
    eg = l[l.medio == "Agua+10NaCl"].set_index("linea").E_geant4_keV
    et = l[l.medio == "Agua+10NaCl"].set_index("linea").E_tabla_keV
    orden = ["H 2223.25", "Cl35 517.07", "Cl35 788.42", "Cl35 1164.86", "Cl35 1951.14", "Cl35 1959.35",
             "Cl35 6110.84", "Cl35 8578.6", "Cl37 755.43", "Cl37 1692.11", "Na 472.20", "O 870.76", "O 2184.44"]
    w("tabla_lineas.tex", [f"{n.split()[0].replace('Cl35', '$^{35}$Cl').replace('Cl37', '$^{37}$Cl')} & {et[n]:.2f} & "
                           f"{eg[n]:.2f} & " + " & ".join(f"{p.loc[n, m]:.0f}" for m in
                                                        ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"])
                           for n in orden])

    f = leer("verificacion_archivos.tsv")
    f = f[f.archivo.str.startswith("Espectro-electrones")]
    real = {"Agua-pura": "agua pura", "Agua+5NaCl": "5~\\% NaCl", "Agua+10NaCl": "10~\\% NaCl", "ninguno": "otra corrida"}
    w("tabla_archivos_electrones.tex",
      [f"\\archivo{{{r.archivo.split('/')[-1].replace('Espectro-energia-electrones-', '…')}}} & {int(r.filas)} & "
       f"{r.fraccion_e_le_gamma:.4f} & {real[r.emparejado_con]} & \\texttt{{{r.md5[:8]}}}" for r in f.itertuples()])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
