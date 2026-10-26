#!/usr/bin/env python3
"""Verifica la prueba de muones verticales: número de eventos, partícula (mu-), inyección desde el archivo
(eFromFile), dirección vertical hacia abajo (pz invertido por ParticleFiller), medio, física, geometría y carga.
Uso: verificar_prueba.py <carpeta_parte> <archivo_flujo> <w_NaCl>"""
import glob, gzip, json, os, re, sys
import numpy as np

carpeta, flujo, w = sys.argv[1], sys.argv[2], float(sys.argv[3])
M_N = 939.565
ok, avisos = True, []
def mal(t):
    global ok; ok = False; print("  [MAL]", t)
def bien(t): print("  [OK] ", t)

F = np.loadtxt(flujo)
N = len(F)
js = [p for p in (os.path.join(carpeta, "output.json.gz"), os.path.join(carpeta, "output.json")) if os.path.exists(p)]
if not js:
    mal("no hay output.json(.gz)"); sys.exit(1)
d = json.load(gzip.open(js[0], "rt") if js[0].endswith(".gz") else open(js[0]))["Output"]
ev = sorted((k for k in d if k.startswith("Event_")), key=lambda k: int(k.split("_")[1]))
(bien if len(ev) == N else mal)(f"eventos en output.json: {len(ev)} (archivo: {N})")
pos = np.array([d[k]["InputFlux"]["Position"] for k in ev])          # mm
mom = np.array([d[k]["InputFlux"]["Momentum"] for k in ev])          # MeV/c
pos_esp = F[:len(ev), 4:7] * 10.0
mom_esp = F[:len(ev), 1:4] * 1000.0 * np.array([1, 1, -1])
dp = np.max(np.abs(pos - pos_esp)); (bien if dp < 0.05 else mal)(f"posición de inyección = la del archivo (máx. dif. {dp:.3g} mm)")
rel = np.max(np.abs(mom - mom_esp) / np.maximum(np.linalg.norm(mom_esp, axis=1)[:, None], 1e-30))
(bien if rel < 1e-4 else mal)(f"momento = (px, py, -pz) del archivo (máx. dif. relativa {rel:.2g})")
ids = [d[k]["InputFlux"]["ID"] for k in ev]
(bien if all(i == 13 for i in ids) else mal)(f"partícula = mu- (PDG 13): {sorted(set(ids))}")
uz = mom[:, 2] / np.linalg.norm(mom, axis=1)
(bien if np.all(uz < -0.9999) else mal)(f"todos los muones van verticales hacia abajo (u_z máx = {uz.max():.5f})")
p = np.linalg.norm(mom, axis=1); print(f"  momento: {p.min():.1f} ... {p.max():.1f} MeV/c")
q = np.array([d[k]["Detector_0"]["OptDevice_0"]["Charge"] for k in ev if "Detector_0" in d[k]])
(bien if len(q) == len(ev) and np.all(q > 0) else mal)(f"todos los muones dan carga: {np.sum(q > 0)} de {len(ev)}")
if len(q):
    print(f"  carga por muón [p.e.]: media {q.mean():.1f}, mediana {np.median(q):.1f}, mín {q.min()}, máx {q.max()}  "
          f"(pico de muones del fondo medido: ~41 000 ADC = 162 p.e. con 3.95 p.e./1000 ADC)")

logs = glob.glob(os.path.join(carpeta, "Flujo-*.txt"))
if not logs:
    mal("no se encontró el registro de MEIGA")
else:
    t = open(logs[0], errors="replace").read()
    (bien if "Injection Mode: eFromFile" in t else mal)("registro: Injection Mode = eFromFile")
    def valor(clave):
        l = next((l for l in t.splitlines() if clave in l), "")
        return l.split("=", 1)[1].strip() if l else None
    # el formato del registro cambió entre versiones de MEIGA: se aceptan los dos
    wv = valor("NaCl final mass fraction =") or valor("Fraccion de impurezas en el agua =")
    try:
        (bien if wv is not None and abs(float(wv.split()[0]) - w) < 1e-9 else mal)(f"registro: fracción de NaCl = {wv} (esperada {w})")
    except ValueError:
        mal(f"registro: fracción de NaCl ilegible: {wv}")
    med = valor("Active medium ="); rho = valor("Active-medium density =")
    # material y densidad esperados (Tabla 3.6 de la tesis) para cada fracción de NaCl
    ESP = {0.0: ("Water_TS_H_of_Water", 0.99820), 0.025: ("SaltyWater_NaCl_2.5pct", 1.01604),
           0.05: ("SaltyWater_NaCl_5.0pct", 1.03401), 0.1: ("SaltyWater_NaCl_10.0pct", 1.07051)}
    if med:
        m_esp, r_esp = ESP.get(round(w, 3), (None, None))
        (bien if med == m_esp else mal)(f"registro: medio activo = {med} (esperado {m_esp})")
        try:
            (bien if abs(float(rho.split()[0]) - r_esp) < 1e-4 else mal)(f"registro: densidad = {rho} (esperada {r_esp} g/cm3)")
        except (AttributeError, ValueError, TypeError):
            mal(f"registro: densidad ilegible: {rho}")
    (bien if "QGSP_BERT_HP_NoThermal" in t or "without S(alpha,beta)" in t else mal)("registro: física sin S(alpha,beta) (QGSP_BERT_HP_NoThermal)")
    (bien if not re.search(r"RegisterPhysics:.*[Tt]hermal", t) else mal)("registro: sin física térmica S(alpha,beta) registrada")
    rad, alt = valor("Water radius ="), valor("Water height =")
    if rad and alt:
        (bien if rad.startswith("48") and alt.startswith("133") else mal)(f"registro: agua R = {rad}, H = {alt}; acero {valor('Steel thickness =')}; Tyvek {valor('Tyvek thickness =')}")
    else:
        (bien if "Tank Radius = 48 cm" in t and "Tank Height = 133 cm" in t else mal)("registro: tanque R = 48 cm, H = 133 cm")
    nrun = len(re.findall(r"Run terminated", t)); (bien if nrun == N else mal)(f"registro: {nrun} corridas terminadas")
    tr = [float(x) for x in re.findall(r"Real=([0-9.eE+-]+)s", t)]
    if tr:
        print(f"  tiempo medio por muón: {np.mean(tr):.1f} s  -> 2000 muones ~ {np.mean(tr)*2000/3600:.1f} h en un núcleo (~{np.mean(tr)*2000/3600/4:.1f} h en 4 partes)")
tam = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(carpeta) for f in fs)
print(f"  tamaño de la prueba: {tam/1e6:.1f} MB -> 2000 muones ~ {tam/N*2000/1e9:.0f} GB")
print("TODO CORRECTO" if ok else "HAY PROBLEMAS: no lance la corrida completa")
sys.exit(0 if ok else 1)
