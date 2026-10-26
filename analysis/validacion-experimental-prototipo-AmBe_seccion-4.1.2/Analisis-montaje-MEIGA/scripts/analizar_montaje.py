#!/usr/bin/env python3
"""
Resultados de las corridas MEIGA del montaje (entrada lateral, haz/halo/fondo) por medio y componente,
comparados con (a) la predicción hecha con corridas de inyección por la tapa (Am-Be + Campaña 1) y
(b) el histograma sin fondo del prototipo (método robusto, normalizado a 300 s).
-> resultados/resumen_montaje.json, histograma_carga_montaje.tsv, figuras fig01-fig04
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
PREV = os.path.join(BASE, "..", "Analisis-corridas-AmBe", "resultados")
MED = {"pura": ("Agua pura", "red", "pura"), "nacl25": ("Agua + 2.5 % NaCl", "green", "2.5"),
       "nacl10": ("Agua + 10 % NaCl", "darkorange", "10")}
CN = {1: "haz", 2: "halo", 3: "fondo"}
N_MODELO = {"haz": 130711, "halo": 167963, "fondo": 74598}            # 5 min, 1 Ci (modelo blindado)
PE = 3.95 / 1000
UMB = 12
NUCN = {1001: "H", 8016: "16O", 8017: "17O", 17035: "35Cl", 17037: "37Cl", 11023: "23Na"}
plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "legend.fontsize": 9})
pred = json.load(open(os.path.join(PREV, "resumen_corridas.json")))["escalado"]
Xr = np.load(os.path.join(PREV, "cargas_robustas.npz"))
T = json.load(open(os.path.join(PREV, "experimento_tomas.json")))

R, H = {}, {}
disponibles = [m for m in MED if os.path.exists(os.path.join(RES, f"eventos_{m}.npz"))]
for m in disponibles:
    e = np.load(os.path.join(RES, f"eventos_{m}.npz"))
    comp, Q, ncm, nuc, t = e["comp"], e["Q"], e["ncap_medio"], e["nucleo"], e["t_cap_ns"]
    r = {}
    for k, c in list(CN.items()) + [(0, "total")]:
        s = (comp == k) if k else np.ones(len(Q), bool)
        n = int(s.sum()); cap = ncm[s] >= 1
        r[c] = {"N": n, "eps_Q1": float(np.mean(Q[s] >= 1)), "eps_Q12": float(np.mean(Q[s] >= UMB)),
                "Q_media_senal": float(Q[s][Q[s] >= 1].mean()), "eta_cap_medio": float(cap.mean()),
                "capturas_medio_por_n": float(ncm[s].mean()), "capturas_fuera_medio_por_n": float((e["ncap"][s] - ncm[s]).mean()),
                "P_senal_dada_captura": float(np.mean(Q[s][cap] >= 1)), "P_senal_sin_captura": float(np.mean(Q[s][~cap] >= 1)),
                "t_cap_mediana_us": float(np.nanmedian(t[s & (ncm >= 1)]) / 1000),
                "nucleo_pct": {NUCN.get(z, str(z)): float(100 * np.mean(nuc[s & (ncm >= 1)] == z))
                               for z in np.unique(nuc[s & (ncm >= 1)])}}
        if c != "total":
            p = pred[m][c]
            r[c]["prediccion_tapa"] = {"eps_Q1": p["eps"], "eta_cap": p["eta_cap"], "Q_media_senal": p["Q_media_pe"]}
    # escalado al modelo de 5 min con la respuesta lateral medida
    r["modelo_5min"] = {c: {"N": N_MODELO[c], "senal_Q1": N_MODELO[c] * r[c]["eps_Q1"], "senal_Q12": N_MODELO[c] * r[c]["eps_Q12"],
                            "capturas": N_MODELO[c] * r[c]["capturas_medio_por_n"]} for c in N_MODELO}
    tot = {k: sum(r["modelo_5min"][c][k] for c in N_MODELO) for k in ("senal_Q1", "senal_Q12", "capturas")}
    r["modelo_5min"]["total"] = tot
    r["prediccion_tapa_total_senal_Q1"] = pred[m]["total"]["eventos_senal"]
    # experimento: sin fondo (método robusto), Q >= 12 p.e., 300 s
    pref = MED[m][2]
    qn, qf = Xr[f"{pref}_neutrones"] * PE, Xr[f"{pref}_fondo"] * PE
    tn, tf = T[f"{pref}_neutrones"]["duracion_s"], T[f"{pref}_fondo"]["duracion_s"]
    det = (np.sum(qn >= UMB) / tn - np.sum(qf >= UMB) / tf) * 300
    eff12 = r["total"]["eps_Q12"]
    r["experimento"] = {"detectados_Q12_300s": float(det), "N_incidentes_equivalentes": float(det / eff12),
                        "pct_de_1Ci": float(100 * det / eff12 / 6.66e8),
                        "capturas_equivalentes": float(det / eff12 * r["total"]["capturas_medio_por_n"]),
                        "factor_sobre_modelo_5min": float(det / tot["senal_Q12"])}
    # histogramas
    B = np.arange(0, 202)
    H[m] = {c: np.histogram(Q[comp == k], bins=B)[0] for k, c in CN.items()}
    H[m]["total"] = np.histogram(Q, bins=B)[0]
    b1 = np.arange(0, 201)
    H[m]["exp"] = np.histogram(qn, bins=b1)[0] / tn * 300 - np.histogram(qf, bins=b1)[0] / tf * 300
    R[m] = r
json.dump(R, open(os.path.join(RES, "resumen_montaje.json"), "w"), indent=2, ensure_ascii=False)
with open(os.path.join(RES, "histograma_carga_montaje.tsv"), "w") as f:
    cols = [(m, c) for m in disponibles for c in ("haz", "halo", "fondo", "total", "exp")]
    f.write("carga_pe\t" + "\t".join(f"{c}_{m}" for m, c in cols) + "\n")
    for q in range(200):
        f.write(f"{q}\t" + "\t".join(f"{H[m][c][q]:.3f}" for m, c in cols) + "\n")

for m in disponibles:
    r = R[m]
    print(f"===== {MED[m][0]}")
    for c in ("haz", "halo", "fondo", "total"):
        x = r[c]; p = x.get("prediccion_tapa", {})
        print(f"  {c:6s} N={x['N']:7d} eps(Q>=1)={100*x['eps_Q1']:5.2f}% (pred tapa {100*p.get('eps_Q1', np.nan):5.2f}%)  "
              f"eta_cap={100*x['eta_cap_medio']:5.2f}% (pred {100*p.get('eta_cap', np.nan):5.2f}%)  <Q>={x['Q_media_senal']:.2f} "
              f"(pred {p.get('Q_media_senal', np.nan):.2f})  eps(Q>=12)={100*x['eps_Q12']:.3f}%  P(s|c)={x['P_senal_dada_captura']:.3f}  "
              f"t_med={x['t_cap_mediana_us']:.0f} us  nucleo={ {k: round(v,1) for k,v in x['nucleo_pct'].items()} }")
    print("  modelo 5 min (respuesta lateral):", {k: round(v) for k, v in r["modelo_5min"]["total"].items()},
          " | predicho con tapa: senal", round(r["prediccion_tapa_total_senal_Q1"]))
    print("  experimento:", {k: round(v, 3) for k, v in r["experimento"].items()})

# figuras
for m in disponibles:
    nom, col, _ = MED[m]
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
    q = np.arange(201)
    for c, ls in (("haz", "-"), ("halo", "--"), ("fondo", ":")):
        n = R[m][c]["N"]
        ax[0].plot(q[1:], H[m][c][1:] / n, ls, color=col, lw=1.5, label=f"{c} ({n:,} n)".replace(",", " "))
    ax[0].set_yscale("log"); ax[0].set_xlim(0, 80); ax[0].set_xlabel("Carga [p.e.]"); ax[0].set_ylabel("Fracción de neutrones incidentes")
    ax[0].set_title(f"{nom}: carga por componente (entrada lateral)", fontsize=10); ax[0].grid(alpha=0.3, ls="--"); ax[0].legend()
    ne = H[m]["exp"]; hs = H[m]["total"][:200].astype(float)
    k = slice(UMB, 60); f = ne[k].sum() / hs[k].sum()
    ax[1].step(q[:-1] + 0.5, ne, where="mid", color=col, lw=1.3, label="Experimento (sin fondo, 300 s)")
    ax[1].plot(q[1:200], hs[1:] * f, "k--", lw=1.4, label=f"MEIGA montaje × {f:.1f}  (≙ {f*1e6/1e6:.1f} M n)")
    ax[1].axvline(UMB, color="0.5", lw=0.7)
    ax[1].set_yscale("log"); ax[1].set_xlim(0, 120); ax[1].set_ylim(1, 3e5); ax[1].set_xlabel("Carga [p.e.]"); ax[1].set_ylabel("Cuentas en 300 s por p.e.")
    ax[1].set_title("Forma: experimento vs simulación del montaje", fontsize=10); ax[1].grid(alpha=0.3, ls="--"); ax[1].legend()
    fig.tight_layout()
    for x in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig01_carga_{m}.{x}"), dpi=200)
    plt.close(fig)
