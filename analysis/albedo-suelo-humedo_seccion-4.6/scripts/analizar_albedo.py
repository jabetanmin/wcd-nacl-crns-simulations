#!/usr/bin/env python3
"""
Espectro de neutrones que emerge del suelo (albedo) y su origen, a partir de las corridas MEIGA de Corrida-suelo-albedo.

Plano contador virtual a z = 5 cm sobre el suelo: se buscan en pasos-neutrones.tsv los pasos que lo cruzan
(z_pre > 5 >= z_post: baja; z_pre < 5 <= z_post: sube). Las corridas son sin tanque; con --excluir-tanque R se descartan
los cruces a menos de R cm del eje x = y = 0.
Para cada neutrón que sube se guarda su energía, si es el neutrón incidente (traza 1) o uno creado en el suelo, y el
proceso que lo creó (p. ej. neutronInelastic: dispersión inelástica / (n,xn)).
Normalización: igual que la figura de la tesis, el flujo que baja del archivo all_bga (1 111 010 neutrones en 1 m² y
3600 s, 308.6 n m⁻² s⁻¹); el que sube en la simulación = (cruces hacia arriba / neutrones incidentes) × ese flujo.
Uso: analizar_albedo.py --corrida seco=<carpeta> --corrida humedo-25=<carpeta> [--corrida humedo-10=…] [--shw …]
     <carpeta>@1 (o @1,2): solo esas partes; p. ej. la parte 1 de una corrida completa en 4 partes tiene los mismos
     50 000 neutrones que la validación (ejecutar_suelo.sh <suelo> validacion)
-> resultados/albedo_suelo.json, resultados/espectros_albedo.tsv, figuras/fig01_albedo_espectros, fig02_origen_albedo
"""
import argparse, glob, json, os, subprocess
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")
os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
SHW = os.environ.get("ALL_BGA_SHW", os.path.join(os.path.expanduser("~"), "Documentos", "Documetos-Jaime-Betancourt",
                   "Flujo-sobre-Bucaramnga", "Flujo-completo-Bga", "Grafica-flujo-Bga", "all_bga_neutron_35.shw"))
ZP = 5.0
M_N = 939.565
B = np.logspace(-11, 6, 171)                                # 10 bins por década, en MeV (como la figura de la tesis)
DU = np.log(B[1:] / B[:-1]); XC = np.sqrt(B[1:] * B[:-1])
REG = [("Térmico", 1e-11, 5e-7), ("Epitérmico", 5e-7, 0.1), ("Evaporación", 0.1, 20), ("Cascada", 20, 1e6)]
AWK = r'''BEGIN{FS="\t"} /^#/{next} {z1=$12+0; z2=$15+0; if((z1>ZP && z2<=ZP)||(z1<ZP && z2>=ZP)){
 x=$10+0; y=$11+0; t=(ZP-z1)/(z2-z1); xc=x+t*($13-x); yc=y+t*($14-y); if(xc*xc+yc*yc<RE*RE) next;
 print $1"\t"$4"\t"$5"\t"$6"\t"$7"\t"$16"\t"(z2>z1?1:-1)}}'''

ap = argparse.ArgumentParser()
ap.add_argument("--corrida", action="append", required=True, metavar="ETIQUETA=CARPETA")
ap.add_argument("--shw", default=SHW)
ap.add_argument("--excluir-tanque", type=float, default=0.0, help="cm; radio alrededor del eje del tanque que se descarta (0 = sin tanque)")
a = ap.parse_args()
R_EXCL = a.excluir_tanque

def tesis():
    d = np.loadtxt(a.shw, usecols=(1, 2, 3))
    p = np.linalg.norm(d, axis=1); E = np.where(p < 1e-2, p ** 2 / (2 * M_N), np.sqrt(p ** 2 + M_N ** 2) - M_N)
    return E[d[:, 2] < 0], E[d[:, 2] > 0]
E_baja, E_sube = tesis()
J_BAJA = len(E_baja) / 3600.0                               # n m⁻² s⁻¹ (1 m², 3600 s, como la figura de la tesis)
letargia = lambda h, norm: h * norm / DU                    # E dΦ/dE por bin

out = {"plano_cm": ZP, "exclusion_tanque_cm": R_EXCL, "J_baja_tesis_n_m2_s": J_BAJA,
       "tesis": {"baja": int(len(E_baja)), "sube": int(len(E_sube)), "albedo_por_incidente": len(E_sube) / len(E_baja)},
       "corridas": {}}
curvas = {"Baja (tesis)": letargia(np.histogram(E_baja, B)[0], 1 / 3600.0),
          "Sube, suelo seco (tesis)": letargia(np.histogram(E_sube, B)[0], 1 / 3600.0)}
origen = {}
for item in a.corrida:
    etq, carpeta = item.split("=", 1)
    partes = None
    if "@" in carpeta:
        carpeta, sel = carpeta.rsplit("@", 1); partes = {int(x) for x in sel.split(",")}
    filas = []
    for f in sorted(glob.glob(os.path.join(carpeta, "parte*", "Datos-simulacion", "pasos-neutrones.tsv"))):
        if partes and int(f.split("parte")[-1].split(os.sep)[0]) not in partes: continue
        txt = subprocess.run(["mawk", "-v", f"ZP={ZP}", "-v", f"RE={R_EXCL}", AWK, f], capture_output=True, text=True,
                             env={"LC_ALL": "C", "PATH": os.environ["PATH"]}).stdout
        parte = int(f.split("parte")[-1].split(os.sep)[0])
        for l in txt.splitlines():
            c = l.split("\t"); filas.append((parte, int(c[0]), int(c[1]), int(c[2]), c[4], float(c[5]), int(c[6])))
    if not filas: raise SystemExit(f"{etq}: no se encontraron cruces del plano en {carpeta}")
    parte, run, trk, par, crea, E, sen = (np.array(x) for x in zip(*filas))
    baja_inc = (sen < 0) & (trk == 1) & (crea == "none")
    N_inc = len({(p_, r_) for p_, r_ in zip(parte[baja_inc], run[baja_inc])})
    sube = sen > 0
    # primer cruce hacia arriba de cada neutrón (el que "emerge"); los siguientes se cuentan aparte
    vistos, primero = set(), np.zeros(len(E), bool)
    for i in np.nonzero(sube)[0]:
        k = (parte[i], run[i], trk[i])
        if k not in vistos: vistos.add(k); primero[i] = True
    tipo = np.array(["incidente reflejado" if t == 1 else "creado: " + c_ for t, c_ in zip(trk, crea)])
    PRINCIPALES = {"incidente reflejado", "creado: neutronInelastic", "creado: hBertiniCaptureAtRest", "creado: protonInelastic"}
    tipo_fig = np.where(np.isin(tipo, list(PRINCIPALES)), tipo, "creado: otros procesos")   # figura: los menores juntos
    norm = J_BAJA / N_inc
    curvas[f"Sube, {etq} (MEIGA)"] = letargia(np.histogram(E[sube], B)[0], norm)
    origen[etq] = {t: letargia(np.histogram(E[sube & (tipo_fig == t)], B)[0], norm) for t in sorted(set(tipo_fig[sube]))}
    reg = {n: {"sube_n_m2_s": float(np.sum((E[sube] >= lo) & (E[sube] < hi)) * norm),
               "sube_tesis_seco_n_m2_s": float(np.sum((E_sube >= lo) & (E_sube < hi)) / 3600.0)} for n, lo, hi in REG}
    out["corridas"][etq] = {"carpeta": carpeta, "partes": sorted(partes) if partes else "todas", "N_incidentes": N_inc, "cruces_sube": int(sube.sum()),
                            "neutrones_que_emergen": int(primero.sum()), "albedo_por_incidente": float(sube.sum() / N_inc),
                            "J_sube_n_m2_s": float(sube.sum() * norm), "cruces_baja_no_incidentes": int(((sen < 0) & ~baja_inc).sum()),
                            "origen_de_los_que_suben": dict(Counter(tipo[sube]).most_common()),
                            "fraccion_creados_en_el_suelo": float(np.mean(trk[sube] != 1)), "por_region": reg}
json.dump(out, open(os.path.join(RES, "albedo_suelo.json"), "w"), indent=2, ensure_ascii=False)
with open(os.path.join(RES, "espectros_albedo.tsv"), "w") as fo:
    fo.write("E_min_MeV\tE_max_MeV\t" + "\t".join(curvas) + "\n")
    for i in range(len(XC)):
        fo.write(f"{B[i]:.4e}\t{B[i+1]:.4e}\t" + "\t".join(f"{v[i]:.5g}" for v in curvas.values()) + "\n")

def bandas(ax):
    for (n, lo, hi), col in zip(REG, ("#e8f0ff", "#e8f7f0", "#fff6e0", "#ffeef4")):
        ax.axvspan(lo, hi, color=col, zorder=0); ax.text(np.sqrt(lo * hi), 1.6e2, n, ha="center", fontsize=9, color="0.35")
estilo = {"Baja (tesis)": ("#2b6cd4", "-"), "Sube, suelo seco (tesis)": ("#e8603c", "-")}
otros = iter([("#8a2be2", "--"), ("#1a9e5f", "--"), ("k", ":")])
fig, ax = plt.subplots(figsize=(11, 6)); bandas(ax)
for nom, y in curvas.items():
    c, ls = estilo.get(nom) or next(otros)
    ax.stairs(np.clip(y, 1e-4, None), B, color=c, ls=ls, lw=1.6, label=nom)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(1e-1, 4e2); ax.set_xlim(1e-11, 1e6)
ax.set_xlabel("Energía cinética $E_n$ [MeV]"); ax.set_ylabel("$E\\,d\\Phi/dE$ [n m$^{-2}$ s$^{-1}$]")
ax.set_title("Neutrones que emergen del suelo: " + ", ".join(e for e in origen)); ax.legend(fontsize=9, loc="lower center", ncol=2)
ax.grid(alpha=0.3, ls=":", which="both"); fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig01_albedo_espectros.{e}"), dpi=170)
plt.close(fig)
fig, axs = plt.subplots(1, len(origen), figsize=(7.5 * len(origen), 5.5), squeeze=False, sharey=True)
for ax, (etq, d) in zip(axs[0], origen.items()):
    bandas(ax)
    for t, y in sorted(d.items(), key=lambda kv: -kv[1].sum()):
        ax.stairs(np.clip(y, 1e-4, None), B, lw=1.4, label=t)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(1e-2, 4e2); ax.set_xlim(1e-11, 1e6)
    ax.set_xlabel("Energía cinética $E_n$ [MeV]"); ax.set_title(f"Origen de los neutrones que suben: {etq}", fontsize=10)
    ax.grid(alpha=0.3, ls=":", which="both"); ax.legend(fontsize=8, loc="lower center")
axs[0][0].set_ylabel("$E\\,d\\Phi/dE$ [n m$^{-2}$ s$^{-1}$]"); fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"fig02_origen_albedo.{e}"), dpi=170)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("por_region",)} for k, v in out["corridas"].items()}, indent=1, ensure_ascii=False))
print("tesis:", out["tesis"])
