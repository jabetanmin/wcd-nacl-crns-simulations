#!/usr/bin/env python3
"""Tablas LaTeX del informe técnico de la respuesta electromagnética (etapa de los fotones gamma).

Lee resultados_gammas/ (procesar_gammas.py y verificar_tesis_gamma.py) y el resumen de neutrones
(capturas de la Campaña 1) y escribe en <salida> las filas de cada tabla.

Uso: python3 tablas_informe_gammas.py <resultados_gammas> <resumen_campana.tsv de neutrones> <salida>
"""
import csv
import json
import sys
from pathlib import Path

ENERGIAS = ["1meV", "2.5meV", "5meV", "7meV", "10meV", "25meV", "50meV", "80meV", "100meV",
            "300meV", "500meV", "700meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
ROT = dict(zip(ENERGIAS, ["1 meV", "2.5 meV", "5 meV", "7 meV", "10 meV", "25 meV", "50 meV", "80 meV", "100 meV",
                          "300 meV", "500 meV", "700 meV", "1 eV", "10 eV", "100 eV", "1 keV"]))
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
NOM = dict(zip(MEDIOS, ["Agua pura", "2.5~\\% NaCl", "5~\\% NaCl", "10~\\% NaCl"]))
E5 = ["1meV", "10meV", "100meV", "1000meV", "1000000meV"]


def miles(n):
    return f"{n:,}".replace(",", "\\,")


def main():
    res, neutr, sal = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    sal.mkdir(parents=True, exist_ok=True)
    R = {(e, m): json.loads((res / e / m / "resumen_gammas.json").read_text()) for e in ENERGIAS for m in MEDIOS}
    cap = {(r["energia"], r["medio"]): int(r["capturas"]) for r in csv.DictReader(open(neutr), delimiter="\t")}
    V = list(csv.DictReader(open(res / "verificacion_tesis_gamma.tsv"), delimiter="\t"))

    # Tabla de interacciones (definiciones homogéneas), 5 energías x 4 medios
    filas = []
    for e in E5:
        filas.append(f"\\midrule\n\\multicolumn{{9}}{{l}}{{\\textbf{{$E_n$ = {ROT[e]}}}}} \\\\")
        for m in MEDIOS:
            r = R[(e, m)]
            P = r["procesos"]
            filas.append(" & ".join([NOM[m], miles(cap[(e, m)]), miles(r["trazas"]["neutron"]),
                                     miles(r["trazas"]["secundarias"]), miles(r["filas"]["total"]),
                                     miles(r["filas"]["tanque"]), miles(P["compt"]["tanque"]),
                                     miles(P["phot"]["tanque"]), miles(r["filas"]["exterior"])]) + " \\\\")
    (sal / "tabla_interacciones.tex").write_text("\n".join(filas) + "\n")

    # Fracciones de procesos físicos en el tanque y rendimientos, intervalo sobre las 16 energías
    filas = []
    for m in MEDIOS:
        fr = {p: [] for p in ("compt", "phot", "Rayl", "conv")}
        fn, fs, ab, cp, ph = [], [], [], [], []
        for e in ENERGIAS:
            r, c = R[(e, m)], cap[(e, m)]
            P = r["procesos"]
            fis = sum(P[p]["tanque"] for p in fr)
            for p in fr:
                fr[p].append(100 * P[p]["tanque"] / fis)
            fn.append(r["trazas"]["neutron"] / c)
            fs.append(r["trazas"]["secundarias"] / c)
            d = {k: r["destino"]["neutron"].get(k, 0) + r["destino"]["secundarias"].get(k, 0)
                 for k in ("phot_tanque", "conv_tanque")}
            ab.append(100 * (d["phot_tanque"] + d["conv_tanque"]) / r["trazas"]["total"])
            cp.append(P["compt"]["tanque"] / c)
            ph.append(P["phot"]["tanque"] / c)
        rng = lambda v, f: f"{min(v):{f}}--{max(v):{f}}"
        filas.append(" & ".join([NOM[m], rng(fn, ".2f"), rng(fs, ".2f"), rng(fr["compt"], ".1f"), rng(fr["phot"], ".2f"),
                                 rng(fr["Rayl"], ".2f"), rng(fr["conv"], ".2f"), rng(ab, ".1f"), rng(cp, ".2f"),
                                 rng(ph, ".2f")]) + " \\\\")
    (sal / "tabla_fracciones.tex").write_text("\n".join(filas) + "\n")

    # Cascadas de captura (gamma-primario), 1-10 meV
    filas = []
    for e in ["1meV", "2.5meV", "5meV", "7meV", "10meV"]:
        for m in MEDIOS:
            c = R[(e, m)]["cascadas_captura"]
            t = c["por_tipo"]
            cl = t.get("Cl")
            otros = c["capturas"] - t["H"]["capturas"] - (cl["capturas"] if cl else 0)
            filas.append(" & ".join([ROT[e], NOM[m], miles(c["capturas"]), miles(cap[(e, m)]),
                                     miles(t["H"]["capturas"]), miles(cl["capturas"]) if cl else "--", miles(otros),
                                     f"{c['fotones'] / c['capturas']:.2f}",
                                     f"{cl['energia_media_cascada_MeV']:.2f}" if cl else "--",
                                     f"{100 * cl['fraccion_conserva_Q']:.1f}" if cl else "--"]) + " \\\\")
    (sal / "tabla_cascadas.tex").write_text("\n".join(filas) + "\n")

    # Fotoabsorción (definición de la tesis), 16 energías
    filas = []
    for e in ENERGIAS:
        cel = []
        for m in MEDIOS:
            t = R[(e, m)]["tesis_fotoabsorcion_previa_compt"]
            w = t["0.01-0.1MeV"]
            cel.append(f"{miles(t['n'])} & ${w['media']:.4f}\\pm{w['std']:.4f}$")
        filas.append(ROT[e] + " & " + " & ".join(cel) + " \\\\")
    (sal / "tabla_fotoabsorcion.tex").write_text("\n".join(filas) + "\n")

    # Verificación: resumen por magnitud y lista de diferencias
    grupos = {}
    for v in V:
        if v["estado"] == "sin valor en la tesis":
            continue
        g = grupos.setdefault(v["magnitud"], [0, 0])
        g[0 if v["estado"] == "igual" else 1] += 1
    nombres = {"N_Cap": "$N_\\mathrm{Cap}$", "N(gamma_Cap)": "$N(\\gamma_\\mathrm{Cap})$",
               "N_Total-int": "$N_\\mathrm{Total\\text{-}int}$", "N_Int(Tanque)": "$N_\\mathrm{Int}(\\gamma_\\mathrm{Tanque})$",
               "N_Int(Com)": "$N_\\mathrm{Int}(\\gamma_\\mathrm{Com})$", "N_Int(Ext)": "$N_\\mathrm{Int}(\\gamma_\\mathrm{Ext})$",
               "pares_%": "Conversión de pares (\\%)", "FWHM_Compton_MeV": "FWHM Compton",
               "Emax_Compton_MeV": "$E_\\mathrm{max}$ Compton", "Cmax_Compton": "$C_\\mathrm{max}$ Compton",
               "phot_N": "Fotoabsorciones", "phot_media_MeV": "Energía media (fotoeléctrico)",
               "phot_sigma_MeV": "Desviación (fotoeléctrico)", "espacial_N": "$N$ (distribución espacial)",
               "espacial_z_media_cm": "$\\bar z$ (distribución espacial)"}
    filas = [f"{nombres.get(k, k)} & {a + b} & {a} & {b} \\\\" for k, (a, b) in grupos.items()]
    (sal / "tabla_verificacion_resumen.tex").write_text("\n".join(filas) + "\n")
    filas = []
    for v in V:
        if v["estado"] == "difiere":
            filas.append(f"{nombres.get(v['magnitud'], v['magnitud'])} & {ROT[v['energia']]} & {NOM[v['medio']]} & "
                         f"{v['tesis']} & {v['reproducido']} \\\\")
    (sal / "tabla_verificacion_diferencias.tex").write_text("\n".join(filas) + "\n")

    # Conversión de pares (definición de la tesis y por interacciones físicas), 5 energías
    T = {(v["energia"], v["medio"]): v for v in V if v["magnitud"] == "pares_%"}
    filas = []
    for e in E5:
        cel = []
        for m in MEDIOS:
            P = R[(e, m)]["procesos"]
            fis = sum(P[p]["tanque"] for p in ("compt", "phot", "Rayl", "conv"))
            cel.append(f"{float(T[(e, m)]['reproducido']):.2f} & {100 * P['conv']['tanque'] / fis:.2f}")
        filas.append(ROT[e] + " & " + " & ".join(cel) + " \\\\")
    (sal / "tabla_pares.tex").write_text("\n".join(filas) + "\n")

    # Distribución espacial (definición de la tesis) y FWHM de Compton
    T = {(v["magnitud"], v["energia"], v["medio"]): v["reproducido"] for v in V}
    filas = []
    for e in ("1meV", "1000000meV"):
        for m in MEDIOS:
            filas.append(f"{ROT[e]} & {NOM[m]} & {miles(int(T[('espacial_N', e, m)]))} & "
                         f"{T[('espacial_z_media_cm', e, m)]} & {T[('espacial_r_media_cm', e, m)]} \\\\")
    (sal / "tabla_espacial.tex").write_text("\n".join(filas) + "\n")
    filas = []
    for m in MEDIOS:
        for e in ["1meV", "10meV", "100meV", "1000meV"]:
            filas.append(f"{NOM[m]} & {ROT[e]} & {T[('FWHM_Compton_MeV', e, m)]} & {T[('Emax_Compton_MeV', e, m)]} & "
                         f"{miles(int(T[('Cmax_Compton', e, m)]))} \\\\")
    (sal / "tabla_fwhm.tex").write_text("\n".join(filas) + "\n")
    tabla_caja_cilindro(res, sal)


def tabla_caja_cilindro(res, sal):
    """Intervalo (64 corridas) del cambio relativo al clasificar con el cilindro r <= 480 mm en lugar de la caja."""
    arch = res.parent / "resultados_gammas_cilindro" / "comparacion_caja_cilindro_gammas.tsv"
    if not arch.exists():
        return
    rango = {}
    for r in csv.DictReader(open(arch), delimiter="\t"):
        v = 100 * float(r["diferencia_relativa"])
        lo, hi = rango.get(r["magnitud"], (v, v))
        rango[r["magnitud"]] = (min(lo, v), max(hi, v))
    filas_def = [
        ("Interacciones físicas", None),
        ("compt_tanque", "Dispersiones Compton en el tanque"),
        ("phot_tanque", "Fotoabsorciones en el tanque"),
        ("Rayl_tanque", "Dispersiones Rayleigh en el tanque"),
        ("conv_tanque", "Conversiones de pares en el tanque"),
        ("fraccion_compton_fisicas", "Fracción Compton de las interacciones físicas"),
        ("fotones_absorbidos_tanque", "Fotones absorbidos en el tanque"),
        ("fotones_que_escapan", "Fotones que escapan"),
        ("FWHM_Compton", "FWHM del espectro Compton"),
        ("z_fotoabs_media", "Profundidad media de la fotoabsorción"),
        ("r_fotoabs_media", "Radio medio de la fotoabsorción"),
        ("Magnitudes con pasos de transporte", None),
        ("Transportation_tanque", "Pasos de transporte en el tanque"),
        ("Transportation_tanque_estricto", "Pasos de transporte en el tanque estricto (Fig.~4.31)"),
        ("pasos_tanque", "$N_\\mathrm{Int}(\\gamma_\\mathrm{Tanque})$ (Tabla~4.10)"),
        ("pasos_exterior", "$N_\\mathrm{Int}(\\gamma_\\mathrm{Ext})$ (Tabla~4.10)"),
        ("f_Compton_tesis", "Fracción Compton de la tesis ($/N_\\mathrm{Int}(\\gamma_\\mathrm{Tanque})$)"),
        ("pares_%_tesis", "Conversión de pares de la tesis"),
        ("fotoabs_tesis_N", "Fotoabsorciones con la definición de la tesis"),
        ("fotoabs_tesis_media", "Energía media antes de la fotoabsorción (tesis)"),
    ]
    filas = []
    for k, nombre in filas_def:
        if nombre is None:
            filas.append(f"\\midrule\n\\multicolumn{{2}}{{l}}{{\\textit{{{k}}}}} \\\\")
            continue
        lo, hi = rango[k]
        fmt = lambda v: "$0$" if abs(v) < 0.0005 else f"${v:+.3f}$" if abs(v) < 1 else f"${v:+.1f}$"
        filas.append(f"{nombre} & {fmt(lo)} a {fmt(hi)} \\\\" if fmt(lo) != fmt(hi) else f"{nombre} & {fmt(lo)} \\\\")
    (sal / "tabla_caja_cilindro.tex").write_text("\n".join(filas) + "\n")


if __name__ == "__main__":
    main()
