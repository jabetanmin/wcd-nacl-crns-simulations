#!/usr/bin/env python3
"""
Escribe las tablas del informe (informe/tablas/*.tex) a partir de los JSON de resultados. Los medios que aún
no tienen corrida (p. ej. 10 % NaCl) aparecen como "pendiente": al procesar esa corrida basta con volver a
ejecutar analizar_montaje.py, comparar_con_calibracion_vem.py y este script, y recompilar el informe.
"""
import json, os
BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, TAB = os.path.join(BASE, "resultados"), os.path.join(BASE, "informe", "tablas")
os.makedirs(TAB, exist_ok=True)
R = json.load(open(os.path.join(RES, "resumen_montaje.json")))
V = json.load(open(os.path.join(RES, "calibracion_vem.json")))
K = json.load(open(os.path.join(RES, "comparacion_calibracion_vem.json")))
MED = [("pura", "Agua pura", "pura"), ("nacl25", "2.5\\,\\% NaCl", "2.5"), ("nacl10", "10\\,\\% NaCl", "10")]
COMP = [("haz", "Haz"), ("halo", "Halo"), ("fondo", "Fondo"), ("total", "Total")]
f1 = lambda x: f"{x:.1f}".replace(".", "{.}")
def num(x, d=2): return f"{x:.{d}f}"
def miles(n): return f"{n:,.0f}".replace(",", "\\,")
def pend(ncol): return " & ".join(["\\multicolumn{%d}{c}{\\emph{pendiente}}" % ncol])

# 1. respuesta por componente
L = ["\\begin{tabular}{llrrrrrr}", "\\toprule",
     "Medio & Comp. & $\\varepsilon(Q\\geq1)$ [\\%] & pred. tapa [\\%] & $\\eta_\\text{cap}$ [\\%] & $\\langle Q\\rangle$ [p.e.] & $\\varepsilon(Q\\geq12)$ [\\%] & $t_\\text{cap}$ [$\\mu$s] \\\\", "\\midrule"]
for m, nom, _ in MED:
    if m not in R:
        L.append(f"{nom} & & \\multicolumn{{6}}{{c}}{{\\emph{{pendiente (corrida en marcha)}}}} \\\\"); L.append("\\midrule"); continue
    for i, (c, cn) in enumerate(COMP):
        x = R[m][c]; p = x.get("prediccion_tapa")
        L.append(f"{nom if i == 0 else ''} & {cn} & {100*x['eps_Q1']:.1f} & {('%.1f' % (100*p['eps_Q1'])) if p else '--'} & "
                 f"{100*x['eta_cap_medio']:.1f} & {x['Q_media_senal']:.2f} & {100*x['eps_Q12']:.3f} & {x['t_cap_mediana_us']:.0f} \\\\")
    L.append("\\midrule")
L[-1] = "\\bottomrule"; L.append("\\end{tabular}")
open(os.path.join(TAB, "respuesta_componentes.tex"), "w").write("\n".join(L) + "\n")

# 2. núcleo de captura y modelo de 5 min
L = ["\\begin{tabular}{lrrrrrr}", "\\toprule",
     "Medio & H [\\%] & $^{35}$Cl [\\%] & $^{23}$Na [\\%] & señal $Q\\geq1$ (5 min) & capturas (5 min) & $Q\\geq12$ (5 min) \\\\", "\\midrule"]
for m, nom, _ in MED:
    if m not in R:
        L.append(f"{nom} & \\multicolumn{{6}}{{c}}{{\\emph{{pendiente}}}} \\\\"); continue
    n = R[m]["total"]["nucleo_pct"]; t = R[m]["modelo_5min"]["total"]
    L.append(f"{nom} & {n.get('H', 0):.1f} & {n.get('35Cl', 0):.1f} & {n.get('23Na', 0):.2f} & {miles(t['senal_Q1'])} & {miles(t['capturas'])} & {miles(t['senal_Q12'])} \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open(os.path.join(TAB, "nucleos_modelo5min.tex"), "w").write("\n".join(L) + "\n")

# 3. calibración por muones
L = ["\\begin{tabular}{llrrr}", "\\toprule", "Toma de fondo & Método & pico muones [ADC] & ADC/p.e. & p.e./1000 ADC \\\\", "\\midrule"]
for met, mn in (("ventana_trigger", "ventana del disparo"), ("robusto", "robusto")):
    for _, nom, p in MED:
        e = V["experimento_fondo"][f"{met}_{p}"]; c = V["calibracion"][f"{met}_{p}"]
        L.append(f"{nom} & {mn} & {miles(e['pico_ADC'])} & {c['ADC_por_pe']:.0f} & {c['pe_por_1000ADC']:.2f} \\\\")
r = V["resumen"]
L += ["\\midrule", f"\\multicolumn{{4}}{{l}}{{Media (rango {r['rango'][0]:.2f}--{r['rango'][1]:.2f})}} & \\textbf{{{r['pe_por_1000ADC_media']:.2f}}} \\\\",
      "\\multicolumn{4}{l}{Calibración usada hasta ahora (cuaderno del prototipo)} & 3.95 \\\\", "\\bottomrule", "\\end{tabular}"]
open(os.path.join(TAB, "calibracion_vem.tex"), "w").write("\n".join(L) + "\n")

# 4. bandas de carga (ventana del disparo)
B = K["metodos"]["ventana_trigger"]
bandas = [b["pe"] for b in B["pura"]["bandas"]]
L = ["\\begin{tabular}{l" + "r" * len(bandas) + "}", "\\toprule",
     "Carga [p.e.] & " + " & ".join(f"{a}--{b}" for a, b in bandas) + " \\\\",
     "Carga [VEM] & " + " & ".join(f"{a/K['VEM_pe']:.2f}--{b/K['VEM_pe']:.2f}" for a, b in bandas) + " \\\\", "\\midrule"]
for _, nom, p in MED:
    L.append(f"{nom}: fuente [s$^{{-1}}$] & " + " & ".join(f"{b['fuente_por_s']:.1f}" for b in B[p]["bandas"]) + " \\\\")
    L.append(f"\\quad fondo [s$^{{-1}}$] & " + " & ".join(f"{b['fondo_por_s']:.1f}" for b in B[p]["bandas"]) + " \\\\")
    L.append(f"\\quad cociente & " + " & ".join(f"{b['cociente']:.2f}" for b in B[p]["bandas"]) + " \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open(os.path.join(TAB, "bandas_carga.tex"), "w").write("\n".join(L) + "\n")

# 5. exceso medido vs MEIGA por encima del disparo
L = ["\\begin{tabular}{lrrrrr}", "\\toprule",
     "Medio & exceso 23--200 p.e. [s$^{-1}$] & MEIGA $Q\\geq$ disparo (300 s) & medido/MEIGA & $L_\\text{exp}$ [ADC] & $L_\\text{sim}$ [p.e.] \\\\", "\\midrule"]
for _, nom, p in MED:
    v, w = K["metodos"]["ventana_trigger"][p], K["metodos"]["robusto"][p]
    s = v.get("sim")
    L.append(f"{nom} & {v['exceso_23_200pe_por_s']:.0f}--{w['exceso_23_200pe_por_s']:.0f} & "
             + (f"{s['eventos_300s_Q_ge_umbral']:.1f} & {miles(v['exceso_sobre_sim_Q_ge_umbral'])}--{miles(w['exceso_sobre_sim_Q_ge_umbral'])}" if s else "\\emph{pendiente} & --")
             + f" & {w['caida_exceso_ADC_4k_10k']:.0f}--{v['caida_exceso_ADC_4k_10k']:.0f} & " + (f"{s['caida_pe_2_8']:.2f}" if s else "--") + " \\\\")
L += ["\\bottomrule", "\\end{tabular}"]
open(os.path.join(TAB, "exceso_vs_meiga.tex"), "w").write("\n".join(L) + "\n")
print("tablas en", TAB, sorted(os.listdir(TAB)))
