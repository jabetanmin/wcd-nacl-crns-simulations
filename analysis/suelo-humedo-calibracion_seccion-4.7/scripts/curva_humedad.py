#!/usr/bin/env python3
"""
Curva de humedad del albedo del suelo SoilBS: cocientes húmedo/seco por región de energía, ajuste de la forma de
Desilets et al. (2010), cociente espectral y tablas y cifras del informe.

Lee las salidas de analizar_albedo.py:
  resultados/albedo_suelo.json, espectros_albedo.tsv                      (corridas completas; la primera es el seco)
  resultados/albedo_suelo_validacion.json, espectros_albedo_validacion.tsv (seco frente a la parte 1 de cada humedad:
                                                                           los mismos 50 000 neutrones de entrada)
Las etiquetas de las corridas deben empezar por "seco" o por "humedo-<w en %>". Cualquier humedad que se agregue a
analizar_albedo.py (p. ej. humedo-15) entra sola en las tablas, las figuras y las cifras.
Con --carpetas, lee además de cada corrida (disco ADATA) los archivos, bytes, manifiesto y tiempos para la tabla de
corridas (resultados/corridas_suelo.json); sin el disco se usa la tabla guardada.
-> resultados/curva_humedad.json, figuras/fig03_cocientes_humedad, fig04_cociente_espectral,
   informe/tablas/*.tex, informe/cifras.tex
"""
import argparse, glob, hashlib, json, os, re, subprocess
import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from regiones import NOMBRES, LIMITES, TEXTO, COLOR, CLAVE, AJUSTE, sombrear

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG, TAB = (os.path.join(BASE, d) for d in ("resultados", "figuras", os.path.join("informe", "tablas")))
os.makedirs(TAB, exist_ok=True)
ap = argparse.ArgumentParser()
ap.add_argument("--carpetas", action="store_true", help="leer archivos, bytes, manifiesto y tiempos de cada corrida")
a = ap.parse_args()

REG = NOMBRES                                                  # clasificación de la tesis (Tabla 2.2), ver regiones.py
REG_TXT = {r: f"{r} ({TEXTO[r]})" for r in REG}
DES = (0.0808, 0.372, 0.115)                                   # Desilets et al. (2010): a0, a1, a2
NUM = {5: "Cinco", 10: "Diez", 15: "Quince", 20: "Veinte", 25: "Veinticinco", 30: "Treinta"}
RHO = lambda w: 1.0 / (w / 1.0 + (1 - w) / 2.7)
desilets = lambda t, a0, a1, a2: a1 + a0 / (t + a2)

def w_de(etq):
    if etq.startswith("seco"): return 0.0
    m = re.match(r"humedo-(\d+)", etq); return int(m.group(1)) / 100 if m else None

def espectro(suf):
    f = [l.rstrip("\n").split("\t") for l in open(os.path.join(RES, f"espectros_albedo{suf}.tsv"), encoding="utf-8")]
    d = np.array(f[1:], dtype=float); lo, hi = d[:, 0], d[:, 1]; du = np.log(hi / lo)
    return {c: d[:, i] * du for i, c in enumerate(f[0]) if i >= 2}, lo, hi   # flujo por intervalo [n m^-2 s^-1]

def en_region(F, lo, hi, r):
    a_, b_ = LIMITES[r]; m = (lo >= a_ * 0.999) & (hi <= b_ * 1.001); return float(np.sum(F[m]))

def cargar(suf):
    d = json.load(open(os.path.join(RES, f"albedo_suelo{suf}.json")))
    J = d["J_baja_tesis_n_m2_s"]; filas = []
    F, lo, hi = espectro(suf); col_t = next(c for c in F if "seco" in c and "tesis" in c)
    for etq, v in d["corridas"].items():
        w = w_de(etq)
        if w is None: continue
        norm = J / v["N_incidentes"]; c = f"Sube, {etq} (MEIGA)"
        reg = {r: {"flujo": en_region(F[c], lo, hi, r),
                   "n": en_region(F[c], lo, hi, r) / norm,                       # cruces hacia arriba (conteos)
                   "tesis": en_region(F[col_t], lo, hi, r)} for r in REG}
        filas.append({"etiqueta": etq, "w": w, "carpeta": v["carpeta"], "N": v["N_incidentes"],
                      "albedo": v["albedo_por_incidente"], "cruces": v["cruces_sube"],
                      "creados": v["fraccion_creados_en_el_suelo"], "origen": v["origen_de_los_que_suben"], "reg": reg})
    filas.sort(key=lambda f: f["w"]); assert filas[0]["w"] == 0, "la primera corrida debe ser el seco"
    S = filas[0]
    for f in filas:
        f["tg"], f["tv"], f["rho"] = f["w"] / (1 - f["w"]), f["w"] * RHO(f["w"]), RHO(f["w"])
        f["cociente"] = {r: f["reg"][r]["flujo"] / S["reg"][r]["flujo"] if S["reg"][r]["n"] > 0 else float("nan") for r in REG}
        f["err"] = {r: f["cociente"][r] * np.sqrt(1 / f["reg"][r]["n"] + (0 if f is S else 1 / S["reg"][r]["n"]))
                    if f["reg"][r]["n"] > 0 and S["reg"][r]["n"] > 0 else float("nan") for r in REG}
        f["cociente_albedo"] = f["albedo"] / S["albedo"]
        f["err_albedo"] = f["cociente_albedo"] * np.sqrt(1 / f["cruces"] + (0 if f is S else 1 / S["cruces"]))
    return d, filas

def banda(suf, lo_, hi_):
    t = np.genfromtxt(os.path.join(RES, f"espectros_albedo{suf}.tsv"), delimiter="\t", names=True, encoding="utf-8",
                      deletechars="")
    n = t.dtype.names; lo, hi = t[n[0]], t[n[1]]; du = np.log(hi / lo); m = (lo >= lo_ * 0.999) & (hi <= hi_ * 1.001)
    return {c: float(np.sum(t[c][m] * du[m])) for c in n[2:]}

dC, C = cargar("")                 # corridas completas
dV, V = cargar("_validacion")      # mismos neutrones
out = {"desilets_literatura": dict(zip(("a0", "a1", "a2"), DES)), "completas": [], "validacion": [], "ajustes": {}}
for nom, F in (("completas", C), ("validacion", V)):
    out[nom] = [{k: f[k] for k in ("etiqueta", "w", "tg", "tv", "rho", "N", "albedo", "creados", "cociente", "err",
                                   "cociente_albedo", "err_albedo")} | {"flujo": {r: f["reg"][r]["flujo"] for r in REG}}
                for f in F]
# ajustes de la forma de Desilets a los cocientes de los mismos neutrones (validación), con sus errores
tg = np.array([f["tg"] for f in V])
for r in AJUSTE:
    y = np.array([f["cociente"][r] for f in V]); e = np.array([max(f["err"][r], 1e-3) for f in V])
    p, cv = curve_fit(desilets, tg, y, p0=DES, sigma=e, absolute_sigma=True, maxfev=20000)
    out["ajustes"][r] = {"a0": p[0], "a1": p[1], "a2": p[2], "err": np.sqrt(np.diag(cv)).tolist(),
                         "residuo_max": float(np.max(np.abs(y - desilets(tg, *p)))),
                         "chi2": float(np.sum(((y - desilets(tg, *p)) / e) ** 2)), "ndf": int(len(y) - 3),
                         "literatura": [float(desilets(t, *DES)) for t in tg]}
bd = {suf: banda(suf, 1e-8, 1e-5) for suf in ("", "_validacion")}
out["banda_10meV_10eV"] = bd

# --- tabla de corridas: archivos, bytes, manifiesto y tiempo (del disco, o la tabla guardada) ---
TC = os.path.join(RES, "corridas_suelo.json")
corr = json.load(open(TC)) if os.path.exists(TC) else {}
if a.carpetas:
    for f in C:
        d = f["carpeta"]
        if not os.path.isdir(d): continue
        lst = sorted(((os.path.getsize(os.path.join(r, x)), "./" + os.path.relpath(os.path.join(r, x), d))
                      for r, _, fs in os.walk(d) for x in fs), key=lambda t: t[1].encode())
        man = hashlib.md5("".join(f"{s} {p}\n" for s, p in lst).encode()).hexdigest()
        tiempos = []
        for log in sorted(glob.glob(os.path.join(d, "parte*", "Flujo-parte*.txt"))):
            m = re.findall(r"Time taken by program is : ([0-9.]+)", open(log, errors="replace").read())
            if m: tiempos.append(float(m[-1]))
        corr[f["etiqueta"]] = {"carpeta": os.path.basename(d), "archivos": len(lst), "bytes": sum(s for s, _ in lst),
                               "manifiesto": man, "partes": len(tiempos), "tiempo_parte_s": tiempos}
    json.dump(corr, open(TC, "w"), indent=2)
out["corridas"] = corr
json.dump(out, open(os.path.join(RES, "curva_humedad.json"), "w"), indent=2, ensure_ascii=False)

# --- figura 3: cocientes por región frente a la humedad, con la forma de Desilets ---
col = COLOR                                                    # sin los colores de los medios
HUM_COL = {5: "#1f5fbf", 10: "#17becf", 15: "#8c564b", 25: "#e377c2", 30: "#bcbd22"}
fig, ax = plt.subplots(1, 2, figsize=(13, 5))
tt = np.linspace(0, max(tg) * 1.05, 200)
for r in REG:
    if min(f["reg"][r]["n"] for f in V) < 100: continue            # regiones casi vacías (ultrafríos): solo en la tabla
    ax[0].errorbar(tg, [f["cociente"][r] for f in V], yerr=[f["err"][r] for f in V], fmt="o", color=col[r], capsize=3,
                   label=REG_TXT[r].replace("$<", "< ").replace("$>", "> ").replace("$", "").replace("~", " ").replace("--", "–"))
    if r in out["ajustes"]:
        p = out["ajustes"][r]; ax[0].plot(tt, desilets(tt, p["a0"], p["a1"], p["a2"]), "-", color=col[r], lw=1.2)
ax[0].plot(tt, desilets(tt, *DES), "k--", lw=1.2, label="Desilets et al. (2010), parámetros de la literatura")
ax[0].axhline(1, color="0.6", lw=0.8)
ax[0].set_xlabel(r"Humedad gravimétrica $\theta_g = w/(1-w)$ [g/g]"); ax[0].set_ylabel("Flujo que sube / flujo que sube del suelo seco")
ax[0].set_title("Cociente por región (mismos 50 000 neutrones); líneas: ajuste de la forma de Desilets", fontsize=10)
ax[0].set_ylim(0.35, 1.95); ax[0].grid(alpha=0.3, ls="--"); ax[0].legend(fontsize=8, loc="upper center", ncol=2)
tv = [f["tv"] for f in C]
ax[1].errorbar(tv, [f["albedo"] for f in C], yerr=[f["albedo"] * np.sqrt(1 / max(f["cruces"], 1)) for f in C], fmt="ko-",
               capsize=3, label="MEIGA (corridas completas)")
ax[1].axhline(dC["tesis"]["albedo_por_incidente"], color="#0b0b0b", ls="--", label="suelo seco de la tesis")
ax[1].set_xlabel(r"Agua en volumen $\theta_v$ [cm$^3$/cm$^3$]"); ax[1].set_ylabel("Neutrones que suben por neutrón que baja")
ax[1].set_title("Albedo total del suelo", fontsize=10); ax[1].grid(alpha=0.3, ls="--"); ax[1].legend(fontsize=8)
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig03_cocientes_humedad.{e}"), dpi=170)
plt.close(fig)

# --- figura 4: cociente espectral húmedo/seco por energía (mismos neutrones), 5 intervalos por década ---
t = np.genfromtxt(os.path.join(RES, "espectros_albedo_validacion.tsv"), delimiter="\t", names=True, encoding="utf-8",
                  deletechars="")
n = t.dtype.names; lo, hi = t[n[0]], t[n[1]]; du = np.log(hi / lo)
cols = [c for c in n[2:] if "MEIGA" in c]; seco = next(c for c in cols if "seco" in c.lower())
B2 = np.logspace(-9, 3, 61)
def rebin(y):
    cnt = y * du; return np.array([cnt[(lo >= x0 * 0.999) & (hi <= x1 * 1.001)].sum() for x0, x1 in zip(B2[:-1], B2[1:])])
s = rebin(t[seco]); fig, ax = plt.subplots(figsize=(11, 5))
sombrear(ax, 1e-9, 1e3)
ax.axvspan(1e-8, 1e-5, ymin=0, ymax=0.06, color="0.55", alpha=0.7, zorder=1); ax.text(3e-7, 0.25, "10 meV–10 eV", ha="center", fontsize=8, color="0.2")

for c in cols:
    if c == seco: continue
    h = rebin(t[c]); ok = s > 0
    wh = int(re.search(r"humedo-(\d+)", c.replace("_", " ")).group(1))
    ax.stairs(np.where(ok, h / np.where(ok, s, 1), np.nan), B2, lw=1.6, color=HUM_COL.get(wh, "0.3"),
              label=c.replace("_", " ").replace("Sube, ", "").replace(" (MEIGA)", "").replace(" (parte 1)", "").replace("humedo-", "") + " % de agua")
ax.axhline(1, color="0.5", lw=0.8); ax.set_xscale("log"); ax.set_ylim(0.2, 2.2); ax.set_xlim(1e-9, 1e3)
ax.set_xlabel("Energía cinética $E_n$ [MeV]"); ax.set_ylabel("Flujo que sube: húmedo / seco")
ax.set_title("Cociente espectral húmedo/seco (mismos 50 000 neutrones, 5 intervalos por década)", fontsize=10)
ax.grid(alpha=0.3, ls=":", which="both"); ax.legend(fontsize=9, ncol=3, loc="upper right", bbox_to_anchor=(1, 0.78)); fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig04_cociente_espectral.{e}"), dpi=170)
plt.close(fig)

# --- tablas LaTeX ---
f2 = lambda x: f"{x:.2f}" if x >= 0.01 else f"{x:.1e}"; f3 = lambda x: f"{x:.3f}"
def etq_tex(f): return "seco" if f["w"] == 0 else f"{100 * f['w']:.0f}\\,\\%"
with open(os.path.join(TAB, "corridas.tex"), "w") as fo:
    fo.write("\\begin{tabular}{lrrrrrr}\n\\toprule\nSuelo & $\\rho$ [g/cm$^3$] & Neutrones & Archivos & Tamaño [GB] & Tiempo por parte [h] & Manifiesto \\\\\n\\midrule\n")
    for f in C:
        c = corr.get(f["etiqueta"], {}); tp = c.get("tiempo_parte_s", [])
        Ntex = f"{f['N']:,}".replace(",", "\\,")
        fo.write(f"{etq_tex(f)} & {f['rho']:.3f} & {Ntex}" + (f" & {c['archivos']} & {c['bytes'] / 1e9:.2f}" if c else " & -- & --"))
        fo.write((f" & {min(tp) / 3600:.1f}--{max(tp) / 3600:.1f} & \\texttt{{{c['manifiesto'][:8]}}}" if tp else " & -- & --") + " \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
with open(os.path.join(TAB, "regiones.tex"), "w") as fo:
    RT = [r for r in REG if r != "Ultrafríos"]                   # ultrafríos: < 100 cruces, sin cociente útil
    fo.write("\\begin{tabular}{lrr" + "r" * len(RT) + "rr}\n\\toprule\n")
    fo.write("Suelo & $\\theta_g$ & $\\theta_v$ & " + " & ".join(r for r in RT) + " & Albedo & 10~meV--10~eV \\\\\n")
    fo.write(" & & & " + " & ".join(f"\\scriptsize {TEXTO[r]}" for r in RT) + " & & \\\\\n\\midrule\n")
    bv = list(bd["_validacion"].items())
    for i, f in enumerate(V):
        b = [v for k, v in bv if "MEIGA" in k][i]; b0 = [v for k, v in bv if "MEIGA" in k][0]
        fo.write(f"{etq_tex(f)} & {f['tg']:.3f} & {f['tv']:.3f} & " +
                 " & ".join(f"{f['cociente'][r]:.3f}" + ("" if f["w"] == 0 else f"$\\pm${f['err'][r]:.3f}") for r in RT) +
                 f" & {f['albedo']:.3f} & {b / b0:.3f} \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
with open(os.path.join(TAB, "flujos.tex"), "w") as fo:
    fo.write("\\begin{tabular}{l" + "r" * len(REG) + "r}\n\\toprule\nSuelo & " + " & ".join(REG) + " & Total \\\\\n")
    fo.write(" & " + " & ".join(f"\\scriptsize {TEXTO[r]}" for r in REG) + " & \\\\\n\\midrule\n")
    fo.write("seco (tesis) & " + " & ".join(f2(C[0]["reg"][r]["tesis"]) for r in REG) + f" & {sum(C[0]['reg'][r]['tesis'] for r in REG):.1f} \\\\\n")
    for f in C:
        fo.write(f"{etq_tex(f)} (MEIGA) & " + " & ".join(f2(f["reg"][r]["flujo"]) for r in REG) + f" & {sum(f['reg'][r]['flujo'] for r in REG):.1f} \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
with open(os.path.join(TAB, "origen.tex"), "w") as fo:
    fo.write("\\begin{tabular}{lrrrr}\n\\toprule\nSuelo & Reflejado & neutronInelastic & Otros procesos & Cruces hacia arriba \\\\\n\\midrule\n")
    for f in C:
        o = f["origen"]; tot = sum(o.values()); ref = o.get("incidente reflejado", 0); ni = o.get("creado: neutronInelastic", 0)
        tt_ = f"{tot:,}".replace(",", "\\,")
        fo.write(f"{etq_tex(f)} & {100 * ref / tot:.1f}\\,\\% & {100 * ni / tot:.1f}\\,\\% & {100 * (tot - ref - ni) / tot:.1f}\\,\\% & {tt_} \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
with open(os.path.join(TAB, "ajustes.tex"), "w") as fo:
    fo.write("\\begin{tabular}{lrrrr}\n\\toprule\nRegión & $a_0$ & $a_1$ & $a_2$ & Residuo máx. \\\\\n\\midrule\n")
    fo.write(f"Desilets et al. (2010) & {DES[0]:.4f} & {DES[1]:.3f} & {DES[2]:.3f} & -- \\\\\n")
    for r, p in out["ajustes"].items():
        fo.write(f"{r} (MEIGA) & {p['a0']:.4f}$\\pm${p['err'][0]:.4f} & {p['a1']:.3f}$\\pm${p['err'][1]:.3f} & "
                 f"{p['a2']:.3f}$\\pm${p['err'][2]:.3f} & {p['residuo_max']:.4f} \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")
with open(os.path.join(TAB, "desilets.tex"), "w") as fo:
    fo.write("\\begin{tabular}{lrrrr}\n\\toprule\nSuelo & $\\theta_g$ & Desilets (literatura) & Intermedios (MEIGA) & Diferencia \\\\\n\\midrule\n")
    for f, lit in zip(V, out["ajustes"]["Intermedios"]["literatura"]):
        if f["w"] == 0: continue
        fo.write(f"{etq_tex(f)} & {f['tg']:.3f} & {lit:.3f} & {f['cociente']['Intermedios']:.3f}$\\pm${f['err']['Intermedios']:.3f} & {f['cociente']['Intermedios'] - lit:+.3f} \\\\\n")
    fo.write("\\bottomrule\n\\end{tabular}\n")

# --- cifras para el texto (macros) ---
M = {"albSecoTesis": f3(dC["tesis"]["albedo_por_incidente"]), "albSeco": f3(C[0]["albedo"]), "NHumedades": str(len(C) - 1),
     "humedades": ", ".join(f"{100 * f['w']:.0f}" for f in C[1:]) + "~\\%"}
for r, k in CLAVE.items():
    M[f"secoTesis{k}"] = f3(C[0]["reg"][r]["flujo"] / C[0]["reg"][r]["tesis"])
for f in V[1:]:
    p = int(round(100 * f["w"])); s = NUM.get(p, str(p))
    M[f"alb{s}"] = f3(next(g["albedo"] for g in C if g["w"] == f["w"]))
    for r, k in CLAVE.items():
        M[f"{k}{s}"] = f3(f["cociente"][r])
for r in AJUSTE:
    k = CLAVE[r]
    for i, c in enumerate(("a", "b", "c")): M[f"aj{k}{c}"] = f"{list(out['ajustes'][r].values())[i]:.3f}"
    M[f"ajRes{k}"] = f"{100 * out['ajustes'][r]['residuo_max']:.1f}"
ws = [round(100 * f["w"]) for f in V]
M["bandaMax"] = f"{100 * (max(v for k, v in bd['_validacion'].items() if 'MEIGA' in k) / [v for k, v in bd['_validacion'].items() if 'MEIGA' in k][0] - 1):.0f}"
with open(os.path.join(BASE, "informe", "cifras.tex"), "w") as fo:
    fo.write("% generado por scripts/curva_humedad.py; no editar a mano\n")
    for k, v in M.items(): fo.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")
    fo.write("\\newif\\ifquince\\quince" + ("true" if 15 in ws else "false") + "\n")
print(json.dumps({f["etiqueta"]: {r: round(f["cociente"][r], 3) for r in REG} for f in V}, indent=1, ensure_ascii=False))
print(json.dumps({r: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in p.items() if k != "literatura"} for r, p in out["ajustes"].items()}, indent=1, ensure_ascii=False))
