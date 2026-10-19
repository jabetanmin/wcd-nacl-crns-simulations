#!/usr/bin/env python3
"""Analisis de las corridas tipo Sidelnik (MEIGA, 500 MeV horizontales) y comparacion con
Sidelnik et al., Adv. Space Res. 65 (2020) 2216 (Tabla 2 y Figs. 2-6).

Lee resultados/<medio>.npz (procesar_corrida.py); escribe resultados/resumen.json y figuras/.
Uso: analizar.py [medio ...]   (por defecto: los .npz que existan de pura, nacl25, nacl5, nacl10)
"""
import os, sys, json, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estilo

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES, FIG = os.path.join(R, "resultados"), os.path.join(R, "figuras")
TODOS = ["pura", "nacl25", "nacl5", "nacl10"]
ETQ = {"pura": "Agua pura", "nacl25": "Agua + 2,5 % NaCl", "nacl5": "Agua + 5 % NaCl", "nacl10": "Agua + 10 % NaCl"}
COL = {"pura": "#e34948", "nacl25": "#1baf7a", "nacl5": "#7b1fa2", "nacl10": "#eda100"}   # colores de Sidelnik
SIDELNIK = {"pura": (25.18, 8.4), "nacl25": (26.73, 8.0), "nacl5": (27.65, 7.7), "nacl10": (29.26, 7.3)}
BORDE = -48.0            # cara interna del agua por donde entra el haz [cm]
ENTRADA = np.array([-48.0, 0.0, 66.562])
E_CHER = 0.264           # MeV, umbral Cherenkov e- en agua (n = 1,33)
MED = [m for m in (sys.argv[1:] or TODOS) if os.path.exists(os.path.join(RES, f"{m}.npz"))]
plt.rcParams.update({"font.size": 10, "axes.edgecolor": "#52514e", "axes.grid": True, "grid.color": "#e4e3df",
                     "grid.linewidth": 0.6, "lines.linewidth": 1.5, "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "savefig.dpi": 160})
S, D = {}, {}


def savefig(fig, n, rect=None):
    fig.tight_layout(rect=rect) if rect else fig.tight_layout(); fig.savefig(os.path.join(FIG, n + ".png")); fig.savefig(os.path.join(FIG, n + ".pdf")); plt.close(fig)


def bi(k, n):
    p = k / n
    return [float(p), float(np.sqrt(p * (1 - p) / n))]


def me(a):
    a = np.asarray(a, float)
    return [float(a.mean()), float(a.std(ddof=1) / np.sqrt(len(a)))]


def pico(x, h, ventana=5):
    """posicion del maximo: histograma suavizado + parabola sobre los 5 bins centrales"""
    hs = np.convolve(h, np.ones(ventana) / ventana, mode="same")
    i = int(np.argmax(hs))
    j = slice(max(i - 2, 0), i + 3)
    a, b, c = np.polyfit(x[j], hs[j], 2)
    return float(-b / (2 * a)) if a < 0 else float(x[i])


AGUA = ("Water", "SaltyWater")
NUC = {(1, 1): "H", (1, 2): "H2", (8, 16): "O16", (8, 17): "O17", (8, 18): "O18", (11, 23): "Na23",
       (17, 35): "Cl35", (17, 37): "Cl37"}

for m in MED:
    z = np.load(os.path.join(RES, f"{m}.npz"), allow_pickle=False)
    N = int(z["N"]); s = S.setdefault(m, {}); s["N"] = N; d = D.setdefault(m, {})
    # ---------------- capturas ----------------
    mat = z["cap_material"]; agua = np.char.startswith(mat, "Water") | np.char.startswith(mat, "SaltyWater")
    run = z["cap_run_id"]
    s["capturas_total"] = int(len(run)); s["capturas_en_agua"] = int(agua.sum())
    s["capturas_por_material"] = dict(collections.Counter(mat).most_common())
    s["capturas_por_neutron_agua"] = float(agua.sum() / N)
    s["P_al_menos_1_captura_agua"] = bi(len(np.unique(run[agua])), N)
    prim = z["cap_track_id"] == 1
    s["P_primario_capturado"] = bi(int((prim & agua).sum()), N)
    Z, A = z["cap_target_Z"], z["cap_target_A"]
    nuc = np.array([NUC.get((int(a), int(b)), f"Z{a}A{b}") for a, b in zip(Z, A)])
    s["capturas_agua_por_nucleo"] = {k: [int(v), v / agua.sum()] for k, v in collections.Counter(nuc[agua]).most_common()}
    x, y, zz = z["cap_post_x_cm"], z["cap_post_y_cm"], z["cap_post_z_cm"]
    dist = (x - BORDE)[agua]
    d3 = np.sqrt((x - ENTRADA[0]) ** 2 + (y - ENTRADA[1]) ** 2 + (zz - ENTRADA[2]) ** 2)[agua]
    xb = np.arange(0, 100.01, 0.5); xc = 0.5 * (xb[1:] + xb[:-1])
    h = np.histogram(dist, xb)[0]
    s["distancia_max_absorcion_cm"] = pico(xc, h)
    s["distancia_media_cm"] = float(dist.mean()); s["distancia_mediana_cm"] = float(np.median(dist))
    s["distancia3D_max_absorcion_cm"] = pico(xc, np.histogram(d3, xb)[0])
    d.update(dist=dist, d3=d3, xc=xc, hdist=h)
    alt = os.path.join(RES, f"{m}_distancias.npz")      # distancias_alternativas.py
    if os.path.exists(alt):
        za = np.load(alt)
        for k in ["d_vertice", "d_inel_primario"]:
            v = za[k][np.isfinite(za[k])]
            hv = np.histogram(v, xb)[0]
            s[f"{k}_max_cm"] = pico(xc, hv); s[f"{k}_mediana_cm"] = float(np.median(v))
            d["h_" + k] = hv
    t = z["cap_global_time_ns"][agua] / 1e3   # us
    tb = np.logspace(-1, 4, 101); ht = np.histogram(t, tb)[0]; tcen = np.sqrt(tb[1:] * tb[:-1])
    sel = (tcen > 20) & (tcen < 1000) & (ht > 0)
    p = np.polyfit(tcen[sel], np.log(ht[sel] / np.diff(tb)[sel]), 1, w=np.sqrt(ht[sel]))
    s["tau_captura_us"] = float(-1 / p[0]); s["tiempo_captura_mediana_us"] = float(np.median(t))
    d.update(t=t)
    ek = z["cap_pre_energy_MeV"][agua] * 1e9   # meV
    s["E_captura_mediana_meV"] = float(np.median(ek)); s["frac_captura_epitermica_gt_0.5eV"] = float((ek > 500).mean())
    d["ecap"] = ek
    # ---------------- gammas de captura ----------------
    sc_run, sc_trk, part, E = z["sc_run"], z["sc_ptrk"], z["sc_part"], z["sc_E"]
    g = part == "gamma"
    clave = sc_run.astype(np.int64) * 10_000_000 + sc_trk
    ckey = run.astype(np.int64) * 10_000_000 + z["cap_track_id"]
    nmap = dict(zip(ckey, nuc))
    gn = np.array([nmap.get(k, "?") for k in clave[g]])
    s["gamma_captura_por_neutron"] = float(g.sum() / N)
    s["E_gamma_captura_por_neutron_MeV"] = float(E[g].sum() / N)
    u, c = np.unique(np.round(E[g], 4), return_counts=True)
    s["lineas_captura_top"] = [[float(e), int(n)] for n, e in sorted(zip(c, u), reverse=True)[:12]]
    d.update(gcapE=E[g], gcapN=gn)
    # ---------------- primario ----------------
    pp, px = z["prim1_proc"], z["prim1_x"]
    s["primario_primera_interaccion"] = dict(collections.Counter(pp))
    s["primario_inelastica_en_agua"] = bi(len(np.unique(z["prim_inel_run"])), N)
    di = z["prim_inel_x"] - BORDE
    s["profundidad_inelastica_primario_media_cm"] = float(di.mean())
    d["dinel"] = di
    # ---------------- espectros ----------------
    EB, GB = z["EB"], z["GB"]
    H = {k[2:]: z[k] for k in z.files if k.startswith("H_")}
    d.update(EB=EB, GB=GB, H=H)
    gcre = {k.split("|")[1]: v for k, v in H.items() if k.startswith("gcre|")}
    s["gammas_creados_agua_por_neutron"] = float(sum(v.sum() for v in gcre.values()) / N)
    s["gammas_creados_por_proceso"] = {k: float(v.sum() / N) for k, v in sorted(gcre.items(), key=lambda kv: -kv[1].sum())[:8]}
    ec = 0.5 * (GB[1:] + GB[:-1])
    egl = {k: v for k, v in H.items() if k.startswith("egamlin|")}
    eT = sum(egl.values())
    s["e_de_gammas_por_neutron"] = float(eT.sum() / N)
    s["e_de_gammas_frac_sobre_umbral"] = float(eT[ec > E_CHER].sum() / eT.sum())
    s["e_de_gammas_por_proceso"] = {k.split("|", 1)[1]: float(v.sum() / N) for k, v in egl.items()}
    # ---------------- Cherenkov y carga ----------------
    nch = z["cher_n_por_run"]; q = z["Q"]
    s["fotones_cherenkov_por_neutron"] = me(nch)
    s["Q_media"] = me(q); s["eficiencia_Q_ge1"] = bi(int((q >= 1).sum()), N)
    s["Q_sobre_fotones"] = float(q.sum() / nch.sum())
    s["carga_igual_json"] = bool(np.array_equal(q, z["json_Q"])) if "json_Q" in z.files else None   # corrida interrumpida: sin output.json.gz
    tpe = z["pe_t_ns"]; eve = z["pe_ev"]
    vent = {"<1 us": (0, 1e3), "1 us-1 ms": (1e3, 1e6), ">1 ms": (1e6, np.inf)}
    s["carga_por_ventana"] = {}
    for k, (a, b) in vent.items():
        w = (tpe >= a) & (tpe < b)
        qq = np.bincount(eve[w], minlength=N)
        s["carga_por_ventana"][k] = {"frac": float(w.mean()), "eficiencia_ge1": float((qq >= 1).mean())}
    d.update(q=q, nch=nch, tpe=tpe)
    print(m, "listo")

json.dump(S, open(os.path.join(RES, "resumen.json"), "w"), indent=1, ensure_ascii=False, default=float)

# ===================== figuras =====================
ref2 = os.path.join(R, "datos", "fig2_agua_pura_digitalizada.csv")
estilo.aplicar()
from matplotlib.lines import Line2D
fig, axs = plt.subplots(1, 2, figsize=(8, 5.4))
for m in MED:
    dd = D[m]
    axs[0].step(dd["xc"], dd["hdist"], where="mid", color=COL[m], label=f"{ETQ[m]} (máx. {S[m]['distancia_max_absorcion_cm']:.1f} cm)")
    axs[0].axvline(SIDELNIK[m][1], color=COL[m], ls=":", lw=1)
    if "h_d_vertice" in dd:
        axs[1].step(dd["xc"], dd["h_d_vertice"] / dd["h_d_vertice"].max(), where="mid", color=COL[m],
                    label=f"{ETQ[m]}: vértice → captura (máx. {S[m]['d_vertice_max_cm']:.1f} cm)")
        axs[1].step(dd["xc"], dd["h_d_inel_primario"] / dd["h_d_inel_primario"].max(), where="mid", color=COL[m], ls="--", lw=1,
                    label=f"{ETQ[m]}: inelástica del primario → captura (máx. {S[m]['d_inel_primario_max_cm']:.1f} cm)")
    axs[1].step(dd["xc"], dd["hdist"] / dd["hdist"].max(), where="mid", color=COL[m], ls=":", lw=1, label=f"{ETQ[m]}: cara de entrada → captura")
if os.path.exists(ref2) and "pura" in MED:
    r = np.loadtxt(ref2, delimiter=",", skiprows=1)
    axs[1].plot(r[:, 0], r[:, 1] / r[:, 1].max(), "o", ms=3, color="#52514e", label="Sidelnik Fig. 2, agua pura (digitalizada)")
axs[0].set_xlabel("Distancia desde la cara de entrada [cm]"); axs[0].set_ylabel("Capturas / 0,5 cm"); axs[0].set_ylim(0, 1.15 * max(D[m_]["hdist"].max() for m_ in MED))
axs[0].set_title("(a) Distancia a lo largo del haz\n(punteada: máximo de Sidelnik)", fontsize=10)
axs[1].set_xlabel("Distancia [cm]"); axs[1].set_ylabel("Normalizado al máximo"); axs[1].set_xlim(0, 100)
axs[1].set_title("(b) Definiciones alternativas\nfrente a la Fig. 2 de Sidelnik", fontsize=10)
fig.legend(handles=[Line2D([], [], color="#0b0b0b", lw=1.5, label="vértice del n → captura"),
                       Line2D([], [], color="#0b0b0b", ls="--", lw=1, label="inelástica → captura"),
                       Line2D([], [], color="#0b0b0b", ls=":", lw=1, label="cara de entrada → captura"),
                       Line2D([], [], color="#52514e", marker="o", ms=4, ls="", label="Sidelnik, Fig. 2")], loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.0), frameon=False, handlelength=1.6)
estilo.leyenda_medios(fig, MED, COL, ETQ, abajo=0.11)
savefig(fig, "fig01_distancia_captura", rect=(0, 0.18, 1, 1))

fig, axs = plt.subplots(1, 2, figsize=(8, 4.0))
for m in MED:
    dd = D[m]; GB = dd["GB"]; gc = 0.5 * (GB[1:] + GB[:-1])
    hg = sum(v for k, v in dd["H"].items() if k.startswith("gcrelin|"))
    axs[0].step(gc, hg / S[m]["N"], where="mid", color=COL[m], lw=0.8, label=ETQ[m])
    # Fig. 4 de Sidelnik: cuentas acumuladas de derecha a izquierda
    axs[1].step(gc, np.cumsum(hg[::-1])[::-1] / S[m]["N"], where="mid", color=COL[m], label=ETQ[m])
axs[0].set_yscale("log"); axs[0].set_xlim(0, 12); axs[0].set_xlabel("Energía del gamma creado en el agua [MeV]"); axs[0].set_ylabel("Gammas / 5 keV / neutrón")
axs[1].set_yscale("log"); axs[1].set_xlim(0, 20); axs[1].set_xlabel("Energía [MeV]"); axs[1].set_ylabel("N(≥E) por neutrón")
estilo.leyenda_medios(fig, MED, COL, ETQ)
savefig(fig, "fig02_espectro_gamma", rect=(0, 0.09, 1, 1))

fig, axs = plt.subplots(1, 2, figsize=(8, 4.0))
for m in MED:
    dd = D[m]; GB = dd["GB"]; gc = 0.5 * (GB[1:] + GB[:-1])
    he = sum(v for k, v in dd["H"].items() if k.startswith("egamlin|"))
    axs[0].step(gc, he / S[m]["N"], where="mid", color=COL[m], lw=0.8, label=ETQ[m])
    EB = dd["EB"]; ce = np.sqrt(EB[1:] * EB[:-1]); w = np.log(EB[1:] / EB[:-1])
    hl = sum(v for k, v in dd["H"].items() if k.startswith("egam|"))
    axs[1].step(ce, hl / S[m]["N"] / w, where="mid", color=COL[m], label=ETQ[m])
for e, t in [(1.994, "borde 2,223 MeV"), (8.33, "borde 8,58 MeV")]:
    axs[0].axvline(e, color="#8a8984", ls=":", lw=1); axs[0].text(e + 0.15, 0.97, t, transform=axs[0].get_xaxis_transform(), fontsize=8.5, rotation=90, va="top")
axs[0].set_yscale("log"); axs[0].set_xlim(0, 12); axs[0].set_xlabel("Energía del electrón creado por un gamma [MeV]"); axs[0].set_ylabel("e$^\\pm$ / 5 keV / neutrón")
axs[1].set_xscale("log"); axs[1].set_yscale("log"); axs[1].axvline(E_CHER, color="#8a8984", ls=":", lw=1)
axs[1].set_xlabel("Energía del electrón [MeV]"); axs[1].set_ylabel("dN/d(ln E) por neutrón")
estilo.leyenda_medios(fig, MED, COL, ETQ)
savefig(fig, "fig03_espectro_electrones", rect=(0, 0.09, 1, 1))

ref6 = os.path.join(R, "datos", "fig6_sidelnik_digitalizada_700pts.csv")
fig, axs = plt.subplots(1, 2, figsize=(8, 4.4))
qb = np.arange(0, 1000, 10)
for m in MED:
    q = D[m]["q"]
    h = np.histogram(q[q >= 1], qb)[0]
    axs[0].step(qb[:-1] + 5, h / h.sum(), where="mid", color=COL[m], label=f"{ETQ[m]}: MEIGA")
    tb = np.logspace(-1, 19, 201)
    ht = np.histogram(D[m]["tpe"], tb)[0]
    axs[1].step(np.sqrt(tb[1:] * tb[:-1]), ht / np.diff(tb) / S[m]["N"], where="mid", color=COL[m], label=ETQ[m])
if os.path.exists(ref6):
    import pandas as pd
    r = pd.read_csv(ref6)
    cols = {"pura": "Pure_H2O_counts_digitized", "nacl25": "NaCl_2p5_counts_digitized", "nacl5": "NaCl_5_counts_digitized", "nacl10": "NaCl_10_counts_digitized"}
    for m in MED:
        c = r[cols[m]].to_numpy(); xs = r.Numero_de_fotones.to_numpy()
        hb = np.interp(qb[:-1] + 5, xs, c, left=np.nan, right=np.nan)
        axs[0].plot(qb[:-1] + 5, hb / np.nansum(hb), "--", color=COL[m], lw=1, label=f"{ETQ[m]}: Sidelnik, Fig. 6")
axs[0].set_yscale("log"); axs[0].set_xlabel("Fotoelectrones en el PMT (Q ≥ 1)"); axs[0].set_ylabel("Fracción / 10 p.e.")
axs[0].set_title("(a) Carga en el PMT frente a la Fig. 6", fontsize=10.5); axs[1].set_title("(b) Tiempo de llegada de los p.e.", fontsize=10.5)
axs[0].legend(handles=[Line2D([], [], color="#0b0b0b", label="MEIGA"), Line2D([], [], color="#0b0b0b", ls="--", lw=1, label="Sidelnik, Fig. 6")], loc="upper right")
estilo.leyenda_medios(fig, MED, COL, ETQ)
axs[1].set_xscale("log"); axs[1].set_yscale("log"); axs[1].set_xlabel("Tiempo de llegada del fotoelectrón [ns]"); axs[1].set_ylabel("p.e. / ns / neutrón")
for tt, l in [(1e3, "1 µs"), (1e6, "1 ms")]:
    axs[1].axvline(tt, color="#c3c2b7", ls=":", lw=1)
savefig(fig, "fig04_carga_y_tiempos", rect=(0, 0.08, 1, 1))

fig, axs = plt.subplots(1, 2, figsize=(8, 4.3))
for m in MED:
    axs[0].hist(D[m]["t"], bins=np.logspace(-1, 4, 101), histtype="step", color=COL[m], lw=1.4,
                label=f"{ETQ[m]} (τ = {S[m]['tau_captura_us']:.0f} µs)")
    axs[1].hist(D[m]["ecap"], bins=np.logspace(-1, 9, 101), histtype="step", color=COL[m], lw=1.4, label=ETQ[m])
axs[0].set_xscale("log"); axs[0].set_yscale("log"); axs[0].set_xlabel("Tiempo de captura [µs]"); axs[0].set_ylabel("Capturas / bin")
axs[1].set_xscale("log"); axs[1].set_yscale("log"); axs[1].axvline(25.3, color="#8a8984", ls=":", lw=1)
axs[1].set_ylim(top=3e5)
axs[1].annotate("25,3 meV\n(kT a 20 °C)", xy=(25.3, 1.2e5), xytext=(2e3, 6e4), fontsize=10.5, color="#555555", va="center",
                arrowprops=dict(arrowstyle="->", color="#555555", lw=0.9))
axs[1].set_xlabel("Energía al capturarse [meV]"); axs[1].set_ylabel("Capturas / bin")
fig.legend(*axs[0].get_legend_handles_labels(), loc="lower center", ncol=2, frameon=False)
savefig(fig, "fig05_tiempo_energia_captura", rect=(0, 0.14, 1, 1))
print(json.dumps(S, indent=1, ensure_ascii=False, default=float)[:7000])
