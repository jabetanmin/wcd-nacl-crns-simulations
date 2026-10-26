#!/usr/bin/env python3
"""
Cuatro maneras de contar la captura en el barrido rápido (1 keV a 1 GeV), para comparar con Sidelnik et al. (2020):
  η_Cap         destino del neutrón incidente (balance_rapidos.py, Tabla 4.8 de la tesis);
  por traza     capturas en el agua / todas las trazas de neutrones del evento (primario + cascada): la
                "probabilidad de captura" de la Tabla 2 de Sidelnik et al. (2020);
  por neutrón   capturas en el agua por neutrón incidente (puede pasar de 1 a alta energía);
  eventos       fracción de eventos con al menos una captura en el agua (la columna capturas_agua del barrido).
Lee <carpeta>/<energía>-<medio>-<N>N/Datos-simulacion/pasos-neutrones.tsv; guarda un resumen en
resultados/capturas_definiciones.tsv, que basta para rehacer la tabla sin el disco.
Uso: captura_definiciones.py [<carpeta del barrido> ...]
-> resultados/capturas_definiciones.tsv, informe/tablas/capturas_definiciones.tex
"""
import csv, os, re, subprocess, sys

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT, TAB = os.path.join(BASE, "resultados", "capturas_definiciones.tsv"), os.path.join(BASE, "informe", "tablas", "capturas_definiciones.tex")
UNID = {"keV": 1e-3, "MeV": 1.0, "GeV": 1e3}
AWK = r'''BEGIN { FS = "\t" } !/^#/ { k = $1 " " $4; if (!(k in t)) { t[k] = 1; n++ }; ru[$1] = 1
  if ($8 == "nCapture" && $9 ~ /Water/) { c++; ev[$1] = 1 } }
  END { printf "%d\t%d\t%d\t%d\n", length(ru), n, c, length(ev) }'''
if sys.argv[1:]:
    filas = []
    for raiz in sys.argv[1:]:
        for d in sorted(os.listdir(raiz)):
            m = re.fullmatch(r"([0-9.]+)(keV|MeV|GeV)-(\w+)-(\d+)N", d)
            f = os.path.join(raiz, d, "Datos-simulacion", "pasos-neutrones.tsv")
            if not m or int(m.group(4)) < 1000 or not os.path.isfile(f): continue
            N, trazas, capt, ev = map(int, subprocess.run(["mawk", AWK, f], capture_output=True, text=True, check=True,
                                                         env={"LC_ALL": "C", "PATH": os.environ["PATH"]}).stdout.split())
            assert N == int(m.group(4)), f"{d}: {N} eventos"
            filas.append({"E_MeV": float(m.group(1)) * UNID[m.group(2)], "medio": m.group(3), "N": N, "trazas": trazas,
                          "capturas": capt, "eventos_con_captura": ev})
    with open(OUT, "w") as fo:
        w = csv.DictWriter(fo, fieldnames=list(filas[0]), delimiter="\t"); w.writeheader(); w.writerows(filas)
F = list(csv.DictReader(open(OUT), delimiter="\t"))
MED = {"Agua-pura": "AguaPura", "Agua+2.5NaCl": "Agua25NaCl", "Agua+5NaCl": "Agua5NaCl", "Agua+10NaCl": "Agua10NaCl"}
B = {(MED[r["medio"]], round(float(r["E_meV"]) * 1e-9, 6)): r for r in csv.DictReader(open(os.path.join(BASE, "resultados", "balance_rapidos.tsv")), delimiter="\t")}
def etq(E): return f"{E * 1e3:g}~keV" if E < 1 else (f"{E:g}~MeV" if E < 1e3 else f"{E / 1e3:g}~GeV")
NOMBRE = [("AguaPura", "Agua pura"), ("Agua25NaCl", "2.5~\\% NaCl"), ("Agua5NaCl", "5~\\% NaCl"), ("Agua10NaCl", "10~\\% NaCl")]
with open(TAB, "w") as fo:
    fo.write("\\begin{tabular}{ll r rrrr}\n\\toprule\n & & trazas & \\multicolumn{4}{c}{captura (\\%)} \\\\\n"
             "\\cmidrule(lr){4-7}\n"
             "Energía & Medio & por neutrón & $\\eta_{\\rm Cap}$ & por traza & por neutrón & eventos \\\\\n\\midrule\n")
    for k, E in enumerate(sorted({float(r["E_MeV"]) for r in F})):
        if k: fo.write("\\midrule\n")
        for n, (mr, nom) in enumerate(NOMBRE):
            r = next((r for r in F if r["medio"] == mr and float(r["E_MeV"]) == E), None)
            if r is None: continue
            x = [100 * float(B[(mr, round(E, 6))]["eta_cap"]), 100 * int(r["capturas"]) / int(r["trazas"]),
                 100 * int(r["capturas"]) / int(r["N"]), 100 * int(r["eventos_con_captura"]) / int(r["N"])]
            fo.write(f"{etq(E) if n == 0 else ''} & {nom} & {int(r['trazas']) / int(r['N']):.2f} & " + " & ".join(f"{v:.1f}" for v in x) + " \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
print(open(TAB).read())
