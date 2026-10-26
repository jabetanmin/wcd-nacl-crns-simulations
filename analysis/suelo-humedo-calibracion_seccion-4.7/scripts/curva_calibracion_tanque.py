#!/usr/bin/env python3
"""
Curva de calibración del WCD por simulación directa (Corrida-tanque-albedo) y comparación con el plegado.

Flujo que SUBE: los 100 000 neutrones de cada suelo inyectados en el tanque con su energía y dirección (entran por la
base y por el costado). Por evento se lee la carga (Carga-total.txt, en el orden de flujo.txt) y el punto de entrada
(z = −0.6 cm: base; si no, costado). Cuentas/h = 3600 · tasa al tanque · fracción con señal; la tasa por la base y
por el costado viene de flujos/entrada_tanque.json (corte rasante en 85°; 80° y sin corte dan el sistemático).
Flujo que BAJA (igual para todas las humedades, J de resultados/albedo_suelo.json, 12 h):
  - por la tapa: del plegado (curva_calibracion_wcd.json, modo completo), escalado de R = 48 a 48.5 cm;
  - por el costado: J · 2 R H · <tan θ · ε_costado(E)> sobre los 200 000 neutrones que bajan
    (200000N-Bga-baja-sobre-suelo.txt), con ε_costado(E) medida en los que suben por el costado (todas las
    humedades juntas). Aproximación: el costado responde igual a un neutrón que baja que a uno que sube.
Umbrales: Q >= 1 p.e. (eps), Q >= 5 p.e. (eps_Q5) y la ventana 1 <= Q < 20 p.e. (ventana).
Uso: curva_calibracion_tanque.py [--tanque <resultados del tanque>] [--entrada <entrada_tanque.json>] [--baja <archivo>]
     (variables TANQUE_RES, ENTRADA_TANQUE, FLUJO_BAJA)
-> resultados/curva_calibracion_tanque.json, resultados/eficiencia_base_costado.tsv,
   figuras/fig13_calibracion_directa, fig14_eficiencia_base_costado, informe/tablas/{calibracion_directa,
   calibracion_directa_resumen}.tex
"""
import argparse, json, os, re
import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG, TAB = (os.path.join(BASE, d) for d in ("resultados", "figuras", os.path.join("informe", "tablas")))
REPO = os.environ.get("REPO_TESIS", os.path.abspath(os.path.join(BASE, "..", "..")))
ap = argparse.ArgumentParser()
ap.add_argument("--tanque", default=os.environ.get("TANQUE_RES", "Corrida-tanque-albedo-resultados-2.5-5"))
ap.add_argument("--entrada", default=os.environ.get("ENTRADA_TANQUE", os.path.join(REPO, "simulations", "tanque-albedo", "flujos", "entrada_tanque.json")))
ap.add_argument("--baja", default=os.environ.get("FLUJO_BAJA", os.path.join(BASE, "flujos", "200000N-Bga-baja-sobre-suelo.txt")))
a = ap.parse_args()

M_N, RC, H = 939.565, 0.485, 1.35                                 # MeV; m (cilindro de entrada)
J_BAJA = json.load(open(os.path.join(RES, "albedo_suelo.json")))["J_baja_tesis_n_m2_s"]   # n m^-2 s^-1
# las tasas de flujos/entrada_tanque.json se calcularon con la normalización anterior (3600 s): se reescalan
from normalizacion import J_BAJA_ANTES_N_M2_S
ESC = J_BAJA / J_BAJA_ANTES_N_M2_S
MEDIOS = [("AguaPura", "Agua pura"), ("Agua25NaCl", "2.5 % NaCl"), ("Agua5NaCl", "5 % NaCl"), ("Agua10NaCl", "10 % NaCl")]
COL = {"Agua pura": "red", "2.5 % NaCl": "green", "5 % NaCl": "purple", "10 % NaCl": "darkorange"}   # colores de los medios en la tesis
SUELOS = ["seco", "agua05", "agua10", "agua15", "agua25", "agua30"]
UMB = {"eps": (1, None), "eps_Q5": (5, None), "ventana": (1, 20)}
EB = np.logspace(-10, 4, 15)                                       # una década por intervalo [MeV]
ent = json.load(open(a.entrada))
for _v in ent["suelos"].values():
    for _k in ("tasa_base_n_s", "tasa_costado_n_s", "tasa_al_tanque_n_s"): _v[_k] *= ESC
    _v["tasa_costado_n_s_por_corte"] = {k: x * ESC for k, x in _v["tasa_costado_n_s_por_corte"].items()}
FW = json.load(open(os.path.join(RES, "curva_calibracion_wcd.json")))
fold, fe = FW["resultados"]["completo"], FW["eficiencias"]

def energia(p):                                                   # p en GeV/c -> energía cinética en MeV
    return np.sqrt((1e3 * p) ** 2 + M_N ** 2) - M_N

def leer(carpeta):
    """Por evento: energía [MeV], ángulo cenital [°], entra por el costado, carga [p.e.]."""
    E, th, cost, Q = [], [], [], []
    for k in (1, 2, 3, 4):
        d = os.path.join(carpeta, f"parte{k}")
        f = np.loadtxt(os.path.join(d, "flujo.txt"), usecols=(1, 2, 3, 6), ndmin=2)
        q = np.loadtxt(os.path.join(d, "Datos-simulacion", "Carga-total.txt"), usecols=1, ndmin=1)
        assert len(f) == len(q), f"{d}: {len(f)} neutrones y {len(q)} cargas"
        p = np.linalg.norm(f[:, :3], axis=1)
        E.append(energia(p)); th.append(np.degrees(np.arccos(np.abs(f[:, 2]) / p))); cost.append(f[:, 3] > 0); Q.append(q)
    return np.concatenate(E), np.concatenate(th), np.concatenate(cost), np.concatenate(Q)

def senal(Q, u):
    lo, hi = UMB[u]; return (Q >= lo) & (Q < hi) if hi else Q >= lo

# --- neutrones que bajan: tan θ y energía de cada cruce del plano ---
b = np.loadtxt(a.baja, usecols=(1, 2, 3)); pb = np.linalg.norm(b, axis=1)
Eb, thb = energia(pb), np.degrees(np.arccos(np.abs(b[:, 2]) / pb)); tanb = np.tan(np.radians(np.minimum(thb, 89.99)))
tasa_baja_costado = {c: J_BAJA * 2 * RC * H * float(np.mean(np.where(thb <= c, tanb, 0.0))) for c in (80, 85, 90)}
tasa_baja_tapa = J_BAJA * np.pi * RC ** 2

out = {"J_baja_n_m2_s": J_BAJA, "cilindro_m": {"R": RC, "H": H}, "tasa_baja_tapa_n_s": tasa_baja_tapa,
       "tasa_baja_costado_n_s_por_corte": tasa_baja_costado, "medios": {}}
eff_tab = []
for mr, mn in MEDIOS:
    runs = {s: os.path.join(a.tanque, f"{s}-{mr}-100000N") for s in SUELOS}
    if not all(os.path.isdir(v) for v in runs.values()): continue
    ev = {s: leer(v) for s, v in runs.items()}
    # ε(E) por la base y por el costado, con todas las humedades juntas
    allE, allth, allc, allQ = (np.concatenate([ev[s][i] for s in SUELOS]) for i in range(4))
    ie = np.clip(np.digitize(allE, EB) - 1, 0, len(EB) - 2)
    eps_E = {}
    for u in UMB:
        s_ = senal(allQ, u); eps_E[u] = {}
        for lado, m in (("base", ~allc), ("costado", allc)):
            n = np.bincount(ie[m], minlength=len(EB) - 1); k = np.bincount(ie[m], weights=s_[m], minlength=len(EB) - 1)
            eps_E[u][lado] = (n, k)
    for i in range(len(EB) - 1):
        r = [f"{mn}", f"{EB[i]:.0e}", f"{EB[i + 1]:.0e}"]
        for lado in ("base", "costado"):
            n, k = eps_E["eps"][lado]; r += [str(int(n[i])), f"{k[i] / n[i]:.4f}" if n[i] else "nan"]
        eff_tab.append(r)
    def eps_costado(u, E):                                       # interpolación en log E de los intervalos con >= 30 eventos
        n, k = eps_E[u]["costado"]; ok = n >= 30; x = np.log10(np.sqrt(EB[:-1] * EB[1:]))[ok]; y = (k[ok] / n[ok])
        return np.interp(np.log10(E), x, y)
    R = {}
    for u in UMB:
        eb_cost = {c: 3600 * J_BAJA * 2 * RC * H * float(np.mean(np.where(thb <= c, tanb, 0) * eps_costado(u, Eb))) for c in (80, 85)}
        eb_cost[90] = eb_cost[85] * tasa_baja_costado[90] / tasa_baja_costado[85]   # los de 85–90° con la ε de los de menos de 85°
        # cota alta del costado que baja (solo Q >= 1): con la ε vertical del plegado, que sí cubre 1 GeV
        eb_cost_vert = (3600 * J_BAJA * 2 * RC * H * float(np.mean(np.where(thb <= 85, tanb, 0) *
                        np.interp(np.log10(Eb), np.log10(fe[mn]["E_MeV"]), fe[mn]["eps"]))) if u == "eps" and mn in fe else None)
        fo = fold[mn][u]["filas"] if mn in fold else None
        filas = []
        for s in SUELOS:
            E, th, c, Q = ev[s]; sg = senal(Q, u); e = ent["suelos"][s]
            fb, fc = float(sg[~c].mean()), float(sg[c].mean())
            sube = {}
            for cor in (80, 85, 90):
                mc = c & (th <= min(cor, 85)); ec = float(sg[mc].mean())
                sube[cor] = 3600 * (e["tasa_base_n_s"] * fb + e["tasa_costado_n_s_por_corte"][str(cor)] * ec)
            i = SUELOS.index(s)
            tapa = fo[i]["baja_h"] * (RC / 0.48) ** 2 if fo else np.nan
            filas.append({"suelo": s, "w": e["w"], "tg": e["w"] / (1 - e["w"]),
                          "eps_todos": float(sg.mean()), "eps_base": fb, "eps_costado": fc,
                          "sube_base_h": 3600 * e["tasa_base_n_s"] * fb, "sube_costado_h": sube[85] - 3600 * e["tasa_base_n_s"] * fb,
                          "sube_h": sube[85], "sube_h_por_corte": sube, "baja_tapa_h": tapa, "baja_costado_h": eb_cost[85],
                          "total_h": tapa + eb_cost[85] + sube[85],
                          "total_h_por_corte": {cor: tapa + eb_cost[cor] + sube[cor] for cor in (80, 85, 90)},
                          "sube_plegado_h": fo[i]["sube_h"] if fo else None, "total_plegado_h": fo[i]["total_h"] if fo else None,
                          "err_rel_sube": float(np.sqrt(sg.sum()) / max(sg.sum(), 1))})
        N0 = filas[0]["total_h"]; tg = np.array([f["tg"] for f in filas]); y = np.array([f["total_h"] / N0 for f in filas])
        try: p, _ = curve_fit(lambda t, a0, a1, a2: a1 + a0 / (t + a2), tg, y, p0=(0.05, 0.8, 0.15), maxfev=50000)
        except RuntimeError: p = (np.nan,) * 3
        caida = {cor: float(1 - filas[-1]["total_h_por_corte"][cor] / filas[0]["total_h_por_corte"][cor]) for cor in (80, 85, 90)}
        if eb_cost_vert is not None:
            t0, t30 = (filas[i]["total_h"] - eb_cost[85] + eb_cost_vert for i in (0, -1))
            caida["baja_costado_vertical"] = float(1 - t30 / t0)
        R[u] = {"filas": filas, "N0_h": N0, "baja_costado_vertical_h": eb_cost_vert, "cociente": y.tolist(), "a0": p[0], "a1": p[1], "a2": p[2],
                "caida_seco_30": float(1 - y[-1]), "caida_seco_30_por_corte": caida,
                "fraccion_baja_seco": (filas[0]["baja_tapa_h"] + filas[0]["baja_costado_h"]) / N0,
                "cociente_plegado": fold[mn][u]["cociente"] if mn in fold else None,
                "caida_plegado": fold[mn][u]["caida_seco_30"] if mn in fold else None,
                "eps_costado_E": {"E_lo": EB[:-1].tolist(), "n": eps_E[u]["costado"][0].tolist(), "k": eps_E[u]["costado"][1].tolist()},
                "eps_base_E": {"n": eps_E[u]["base"][0].tolist(), "k": eps_E[u]["base"][1].tolist()}}
    out["medios"][mn] = R
    print(f"{mn:11s} Q>=1: N0 = {R['eps']['N0_h']:.0f}/h, del que baja {100 * R['eps']['fraccion_baja_seco']:.0f} %, "
          f"caída seco-30 % = {100 * R['eps']['caida_seco_30']:.1f} % (plegado {100 * R['eps']['caida_plegado']:.1f} %), "
          f"corte 80/90: {100 * R['eps']['caida_seco_30_por_corte'][80]:.1f}/{100 * R['eps']['caida_seco_30_por_corte'][90]:.1f} %, "
          f"costado que baja con ε vertical: {100 * R['eps']['caida_seco_30_por_corte']['baja_costado_vertical']:.1f} % "
          f"({R['eps']['baja_costado_vertical_h']:.0f}/h frente a {R['eps']['filas'][0]['baja_costado_h']:.0f}/h)")
json.dump(out, open(os.path.join(RES, "curva_calibracion_tanque.json"), "w"), indent=2, ensure_ascii=False)
with open(os.path.join(RES, "eficiencia_base_costado.tsv"), "w") as fo_:
    fo_.write("# medio\tE_lo_MeV\tE_hi_MeV\tN_base\teps_base_Q1\tN_costado\teps_costado_Q1\n")
    for r in eff_tab: fo_.write("\t".join(r) + "\n")
M = out["medios"]
if not M: raise SystemExit("no hay corridas completas del tanque")
lab = {"seco": "seco", "agua05": "5\\,\\%", "agua10": "10\\,\\%", "agua15": "15\\,\\%", "agua25": "25\\,\\%", "agua30": "30\\,\\%"}

# --- figura 13: curva directa frente al plegado, y de dónde vienen las cuentas ---
fig, ax = plt.subplots(1, 3, figsize=(15, 4.8))
for k, (u, tit) in enumerate((("eps", "Q ≥ 1 p.e."), ("ventana", "1 ≤ Q < 20 p.e."))):
    for mn, R in M.items():
        tg = [f["tg"] for f in R[u]["filas"]]
        lo_ = [f["total_h_por_corte"][80] / R[u]["filas"][0]["total_h_por_corte"][80] for f in R[u]["filas"]]
        hi_ = [f["total_h_por_corte"][90] / R[u]["filas"][0]["total_h_por_corte"][90] for f in R[u]["filas"]]
        ax[k].fill_between(tg, lo_, hi_, color=COL[mn], alpha=0.15, lw=0)
        ax[k].plot(tg, R[u]["cociente"], "o-", color=COL[mn], lw=2, ms=6, label=f"{mn}: directa")
        if R[u]["cociente_plegado"]: ax[k].plot(tg, R[u]["cociente_plegado"], "s--", color=COL[mn], lw=1.2, ms=4, mfc="white", label=f"{mn}: plegado")
    ax[k].set_xlabel(r"Humedad gravimétrica $\theta_g$ [g/g]"); ax[k].set_ylabel(r"$N/N_0$ (húmedo / seco)")
    ax[k].set_title(f"Curva de calibración, {tit}", fontsize=10); ax[k].grid(alpha=0.3, ls="--"); ax[k].legend(fontsize=7.5)
mn0 = "Agua pura" if "Agua pura" in M else next(iter(M)); F = M[mn0]["eps"]["filas"]; tg = [f["tg"] for f in F]
for key, cc, nom in (("baja_tapa_h", "#a8a6a0", "baja, por la tapa"), ("baja_costado_h", "#5f5e5a", "baja, por el costado"),
                     ("sube_base_h", "#1f5fbf", "sube, por la base"), ("sube_costado_h", "#17becf", "sube, por el costado")):
    ax[2].plot(tg, [f[key] / 1e3 for f in F], "o-", color=cc, lw=1.8, label=nom)
ax[2].plot(tg, [f["sube_plegado_h"] / 1e3 for f in F], "s:", color="#8c564b", lw=1.4, label="sube, plegado (solo la base)")
ax[2].set_xlabel(r"Humedad gravimétrica $\theta_g$ [g/g]"); ax[2].set_ylabel("Cuentas por hora [miles], Q ≥ 1 p.e.")
ax[2].set_title(f"De dónde vienen las cuentas ({mn0.lower()})", fontsize=10); ax[2].grid(alpha=0.3, ls="--"); ax[2].legend(fontsize=7.5)
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig13_calibracion_directa.{e}"), dpi=170)
plt.close(fig)

# --- figura 14: eficiencia por la base y por el costado frente a la del plegado (incidencia vertical por la tapa) ---
fig, ax = plt.subplots(figsize=(9, 5.5)); Ec = np.sqrt(EB[:-1] * EB[1:])
for mn, R in M.items():
    for lado, ls, mk in (("base", "-", "o"), ("costado", "--", "s")):
        n = np.array(R["eps"][f"eps_{lado}_E"]["n"]); k = np.array(R["eps"][f"eps_{lado}_E"]["k"]); ok = n >= 30
        ax.errorbar(Ec[ok], k[ok] / n[ok], yerr=np.sqrt(k[ok] * (1 - k[ok] / n[ok])) / n[ok], fmt=mk + ls, color=COL[mn], ms=5,
                    lw=1.6, capsize=2, mfc="white" if lado == "costado" else COL[mn], label=f"{mn}, por {'la ' if lado == 'base' else 'el '}{lado}")
    if mn in fe: ax.plot(fe[mn]["E_MeV"], fe[mn]["eps"], ":", color=COL[mn], lw=1.4, label=f"{mn}, vertical por la tapa (plegado)")
ax.set_xscale("log"); ax.set_xlim(1e-10, 1e4); ax.set_ylim(0, 1.0); ax.grid(alpha=0.3, ls=":", which="both")
ax.set_xlabel("Energía cinética del neutrón $E_n$ [MeV]"); ax.set_ylabel("Fracción con Q ≥ 1 p.e.")
ax.set_title("Eficiencia del WCD según por dónde entra el neutrón", fontsize=11); ax.legend(fontsize=7.5, loc="upper left")
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig14_eficiencia_base_costado.{e}"), dpi=170)
plt.close(fig)

# --- tablas ---
with open(os.path.join(TAB, "calibracion_directa.tex"), "w") as t:
    t.write("\\begin{tabular}{ll rrrr r rr}\n\\toprule\n & & \\multicolumn{2}{c}{baja [cuentas/h]} & \\multicolumn{2}{c}{sube [cuentas/h]} & total & \\multicolumn{2}{c}{$N/N_0$} \\\\\n"
            "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}\\cmidrule(lr){8-9}\nMedio & Suelo & tapa & costado & base & costado & [cuentas/h] & directa & plegado \\\\\n\\midrule\n")
    for mn, R in M.items():
        for i, f in enumerate(R["eps"]["filas"]):
            t.write(f"{mn.replace('%', chr(92) + '%') if i == 0 else ''} & {lab[f['suelo']]} & {f['baja_tapa_h']:.0f} & {f['baja_costado_h']:.0f} & "
                    f"{f['sube_base_h']:.0f} & {f['sube_costado_h']:.0f} & {f['total_h']:.0f} & {R['eps']['cociente'][i]:.3f} & "
                    f"{R['eps']['cociente_plegado'][i]:.3f} \\\\\n")
        t.write("\\midrule\n" if mn != list(M)[-1] else "")
    t.write("\\bottomrule\n\\end{tabular}\n")
with open(os.path.join(TAB, "calibracion_directa_resumen.tex"), "w") as t:
    t.write("\\begin{tabular}{l rr rrr rr r}\n\\toprule\n & \\multicolumn{2}{c}{$N_0$ [cuentas/h]} & \\multicolumn{3}{c}{caída seco--30\\,\\%, $Q\\ge1$} & "
            "\\multicolumn{2}{c}{caída, ventana} & del flujo \\\\\n\\cmidrule(lr){2-3}\\cmidrule(lr){4-6}\\cmidrule(lr){7-8}\n"
            "Medio & directa & plegado & directa & intervalo & plegado & directa & plegado & que baja \\\\\n\\midrule\n")
    for mn, R in M.items():
        c1, cv = R["eps"], R["ventana"]; v = [x for x in c1["caida_seco_30_por_corte"].values()] + [c1["caida_seco_30"]]
        t.write(f"{mn.replace('%', chr(92) + '%')} & {c1['N0_h']:.0f} & {c1['filas'][0]['total_plegado_h']:.0f} & "
                f"{100 * c1['caida_seco_30']:.1f}\\,\\% & {100 * min(v):.1f}--{100 * max(v):.1f}\\,\\% & {100 * c1['caida_plegado']:.1f}\\,\\% & "
                f"{100 * cv['caida_seco_30']:.1f}\\,\\% & {100 * cv['caida_plegado']:.1f}\\,\\% & {100 * c1['fraccion_baja_seco']:.0f}\\,\\% \\\\\n")
    t.write("\\bottomrule\n\\end{tabular}\n")
print("tasas del flujo que baja [n/s]: tapa", round(tasa_baja_tapa, 1), "costado", {k: round(v, 1) for k, v in tasa_baja_costado.items()})
