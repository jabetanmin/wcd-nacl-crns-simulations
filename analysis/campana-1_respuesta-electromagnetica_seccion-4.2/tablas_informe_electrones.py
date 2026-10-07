#!/usr/bin/env python3
"""Tablas LaTeX del informe técnico de la respuesta electromagnética (etapa de los electrones y positrones).

Lee resultados_electrones/ (procesar_electrones.py y verificar_tesis_electrones.py) y el resumen de neutrones
(capturas de la Campaña 1) y escribe en <salida> las filas de cada tabla.

Uso: python3 tablas_informe_electrones.py <resultados_electrones> <resumen_campana.tsv de neutrones> <salida>
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from procesar_electrones import ajuste_pico_cherenkov  # noqa: E402

ENERGIAS = ["1meV", "2.5meV", "5meV", "7meV", "10meV", "25meV", "50meV", "80meV", "100meV",
            "300meV", "500meV", "700meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
ROT = dict(zip(ENERGIAS, ["1 meV", "2.5 meV", "5 meV", "7 meV", "10 meV", "25 meV", "50 meV", "80 meV", "100 meV",
                          "300 meV", "500 meV", "700 meV", "1 eV", "10 eV", "100 eV", "1 keV"]))
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
NOM = dict(zip(MEDIOS, ["Agua pura", "2.5~\\% NaCl", "5~\\% NaCl", "10~\\% NaCl"]))
E5 = ["1meV", "10meV", "100meV", "1000meV", "1000000meV"]
ROT_MAG = {"1meV": "1 meV", "10meV": "10 meV", "100meV": "100 meV", "1000meV": "1 eV", "10000meV": "10 eV",
           "1000000meV": "1 keV", "5 energías": "5 energías", "": "---"}


def miles(n):
    return f"{n:,}".replace(",", "\\,")


def intervalo(v, fmt):
    a, b = min(v), max(v)
    return f"{a:{fmt}}" if f"{a:{fmt}}" == f"{b:{fmt}}" else f"{a:{fmt}}--{b:{fmt}}"


def main():
    res, neutr, sal = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    sal.mkdir(parents=True, exist_ok=True)
    R = {(e, m): json.loads((res / e / m / "resumen_electrones.json").read_text()) for e in ENERGIAS for m in MEDIOS}
    cap = {(r["energia"], r["medio"]): int(r["capturas"]) for r in csv.DictReader(open(neutr), delimiter="\t")}
    V = list(csv.DictReader(open(res / "verificacion_tesis_electrones.tsv"), delimiter="\t"))

    # Pasos por proceso en el tanque estricto y trazas, 5 energías x 4 medios
    filas = []
    for e in E5:
        filas.append(f"\\midrule\n\\multicolumn{{9}}{{l}}{{\\textbf{{$E_n$ = {ROT[e]}}}}} \\\\")
        for m in MEDIOS:
            r = R[(e, m)]
            P = r["procesos"]
            filas.append(" & ".join([NOM[m], miles(cap[(e, m)]), miles(r["trazas"]["e-"]), miles(r["trazas"]["e+"])]
                                    + [miles(P[p]["tanque_estricto"])
                                       for p in ("eIoni", "Cerenkov", "msc", "eBrem", "Scintillation")]) + " \\\\")
    (sal / "tabla_procesos.tex").write_text("\n".join(filas) + "\n")

    # Rendimientos por captura: intervalo sobre las 16 energías
    defs = [
        ("Trazas $e^-$", lambda r: r["trazas"]["e-"], ".2f"),
        ("Trazas $e^+$", lambda r: r["trazas"]["e+"], ".4f"),
        ("$e^-$ nacidos sobre el umbral", lambda r: r["trazas_sobre_umbral_tanque"]["e-"], ".2f"),
        ("Trazas con pasos Cherenkov", lambda r: r["trazas_emisoras"]["e-"] + r["trazas_emisoras"]["e+"], ".2f"),
        ("Pasos \\var{eIoni}", lambda r: r["procesos"]["eIoni"]["tanque_estricto"], ".2f"),
        ("Pasos \\var{Cerenkov}", lambda r: r["procesos"]["Cerenkov"]["tanque_estricto"], ".2f"),
        ("Longitud sobre el umbral [mm]", lambda r: r["longitud_sobre_umbral_mm"], ".2f"),
        ("Pasos en la ventana de la Tabla~4.19", lambda r: r["ventanas_Cerenkov"]["tesis_agua"], ".2f"),
    ]
    filas = []
    for nombre, f, fmt in defs:
        celdas = [intervalo([f(R[(e, m)]) / cap[(e, m)] for e in ENERGIAS], fmt) for m in MEDIOS]
        filas.append(" & ".join([nombre] + celdas) + " \\\\")
    (sal / "tabla_rendimientos.tex").write_text("\n".join(filas) + "\n")

    # Particularidades del registro: fracciones (intervalo sobre las 64 corridas)
    def fr(f):
        return intervalo([f(R[(e, m)]) for e in ENERGIAS for m in MEDIOS], ".1f")

    filas = [
        ("Pasos de $e^\\pm$ fuera del tanque [\\%]", fr(lambda r: 100 * r["filas"]["exterior"] / r["filas"]["total"])),
        ("Pasos \\var{eIoni} con $E=0$ en el tanque [\\%]",
         fr(lambda r: 100 * r["procesos"]["eIoni"]["E_cero_tanque"] / r["procesos"]["eIoni"]["tanque"])),
        ("Pasos \\var{Scintillation} con $E=0$ [\\%]",
         fr(lambda r: 100 * r["procesos"]["Scintillation"]["E_cero_tanque"] / r["procesos"]["Scintillation"]["tanque"])),
        ("Pasos \\var{Scintillation} por traza [\\%]",
         fr(lambda r: 100 * r["procesos"]["Scintillation"]["total"] / (r["trazas"]["e-"] + r["trazas"]["e+"]))),
        ("Pasos \\var{Cerenkov} en la ventana del Pyrex (180--190 keV) [\\%]",
         fr(lambda r: 100 * r["ventanas_Cerenkov"]["pyrex"] / r["ventanas_Cerenkov"]["Cerenkov_estricto"])),
        ("Pasos \\var{Cerenkov} bajo el umbral del agua [\\%]",
         fr(lambda r: 100 * r["ventanas_Cerenkov"]["bajo_umbral_agua"] / r["ventanas_Cerenkov"]["Cerenkov_estricto"])),
        ("Pasos \\var{Cerenkov} en la ventana de la Tabla~4.19 [\\%]",
         fr(lambda r: 100 * r["ventanas_Cerenkov"]["tesis_agua"] / r["ventanas_Cerenkov"]["Cerenkov_estricto"])),
    ]
    (sal / "tabla_registro.tex").write_text("\n".join(f"{a} & {b} \\\\" for a, b in filas) + "\n")

    # Ajuste fino del máximo Cherenkov
    filas = []
    for e in E5:
        celdas = []
        for m in MEDIOS:
            mu, u, sg = ajuste_pico_cherenkov(R[(e, m)]["histogramas"]["Cerenkov_umbral_estricto"])
            celdas.append(f"{mu * 1e3:.3f}")
        filas.append(" & ".join([ROT[e]] + celdas) + " \\\\")
    (sal / "tabla_ajuste_cherenkov.tex").write_text("\n".join(filas) + "\n")

    # Tabla 4.19 reproducida y por captura
    filas = []
    for e in E5:
        celdas = []
        for m in MEDIOS:
            n = next(int(v["reproducido"]) for v in V if v["magnitud"].startswith("Tabla 4.19")
                     and v["energia"] == e and v["medio"] == m)
            celdas.append(f"{miles(n)} & {n / cap[(e, m)]:.2f}")
        filas.append(" & ".join([ROT[e]] + celdas) + " \\\\")
    (sal / "tabla_ventana.tex").write_text("\n".join(filas) + "\n")

    # Verificación: resumen por magnitud y diferencias
    grupos = {}
    for v in V:
        if v["estado"] == "sin valor en la tesis":
            continue
        g = v["magnitud"].split(" eIoni")[0] if v["magnitud"].startswith("Tabla E.1") else v["magnitud"]
        g = "Tabla E.1 (pasos por proceso)" if g.startswith("Tabla E.1") else g
        d = grupos.setdefault(g, [0, 0, 0, 0])
        d[0] += 1
        d[{"igual": 1, "compatible": 2, "difiere": 3}[v["estado"]]] += 1
    nombres = {"Tabla 4.19 N_e en la ventana": "Tabla~4.19 (pasos en la ventana)",
               "fracción en la ventana: mínimo (%)": "Fracción en la ventana, mínimo",
               "fracción en la ventana: máximo (%)": "Fracción en la ventana, máximo",
               "Fig. 4.46 máximo del espectro eIoni (MeV)": "Fig.~4.46 (máximo de \\var{eIoni})",
               "Tabla 4.17 umbral Cherenkov (MeV)": "Tabla~4.17 (umbrales)",
               "Tabla 4.18 / Fig. 4.47 máximo Cherenkov ajustado (MeV)": "Tabla~4.18 y Fig.~4.47 (ajuste)",
               "Tabla E.1 (pasos por proceso)": "Tabla~E.1 (pasos por proceso)"}
    filas = [f"{nombres.get(g, g)} & {d[0]} & {d[1]} & {d[2]} & {d[3]} \\\\" for g, d in grupos.items()]
    tot = [sum(d[i] for d in grupos.values()) for i in range(4)]
    filas.append(f"\\midrule\nTotal & {tot[0]} & {tot[1]} & {tot[2]} & {tot[3]} \\\\")
    (sal / "tabla_verificacion_resumen.tex").write_text("\n".join(filas) + "\n")

    filas = []
    for v in V:
        if v["estado"] != "difiere":
            continue
        mag = v["magnitud"].replace("Tabla E.1 ", "Tabla~E.1, \\var{") + "}" if v["magnitud"].startswith("Tabla E.1") \
            else "Fig.~4.46, máximo [MeV]"
        t, r = v["tesis"], v["reproducido"]
        if t.isdigit():
            t, r = miles(int(t)), miles(int(r))
        else:
            t, r = f"{float(t):.3f}", f"{float(r):.3f}"
        filas.append(f"{mag} & {ROT_MAG.get(v['energia'], v['energia'])} & {NOM[v['medio']]} & {t} & {r} \\\\")
    (sal / "tabla_verificacion_diferencias.tex").write_text("\n".join(filas) + "\n")
    print(f"tablas escritas en {sal}")


if __name__ == "__main__":
    main()
