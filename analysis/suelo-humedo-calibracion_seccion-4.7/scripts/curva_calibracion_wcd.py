#!/usr/bin/env python3
"""
Curva de calibración del WCD por plegado: cuentas = A · Σ_E [Φ_baja(E) + Φ_sube,w(E)] · ε(E), para cada humedad w.

Flujos (resultados/espectros_albedo.tsv, corridas completas): el que baja es la curva "Baja" de la tesis, igual para
todas las humedades; el que sube es el de MEIGA para cada suelo. Están por intervalo de energía, en n m^-2 s^-1, con la
normalización de la tesis (all_bga_neutron_35.shw como 1 m^2 y 12 h; ver normalizacion.py).
Eficiencias ε(E) para Q >= 1, 3, 5, 10 y 20 p.e. (haz vertical por la tapa, PMT a 0.3·H/2, sin S(α,β)):
  - 1 meV – 1 keV: Campaña 1 (analysis/campana-1_respuesta-electromagnetica_seccion-4.2/resultados_carga/
    resumen_carga_campana.tsv), 16 energías y 4 medios;
  - 1 keV – 1 GeV: barrido rápido (resultados/eficiencias_rapidos.tsv, paquete Barrido-rapidos-WCD), 8 energías,
    agua pura y 10 % NaCl. Para Q >= 1 se empalma en 1 keV multiplicando por ε_Campaña1(1 keV) / ε_barrido(1 keV)
    (1.12 en agua pura, 1.07 con NaCl: el PMT de Sidelnik del barrido es más pequeño). Para los umbrales altos ese
    cociente no sirve (en 1 keV casi no hay cuentas sobre 5 o 10 p.e.) y se usa el barrido sin escalar. ε <= 1.
    La diferencia entre la curva con y sin empalme se da como incertidumbre sistemática.
Interpolación en log E; por debajo de 1 meV, ε(1 meV); por encima de 1 GeV, ε(1 GeV).
Dos resultados: "completo" (1 meV – 1 GeV; medios con barrido) y "hasta_1keV" (solo neutrones de hasta 1 keV; 4 medios).
Área: la sección del tanque, π R^2 con R = 48 cm, para el flujo que baja (por la tapa) y el que sube (por el fondo).
-> resultados/curva_calibracion_wcd.json, figuras/fig09_curva_calibracion_wcd, fig10_cuentas_por_banda,
   informe/tablas/{calibracion_wcd,eficiencia_wcd,cuentas_banda}.tex
"""
import csv, json, os, re
import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from regiones import REGIONES, COLOR, TEXTO

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG, TAB = (os.path.join(BASE, d) for d in ("resultados", "figuras", os.path.join("informe", "tablas")))
REPO = os.environ.get("REPO_TESIS", os.path.abspath(os.path.join(BASE, "..", "..")))
C1 = os.path.join(REPO, "analysis", "campana-1_respuesta-electromagnetica_seccion-4.2", "resultados_carga", "resumen_carga_campana.tsv")
RAP = os.path.join(RES, "eficiencias_rapidos.tsv")
AREA = np.pi * 0.48 ** 2
MEDIOS = [("Agua-pura", "AguaPura", "Agua pura"), ("Agua+2.5NaCl", "Agua25NaCl", "2.5 % NaCl"),
          ("Agua+5NaCl", "Agua5NaCl", "5 % NaCl"), ("Agua+10NaCl", "Agua10NaCl", "10 % NaCl")]
UMB = ["eps", "eps_Q3", "eps_Q5", "eps_Q10", "eps_Q20"]
COLS_RAP = {"eps": 4, "eps_Q3": 5, "eps_Q5": 6, "eps_Q10": 7, "eps_Q20": 8}
BANDAS = [(r[0], r[1], r[2]) for r in REGIONES]                      # Tabla 2.2 de la tesis (regiones.py)
COL = {"Agua pura": "red", "2.5 % NaCl": "green", "5 % NaCl": "purple", "10 % NaCl": "darkorange"}   # colores de los medios en la tesis

c1 = {}
for r in csv.DictReader(open(C1), delimiter="\t"):
    d = {u: float(r[u]) for u in UMB}; d["ventana"] = d["eps"] - d["eps_Q20"]
    c1.setdefault(r["medio"], []).append((float(r["E_meV"]) * 1e-9, d))
rap = {}
if os.path.exists(RAP):
    for l in open(RAP):
        if l.startswith("#") or not l.strip(): continue
        c = l.rstrip("\n").split("\t")
        if int(c[2]) < 1000: continue                                       # pruebas de 20 neutrones
        d = {u: float(c[k]) for u, k in COLS_RAP.items()}; d["ventana"] = d["eps"] - d["eps_Q20"]
        rap.setdefault(c[0], []).append((float(c[1]) * 1e-6, d, int(c[2]), float(c[9])))
tabla_eps, escala = {}, {}
for mc, mr, mn in MEDIOS:
    p = sorted(c1[mc]); tabla_eps[mn] = {"c1": p}
    if mr in rap:
        q = sorted(rap[mr]); d1 = dict((e, d) for e, d, _, _ in q)[1e-3]; e1 = p[-1][1]
        escala[mn] = {u: (e1[u] / d1[u] if d1[u] > 0 else 1.0) for u in UMB + ["ventana"]}
        tabla_eps[mn]["rap"] = q
def eps_fn(mn, u, completo, empalme=True):
    pts = [(e, d[u]) for e, d in tabla_eps[mn]["c1"]]
    k = escala[mn][u] if (completo and empalme and u == "eps") else 1.0
    if completo: pts += [(e, min(1.0, d[u] * k)) for e, d, _, _ in tabla_eps[mn]["rap"] if e > 1.0001e-3]
    x, y = np.log10([e for e, _ in pts]), [v for _, v in pts]
    return lambda E: np.interp(np.log10(E), x, y, left=y[0], right=y[-1] if completo else np.nan)

f = list(csv.reader(open(os.path.join(RES, "espectros_albedo.tsv")), delimiter="\t"))
cab, dat = f[0], np.array(f[1:], dtype=float)
lo, hi = dat[:, 0], dat[:, 1]; Ec = np.sqrt(lo * hi); du = np.log(hi / lo)
flujo = {c: dat[:, i] * du for i, c in enumerate(cab) if i >= 2}
baja = next(c for c in flujo if c.startswith("Baja"))
suelos = [(0.0, next(c for c in flujo if "seco" in c and "MEIGA" in c))] + \
         sorted((int(re.search(r"humedo-(\d+)", c).group(1)) / 100, c) for c in flujo if "humedo-" in c)
desilets = lambda t, a0, a1, a2: a1 + a0 / (t + a2)

out = {"area_m2": AREA, "escala_empalme_1keV": escala, "resultados": {}}
for modo, completo, empalme in (("completo", True, True), ("completo_sin_empalme", True, False), ("hasta_1keV", False, True)):
    med = [mn for _, mr, mn in MEDIOS if (not completo) or mn in escala]
    if not med: continue
    m_E = np.ones(len(Ec), bool) if completo else hi <= 1.001e-3
    R = {}
    for mn in med:
        R[mn] = {}
        for u in ("eps", "eps_Q3", "eps_Q5", "eps_Q10", "ventana"):
            ef = np.where(m_E, eps_fn(mn, u, completo, empalme)(Ec), 0.0); ef = np.nan_to_num(ef)
            filas = []
            for w, c in suelos:
                nb = 3600 * AREA * float(np.sum(flujo[baja] * ef)); ns = 3600 * AREA * float(np.sum(flujo[c] * ef))
                banda = {b: 3600 * AREA * float(np.sum(((flujo[baja] + flujo[c]) * ef)[(Ec >= a) & (Ec < z)])) for b, a, z in BANDAS}
                filas.append({"w": w, "tg": w / (1 - w), "tv": w / (w + (1 - w) / 2.7), "baja_h": nb, "sube_h": ns,
                              "total_h": nb + ns, "por_banda_h": banda})
            N0 = filas[0]["total_h"]; tg = np.array([x["tg"] for x in filas]); y = np.array([x["total_h"] / N0 for x in filas])
            try: p, _ = curve_fit(desilets, tg, y, p0=(0.05, 0.8, 0.15), maxfev=50000)
            except RuntimeError: p = (np.nan,) * 3
            dN = np.gradient(y * N0, tg)                                     # cuentas/h por unidad de θ_g
            res = {f"{t}h": [float(np.sqrt(x["total_h"] * t) / (abs(d) * t)) if d != 0 else None for x, d in zip(filas, dN)]
                   for t in (1, 6, 24)}
            R[mn][u] = {"filas": filas, "N0_h": N0, "cociente": y.tolist(), "a0": p[0], "a1": p[1], "a2": p[2],
                        "caida_seco_30": float(1 - y[-1]), "fraccion_baja_seco": filas[0]["baja_h"] / N0,
                        "dN_dtheta_por_h": dN.tolist(), "resolucion_theta_g": res}
    out["resultados"][modo] = R
out["eficiencias"] = {mn: {"E_MeV": [e for e, _ in tabla_eps[mn]["c1"]] + [e for e, _, _, _ in tabla_eps[mn].get("rap", []) if e > 1.0001e-3],
                           "eps": [d["eps"] for _, d in tabla_eps[mn]["c1"]] + [min(1.0, d["eps"] * escala[mn]["eps"]) for e, d, _, _ in tabla_eps[mn].get("rap", []) if e > 1.0001e-3]}
                      for mn in tabla_eps}
json.dump(out, open(os.path.join(RES, "curva_calibracion_wcd.json"), "w"), indent=2, ensure_ascii=False)

# --- figura 9: curva de calibración (Q >= 1 y ventana) y tasa ---
C = out["resultados"].get("completo", {}); H = out["resultados"]["hasta_1keV"]
tgs = np.array([x["tg"] for x in H["Agua pura"]["eps"]["filas"]]); tt = np.linspace(0, tgs.max() * 1.05, 200)
fig, ax = plt.subplots(1, 3, figsize=(16, 5.2))
for k, (u, tit) in enumerate((("eps", "Curva de calibración, $Q \\geq 1$ p.e."), ("ventana", "Curva de calibración, ventana $1 \\leq Q < 20$ p.e."))):
    for mn, d in C.items():
        a = d[u]
        ax[k].plot(tgs, a["cociente"], "o", color=COL[mn], ms=8, mec="white", mew=1.2, label=mn)
        if np.isfinite(a["a0"]): ax[k].plot(tt, desilets(tt, a["a0"], a["a1"], a["a2"]), "-", color=COL[mn], lw=1.6)
    ax[k].set_xlabel(r"Humedad gravimétrica $\theta_g$ [g/g]"); ax[k].set_title(tit, fontsize=10)
    ax[k].set_ylim(0.86, 1.005); ax[k].grid(alpha=0.3, ls="--")
ax[0].set_ylabel("Cuentas del WCD / cuentas con suelo seco"); ax[0].legend(fontsize=9, title="Medio (líneas: forma de Desilets)", title_fontsize=8)
for mn, d in C.items():
    a = d["eps"]
    ax[2].plot(tgs, [x["total_h"] for x in a["filas"]], "o-", color=COL[mn], ms=7, mec="white", lw=1.6, label=f"{mn}: total")
    ax[2].plot(tgs, [x["baja_h"] for x in a["filas"]], ":", color=COL[mn], lw=1.4)
ax[2].plot([], [], ":", color="0.4", label="parte del flujo que baja")
ax[2].set_xlabel(r"Humedad gravimétrica $\theta_g$ [g/g]"); ax[2].set_ylabel("Cuentas por hora ($Q \\geq 1$, tanque R = 48 cm)")
ax[2].set_title("Tasa (normalización de la figura de la tesis)", fontsize=10); ax[2].set_ylim(0, None)
ax[2].grid(alpha=0.3, ls="--"); ax[2].legend(fontsize=8, loc="lower left")
fig.tight_layout()
for x in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig09_curva_calibracion_wcd.{x}"), dpi=170)
plt.close(fig)

# --- figura 10: eficiencia y de dónde vienen las cuentas ---
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
for mn in [m for m in COL if m in escala]:
    e = out["eficiencias"][mn]; ax[0].plot(e["E_MeV"], e["eps"], "o-", color=COL[mn], ms=5, lw=1.4, label=mn)
ax[0].axvline(1e-3, color="0.5", ls=":", lw=1); ax[0].text(1.3e-3, 0.03, "empalme\n1 keV", fontsize=8, color="0.35")
ax[0].set_xscale("log"); ax[0].set_ylim(0, 0.9); ax[0].set_xlabel("Energía del neutrón [MeV]"); ax[0].set_ylabel(r"$\varepsilon(E)$, $Q \geq 1$ p.e.")
ax[0].set_title("Eficiencia del WCD (Campaña 1 hasta 1 keV; barrido rápido hasta 1 GeV)", fontsize=10); ax[0].grid(alpha=0.3, ls="--", which="both"); ax[0].legend(fontsize=9)
if C:
    mn = "Agua pura"; F = C[mn]["eps"]["filas"]; x = np.arange(len(F)); wbar = 0.2
    colb = COLOR                                                    # sin los colores de los medios
    base = np.zeros(len(F))
    for b, _, _ in BANDAS:
        v = np.array([r["por_banda_h"][b] for r in F]); ax[1].bar(x, v, 0.6, bottom=base, color=colb[b], edgecolor="white", linewidth=1.5, label=f"{b} ({TEXTO[b]})".replace("$<", "< ").replace("$>", "> ").replace("$", "").replace("~", " ").replace("--", "–")); base += v
    ax[1].set_xticks(x); ax[1].set_xticklabels(["seco" if r["w"] == 0 else f"{100 * r['w']:.0f} %" for r in F])
    ax[1].set_ylabel("Cuentas por hora (agua pura)"); ax[1].set_title("De qué energías vienen las cuentas (baja + sube)", fontsize=10)
    ax[1].set_ylim(0, base.max() * 1.35); ax[1].legend(fontsize=7.5, ncol=2, loc="upper right"); ax[1].grid(alpha=0.3, ls="--", axis="y")
fig.tight_layout()
for x_ in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig10_cuentas_por_banda.{x_}"), dpi=170)
plt.close(fig)

# --- tablas ---
etq = lambda w: "seco" if w == 0 else f"{100 * w:.0f}\\,\\%"
with open(os.path.join(TAB, "calibracion_wcd.tex"), "w") as fo:
    cols = list(C)
    fo.write("\\begin{tabular}{lr" + "rr" * len(cols) + "}\n\\toprule\n & & " +
             " & ".join(f"\\multicolumn{{2}}{{c}}{{{mn.replace('%', chr(92) + '%')}}}" for mn in cols) + " \\\\\n")
    fo.write("Suelo & $\\theta_g$ & " + " & ".join("$Q\\geq1$ & ventana" for _ in cols) + " \\\\\n\\midrule\n")
    for i, w in enumerate(x_["w"] for x_ in H["Agua pura"]["eps"]["filas"]):
        fo.write(f"{etq(w)} & {w / (1 - w):.3f} & " + " & ".join(
            f"{C[mn]['eps']['cociente'][i]:.3f} & {C[mn]['ventana']['cociente'][i]:.3f}" for mn in cols) + " \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
with open(os.path.join(TAB, "calibracion_resumen.tex"), "w") as fo:
    fo.write("\\begin{tabular}{lrrrrrr}\n\\toprule\n & \\multicolumn{3}{c}{$Q\\geq1$} & \\multicolumn{2}{c}{ventana $1\\leq Q<20$} & solo $\\leq$1 keV \\\\\n"
             "\\cmidrule(lr){2-4}\\cmidrule(lr){5-6}\\cmidrule(lr){7-7}\nMedio & $N_0$ [cuentas/h] & del flujo que baja & caída seco--30\\,\\% & $N_0$ [cuentas/h] & caída & caída \\\\\n\\midrule\n")
    for mn in cols:
        a, v, h = C[mn]["eps"], C[mn]["ventana"], H[mn]["eps"]
        fo.write(f"{mn.replace('%', chr(92) + '%')} & {a['N0_h']:.0f} & {100 * a['fraccion_baja_seco']:.0f}\\,\\% & {100 * a['caida_seco_30']:.1f}\\,\\% & "
                 f"{v['N0_h']:.0f} & {100 * v['caida_seco_30']:.1f}\\,\\% & {100 * h['caida_seco_30']:.1f}\\,\\% \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
with open(os.path.join(TAB, "eficiencia_wcd.tex"), "w") as fo:
    MR = [(mr, mn) for _, mr, mn in MEDIOS if mr in rap]
    fo.write("\\begin{tabular}{l" + "r" * (2 * len(MR)) + "}\n\\toprule\n & \\multicolumn{" + str(len(MR)) + "}{c}{$\\varepsilon$ ($Q\\geq1$)} & \\multicolumn{" + str(len(MR)) +
             "}{c}{capturas en el agua} \\\\\n\\cmidrule(lr){2-" + str(1 + len(MR)) + "}\\cmidrule(lr){" + str(2 + len(MR)) + "-" + str(1 + 2 * len(MR)) + "}\nEnergía & " +
             " & ".join(mn.replace(" NaCl", "").replace("%", chr(92) + "%").replace("Agua pura", "pura") for _, mn in MR) * 1 + " & " +
             " & ".join(mn.replace(" NaCl", "").replace("%", chr(92) + "%").replace("Agua pura", "pura") for _, mn in MR) + " \\\\\n\\midrule\n")
    q = {mr: {e: (d, n, cap) for e, d, n, cap in rap[mr]} for mr, _ in MR}
    for e in sorted(q[MR[0][0]]):
        lab = f"{e * 1e3:g} keV" if e < 1 else (f"{e:g} MeV" if e < 1e3 else f"{e / 1e3:g} GeV")
        fo.write(f"{lab} & " + " & ".join(f"{q[mr][e][0]['eps']:.3f}" for mr, _ in MR) + " & " + " & ".join(f"{q[mr][e][2]:.3f}" for mr, _ in MR) + " \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
if C:
    with open(os.path.join(TAB, "cuentas_banda.tex"), "w") as fo:
        fo.write("\\begin{tabular}{l" + "r" * len(BANDAS) + "rr}\n\\toprule\nSuelo & " + " & ".join(b for b, _, _ in BANDAS) +
                 " & del flujo & total \\\\\n & " + " & ".join(f"\\scriptsize {TEXTO[b]}" for b, _, _ in BANDAS) + " & que baja & \\\\\n\\midrule\n")
        for r in C["Agua pura"]["eps"]["filas"]:
            fo.write(f"{etq(r['w'])} & " + " & ".join(f"{r['por_banda_h'][b]:.0f}" for b, _, _ in BANDAS) + f" & {r['baja_h']:.0f} & {r['total_h']:.0f} \\\\\n")
        fo.write("\\bottomrule\n\\end{tabular}\n")
for modo, R in out["resultados"].items():
    for mn, d in R.items():
        for u in ("eps", "eps_Q5", "ventana"):
            a = d[u]
            print(f"{modo:10s} {mn:11s} {u:7s} N0={a['N0_h']:8.0f}/h  baja={a['fraccion_baja_seco']:.2f}  N/N0={[round(v, 3) for v in a['cociente']]}"
                  f"  caida={a['caida_seco_30']:.3f}  a=({a['a0']:.3f},{a['a1']:.3f},{a['a2']:.3f})  res1h={[round(v, 3) if v else None for v in a['resolucion_theta_g']['1h']]}")
S = out["resultados"].get("completo_sin_empalme", {})
out["sistematico_empalme"] = {mn: [abs(a - b) for a, b in zip(C[mn]["eps"]["cociente"], S[mn]["eps"]["cociente"])] for mn in C}
json.dump(out, open(os.path.join(RES, "curva_calibracion_wcd.json"), "w"), indent=2, ensure_ascii=False)
print("sistematico del empalme en N/N0:", {m: [round(x, 4) for x in v] for m, v in out["sistematico_empalme"].items()})
print("escala empalme:", {m: {u: round(v, 3) for u, v in e.items()} for m, e in escala.items()})
