#!/usr/bin/env python3
"""Genera las tablas LaTeX del informe a partir de resumen_barrido.tsv y resumen_capturas.tsv."""
import csv
import math
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DATOS = AQUI.parent
CON, SIN = "QGSP_BERT_HP", "QGSP_BERT_HP_NoThermal"


def leer(nombre):
    with open(DATOS / nombre, newline="") as fh:
        filas = list(csv.DictReader(fh, delimiter="\t"))
    d = {}
    for r in filas:
        d[(float(r["energia_eV"]), r["fisica"])] = r
    energias = sorted({k[0] for k in d})
    return d, energias


def etiqueta(e):
    if e < 1:
        return f"{e * 1000:g}\\,meV"
    return f"{e:g}\\,eV" if e < 1000 else f"{e / 1000:g}\\,keV"


def f2(x):
    return f"{float(x):.2f}"


def tabla_captura():
    d, es = leer("resumen_barrido.tsv")
    lineas = [r"\begin{tabular}{lrrrrrr}", r"\toprule",
              r"& \multicolumn{2}{c}{Captura en el agua (\%)} & & & \multicolumn{2}{c}{$\langle N\rangle$} \\",
              r"\cmidrule(lr){2-3}\cmidrule(lr){6-7}",
              r"$E_0$ & con $S(\alpha,\beta)$ & sin $S(\alpha,\beta)$ & Efecto (pts) & Signif. & con & sin \\",
              r"\midrule"]
    for e in es:
        c, s = d[(e, CON)], d[(e, SIN)]
        pc, ps = float(c["captura_agua_pct"]), float(s["captura_agua_pct"])
        ec, es_ = float(c["captura_agua_err_pct"]), float(s["captura_agua_err_pct"])
        dif = pc - ps
        sig = dif / math.hypot(ec, es_)
        lineas.append(f"{etiqueta(e)} & ${pc:.2f}\\pm{ec:.2f}$ & ${ps:.2f}\\pm{es_:.2f}$ & ${dif:+.2f}$ & "
                      f"${sig:+.1f}\\sigma$ & ${float(c['N_medio']):.1f}$ & ${float(s['N_medio']):.1f}$ \\\\")
    lineas += [r"\bottomrule", r"\end{tabular}"]
    (AQUI / "tabla_captura.tex").write_text("\n".join(lineas) + "\n")


def tabla_destinos():
    d, es = leer("resumen_barrido.tsv")
    cab = r"$E_0$ & Física & Agua & Estructura & Tapa & Lateral & Fondo & Aire \\"
    lineas = [r"\begin{longtable}{llrrrrrr}",
              r"\caption{Destino de los neutrones incidentes, en porcentaje: captura en el agua, captura en la "
              r"estructura (acero y Tyvek), reflexión por la tapa, escape lateral, transmisión por el fondo y "
              r"desviación en el aire antes de llegar al tanque.}\\",
              r"\toprule", cab, r"\midrule", r"\endfirsthead",
              r"\toprule", cab, r"\midrule", r"\endhead"]
    for e in es:
        for f, nombre in ((CON, r"con $S(\alpha,\beta)$"), (SIN, r"sin $S(\alpha,\beta)$")):
            r = d[(e, f)]
            celdas = [f2(r[k]) for k in ("captura_agua_pct", "captura_estructura_pct", "reflexion_tapa_pct",
                                         "escape_lateral_pct", "transmision_fondo_pct", "desviado_en_aire_pct")]
            prim = etiqueta(e) if f == CON else ""
            lineas.append(f"{prim} & {nombre} & " + " & ".join(celdas) + r" \\")
        if e != es[-1]:
            lineas.append(r"\addlinespace[2pt]")
    lineas += [r"\bottomrule", r"\end{longtable}"]
    (AQUI / "tabla_destinos.tex").write_text("\n".join(lineas) + "\n")


def tabla_capturas():
    d, es = leer("resumen_capturas.tsv")
    lineas = [r"\begin{tabular}{lrrrrrrrr}", r"\toprule",
              r"& \multicolumn{2}{c}{Prof. mediana (cm)} & \multicolumn{2}{c}{$t$ mediano ($\mu$s)} & "
              r"\multicolumn{2}{c}{$\tau_\mathrm{ef}$ ($\mu$s)} & \multicolumn{2}{c}{$E$ mediana (meV)} \\",
              r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}",
              r"$E_0$ & con & sin & con & sin & con & sin & con & sin \\", r"\midrule"]
    for e in es:
        c, s = d[(e, CON)], d[(e, SIN)]
        lineas.append(
            f"{etiqueta(e)} & {float(c['profundidad_mediana_cm']):.1f} & {float(s['profundidad_mediana_cm']):.1f} & "
            f"{float(c['tiempo_mediano_us']):.0f} & {float(s['tiempo_mediano_us']):.0f} & "
            f"${float(c['vida_media_us']):.0f}\\pm{float(c['vida_media_err_us']):.0f}$ & "
            f"${float(s['vida_media_us']):.0f}\\pm{float(s['vida_media_err_us']):.0f}$ & "
            f"{float(c['energia_mediana_meV']):.1f} & {float(s['energia_mediana_meV']):.1f} \\\\")
    lineas += [r"\bottomrule", r"\end{tabular}"]
    (AQUI / "tabla_capturas.tex").write_text("\n".join(lineas) + "\n")


def tabla_eficiencia():
    with open(DATOS / "resumen_em.tsv", newline="") as fh:
        filas = list(csv.DictReader(fh, delimiter="\t"))
    d = {(float(r["energia_eV"]), r["fisica"]): r for r in filas}
    es = sorted({k[0] for k in d})
    lineas = [r"\begin{tabular}{lrrrrrrrr}", r"\toprule",
              r"& \multicolumn{2}{c}{$\varepsilon$, $Q\geq1$ (\%)} & \multicolumn{2}{c}{$\varepsilon$, $Q\geq3$ (\%)} & "
              r"\multicolumn{2}{c}{Señal tras captura (\%)} & \multicolumn{2}{c}{$\gamma$ que interactúan (\%)} \\",
              r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}",
              r"$E_0$ & con & sin & con & sin & con & sin & con & sin \\", r"\midrule"]
    for e in es:
        c, s = d[(e, CON)], d[(e, SIN)]
        lineas.append(
            f"{etiqueta(e)} & ${float(c['eficiencia_Q1_pct']):.2f}\\pm{float(c['eficiencia_Q1_err_pct']):.2f}$ & "
            f"${float(s['eficiencia_Q1_pct']):.2f}\\pm{float(s['eficiencia_Q1_err_pct']):.2f}$ & "
            f"{float(c['eficiencia_Q3_pct']):.2f} & {float(s['eficiencia_Q3_pct']):.2f} & "
            f"{float(c['senal_tras_captura_agua_pct']):.1f} & {float(s['senal_tras_captura_agua_pct']):.1f} & "
            f"{float(c['gammas_interactuan_agua_pct']):.1f} & {float(s['gammas_interactuan_agua_pct']):.1f} \\\\")
    lineas += [r"\bottomrule", r"\end{tabular}"]
    (AQUI / "tabla_eficiencia.tex").write_text("\n".join(lineas) + "\n")


if __name__ == "__main__":
    tabla_captura()
    tabla_destinos()
    tabla_capturas()
    tabla_eficiencia()
    print("Tablas generadas en", AQUI)
