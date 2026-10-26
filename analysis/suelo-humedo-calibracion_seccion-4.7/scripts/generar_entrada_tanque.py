#!/usr/bin/env python3
"""
Entrada al WCD de los neutrones que SUBEN del suelo, para cada humedad (simulación directa de la curva de calibración).

1. Extracción: de cada corrida del suelo (pasos-neutrones.tsv) se toman los cruces hacia arriba del plano a 5 cm
   (z_pre < 5 <= z_post): energía (pre_energy) y dirección (post − pre). Se guardan en
   resultados/neutrones_que_suben/<etiqueta>.npz (E_MeV, ux, uy, uz, creado). Los cruces son el flujo que sube.
2. Entrada al tanque. El campo que sube es uniforme sobre el suelo y casi no se atenúa en los 2 m de aire
   (≈ 0.24 g/cm²), así que el número de neutrones que atraviesa cualquier superficie se obtiene de los mismos cruces
   del plano: si p(u) es la distribución de direcciones de los cruces, la fluencia por dirección es ∝ p(u)/u_z.
   - Base (disco R = 48.5 cm en z = −0.5 cm): tasa = J · πR²; cada cruce entra con peso 1; posición uniforme en el disco.
   - Costado (cilindro R = 48.5 cm, z de −0.5 a 134.5 cm): tasa = J · 2RH · <tan θ>; se elige el cruce con peso tan θ,
     un punto uniforme del costado y el acimut de entrada con densidad ∝ cos δ respecto de la normal hacia adentro
     (el campo es simétrico en acimut). Los más rasantes vienen de muy lejos: se cortan en θ > θ_corte
     (85° por defecto, ≈ 25–40 m de distancia horizontal); 80° y sin corte dan la incertidumbre sistemática.
   La tapa no recibe neutrones que suben. Se inyecta 1 mm fuera de la superficie.
3. Normalización: tasa que llega al tanque [n/s] = tasa por la base + tasa por el costado, con J_sube de
   resultados/albedo_suelo.json. La tasa detectada es esa tasa por la fracción de inyectados con señal.
Formato MEIGA eFromFile: "13 px py pz x y z 6 0 0 0 0" (GeV/c, cm; pz invertido: pz > 0 en el archivo = hacia abajo).
Uso: generar_entrada_tanque.py --salida <carpeta flujos del paquete> [--N 100000] [--N-prueba 2000] [--corte 85] [--semilla 20261026]
-> <salida>/<N>N-sube-<etiqueta>.txt, <salida>/prueba/<N>N-sube-<etiqueta>.txt, <salida>/entrada_tanque.json
"""
import argparse, glob, json, os, re, subprocess
import numpy as np

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES = os.path.join(BASE, "resultados"); EXT = os.path.join(RES, "neutrones_que_suben"); os.makedirs(EXT, exist_ok=True)
ap = argparse.ArgumentParser()
ap.add_argument("--salida", required=True)
ap.add_argument("--N", type=int, default=100000)
ap.add_argument("--N-prueba", type=int, default=2000)
ap.add_argument("--corte", type=float, default=85.0, help="ángulo cenital máximo de los que entran por el costado [grados]")
ap.add_argument("--semilla", type=int, default=20261026)
a = ap.parse_args()
M_N = 939.565
ZB, ZT, RC = -0.5, 134.5, 48.5                                 # base, tapa y radio del cilindro de entrada [cm]
AWK = r'''BEGIN{FS="\t"} /^#/{next} {z1=$12+0; z2=$15+0; if (z1 < 5 && z2 >= 5) {
  dx=$13-$10; dy=$14-$11; dz=z2-z1; n=sqrt(dx*dx+dy*dy+dz*dz); if (n > 0) print $16, dx/n, dy/n, dz/n, ($4==1 ? 0 : 1) }}'''

def w_de(etq):
    if etq.startswith("seco"): return 0.0
    m = re.match(r"humedo-(\d+)", etq); return int(m.group(1)) / 100 if m else None

d = json.load(open(os.path.join(RES, "albedo_suelo.json")))
rng = np.random.default_rng(a.semilla)
resumen = {"corte_grados": a.corte, "cilindro": {"R_cm": RC, "z_min_cm": ZB, "z_max_cm": ZT}, "semilla": a.semilla, "suelos": {}}
os.makedirs(os.path.join(a.salida, "prueba"), exist_ok=True)

for etq, v in d["corridas"].items():
    w = w_de(etq)
    if w is None or not os.path.isdir(v["carpeta"]): continue
    nom = "seco" if w == 0 else f"agua{100 * w:02.0f}"
    cache = os.path.join(EXT, f"{nom}.npz")
    if not os.path.exists(cache):
        filas = []
        for f in sorted(glob.glob(os.path.join(v["carpeta"], "parte*", "Datos-simulacion", "pasos-neutrones.tsv"))):
            out = subprocess.run(["mawk", AWK, f], capture_output=True, text=True, check=True,
                                 env={"LC_ALL": "C", "PATH": os.environ["PATH"]}).stdout
            filas.append(np.loadtxt(out.splitlines(), ndmin=2) if out else np.zeros((0, 5)))
        X = np.vstack(filas)
        np.savez_compressed(cache, E_MeV=X[:, 0], ux=X[:, 1], uy=X[:, 2], uz=X[:, 3], creado=X[:, 4].astype(np.int8))
    S = np.load(cache); E, ux, uy, uz = S["E_MeV"], S["ux"], S["uy"], S["uz"]
    J = v["J_sube_n_m2_s"]
    res = {"w": w, "cruces": int(len(E)), "J_sube_n_m2_s": J, "E_media_MeV": float(E.mean())}
    st = np.sqrt(np.clip(1 - uz ** 2, 0, None)); tan = st / uz
    cuz = np.cos(np.radians(a.corte))
    def tan_medio(c): return float(np.mean(np.where(uz > c, tan, 0.0)))
    Rm, Hm = RC / 100, (ZT - ZB) / 100
    r_base = J * np.pi * Rm ** 2
    r_lado = {f"{g:g}": J * 2 * Rm * Hm * tan_medio(np.cos(np.radians(g)) if g < 90 else 0.0) for g in (80, 85, 90)}
    r_cos = r_lado[f"{a.corte:g}"] if f"{a.corte:g}" in r_lado else J * 2 * Rm * Hm * tan_medio(cuz)
    res.update({"tasa_base_n_s": r_base, "tasa_costado_n_s": r_cos, "tasa_costado_n_s_por_corte": r_lado,
                "tan_medio": tan_medio(cuz), "tasa_al_tanque_n_s": r_base + r_cos})
    pl = np.where(uz > cuz, tan, 0.0); pl = pl / pl.sum()
    for modo, N in (("completa", a.N), ("prueba", a.N_prueba)):
        nb = rng.binomial(N, r_base / (r_base + r_cos)); nl = N - nb
        # base: cruce al azar (peso 1), posición uniforme en el disco, 1 mm por debajo
        ib = rng.integers(0, len(E), nb); rr = RC * np.sqrt(rng.random(nb)); ff = 2 * np.pi * rng.random(nb)
        Pb = np.column_stack([rr * np.cos(ff), rr * np.sin(ff), np.full(nb, ZB - 0.1)])
        Ub = np.column_stack([ux[ib], uy[ib], uz[ib]])
        # costado: cruce con peso tan θ, punto uniforme, acimut de entrada con densidad ∝ cos δ
        il = rng.choice(len(E), nl, p=pl); phi = 2 * np.pi * rng.random(nl); zl = ZB + (ZT - ZB) * rng.random(nl)
        delta = np.arcsin(2 * rng.random(nl) - 1); psi = phi + np.pi + delta
        Pl = np.column_stack([(RC + 0.1) * np.cos(phi), (RC + 0.1) * np.sin(phi), zl])
        Ul = np.column_stack([st[il] * np.cos(psi), st[il] * np.sin(psi), uz[il]])
        I = np.concatenate([ib, il]); P = np.vstack([Pb, Pl]); U = np.vstack([Ub, Ul])
        orden = rng.permutation(N); I, P, U = I[orden], P[orden], U[orden]
        p = np.sqrt(E[I] ** 2 + 2 * M_N * E[I]) / 1000.0                       # GeV/c
        F = np.column_stack([p * U[:, 0], p * U[:, 1], -p * U[:, 2], P])
        dest = os.path.join(a.salida, "" if modo == "completa" else "prueba", f"{N}N-sube-{nom}.txt")
        np.savetxt(dest, np.column_stack([F, np.full(N, 6)]), fmt="13 %.8e %.8e %.8e %.4f %.4f %.4f %d 0 0 0 0")
        res[modo] = {"archivo": os.path.basename(dest), "N": N, "por_la_base": int(nb), "por_el_costado": int(nl),
                     "E_media_MeV": float(E[I].mean())}
    resumen["suelos"][nom] = res
    print(f"{nom:7s} cruces {res['cruces']:6d}  <tan> {res['tan_medio']:.3f}  tasa base {r_base:6.1f} + costado {r_cos:6.1f} = {r_base + r_cos:6.1f} n/s"
          f"  (costado con corte 80/85/90: {' / '.join(f'{v:.0f}' for v in r_lado.values())})", flush=True)
json.dump(resumen, open(os.path.join(a.salida, "entrada_tanque.json"), "w"), indent=2)
