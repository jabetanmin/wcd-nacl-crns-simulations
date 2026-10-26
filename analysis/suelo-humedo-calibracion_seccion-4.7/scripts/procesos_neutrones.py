#!/usr/bin/env python3
"""
Procesos que sufren en el suelo los neutrones inyectados y los que ellos crean, por humedad.

Lee de cada corrida (parte*/Datos-simulacion):
  interacciones-neutrones.tsv : una línea por interacción de un neutrón (proceso, material, traza, proceso creador)
  capturas-neutrones.tsv      : una línea por captura (núcleo blanco Z, A; material)
y cuenta, por neutrón inyectado:
  - interacciones en el suelo por proceso (hadElastic, neutronInelastic, nCapture, otros), del neutrón incidente
    (traza 1) y de los neutrones secundarios;
  - destino del neutrón incidente según su última interacción: capturado (nCapture), destruido por dispersión
    inelástica (neutronInelastic: sus productos siguen como trazas nuevas), solo dispersiones elásticas (sale del
    suelo o del mundo) o sin interacción (neutrones de más de ~60 MeV que atraviesan el metro de suelo y salen por el
    fondo; su fracción crece con el agua porque el suelo húmedo tiene menos masa por cm²);
  - neutrones creados por proceso creador (neutronInelastic, protonInelastic, ...);
  - capturas por núcleo y material.
Las corridas se toman de resultados/albedo_suelo.json (las mismas de analizar_albedo.py).
-> resultados/procesos_neutrones.json, informe/tablas/{procesos,destino,creados,capturas}.tex
"""
import json, os, re, subprocess
from collections import defaultdict

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, TAB = os.path.join(BASE, "resultados"), os.path.join(BASE, "informe", "tablas")
NUC = {1: "H", 6: "C", 7: "N", 8: "O", 11: "Na", 12: "Mg", 13: "Al", 14: "Si", 15: "P", 16: "S", 19: "K", 20: "Ca",
       22: "Ti", 26: "Fe"}
AWK_INT = r'''BEGIN{FS="\t"} /^#/{next}
{ run=$1; trk=$4; crea=$7; p=$8; s=($9 ~ /^SoilBS/) ? "suelo" : "fuera"
  q=(p=="hadElastic"||p=="neutronInelastic"||p=="nCapture") ? p : "otros"
  c[(trk==1 ? "inc" : "sec") SUBSEP q SUBSEP s]++
  if (trk!=1) { k=run SUBSEP trk; if (!(k in vis)) { vis[k]=1; cr[crea]++ } }
  else if ($6+0 >= paso[run]) { paso[run]=$6+0; ult[run]=q } }
END{ for (k in c) { split(k, a, SUBSEP); print "I", a[1], a[2], a[3], c[k] }
     for (k in cr) print "C", k, cr[k]
     for (r in ult) d[ult[r]]++; for (k in d) print "D", k, d[k] }'''
AWK_CAP = r'''BEGIN{FS="\t"} /^#/{next} { m=($8 ~ /^SoilBS/) ? "suelo" : "fuera"; c[$9 SUBSEP $10 SUBSEP m]++ }
END{ for (k in c) { split(k, a, SUBSEP); print a[1], a[2], a[3], c[k] } }'''

def w_de(etq):
    if etq.startswith("seco"): return 0.0
    m = re.match(r"humedo-(\d+)", etq); return int(m.group(1)) / 100 if m else None

d = json.load(open(os.path.join(RES, "albedo_suelo.json")))
out = {}
for etq, v in d["corridas"].items():
    w = w_de(etq); carpeta = v["carpeta"]
    if w is None or not os.path.isdir(carpeta): continue
    I = defaultdict(int); Cr = defaultdict(int); D = defaultdict(int); Cap = defaultdict(int); N = 0
    for k in sorted(x for x in os.listdir(carpeta) if x.startswith("parte")):
        ds = os.path.join(carpeta, k, "Datos-simulacion")
        N += sum(1 for l in open(os.path.join(carpeta, k, f"{k}.txt")) if l.strip())
        txt = subprocess.run(["mawk", AWK_INT, os.path.join(ds, "interacciones-neutrones.tsv")], capture_output=True,
                             text=True, env={"LC_ALL": "C", "PATH": os.environ["PATH"]}, check=True).stdout
        for l in txt.splitlines():
            c = l.split()
            if c[0] == "I": I[(c[1], c[2], c[3])] += int(c[4])
            elif c[0] == "C": Cr[c[1]] += int(c[2])
            else: D[c[1]] += int(c[2])
        txt = subprocess.run(["mawk", AWK_CAP, os.path.join(ds, "capturas-neutrones.tsv")], capture_output=True,
                             text=True, env={"LC_ALL": "C", "PATH": os.environ["PATH"]}, check=True).stdout
        for l in txt.splitlines():
            z, a_, m, n = l.split(); Cap[(int(z), int(a_), m)] += int(n)
    sin = N - sum(D.values())
    out[etq] = {"w": w, "N_inyectados": N,
                "interacciones": {f"{a}|{b}|{c}": n for (a, b, c), n in sorted(I.items())},
                "destino_incidente": dict(D) | {"sin interaccion": sin},
                "creados": dict(sorted(Cr.items(), key=lambda t: -t[1])),
                "capturas": {f"{NUC.get(z, z)}-{a_}|{m}": n for (z, a_, m), n in sorted(Cap.items(), key=lambda t: -t[1])}}
    print(etq, N, "inyectados;", sum(I.values()), "interacciones;", sum(Cap.values()), "capturas", flush=True)
json.dump(out, open(os.path.join(RES, "procesos_neutrones.json"), "w"), indent=1, ensure_ascii=False)

# --- tablas ---
filas = sorted(out.items(), key=lambda t: t[1]["w"])
etq_tex = lambda w: "seco" if w == 0 else f"{100 * w:.0f}\\,\\%"
P = ["hadElastic", "neutronInelastic", "nCapture", "otros"]
with open(os.path.join(TAB, "procesos.tex"), "w") as fo:
    fo.write("\\begin{tabular}{l" + "r" * 8 + "}\n\\toprule\n & \\multicolumn{4}{c}{Neutrón incidente} & \\multicolumn{4}{c}{Neutrones secundarios} \\\\\n"
             "\\cmidrule(lr){2-5}\\cmidrule(lr){6-9}\nSuelo & elástica & inelástica & captura & otros & elástica & inelástica & captura & otros \\\\\n\\midrule\n")
    for etq, r in filas:
        N = r["N_inyectados"]; g = lambda t, p: r["interacciones"].get(f"{t}|{p}|suelo", 0) / N
        fo.write(etq_tex(r["w"]) + " & " + " & ".join(f"{g('inc', p):.2f}" for p in P) + " & " +
                 " & ".join(f"{g('sec', p):.2f}" for p in P) + " \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
DEST = [("nCapture", "capturado"), ("neutronInelastic", "inelástica"), ("hadElastic", "solo elásticas"),
        ("otros", "otros"), ("sin interaccion", "atraviesa sin interactuar")]
with open(os.path.join(TAB, "destino.tex"), "w") as fo:
    fo.write("\\begin{tabular}{l" + "r" * len(DEST) + "}\n\\toprule\nSuelo & " + " & ".join(t for _, t in DEST) + " \\\\\n\\midrule\n")
    for etq, r in filas:
        N = r["N_inyectados"]
        fo.write(etq_tex(r["w"]) + " & " + " & ".join(f"{100 * r['destino_incidente'].get(k, 0) / N:.1f}\\,\\%" for k, _ in DEST) + " \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
CR = ["neutronInelastic", "protonInelastic", "hBertiniCaptureAtRest", "pi-Inelastic", "pi+Inelastic"]
with open(os.path.join(TAB, "creados.tex"), "w") as fo:
    fo.write("\\begin{tabular}{l" + "r" * (len(CR) + 2) + "}\n\\toprule\nSuelo & " +
             " & ".join({"neutronInelastic": "inelástica $n$", "protonInelastic": "inelástica $p$",
                         "hBertiniCaptureAtRest": "captura $h$ en reposo", "pi-Inelastic": "$\\pi^-$",
                         "pi+Inelastic": "$\\pi^+$"}[c] for c in CR) + " & otros & total \\\\\n\\midrule\n")
    for etq, r in filas:
        N = r["N_inyectados"]; tot = sum(r["creados"].values())
        fo.write(etq_tex(r["w"]) + " & " + " & ".join(f"{r['creados'].get(c, 0) / N:.3f}" for c in CR) +
                 f" & {(tot - sum(r['creados'].get(c, 0) for c in CR)) / N:.3f} & {tot / N:.3f} \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
nucs = defaultdict(int)
for _, r in filas:
    for k, n in r["capturas"].items():
        if k.endswith("|suelo"): nucs[k.split("|")[0].split("-")[0]] += n
top = [k for k, _ in sorted(nucs.items(), key=lambda t: -t[1])][:7]
with open(os.path.join(TAB, "capturas.tex"), "w") as fo:
    fo.write("\\begin{tabular}{lr" + "r" * (len(top) + 1) + "}\n\\toprule\nSuelo & capturas por n & " +
             " & ".join(k for k in top) + " & otros \\\\\n\\midrule\n")
    for etq, r in filas:
        N = r["N_inyectados"]; s = defaultdict(int)
        for k, n in r["capturas"].items():
            if k.endswith("|suelo"): s[k.split("|")[0].split("-")[0]] += n
        tot = sum(s.values())
        fo.write(etq_tex(r["w"]) + f" & {tot / N:.3f} & " + " & ".join(f"{100 * s.get(k, 0) / tot:.1f}" for k in top) +
                 f" & {100 * (tot - sum(s.get(k, 0) for k in top)) / tot:.1f} \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
