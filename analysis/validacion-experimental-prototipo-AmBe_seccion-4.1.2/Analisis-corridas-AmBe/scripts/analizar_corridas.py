#!/usr/bin/env python3
"""
Análisis comparativo de las corridas MEIGA con la fuente 241Am-Be (agua pura, 2.5 % y 10 % NaCl;
1 637 458 neutrones cada una, inyección vertical por la tapa: disco r <= 20 cm a z = 1.5 m) y
escalado al montaje blindado (373 272 neutrones en 5 min: haz 130 711 / halo 167 963 / fondo 74 598).

  * Haz: respuesta de las corridas AmBe, repondera cada evento por su energía inicial para pasar del
    espectro del archivo de entrada (437 energías discretas, sesgo por densidad de puntos) al
    ISO 8529 digitalizado.
  * Halo (0.5 eV-100 keV, 1/E) y fondo (1e-4-0.5 eV, maxwelliano kT = 25.3 meV): respuesta de la
    Campaña 1 (16 energías monoenergéticas, misma inyección por la tapa, 100 000 neutrones cada una),
    promediada con el espectro de cada componente (interpolación lineal en log E, constante fuera de
    la malla).
Entradas: resultados/carga_<m>.npz (extraer_carga.py), eventos/capturas/residuos/gammas/inelasticos
(procesar_pasos.sh, solo NaCl), tablas de la Campaña 1 del repositorio.
Salidas: resultados/resumen_corridas.json, escalado_373272.tsv/.json, figuras fig01-fig06.
"""
import gzip, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(AQUI, ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
FUENTE = os.path.abspath(os.path.join(BASE, "..", "Analisis-fuente-AmBe", "resultados"))
REPO = os.path.join(os.environ.get("REPO_TESIS", os.path.join(os.path.expanduser("~"), "Documentos", "Documetos-Jaime-Betancourt", "Repositorio-Jaime-tesis", "wt-revision-tesis")), "analysis")
C1_CARGA = f"{REPO}/campana-1_respuesta-electromagnetica_seccion-4.2/resultados_carga/resumen_carga_campana.tsv"
MEDIOS = {"pura": ("Agua pura", "Agua-pura", "red"), "nacl25": ("Agua + 2.5 % NaCl", "Agua+2.5NaCl", "green"),
          "nacl10": ("Agua + 10 % NaCl", "Agua+10NaCl", "darkorange")}
N_COMP = {"haz": 130711, "halo": 167963, "fondo": 74598}
Z_TAPA = 1330.0                 # mm, cara interna de la tapa (agua de 0 a 1330 mm)
NUCLEO = {"deuteron": "H", "Cl36": "35Cl", "Cl38": "37Cl", "Na24": "23Na", "O17": "16O"}
plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "legend.fontsize": 9.5})


def guardar(fig, nombre):
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{nombre}.{ext}"), dpi=200)
    plt.close(fig)


def leer_tsv(ruta, dtype=None):
    with gzip.open(ruta, "rt") as f:
        return [l.rstrip("\n").split("\t") for l in f]


# ------------------------------------------------------------------ pesos ISO 8529
E1, E2, L = np.loadtxt(os.path.join(FUENTE, "ISO8529_AmBe_digitalizado.txt"), unpack=True)
NORM_ISO = np.sum(L * np.log(E2 / E1))
E_ISO = float(np.sum(L * (E2 - E1)) / NORM_ISO)


def masa_iso(a, b):
    """Probabilidad ISO en [a, b] (B_E·E constante por grupo)."""
    s = 0.0
    for e1, e2, l in zip(E1, E2, L):
        lo, hi = max(a, e1), min(b, e2)
        if hi > lo:
            s += l * np.log(hi / lo)
    return s / NORM_ISO


def pesos_iso(E0):
    """Peso por evento: P_ISO(celda de E_j) / (n_j / N), celdas = puntos medios entre energías."""
    Er = np.round(E0, 5)
    u, inv, n = np.unique(Er, return_inverse=True, return_counts=True)
    bordes = np.concatenate([[u[0] - (u[1] - u[0]) / 2], 0.5 * (u[1:] + u[:-1]), [u[-1] + (u[-1] - u[-2]) / 2]])
    P = np.array([masa_iso(bordes[j], bordes[j + 1]) for j in range(len(u))])
    w = P / (n / len(E0))
    return w[inv], len(u), float(P.sum())


def media_w(x, w):
    x = np.asarray(x, float)
    m = np.sum(w * x) / np.sum(w)
    neff = np.sum(w) ** 2 / np.sum(w ** 2)
    u = np.sqrt(np.sum(w * (x - m) ** 2) / np.sum(w) / neff)
    return float(m), float(u)


# ------------------------------------------------------------------ corridas AmBe
R, ev_data = {}, {}
for m, (nom, _, _) in MEDIOS.items():
    d = np.load(os.path.join(RES, f"carga_{m}.npz"))
    E0, Q = d["E0"], d["carga"]
    w, n_e, p_tot = pesos_iso(E0)
    r = {"eventos": int(len(E0)), "energias_distintas": n_e, "fraccion_ISO_cubierta": p_tot,
         "E_media_archivo": float(E0.mean()), "E_media_reponderada": media_w(E0, w)[0], "E_media_ISO": E_ISO,
         "neff_pesos": float(np.sum(w) ** 2 / np.sum(w ** 2))}
    for nombre_obs, x in (("eps_Q1", Q >= 1), ("eps_Q3", Q >= 3), ("eps_Q5", Q >= 5), ("eps_Q10", Q >= 10), ("eps_Q20", Q >= 20)):
        r[nombre_obs] = {"archivo": float(np.mean(x)), "u_archivo": float(np.sqrt(np.mean(x) * (1 - np.mean(x)) / len(x))),
                         "ISO": media_w(x, w)[0], "u_ISO": media_w(x, w)[1]}
    s = Q >= 1
    r["Q_media_senal"] = {"archivo": float(Q[s].mean()), "ISO": media_w(Q[s], w[s])[0], "u_ISO": media_w(Q[s], w[s])[1]}
    r["Q_media_por_neutron"] = {"archivo": float(Q.mean()), "ISO": media_w(Q, w)[0]}
    ev_data[m] = {"E0": E0, "Q": Q, "w": w}
    R[m] = r

# --- capturas (solo NaCl, con datos crudos)
for m in ("nacl25", "nacl10"):
    ev = leer_tsv(os.path.join(RES, f"eventos_{m}.tsv.gz"))
    E0e = np.array([float(x[1]) for x in ev]); fin = np.array([x[3] for x in ev])
    nel = np.array([int(x[2]) for x in ev])
    pf = np.array([[float(x[4]), float(x[5]), float(x[6])] for x in ev])
    E0, Q, w = ev_data[m]["E0"], ev_data[m]["Q"], ev_data[m]["w"]
    assert len(ev) == len(E0), (m, len(ev), len(E0))
    assert np.allclose(E0e, E0, rtol=2e-5, atol=2e-6), "orden de eventos distinto entre pasos y output.json"
    cap = leer_tsv(os.path.join(RES, f"capturas_{m}.tsv.gz"))
    trk = np.array([int(x[0]) for x in cap]); pc = np.array([[float(x[2]), float(x[3]), float(x[4])] for x in cap])
    resid = leer_tsv(os.path.join(RES, f"residuos_{m}.tsv.gz"))
    pr = np.array([[float(x[1]), float(x[2]), float(x[3])] for x in resid]); nr = [x[0] for x in resid]
    # núcleo de cada captura: residuo en la misma posición (recorrido en paralelo)
    # recorrido en paralelo: el residuo j corresponde a la captura k si está en la misma posición
    igual = lambda a, b: np.max(np.abs(a - b)) <= 1e-3
    nuc, j = [], 0
    for k in range(len(cap)):
        if j < len(resid) and igual(pr[j], pc[k]):
            nuc.append(NUCLEO.get(nr[j], "otros")); j += 1
        elif j + 1 < len(resid) and igual(pr[j + 1], pc[k]):        # residuo sobrante: se salta
            nuc.append(NUCLEO.get(nr[j + 1], "otros")); j += 2
        else:                                                         # captura sin residuo registrado
            nuc.append("sin residuo")
    nuc = np.array(nuc)
    # las capturas están en orden de evento: el evento e tiene ncap_e capturas (todas las trazas)
    ncap = np.array([int(x[7]) for x in ev])
    assert ncap.sum() == len(cap), (ncap.sum(), len(cap))
    evento_de = np.repeat(np.arange(len(E0)), ncap)
    ev_cap = np.where(fin == "nCapture")[0]
    prim = np.where(trk == 1)[0]
    assert len(ev_cap) == len(prim) and np.all(evento_de[prim] == ev_cap), "capturas del primario desalineadas"
    assert np.allclose(pf[ev_cap], pc[prim], atol=2e-3), "posiciones de captura del primario no coinciden"
    sec = np.where(trk != 1)[0]
    ambiguas = 0
    nuc_prim = np.full(len(E0), "", dtype=object); nuc_prim[ev_cap] = nuc[prim]
    en_agua = (pc[:, 2] >= 0) & (pc[:, 2] <= Z_TAPA) & (np.hypot(pc[:, 0], pc[:, 1]) <= 480)
    prof = Z_TAPA - pc[prim, 2]
    r = R[m]
    r["capturas_totales"] = int(len(cap)); r["capturas_primario"] = int(len(prim)); r["capturas_secundarios"] = int(len(sec))
    r["capturas_fuera_del_agua"] = int(np.sum(~en_agua))
    r["fin_primario_pct"] = {p: float(100 * np.mean(fin == p)) for p in np.unique(fin)}
    x = ncap >= 1
    r["eta_cap"] = {"archivo": float(np.mean(x)), "ISO": media_w(x, w)[0], "u_ISO": media_w(x, w)[1]}
    r["capturas_por_neutron"] = {"archivo": float(ncap.mean()), "ISO": media_w(ncap, w)[0]}
    r["P_senal_dada_captura"] = {"archivo": float(np.mean(Q[x] >= 1)), "ISO": media_w(Q[x] >= 1, w[x])[0]}
    r["P_senal_sin_captura"] = float(np.mean(Q[~x] >= 1))
    r["nucleo_captura_pct"] = {k: float(100 * np.mean(nuc == k)) for k in ["H", "35Cl", "37Cl", "23Na", "16O", "otros", "sin residuo"]}
    r["profundidad_captura_primario_mm"] = {"media": float(prof.mean()), "mediana": float(np.median(prof)),
                                            "p25": float(np.percentile(prof, 25)), "p75": float(np.percentile(prof, 75))}
    r["elasticas_hasta_captura_media"] = float(nel[ev_cap].mean())
    ev_data[m].update({"ncap": ncap, "prof": prof, "E0cap": E0[ev_cap], "nuc_prim": nuc_prim, "nucs": nuc})
    g = leer_tsv(os.path.join(RES, f"gammas_captura_{m}.tsv.gz"))
    ev_data[m]["Eg"] = np.array([float(x[3]) for x in g])
    r["gammas_de_captura"] = int(len(g)); r["gammas_por_captura"] = float(len(g) / len(cap))
    print(m, "capturas", len(cap), "primario", len(prim), "secundarios", len(sec),
          "sin residuo", int(np.sum(nuc == "sin residuo")), flush=True)

# ------------------------------------------------------------------ Campaña 1 (halo y fondo)
c1 = {}
with open(C1_CARGA) as f:
    cab = f.readline().rstrip("\n").split("\t")
    for l in f:
        v = dict(zip(cab, l.rstrip("\n").split("\t")))
        c1.setdefault(v["medio"], []).append(v)
KT = 0.0253        # eV


def plegar(medio_c1, obs, espectro, Emin, Emax, n=4000):
    filas = sorted(c1[medio_c1], key=lambda v: float(v["E_meV"]))
    Em = np.array([float(v["E_meV"]) * 1e-3 for v in filas])     # eV (etiquetas de carpeta)
    y = np.array([float(v[obs]) for v in filas])
    E = np.geomspace(Emin, Emax, n)
    yi = np.interp(np.log10(E), np.log10(Em), y)                    # constante fuera de la malla
    phi = espectro(E) * E                                           # densidad por unidad de ln E
    return float(np.trapz(yi * phi, np.log(E)) / np.trapz(phi, np.log(E)))


halo = lambda E: 1 / E
fondo = lambda E: E * np.exp(-E / KT)
RC1 = {}
for m, (nom, mc1, _) in MEDIOS.items():
    RC1[m] = {}
    for comp, esp, a, b in (("halo", halo, 0.5, 1e5), ("fondo", fondo, 1e-4, 0.5)):
        RC1[m][comp] = {o: plegar(mc1, o, esp, a, b) for o in ("eps", "eta_cap", "Q_media_pe", "P_senal_captura",
                                                              "eps_Q3", "eps_Q5", "eps_Q10", "eps_Q20")}
        RC1[m][comp]["u_eps"] = plegar(mc1, "u_eps", esp, a, b)

# ------------------------------------------------------------------ captura del haz en agua pura (estimada)
# La corrida de agua pura no conserva los archivos de pasos: η_cap del haz se estima de dos formas.
#  A) ε = P(s|cap)·η + P(s|sin cap)·(1-η)  con P(s|sin cap) de 2.5 % NaCl y
#     P(s|cap)_pura = P(s|cap)_C1,pura × [P(s|cap)_AmBe / P(s|cap)_C1]_2.5 %
#  B) η_pura = η_2.5,AmBe × (η_C1,pura / η_C1,2.5)   (plegado con el espectro del halo)
r25 = R["nacl25"]
Psin = r25["P_senal_sin_captura"]
Pcap_p = RC1["pura"]["halo"]["P_senal_captura"] * r25["P_senal_dada_captura"]["ISO"] / RC1["nacl25"]["halo"]["P_senal_captura"]
etaA = (R["pura"]["eps_Q1"]["ISO"] - Psin) / (Pcap_p - Psin)
etaB = r25["eta_cap"]["ISO"] * RC1["pura"]["halo"]["eta_cap"] / RC1["nacl25"]["halo"]["eta_cap"]
R["pura"]["eta_cap"] = {"ISO": float(0.5 * (etaA + etaB)), "u_ISO": float(abs(etaA - etaB) / 2),
                        "estimado": True, "metodo_A": float(etaA), "metodo_B": float(etaB),
                        "P_senal_captura_supuesta": float(Pcap_p), "P_senal_sin_captura_supuesta": float(Psin)}

# ------------------------------------------------------------------ escalado a 373 272 neutrones
filas, ESC = [], {}
for m, (nom, _, _) in MEDIOS.items():
    r = R[m]
    resp = {"haz": {"eps": r["eps_Q1"]["ISO"], "u_eps": r["eps_Q1"]["u_ISO"],
                    "eta_cap": r["eta_cap"]["ISO"] if "eta_cap" in r else np.nan,
                    "Q_media_pe": r["Q_media_senal"]["ISO"],
                    "eps_Q20": r["eps_Q20"]["ISO"]},
            "halo": RC1[m]["halo"], "fondo": RC1[m]["fondo"]}
    ESC[m] = {}
    tot = {"senal": 0.0, "capturas": 0.0, "carga": 0.0, "Q20": 0.0}
    for comp, N in N_COMP.items():
        x = resp[comp]
        ns, nc = N * x["eps"], N * x["eta_cap"]
        q = ns * x["Q_media_pe"]
        q20 = N * x["eps_Q20"]
        ESC[m][comp] = {"N": N, "eps": x["eps"], "eta_cap": x["eta_cap"], "Q_media_pe": x["Q_media_pe"],
                        "eventos_senal": ns, "u_eventos_senal": float(np.sqrt(ns + (N * x["u_eps"]) ** 2)),
                        "capturas": nc, "carga_total_pe": q, "eventos_Q20": q20}
        filas.append([nom, comp, N, x["eps"], ns, x["eta_cap"], nc, x["Q_media_pe"], q, q20])
        tot["senal"] += ns; tot["capturas"] += nc if np.isfinite(nc) else np.nan; tot["carga"] += q; tot["Q20"] += q20
    ESC[m]["total"] = {"N": sum(N_COMP.values()), "eventos_senal": tot["senal"], "capturas": tot["capturas"],
                       "carga_total_pe": tot["carga"], "eventos_Q20": tot["Q20"],
                       "eps_global": tot["senal"] / sum(N_COMP.values()), "tasa_senal_por_s": tot["senal"] / 300.0}
    filas.append([nom, "total", sum(N_COMP.values()), tot["senal"] / sum(N_COMP.values()), tot["senal"],
                  tot["capturas"] / sum(N_COMP.values()), tot["capturas"], tot["carga"] / tot["senal"], tot["carga"], tot["Q20"]])
with open(os.path.join(RES, "escalado_373272.tsv"), "w") as f:
    f.write("medio\tcomponente\tN\teps_Q1\teventos_senal\teta_cap\tcapturas\tQ_media_senal_pe\tcarga_total_pe\teventos_Q20\n")
    for fl in filas:
        f.write("\t".join(str(round(v, 6)) if isinstance(v, float) else str(v) for v in fl) + "\n")
json.dump({"corridas": R, "campana1_plegada": RC1, "escalado": ESC}, open(os.path.join(RES, "resumen_corridas.json"), "w"),
          indent=2, ensure_ascii=False, default=float)

# ------------------------------------------------------------------ figuras
# fig01: eficiencia y captura frente a E (Campaña 1 + corridas AmBe por bandas)
Bb = np.array([0.1, 0.3, 0.6, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7, 8, 9, 11])
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
for m, (nom, mc1, col) in MEDIOS.items():
    filas1 = sorted(c1[mc1], key=lambda v: float(v["E_meV"]))
    Ec = np.array([float(v["E_meV"]) * 1e-3 for v in filas1])
    ax[0].plot(Ec, [100 * float(v["eps"]) for v in filas1], "o-", color=col, ms=4, lw=1, label=f"{nom}, Campaña 1")
    ax[1].plot(Ec, [100 * float(v["eta_cap"]) for v in filas1], "o-", color=col, ms=4, lw=1, label=f"{nom}, Campaña 1")
    E0, Q = ev_data[m]["E0"], ev_data[m]["Q"]
    k = np.digitize(E0, Bb) - 1
    c = 0.5 * (Bb[1:] + Bb[:-1]) * 1e6
    ax[0].plot(c, [100 * np.mean(Q[k == i] >= 1) for i in range(len(c))], "s--", color=col, ms=4, mfc="white", label=f"{nom}, AmBe")
    if "ncap" in ev_data[m]:
        nc = ev_data[m]["ncap"]
        ax[1].plot(c, [100 * np.mean(nc[k == i] >= 1) for i in range(len(c))], "s--", color=col, ms=4, mfc="white", label=f"{nom}, AmBe")
ax[0].legend(fontsize=7.5, loc="upper left")
for a, t in zip(ax, ["Eventos con señal, $Q\\geq1$ p.e. [%]", "Eventos con captura [%]"]):
    a.set_xscale("log"); a.set_xlabel("$E_n$ [eV]"); a.set_ylabel(t); a.grid(alpha=0.3, ls="--", which="both")
    a.axvspan(1e-4, 0.5, color="royalblue", alpha=0.07); a.axvspan(0.5, 1e5, color="orange", alpha=0.07)
    a.axvspan(1e5, 1.1e7, color="crimson", alpha=0.05)
ax[0].text(2e-3, 2, "fondo", color="royalblue"); ax[0].text(30, 2, "halo", color="darkorange"); ax[0].text(3e5, 2, "haz", color="crimson")
ax[0].set_ylim(0, 75); ax[1].set_ylim(0, 85); ax[1].legend(fontsize=7.5, ncol=1, loc="upper left")
guardar(fig, "fig01_respuesta_vs_energia")

# fig02: histogramas de carga (archivo vs ISO)
fig, ax = plt.subplots(figsize=(8, 5))
Bq = np.arange(0.5, 201.5, 1)
for m, (nom, _, col) in MEDIOS.items():
    Q, w = ev_data[m]["Q"], ev_data[m]["w"]
    h, _ = np.histogram(Q, bins=Bq); hw, _ = np.histogram(Q, bins=Bq, weights=w)
    ax.plot(Bq[:-1] + 0.5, h / len(Q), color=col, lw=1.5, label=f"{nom}")
    ax.plot(Bq[:-1] + 0.5, hw / w.sum(), color=col, lw=1, ls=":", label=f"{nom}, reponderado ISO")
ax.set_yscale("log"); ax.set_xlim(0, 120); ax.set_xlabel("Carga [p.e.]"); ax.set_ylabel("Fracción de neutrones incidentes")
ax.grid(alpha=0.3, ls="--"); ax.legend(fontsize=8.5)
guardar(fig, "fig02_histograma_carga")

# fig03: núcleo de captura y profundidad (NaCl)
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
cats = ["H", "35Cl", "37Cl", "23Na", "16O", "otros"]
for i, m in enumerate(("nacl25", "nacl10")):
    nom, _, col = MEDIOS[m]
    v = [R[m]["nucleo_captura_pct"][k] for k in cats]
    ax[0].bar(np.arange(len(cats)) + (i - 0.5) * 0.38, v, 0.38, color=col, label=nom)
    for x_, y_ in zip(np.arange(len(cats)) + (i - 0.5) * 0.38, v):
        ax[0].text(x_, y_ + 0.8, f"{y_:.1f}", ha="center", fontsize=7.5)
    ax[1].hist(ev_data[m]["prof"] / 10, bins=133, range=(0, 133), histtype="step", color=col, lw=1.4, density=True, label=nom)
ax[0].set_xticks(range(len(cats))); ax[0].set_xticklabels(["H", "$^{35}$Cl", "$^{37}$Cl", "$^{23}$Na", "$^{16}$O", "otros"])
ax[0].set_ylabel("Capturas [%]"); ax[0].legend(); ax[0].grid(alpha=0.3, ls="--", axis="y"); ax[0].set_yscale("log"); ax[0].set_ylim(0.01, 150)
ax[1].set_xlabel("Profundidad de captura bajo la tapa [cm]"); ax[1].set_ylabel("densidad"); ax[1].legend(); ax[1].grid(alpha=0.3, ls="--")
guardar(fig, "fig03_nucleo_profundidad")

# fig04: espectro de gammas de captura
fig, ax = plt.subplots(figsize=(9, 4.8))
Bg = np.arange(0, 11, 0.01)
for m in ("nacl25", "nacl10"):
    nom, _, col = MEDIOS[m]
    h, _ = np.histogram(ev_data[m]["Eg"], bins=Bg)
    ax.stairs(h / R[m]["capturas_totales"], Bg, color=col, lw=1, label=nom)
ax.set_yscale("log"); ax.set_xlabel("$E_\\gamma$ [MeV]"); ax.set_ylabel("gammas por captura y bin de 10 keV")
for e, t in ((2.224, "H 2.224"), (6.111, "Cl 6.11"), (7.414, "Cl 7.41"), (7.790, "7.79"), (8.580, "8.58"), (1.165, "1.165")):
    ax.axvline(e, color="0.6", lw=0.6, ls=":"); ax.text(e, 0.4, t, rotation=90, fontsize=7, va="top")
ax.grid(alpha=0.3, ls="--"); ax.legend()
guardar(fig, "fig04_gammas_captura")

# fig05: escalado por componente
fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
comps = ["haz", "halo", "fondo"]
for i, m in enumerate(MEDIOS):
    nom, _, col = MEDIOS[m]
    ns = [ESC[m][c]["eventos_senal"] for c in comps]
    ax[0].bar(np.arange(3) + (i - 1) * 0.27, ns, 0.27, color=col, label=nom)
    qq = [ESC[m][c]["carga_total_pe"] for c in comps]
    ax[1].bar(np.arange(3) + (i - 1) * 0.27, qq, 0.27, color=col, label=nom)
for a, t in zip(ax, ["Eventos con señal en 5 min", "Carga total en 5 min [p.e.]"]):
    a.set_xticks(range(3)); a.set_xticklabels([f"haz\n130 711 n", f"halo\n167 963 n", f"fondo\n74 598 n"])
    a.set_ylabel(t); a.grid(alpha=0.3, ls="--", axis="y"); a.legend(fontsize=8.5)
guardar(fig, "fig05_escalado_componentes")

# fig06: efecto de la reponderación en la energía
fig, ax = plt.subplots(figsize=(8, 4.4))
E0, w = ev_data["pura"]["E0"], ev_data["pura"]["w"]
B = np.append(E1, E2[-1])
h, _ = np.histogram(E0, bins=B); hw, _ = np.histogram(E0, bins=B, weights=w)
lb = np.log(E2 / E1)
ax.stairs(h / len(E0) / lb, B, color="crimson", lw=1.3, label="Archivo de entrada usado en MEIGA")
ax.stairs(hw / w.sum() / lb, B, color="seagreen", lw=1.3, label="Reponderado")
ax.stairs(L / NORM_ISO, B, color="k", lw=1, ls="--", label="ISO 8529 digitalizado")
ax.set_xscale("log"); ax.set_xlabel("$E_n$ [MeV]"); ax.set_ylabel("Fracción por unidad de letargia"); ax.legend(); ax.grid(alpha=0.3, ls="--", which="both")
guardar(fig, "fig06_reponderacion")

print(json.dumps({m: {k: R[m][k] for k in ("eps_Q1", "Q_media_senal") } for m in R}, indent=1, default=float))
print(open(os.path.join(RES, "escalado_373272.tsv")).read())
