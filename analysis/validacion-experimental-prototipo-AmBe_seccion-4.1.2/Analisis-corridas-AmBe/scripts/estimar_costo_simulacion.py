#!/usr/bin/env python3
"""
Neutrones por intervalo de energía, tiempo y tamaño de salida para simular el montaje experimental en MEIGA
(tres medios), con la composición haz 35 % (ISO 8529) / halo 45 % (0.5 eV-100 keV, 1/E) / fondo 20 %
(1e-4-0.5 eV, maxwelliano). Tiempo por neutrón: modelo t = a + b·Q + c·captura ajustado a los tiempos reales
por evento de las corridas AmBe (registros de MEIGA), con Q y la captura de cada componente (corridas AmBe
para el haz, Campaña 1 plegada para halo y fondo). Tamaño: medido por neutrón (formato antiguo de las corridas
AmBe; formato TSV actual de la Campaña 2 a 25 meV y de la réplica de Sidelnik) y ≈ 1.8 MB por segundo simulado.
-> resultados/costo_simulacion.json, neutrones_por_intervalo.tsv
"""
import gzip, json, os
import numpy as np
BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES = os.path.join(BASE, "resultados")
FU = os.path.abspath(os.path.join(BASE, "..", "Analisis-fuente-AmBe", "resultados"))
d = json.load(open(os.path.join(RES, "resumen_corridas.json")))
R, C1 = d["corridas"], d["campana1_plegada"]
MED = ["pura", "nacl25", "nacl10"]
FR = {"haz": 0.35, "halo": 0.45, "fondo": 0.20}

# --- modelo de tiempo por neutrón (ajuste a eventos AmBe)
coef = {}
for m in ("nacl25", "nacl10"):
    t = np.load(os.path.join(RES, f"tiempos_{m}.npz"))["real"]
    q = np.load(os.path.join(RES, f"carga_{m}.npz"))["carga"]
    with gzip.open(os.path.join(RES, f"eventos_{m}.tsv.gz"), "rt") as f:
        nc = np.array([int(l.split("\t")[7]) for l in f])
    A = np.column_stack([np.ones_like(t), q, (nc > 0).astype(float)])
    coef[m] = np.linalg.lstsq(A, t, rcond=None)[0]
    coef[m + "_media_medida"] = float(t.mean())
coef["pura"] = 0.5 * (coef["nacl25"] + coef["nacl10"])
def t_n(m, Qn, eta):
    a, b, c = coef[m]; return float(a + b * Qn + c * eta)

resp = {}
for m in MED:
    r = R[m]
    resp[m] = {"haz": (r["Q_media_por_neutron"]["ISO"], r["eta_cap"]["ISO"]),
               "halo": (C1[m]["halo"]["eps"] * C1[m]["halo"]["Q_media_pe"], C1[m]["halo"]["eta_cap"]),
               "fondo": (C1[m]["fondo"]["eps"] * C1[m]["fondo"]["Q_media_pe"], C1[m]["fondo"]["eta_cap"])}
tn = {m: {c: t_n(m, *resp[m][c]) for c in FR} for m in MED}
# el haz en NaCl se toma directamente de los tiempos medidos (más fiable que el modelo)
tn["nacl25"]["haz"] = coef["nacl25_media_medida"]; tn["nacl10"]["haz"] = coef["nacl10_media_medida"]

# --- tamaño por neutrón [kB]
MB_POR_S = 1.8          # 2.5 %: 123.8 kB/0.0728 s = 1.70; 10 %: 179.2/0.0884 = 2.03; Sidelnik: 827/0.485 = 1.71
TSV_TERMICO = {"pura": 52.5, "nacl25": 41.7, "nacl10": 34.8}   # Campaña 2, 25 meV, formato actual (kB/n)
kb = {m: {c: tn[m][c] * MB_POR_S * 1000 for c in FR} for m in MED}
for m in MED:
    kb[m]["fondo"] = TSV_TERMICO[m]                          # medido
    kb[m]["halo"] = max(kb[m]["halo"], TSV_TERMICO[m])

# --- intervalos de energía
E1, E2, L = np.loadtxt(os.path.join(FU, "ISO8529_AmBe_digitalizado.txt"), unpack=True)
NI = np.sum(L * np.log(E2 / E1))
def iso(a, b):
    lo, hi = np.maximum(a, E1), np.minimum(b, E2)
    return float(np.sum(np.where(hi > lo, L * np.log(np.where(hi > lo, hi / lo, 1)), 0)) / NI)
def halo(a, b): return float(np.log(b / a) / np.log(1e5 / 0.5))
Eg = np.geomspace(1e-4, 0.5, 20001); fg = Eg * np.exp(-Eg / 0.0253)
cg = np.concatenate([[0], np.cumsum(0.5 * (fg[1:] + fg[:-1]) * np.diff(Eg))]); cg /= cg[-1]
def fondo(a, b): return float(np.interp(b, Eg, cg) - np.interp(a, Eg, cg))
INT = [("fondo", "0.1 meV – 25 meV", 1e-4, 0.025, fondo), ("fondo", "25 meV – 0.5 eV", 0.025, 0.5, fondo),
       ("halo", "0.5 – 10 eV", 0.5, 10, halo), ("halo", "10 – 100 eV", 10, 100, halo), ("halo", "100 eV – 1 keV", 100, 1e3, halo),
       ("halo", "1 – 10 keV", 1e3, 1e4, halo), ("halo", "10 – 100 keV", 1e4, 1e5, halo),
       ("haz", "0.1 – 1 MeV", 0.1, 1, iso), ("haz", "1 – 2 MeV", 1, 2, iso), ("haz", "2 – 4 MeV", 2, 4, iso),
       ("haz", "4 – 6 MeV", 4, 6, iso), ("haz", "6 – 8 MeV", 6, 8, iso), ("haz", "8 – 11 MeV", 8, 11, iso)]
ESC = {"modelo_5min": 373272, "recomendado": 1_000_000, "experimento_5min": 20_000_000}
filas = []
for comp, et, a, b, f in INT:
    frac = FR[comp] * f(a, b)
    filas.append([comp, et, frac] + [frac * N for N in ESC.values()])
with open(os.path.join(RES, "neutrones_por_intervalo.tsv"), "w") as fo:
    fo.write("componente\tintervalo\tfraccion\t" + "\t".join(ESC) + "\n")
    for r_ in filas:
        fo.write(f"{r_[0]}\t{r_[1]}\t{r_[2]:.5f}\t" + "\t".join(f"{x:.0f}" for x in r_[3:]) + "\n")
costo = {}
for m in MED:
    costo[m] = {"t_por_neutron_s": tn[m], "kB_por_neutron": kb[m], "escenarios": {}}
    for e, N in ESC.items():
        t = sum(FR[c] * N * tn[m][c] for c in FR); s = sum(FR[c] * N * kb[m][c] for c in FR) / 1e6
        costo[m]["escenarios"][e] = {"N": N, "horas_1_nucleo": t / 3600, "dias_1_nucleo": t / 86400,
                                     "horas_4_nucleos": t / 3600 / 4, "GB": s}
json.dump({"coeficientes_tiempo": {k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in coef.items()},
           "costo": costo}, open(os.path.join(RES, "costo_simulacion.json"), "w"), indent=2, ensure_ascii=False)
print(open(os.path.join(RES, "neutrones_por_intervalo.tsv")).read())
for m in MED:
    print(m, {c: (round(tn[m][c], 4), round(kb[m][c], 1)) for c in FR})
    for e, v in costo[m]["escenarios"].items():
        print("   ", e, {k: round(x, 2) for k, x in v.items()})
