#!/usr/bin/env python3
"""
Histogramas de carga SIN FONDO del detector prototipo (agua pura, 2.5 % y 10 % NaCl), con el método de
las carpetas Comparacion-robusta-fondo-neutrones-* (notebook analisis-datos-Flujo-Completo-Bga, celdas 27-31):
  * cada disparo (32 muestras, canal 1): línea base = mediana de las 20 primeras muestras,
    carga = suma de (señal - línea base) positiva en toda la traza; todos los disparos, sin corte de pico;
  * 6000 bins entre 10 y 60000 ADC; diferencia = cuentas(fuente) - cuentas(fondo).
Se reproduce la diferencia original (sin normalizar) y se compara con los Diferencia-datos-*.dat
del TOSHIBA; luego se normaliza por tiempo (300 s) y se calculan neutrones detectados, incidentes y capturados.
-> resultados/sin_fondo_<medio>.tsv, sin_fondo_resumen.json, figuras fig11-fig12
"""
import gzip, json, os, subprocess
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DP = os.path.join(os.environ.get("TOSHIBA", os.path.join("/media", os.environ.get("USER", "ubuntu"), "TOSHIBA EXT")), "Simulaciones-Jaime-2024", "Detector-prototipo")   # disco: variable TOSHIBA
BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
MED = {"pura": ("pura", "Agua pura", "red", "Comparacion-robusta-fondo-neutrones-agua-pura/Diferencia-datos-A-pura.dat"),
       "nacl25": ("2.5", "Agua + 2.5 % de NaCl", "green", "Comparacion-robusta-fondo-neutrones-A25NaCl/Diferencia-datos-A-25NaCl.dat"),
       "nacl10": ("10", "Agua + 10 % de NaCl", "orange", "Comparacion-robusta-fondo-neutrones-agua-10NaCl/Diferencia-datos-A-10NaCl.dat")}
BINS, MIN_X, MAX_X = 6000, 10, 60000
PE = 3.95 / 1000
T_REF = 300.0
Q_UMBRAL_PE = 12          # umbral común de análisis (por encima del codo de disparo de los tres medios)
plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "legend.fontsize": 9})


def cargas_robustas(f):
    """Carga positiva de cada disparo, calculada en awk (scripts/carga_robusta.awk)."""
    awk = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carga_robusta.awk")
    out = subprocess.run(["mawk", "-f", awk, f], capture_output=True, text=True,
                         env={"LC_ALL": "C", "PATH": os.environ["PATH"]}).stdout
    return np.array(out.split(), dtype=float)


T = json.load(open(os.path.join(RES, "experimento_tomas.json")))
cache = os.path.join(RES, "cargas_robustas.npz")
if os.path.exists(cache):
    Qr = dict(np.load(cache))
else:
    Qr = {}
    for m, (pref, *_rest) in MED.items():
        for t in ("neutrones", "fondo"):
            Qr[f"{pref}_{t}"] = cargas_robustas(os.path.join(DP, f"{pref}_{t}.dat"))
            print(pref, t, len(Qr[f"{pref}_{t}"]), flush=True)
    np.savez_compressed(cache, **Qr)

# ---------------- respuesta simulada por neutrón incidente (montaje: haz + halo + fondo)
cab = open(os.path.join(RES, "histograma_carga_simulado.tsv")).readline().split()
S = np.loadtxt(os.path.join(RES, "histograma_carga_simulado.tsv"), skiprows=1)
col = lambda n: S[:, cab.index(n)]
d = json.load(open(os.path.join(RES, "resumen_corridas.json")))
N_COMP = {"haz": 130711, "halo": 167963, "fondo": 74598}; N_MOD = sum(N_COMP.values())

# P(captura | Q >= umbral) del haz, desde las corridas AmBe (eventos con número de capturas)
def p_cap_haz(m):
    q = np.load(os.path.join(RES, f"carga_{m}.npz"))["carga"]
    with gzip.open(os.path.join(RES, f"eventos_{m}.tsv.gz"), "rt") as f:
        nc = np.array([int(l.split("\t")[7]) for l in f])
    s = q >= Q_UMBRAL_PE
    return float(np.mean(nc[s] >= 1)), float(np.mean(s & (nc == 0)))
pc = {m: p_cap_haz(m) for m in ("nacl25", "nacl10")}
# agua pura: la probabilidad de señal sin captura (gammas inelásticos) se toma de 2.5 % (no depende del NaCl)
qp = np.load(os.path.join(RES, "carga_pura.npz"))["carga"]
eps_p = float(np.mean(qp >= Q_UMBRAL_PE))
pc["pura"] = (1 - pc["nacl25"][1] / eps_p, pc["nacl25"][1])

R, H = {}, {}
for m, (pref, nom, c, orig) in MED.items():
    qn, qf = Qr[f"{pref}_neutrones"], Qr[f"{pref}_fondo"]
    tn, tf = T[f"{pref}_neutrones"]["duracion_s"], T[f"{pref}_fondo"]["duracion_s"]
    hn, e = np.histogram(qn, bins=BINS, range=(MIN_X, MAX_X)); hf, _ = np.histogram(qf, bins=BINS, range=(MIN_X, MAX_X))
    cen = 0.5 * (e[1:] + e[:-1])
    dif_orig = hn - hf
    ref = np.loadtxt(os.path.join(DP, orig))
    neto = (hn / tn - hf / tf) * T_REF
    u = np.sqrt(hn / tn ** 2 + hf / tf ** 2) * T_REF
    H[m] = {"cen": cen, "dif_orig": dif_orig, "neto": neto, "u": u}
    np.savetxt(os.path.join(RES, f"sin_fondo_{m}.tsv"), np.column_stack([cen, cen * PE, dif_orig, neto, u]),
               fmt="%.4f\t%.5f\t%d\t%.4f\t%.4f",
               header="ADC_centro\tpe_centro\tdiferencia_sin_normalizar(notebook)\tneto_300s(normalizado por tiempo)\tu_neto")
    # muones del fondo para la calibración del método robusto
    hm, em = np.histogram(qf, bins=np.arange(0, 200000, 2000)); cm = 0.5 * (em[1:] + em[:-1])
    sel = cm > 20000; mu = float(cm[sel][np.argmax(np.convolve(hm, np.ones(5) / 5, "same")[sel])])
    # conteos
    thr = Q_UMBRAL_PE / PE
    an, af = np.sum(qn >= thr), np.sum(qf >= thr)
    det = (an / tn - af / tf) * T_REF; udet = np.sqrt(an / tn ** 2 + af / tf ** 2) * T_REF
    h5 = col(f"5min_total_{m}"); hr = col(f"corrida_{m}")
    eff = h5[Q_UMBRAL_PE:].sum() / N_MOD                  # eficiencia simulada por neutrón incidente (montaje)
    N_inc = det / eff
    eta = d["escalado"][m]["total"]["capturas"] / N_MOD    # capturas por neutrón incidente (montaje)
    # P(captura | señal) del montaje: haz desde AmBe, halo y fondo ~1 (sin otra fuente de luz)
    seff = {cp: col(f"5min_{cp}_{m}")[Q_UMBRAL_PE:].sum() for cp in N_COMP}
    p_cd = (seff["haz"] * pc[m][0] + seff["halo"] + seff["fondo"]) / sum(seff.values())
    R[m] = {"duracion_fuente_s": tn, "duracion_fondo_s": tf,
            "disparos_fuente": int(len(qn)), "disparos_fondo": int(len(qf)),
            "reproduce_archivo_original": bool(np.array_equal(dif_orig, ref[:, 1].astype(int))),
            "max_dif_vs_original": int(np.max(np.abs(dif_orig - ref[:, 1]))),
            "netos_todos_300s": float((len(qn) / tn - len(qf) / tf) * T_REF),
            "netos_sin_normalizar_notebook": int(dif_orig.sum()),
            "pico_muones_fondo_pe": mu * PE,
            "umbral_pe": Q_UMBRAL_PE,
            "detectados_300s": float(det), "u_detectados": float(udet),
            "tasa_detectados_s": float(det / T_REF),
            "eficiencia_sim_por_neutron": float(eff),
            "neutrones_incidentes_300s": float(N_inc), "u_neutrones_incidentes": float(udet / eff),
            "pct_de_emitidos_1Ci": float(100 * N_inc / 6.66e8),
            "capturas_por_neutron_sim": float(eta),
            "neutrones_capturados_300s": float(N_inc * eta),
            "P_captura_dado_detectado": float(p_cd),
            "detectados_con_captura_300s": float(det * p_cd),
            "detectados_sin_captura_300s": float(det * (1 - p_cd)),
            "carga_media_detectados_pe": float(((qn[qn >= thr].sum() / tn - qf[qf >= thr].sum() / tf) / (an / tn - af / tf)) * PE),
            "carga_media_sim_pe": float((np.arange(len(h5))[Q_UMBRAL_PE:] * h5[Q_UMBRAL_PE:]).sum() / h5[Q_UMBRAL_PE:].sum())}
    print(m, json.dumps(R[m], ensure_ascii=False), flush=True)
json.dump({"medios": R, "P_cap_haz": pc}, open(os.path.join(RES, "sin_fondo_resumen.json"), "w"), indent=2, ensure_ascii=False)

# ---------------- figuras
fig, ax = plt.subplots(figsize=(10, 6))
for m, (pref, nom, c, _) in MED.items():
    ax.plot(H[m]["cen"], H[m]["dif_orig"], color=c, lw=1, label=nom)
ax.set_yscale("log"); ax.set_ylim(10, 1e5); ax.set_xlim(0, 40000); ax.set_xlabel("ADC [u.a.]"); ax.set_ylabel("Cuentas [u.a.]")
ax.grid(alpha=0.3); ax.legend(); ax.set_title("Reproducción: fuente − fondo sin normalizar (como Comparacion-3-configuraciones.png)", fontsize=10)
fig.tight_layout(); [fig.savefig(os.path.join(FIG, f"fig11_sin_fondo_reproduccion.{x}"), dpi=200) for x in ("png", "pdf")]; plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(14, 5))
b1 = np.arange(0, 201, 1)
for m, (pref, nom, c, _) in MED.items():
    pe = H[m]["cen"] * PE
    nb = np.histogram(pe, bins=b1, weights=H[m]["neto"])[0]
    ax[0].step(b1[:-1] + 0.5, nb, where="mid", color=c, lw=1.4, label=f"{nom}: {R[m]['detectados_300s']:,.0f} detectados (Q≥{Q_UMBRAL_PE} p.e.)".replace(",", " "))
    h5 = col(f"5min_total_{m}")
    f = R[m]["neutrones_incidentes_300s"] / N_MOD
    ax[1].step(b1[:-1] + 0.5, nb, where="mid", color=c, lw=1.2, label=f"Exp: {nom}")
    ax[1].plot(np.arange(len(h5))[1:], h5[1:] * f, "--", color=c, lw=1.4, label=f"Sim ×{f:.0f} (N_inc = {R[m]['neutrones_incidentes_300s']/1e6:.1f} M)")
for a in ax:
    a.set_yscale("log"); a.set_xlim(0, 120); a.set_ylim(1, 3e5); a.set_xlabel("Carga [p.e.] (ADC·3.95/1000)"); a.grid(alpha=0.3, ls="--"); a.legend(fontsize=8)
    a.axvline(Q_UMBRAL_PE, color="0.5", lw=0.7)
ax[0].set_ylabel("Cuentas netas en 300 s por p.e."); ax[0].set_title("Sin fondo, normalizado por tiempo", fontsize=10)
ax[1].set_title("Simulación escalada al número de neutrones incidentes inferido", fontsize=10)
fig.tight_layout(); [fig.savefig(os.path.join(FIG, f"fig12_sin_fondo_normalizado.{x}"), dpi=200) for x in ("png", "pdf")]; plt.close(fig)
