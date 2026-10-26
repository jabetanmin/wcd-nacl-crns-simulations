#!/usr/bin/env python3
"""
Respuesta del detector a las corridas Am-Be moderado (10 meV-10 eV), haz horizontal a media altura, PMT bajado a
0.3*fWaterHalfHeight (cara plana a 86.45 cm del fondo), en agua pura y con 2.5 y 10 % NaCl (500 000 n por medio).
Eficiencia (Q >= 1 p.e., disparo del prototipo con el factor horizontal común), capturas en el medio y núcleo de la
primera captura, tiempo de captura (tau de la cola exponencial), posición de la captura y carga según la altura;
comparación con el montaje del PMT en la tapa (Analisis-montaje-MEIGA, mismos medios) en la misma banda de energía.
Requiere resultados/eventos_{pura,nacl25,nacl10}_horiz.npz (procesar_montaje.py), respuesta_prototipo_horizontal-PMTbajo.json
y decision_calibracion_muones.json.
-> resultados/resumen_horizontal.json, figuras/fig01..fig04, informe/tablas/*.tex
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG, TAB = (os.path.join(BASE, d) for d in ("resultados", "figuras", os.path.join("informe", "tablas")))
os.makedirs(TAB, exist_ok=True)
TAPA = os.path.join(BASE, "..", "Analisis-montaje-MEIGA", "resultados")
MED = [("pura", "Agua pura", "red"), ("nacl25", "Agua + 2.5 % NaCl", "green"), ("nacl10", "Agua + 10 % NaCl", "darkorange")]
CLAVE_RP = {"pura": "pura", "nacl25": "2.5", "nacl10": "10"}
NUC = {1001: "H", 8016: "O", 8017: "O", 8018: "O", 11023: "Na", 17035: "Cl35", 17037: "Cl37"}
Z_PMT = 86.45                                                 # cara plana del PMT sobre el fondo del agua [cm]
H_AGUA = 133.0
E_BANDA = (0.01, 10.0)                                        # eV
RP = json.load(open(os.path.join(RES, "respuesta_prototipo_horizontal-PMTbajo.json")))
DEC = json.load(open(os.path.join(RES, "decision_calibracion_muones.json")))
K = RP["metodos"]["ventana_trigger"]["k_libre"]["k_ADC_por_pe"]
Q_DISP = 1200 * 2.97 / K                                      # p.e. aprox. del disparo (pico 1200 ADC, Q/A = 2.97)

def tau_cola(t_ns):
    """tau [us] de la cola exponencial: ajuste lineal de ln(cuentas) entre 50 y 600 us"""
    t = t_ns[np.isfinite(t_ns)] / 1000.0
    h, e = np.histogram(t, np.arange(50, 601, 10)); c = 0.5 * (e[1:] + e[:-1]); ok = h > 5
    b, _ = np.polyfit(c[ok], np.log(h[ok]), 1, w=np.sqrt(h[ok]))
    return float(-1 / b)

out = {"k_comun_ADC_por_pe": K, "Q_disparo_pe_aprox": Q_DISP,
       "implementar_calibracion_muones": DEC["implementar_calibracion_muones"], "medios": {}}
D = {}
for m, nom, _ in MED:
    d = dict(np.load(os.path.join(RES, f"eventos_{m}_horiz.npz"))); D[m] = d
    T = dict(np.load(os.path.join(TAPA, f"eventos_{m}.npz")))
    bt = (T["E0_eV"] >= E_BANDA[0]) & (T["E0_eV"] <= E_BANDA[1])
    Q = d["Q"]; n = len(Q); cap = d["ncap_medio"] > 0
    nuc = d["nucleo"][cap]
    fr_nuc = {}
    for u in np.unique(nuc):
        c_ = NUC.get(int(u), str(u)); fr_nuc[c_] = fr_nuc.get(c_, 0.0) + float(np.mean(nuc == u))
    rp = RP["metodos"]["ventana_trigger"]["k_libre"]["fraccion_disparo"][CLAVE_RP[m]]
    zc = d["z_cap_cm"]; zb = np.arange(0, H_AGUA + 0.1, 133 / 7)
    q_z = [float(Q[cap & (zc >= a) & (zc < b)].mean()) for a, b in zip(zb[:-1], zb[1:])]
    out["medios"][m] = {
        "N": int(n), "eps_Q1": float(np.mean(Q >= 1)), "eps_disparo_electronica": rp,
        "eps_Q_disparo_aprox": float(np.mean(Q >= Q_DISP)),
        "eta_cap_medio": float(np.mean(cap)), "eta_cap_total": float(np.mean(d["ncap"] > 0)),
        "Q_media_senal": float(Q[Q >= 1].mean()), "Q_p99_senal": float(np.percentile(Q[Q >= 1], 99)),
        "nucleo_primera_captura": fr_nuc, "t_cap_mediana_us": float(np.nanmedian(d["t_cap_ns"][cap]) / 1000),
        "tau_cola_us": tau_cola(d["t_cap_ns"][cap]),
        "z_cap_media_cm": float(np.nanmean(zc[cap])), "x_cap_media_cm": float(np.nanmean(d["x_cap_cm"][cap])),
        "Q_media_por_altura": {"bordes_cm": zb.tolist(), "Q_media": q_z},
        "tapa_misma_banda": {"N": int(bt.sum()), "eps_Q1": float(np.mean(T["Q"][bt] >= 1)),
                             "eta_cap_medio": float(np.mean(T["ncap_medio"][bt] > 0)),
                             "Q_media_senal": float(T["Q"][bt][T["Q"][bt] >= 1].mean())}}
json.dump(out, open(os.path.join(RES, "resumen_horizontal.json"), "w"), indent=2, ensure_ascii=False)

# --- figuras ---
bq = np.arange(0.5, 80.5, 1)
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
for m, nom, col in MED:
    Q = D[m]["Q"]; T = np.load(os.path.join(TAPA, f"eventos_{m}.npz"))
    bt = (T["E0_eV"] >= E_BANDA[0]) & (T["E0_eV"] <= E_BANDA[1])
    ax[0].stairs(np.histogram(Q, bq)[0] / len(Q), bq, color=col, lw=1.6, label=f"{nom}, PMT bajado")
    ax[0].stairs(np.histogram(T["Q"][bt], bq)[0] / bt.sum(), bq, color=col, lw=1, ls="--", label=f"{nom}, PMT en la tapa")
    s = Q >= 1
    eb = np.logspace(-2, 1, 16); i = np.digitize(D[m]["E0_eV"], eb) - 1
    ef = [np.mean(s[i == j]) for j in range(len(eb) - 1)]
    ax[1].plot(np.sqrt(eb[1:] * eb[:-1]), ef, "o-", color=col, label=nom)
ax[0].axvline(Q_DISP, color="0.4", ls=":", lw=1); ax[0].text(Q_DISP + 0.5, 3e-2, "disparo", fontsize=8, color="0.3")
ax[0].set_yscale("log"); ax[0].set_xlabel("Carga [p.e.]"); ax[0].set_ylabel("Fracción de neutrones incidentes por p.e.")
ax[0].set_title("Carga por neutrón incidente (banda 10 meV–10 eV)", fontsize=10); ax[0].legend(fontsize=7.5); ax[0].grid(alpha=0.3, ls="--")
ax[1].set_xscale("log"); ax[1].set_xlabel("Energía del neutrón incidente [eV]"); ax[1].set_ylabel("Eficiencia $Q\\geq1$ p.e.")
ax[1].set_title("Eficiencia según la energía, PMT bajado", fontsize=10); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3, ls="--")
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig01_carga_eficiencia.{e}"), dpi=170)
plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
nombres = ["H", "Cl35", "Cl37", "Na", "O"]; w = 0.26
for j, (m, nom, col) in enumerate(MED):
    f = out["medios"][m]["nucleo_primera_captura"]
    ax[0].bar(np.arange(len(nombres)) + (j - 1) * w, [f.get(x, 0) for x in nombres], w, color=col, label=nom)
    t = D[m]["t_cap_ns"][D[m]["ncap_medio"] > 0] / 1000
    ax[1].hist(t, bins=np.arange(0, 1001, 10), histtype="step", color=col, lw=1.4,
               label=f"{nom}: τ = {out['medios'][m]['tau_cola_us']:.0f} μs")
ax[0].set_xticks(range(len(nombres))); ax[0].set_xticklabels(["$^1$H", "$^{35}$Cl", "$^{37}$Cl", "$^{23}$Na", "$^{16}$O"])
ax[0].set_ylabel("Fracción de las primeras capturas en el medio"); ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3, ls="--", axis="y")
ax[1].set_yscale("log"); ax[1].set_xlabel("Tiempo de la primera captura [μs]"); ax[1].set_ylabel("Capturas por 10 μs")
ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3, ls="--")
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig02_capturas.{e}"), dpi=170)
plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
d = D["pura"]; cap = d["ncap_medio"] > 0
hh = ax[0].hist2d(d["x_cap_cm"][cap], d["z_cap_cm"][cap], bins=[np.arange(-48, 48.1, 2), np.arange(0, 133.1, 2)], cmap="viridis", cmin=1, norm=LogNorm())
fig.colorbar(hh[3], ax=ax[0], label="Capturas por 2×2 cm")
ax[0].axhline(Z_PMT, color="w", ls="--", lw=1); ax[0].text(-46, Z_PMT + 2, "cara del PMT", color="w", fontsize=8)
ax[0].annotate("haz", xy=(-46, 66.56), xytext=(-46, 40), color="w", fontsize=8, arrowprops=dict(color="w", arrowstyle="->"))
ax[0].set_xlabel("x de la captura [cm]"); ax[0].set_ylabel("z de la captura [cm]"); ax[0].set_title("Agua pura: dónde se capturan (proyección x–z)", fontsize=10)
for m, nom, col in MED:
    r = out["medios"][m]["Q_media_por_altura"]; zb = np.array(r["bordes_cm"])
    ax[1].plot(0.5 * (zb[1:] + zb[:-1]), r["Q_media"], "o-", color=col, label=nom)
ax[1].axvline(Z_PMT, color="0.4", ls="--", lw=1); ax[1].axvline(66.56, color="0.6", ls=":", lw=1)
ax[1].set_xlabel("z de la primera captura [cm]"); ax[1].set_ylabel("Carga media de los capturados [p.e.]")
ax[1].set_title("Carga según la altura de la captura (PMT a 86.45 cm, haz a 66.56 cm)", fontsize=10); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3, ls="--")
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig03_posicion_captura.{e}"), dpi=170)
plt.close(fig)

# --- tablas LaTeX ---
pc = lambda x: f"{100 * x:.2f}".replace(".", ".")
filas = []
for m, nom, _ in MED:
    r = out["medios"][m]; t = r["tapa_misma_banda"]
    filas.append(f"{nom.replace('%', chr(92) + '%')} & {pc(r['eps_Q1'])} & {pc(t['eps_Q1'])} & {100 * r['eps_disparo_electronica']:.3f} & "
                 f"{pc(r['eta_cap_medio'])} & {pc(t['eta_cap_medio'])} & {r['Q_media_senal']:.2f} & {t['Q_media_senal']:.2f} & "
                 f"{r['t_cap_mediana_us']:.0f} & {r['tau_cola_us']:.0f} \\\\")
open(os.path.join(TAB, "respuesta_detector.tex"), "w").write(
    "\\begin{tabular}{lrrrrrrrrr}\n\\toprule\n"
    " & \\multicolumn{2}{c}{$\\varepsilon$ ($Q\\geq1$) [\\%]} & $\\varepsilon_\\text{disp}$ [\\%] & \\multicolumn{2}{c}{$\\eta_\\text{cap}$ [\\%]} & "
    "\\multicolumn{2}{c}{$\\langle Q\\rangle$ [p.e.]} & $t_{1/2}$ & $\\tau$ \\\\\n"
    "Medio & bajado & tapa & bajado & bajado & tapa & bajado & tapa & [$\\mu$s] & [$\\mu$s] \\\\\n\\midrule\n"
    + "\n".join(filas) + "\n\\bottomrule\n\\end{tabular}\n")
filas = []
for m, nom, _ in MED:
    f = out["medios"][m]["nucleo_primera_captura"]
    filas.append(f"{nom.replace('%', chr(92) + '%')} & " + " & ".join(f"{100 * f.get(x, 0):.1f}" for x in nombres) + " \\\\")
open(os.path.join(TAB, "nucleos.tex"), "w").write(
    "\\begin{tabular}{lrrrrr}\n\\toprule\nMedio & $^1$H & $^{35}$Cl & $^{37}$Cl & $^{23}$Na & $^{16}$O \\\\\n\\midrule\n"
    + "\n".join(filas) + "\n\\bottomrule\n\\end{tabular}\n")
C = DEC["comparacion_PMT_tapa"]; filas = []
for met, nm in (("ventana_trigger", "ventana del disparo"), ("robusto", "carga robusta")):
    for pos, np_ in (("tapa", "tapa"), ("bajado", "bajado")):
        c = C[met][pos]
        filas.append(f"{nm} & {np_} & {c['k_libre']:.0f} & {c['N_inc_300s'] / 1e6:.2f} & {c['rms_ln']:.2f} & "
                     f"{c['k_libre_electronica']:.0f} & {c['rms_libre_electronica']:.2f} & {c['k_libre'] / c['k_muones']:.1f} \\\\")
open(os.path.join(TAB, "factores_comunes.tex"), "w").write(
    "\\begin{tabular}{llrrrrrr}\n\\toprule\n & & \\multicolumn{3}{c}{Resolución de 1 p.e.} & \\multicolumn{2}{c}{Electrónica completa} & \\\\\n"
    "Carga exp. & PMT & $k$ [ADC/p.e.] & $N$ [$10^6$] & rms & $k$ [ADC/p.e.] & rms & $k/k_\\mu$ \\\\\n\\midrule\n"
    + "\n".join(filas) + "\n\\bottomrule\n\\end{tabular}\n")
print(json.dumps({m: {k: v for k, v in r.items() if k != "Q_media_por_altura"} for m, r in out["medios"].items()}, indent=1, ensure_ascii=False))
