#!/usr/bin/env python3
"""
Histogramas simulados de la figura Comparacion-Exp-vs-Sim-Termicos (tesis Sec. 4.1.2, 'compara-sim-exp'),
producida por Nuevo-analisis/analisis-datos-termicos-Bga.ipynb:
  * simulación = datos/counts-number-photons.txt (carga en p.e. por evento con señal, bins de 1 p.e.) del
    flujo de neutrones TÉRMICOS que emerge del suelo seco de Bucaramanga (Sec. 4.5), 207 968 neutrones
    (filtered_neutrons.shw, 10 meV - 10 eV);
  * en la figura: x = p.e.·1000/3.95 ADC, y = cuentas×10 (HEIGHT_FACTOR); experimento = fuente − fondo
    (método PASO 1-3, bins de 20 ADC) sin normalizar por tiempo.
Se extraen los histogramas, los conteos de neutrones de la simulación y el número de neutrones simulados
que equivale a cada curva, comparándolo con el experimento.
-> resultados/figura_termicos_histogramas.tsv, figura_termicos_neutrones.json, figuras/fig13
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DP = os.path.join(os.environ.get("TOSHIBA", os.path.join("/media", os.environ.get("USER", "ubuntu"), "TOSHIBA EXT")), "Simulaciones-Jaime-2024")
SIMF = f"{DP}/Detector-prototipo/Nuevo-analisis/datos/counts-number-photons.txt"
CAPT = f"{DP}/Simulacion-flujo-completo-Bucaramanga/Analisis-completo/Neutrones-termicos/Neutrones-capturados"
FLUJO = os.environ.get("FLUJO_TERMICO_SHW", os.path.join(os.path.expanduser("~"), "Documentos", "Documetos-Jaime-Betancourt", "Flujo-sobre-Bucaramnga", "Flujo-termico-suelo-seco", "filtered_neutrons.shw"))
BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
MED = {"pura": ("Agua pura", 1, "Agua-pura", "red", "pura"), "nacl25": ("Agua + 2.5 % NaCl", 2, "Agua+25NaCl", "green", "2.5"),
       "nacl10": ("Agua + 10 % NaCl", 4, "Agua+10NaCl", "orange", "10")}
HEIGHT, SHIFT, BW_EXP = 10, 3.95, 20
ADC_POR_PE = 1000 / SHIFT                      # 253.16 ADC por p.e.
PE = SHIFT / 1000
AJUSTE = (12, 60)                              # p.e., zona donde ambos están por encima de umbral y con estadística

S = np.loadtxt(SIMF, comments="#")
N_SIM = sum(1 for _ in open(FLUJO))
X = np.load(os.path.join(RES, "experimento_cargas.npz"))
T = json.load(open(os.path.join(RES, "experimento_tomas.json")))
edges = np.arange(1200, 200000 + BW_EXP, BW_EXP); cen = edges[:-1] + BW_EXP / 2
out, tabla = {"N_simulados": N_SIM, "archivo_simulacion": SIMF, "HEIGHT_FACTOR": HEIGHT,
              "factor_ancho_bin_exp/sim": BW_EXP / ADC_POR_PE,
              "N_equivalente_de_la_figura": HEIGHT / (BW_EXP / ADC_POR_PE) * N_SIM}, []
for m, (nom, c, carp, col, pref) in MED.items():
    h = S[:, c]                                  # cuentas por p.e. (bin centrado en q+0.5)
    q = S[:, 0]
    cap = sum(1 for _ in open(f"{CAPT}/{carp}/neutrones-capturados.txt"))
    cap_agua = sum(1 for _ in open(f"{CAPT}/{carp}/neutrones-capturados-limpio-{'AP' if m=='pura' else ('A25NaCl' if m=='nacl25' else 'A10NaCl')}.txt"))
    det = h.sum(); det12 = h[q >= 12].sum()
    # experimento (como la figura: resta sin normalizar) y normalizado a 300 s
    qn, qf = X[f"{pref}_neutrones"], X[f"{pref}_fondo"]
    tn, tf = T[f"{pref}_neutrones"]["duracion_s"], T[f"{pref}_fondo"]["duracion_s"]
    hn, _ = np.histogram(qn, edges); hf, _ = np.histogram(qf, edges)
    d_fig = hn - hf; d_300 = (hn / tn - hf / tf) * 300
    pe_exp = cen * PE
    # factor de escala por medio: densidad experimental (por bin de 20 ADC) / densidad simulada (por p.e.)
    sel_e = (pe_exp >= AJUSTE[0]) & (pe_exp < AJUSTE[1]); sel_s = (q >= AJUSTE[0]) & (q < AJUSTE[1])
    k_fig = d_fig[sel_e].sum() / h[sel_s].sum()          # cuentas exp en la zona / cuentas sim en la zona
    k_300 = d_300[sel_e].sum() / h[sel_s].sum()
    r = {"neutrones_simulados": N_SIM, "detectados_sim_Q>=1": int(det), "eps_sim_Q>=1": det / N_SIM,
         "detectados_sim_Q>=12": int(det12), "eps_sim_Q>=12": det12 / N_SIM,
         "capturados_sim": cap, "capturados_sim_en_agua": cap_agua, "eta_cap_sim": cap / N_SIM,
         "P_senal_dada_captura_sim": det / cap, "carga_media_sim_pe": float((q * h).sum() / det),
         "exp_netos_figura_Q>=12": float(d_fig[pe_exp >= 12].sum()), "exp_netos_300s_Q>=12": float(d_300[pe_exp >= 12].sum()),
         "exp_duracion_fuente_s": tn,
         "N_equivalente_figura_ajustado": k_fig * N_SIM, "N_equivalente_300s": k_300 * N_SIM,
         "capturados_equivalentes_300s": k_300 * cap, "factor_altura_que_ajusta": k_fig * BW_EXP / ADC_POR_PE}
    out[m] = r
    tabla.append((m, q, h))
json.dump(out, open(os.path.join(RES, "figura_termicos_neutrones.json"), "w"), indent=2, ensure_ascii=False)
with open(os.path.join(RES, "figura_termicos_histogramas.tsv"), "w") as f:
    f.write("pe_centro\tADC_centro_figura\t" + "\t".join(f"sim_{m}\tsim_{m}_x10_figura" for m, _, _ in tabla) + "\n")
    for i in range(len(S)):
        f.write(f"{S[i,0]:.1f}\t{S[i,0]*ADC_POR_PE:.1f}\t" + "\t".join(f"{int(h[i])}\t{int(h[i])*HEIGHT}" for _, _, h in tabla) + "\n")
print(json.dumps(out, indent=1, ensure_ascii=False))

# figura: reproducción y versión con la escala ajustada por medio
fig, ax = plt.subplots(1, 2, figsize=(15, 5.4))
for m, (nom, c, carp, col, pref) in MED.items():
    qn, qf = X[f"{pref}_neutrones"], X[f"{pref}_fondo"]
    hn, _ = np.histogram(qn, edges); hf, _ = np.histogram(qf, edges)
    xc = cen - (1500 if m == "pura" else 0)
    ax[0].step(xc, hn - hf, where="mid", color=col, lw=1, label=f"Exp: {nom}")
    ax[0].plot(S[:, 0] * ADC_POR_PE, S[:, c] * HEIGHT, "--", color=col, lw=1.8, label=f"Sim ×10: {nom}")
    tn, tf = T[f"{pref}_neutrones"]["duracion_s"], T[f"{pref}_fondo"]["duracion_s"]
    b1 = np.arange(0, 201)
    ne = np.histogram(cen * PE, bins=b1, weights=(hn / tn - hf / tf) * 300)[0]
    k = out[m]["N_equivalente_300s"] / N_SIM
    ax[1].step(b1[:-1] + 0.5, ne, where="mid", color=col, lw=1.2, label=f"Exp (300 s): {nom}")
    ax[1].plot(S[:, 0], S[:, c] * k, "--", color=col, lw=1.6, label=f"Sim × {k:.0f}  (≙ {out[m]['N_equivalente_300s']/1e6:.1f} M n)")
ax[0].set_yscale("log"); ax[0].set_ylim(10, 1e5); ax[0].set_xlim(0, 40000); ax[0].set_xlabel("ADC [u.a.]"); ax[0].set_ylabel("Cuentas [u.a.]")
ax[0].set_title("Reproducción de Comparacion-Exp-vs-Sim-Termicos", fontsize=10)
ax[1].set_yscale("log"); ax[1].set_ylim(1, 3e5); ax[1].set_xlim(0, 120); ax[1].set_xlabel("Carga [p.e.]"); ax[1].set_ylabel("Cuentas en 300 s por p.e.")
ax[1].set_title("Escala ajustada por medio (12–60 p.e.) → neutrones térmicos equivalentes", fontsize=10)
for a in ax: a.grid(alpha=0.3, ls="--"); a.legend(fontsize=8)
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig13_figura_termicos_neutrones.{e}"), dpi=200)
