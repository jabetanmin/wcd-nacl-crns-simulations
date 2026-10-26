#!/usr/bin/env python3
"""
PMT en la tapa (corrida de agua pura) frente a PMT bajado a 0.3*fWaterHalfHeight (prueba de 200 000 n), con los
mismos neutrones de entrada (primeras 200 000 líneas del archivo de 1 000 000): eficiencia, carga, cola por
encima del disparo (≈24 p.e. con la calibración por muones) y dependencia con la altura de la captura.
Requiere resultados/eventos_pura.npz y resultados/eventos_pura_pmtbajo.npz
(procesar_montaje.py <carpeta 200000N-...-PMTbajo-...> pura_pmtbajo).
-> resultados/comparacion_pmt_bajo.json, figuras/fig09_pmt_bajo
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
B = np.load(os.path.join(RES, "eventos_pura_pmtbajo.npz"))
n = len(B["Q"])
A = {k: v[:n] for k, v in np.load(os.path.join(RES, "eventos_pura.npz")).items()}
assert np.array_equal(A["comp"], B["comp"]) and np.allclose(A["E0_eV"], B["E0_eV"]), "las entradas no coinciden"
V = json.load(open(os.path.join(RES, "calibracion_vem.json")))
U = 3000 * V["resumen"]["pe_por_1000ADC_media"] / 1000          # disparo en p.e.
CN = {0: "total", 1: "haz", 2: "halo", 3: "fondo"}

def resumen(E, s):
    Q = E["Q"][s]; cap = E["ncap_medio"][s] >= 1
    err = lambda p, m: float(np.sqrt(p * (1 - p) / max(m, 1)))
    p1, pu = np.mean(Q >= 1), np.mean(Q >= U)
    return {"N": int(s.sum()), "eps_Q1": float(p1), "eps_Q1_err": err(p1, s.sum()), "Q_media_senal": float(Q[Q >= 1].mean()),
            "Q_media_dada_captura": float(Q[cap].mean()), "eps_Q12": float(np.mean(Q >= 12)), "eps_Q_disparo": float(pu),
            "eventos_Q_disparo": int(np.sum(Q >= U)), "eta_cap": float(cap.mean())}

out = {"N": n, "umbral_disparo_pe": U, "componentes": {}}
for k, c in CN.items():
    s = (A["comp"] == k) if k else np.ones(n, bool)
    a, b = resumen(A, s), resumen(B, s)
    out["componentes"][c] = {"tapa": a, "bajo": b, "razon_Q_media": b["Q_media_senal"] / a["Q_media_senal"],
                             "razon_Q_dada_captura": b["Q_media_dada_captura"] / a["Q_media_dada_captura"],
                             "razon_eps_Q1": b["eps_Q1"] / a["eps_Q1"]}
# carga media en función de la altura de la captura (solo eventos con captura en el agua)
zb = [(0, 30), (30, 60), (60, 75), (75, 90), (90, 120), (120, 134)]
out["por_altura"] = []
for lo, hi in zb:
    fila = {"z_cm": [lo, hi]}
    for nom, E in (("tapa", A), ("bajo", B)):
        s = (E["ncap_medio"] >= 1) & (E["z_cap_cm"] >= lo) & (E["z_cap_cm"] < hi)
        fila[nom] = {"capturas": int(s.sum()), "Q_media": float(E["Q"][s].mean()) if s.any() else None}
    out["por_altura"].append(fila)
json.dump(out, open(os.path.join(RES, "comparacion_pmt_bajo.json"), "w"), indent=2, ensure_ascii=False)

t = out["componentes"]["total"]
print(f"N = {n}; disparo = {U:.1f} p.e.")
for c, x in out["componentes"].items():
    print(f"  {c:6s} eps(Q>=1) tapa {100*x['tapa']['eps_Q1']:.2f} % -> bajo {100*x['bajo']['eps_Q1']:.2f} %  |  <Q> {x['tapa']['Q_media_senal']:.2f} -> "
          f"{x['bajo']['Q_media_senal']:.2f} p.e. (x{x['razon_Q_media']:.2f})  |  Q>=disparo {x['tapa']['eventos_Q_disparo']} -> {x['bajo']['eventos_Q_disparo']}")
for f in out["por_altura"]:
    print(f"  captura z {f['z_cm']}: <Q> tapa {f['tapa']['Q_media']}, bajo {f['bajo']['Q_media']}  ({f['bajo']['capturas']} capturas)")

fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
b = np.arange(0, 61)
for nom, E, ls in (("PMT en la tapa", A, "-"), ("PMT bajado (46.55 cm bajo la tapa)", B, "--")):
    h = np.histogram(E["Q"], b)[0] / n
    ax[0].stairs(np.clip(h, 1e-7, None), b, color="red", ls=ls, lw=1.4, label=f"{nom}: ⟨Q⟩ = {E['Q'][E['Q'] >= 1].mean():.2f} p.e.")
ax[0].axvline(U, color="0.5", lw=0.8); ax[0].text(U + 0.5, 3e-2, "disparo", fontsize=8, color="0.3")
ax[0].set_yscale("log"); ax[0].set_ylim(1e-6, 1); ax[0].set_xlabel("Carga [p.e.]"); ax[0].set_ylabel("Fracción de neutrones incidentes")
ax[0].set_title(f"Agua pura, mismos {n:,} neutrones".replace(",", " "), fontsize=10); ax[0].grid(alpha=0.3, ls="--"); ax[0].legend(fontsize=8)
zc = [0.5 * (lo + hi) for lo, hi in zb]
for nom, ls, mk in (("tapa", "-", "o"), ("bajo", "--", "s")):
    ax[1].plot(zc, [f[nom]["Q_media"] for f in out["por_altura"]], ls, marker=mk, color="red", label="PMT en la tapa" if nom == "tapa" else "PMT bajado")
ax[1].axvline(133, color="k", lw=0.8); ax[1].axvline(86.45, color="royalblue", lw=0.8, ls=":", label="cara del PMT bajado")
ax[1].axvline(66.56, color="0.5", lw=0.8, ls="--", label="altura del haz")
ax[1].set_xlabel("Altura de la captura sobre el fondo [cm]"); ax[1].set_ylabel("⟨Q⟩ de los eventos con captura [p.e.]")
ax[1].set_title("Carga según dónde ocurre la captura", fontsize=10); ax[1].grid(alpha=0.3, ls="--"); ax[1].legend(fontsize=8)
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig09_pmt_bajo.{e}"), dpi=200)
