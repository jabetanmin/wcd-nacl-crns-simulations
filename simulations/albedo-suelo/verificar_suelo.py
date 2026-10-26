#!/usr/bin/env python3
"""Verifica la prueba del albedo del suelo: eventos, linea del suelo en el registro, pasos en el suelo y cruces del plano."""
import glob, os, re, sys
d, w, N = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
ok = True
def res(c, t):
    global ok
    ok &= bool(c); print("  [OK] " if c else "  [MAL]", t)
log = open(glob.glob(os.path.join(d, "Flujo-*.txt"))[0], errors="replace").read()
lin = next((l for l in log.splitlines() if "[INFO] Suelo SoilBS" in l), "")
nom = "SoilBS," if w == 0 else f"SoilBS_agua{w:.3f},"
rho = 1 / (w / 1.0 + (1 - w) / 2.7)
res(nom in lin, f"registro: {lin.strip() or 'sin linea del suelo'}")
m = re.search(r"densidad = ([0-9.]+)", lin); res(m and abs(float(m.group(1)) - rho) < 1e-3, f"densidad del suelo = {m.group(1) if m else '?'} g/cm3 (esperada {rho:.4f})")
res("tamano = (20, 20, 1)" in lin, "suelo de 20 x 20 x 1 m")
res(len(re.findall("Run terminated", log)) == N, f"{len(re.findall('Run terminated', log))} corridas terminadas de {N}")
res("Overlap is detected" not in log, "sin solapamientos de volumenes")
res("SIN TANQUE" in log, "sin tanque (MEIGA_SIN_TANQUE): " + next((l.strip() for l in log.splitlines() if "SIN TANQUE" in l), "NO aparece la linea"))
ps = os.path.join(d, "Datos-simulacion", "pasos-neutrones.tsv")
n_suelo = baja = sube = 0
for l in open(ps):
    if l[0] == "#": continue
    c = l.split("\t")
    if c[8].startswith("SoilBS"): n_suelo += 1
    z1, z2 = float(c[11]), float(c[14])
    if z1 > 5 >= z2: baja += 1
    elif z1 < 5 <= z2: sube += 1
res(n_suelo > 0, f"pasos de neutrones dentro del suelo: {n_suelo}")
res(baja >= N, f"cruces del plano a 5 cm: {baja} bajando (>= {N} incidentes), {sube} subiendo")
tam = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(d) for f in fs)
tr = [float(x) for x in re.findall(r"Real=([0-9.eE+-]+)s", log)]
if tr: print(f"  tiempo medio por neutron: {sum(tr)/len(tr):.3f} s -> 200 000 n ~ {sum(tr)/len(tr)*2e5/4/3600:.1f} h en 4 partes (prueba con energias extremas)")
print(f"  tamano de la prueba: {tam/1e6:.1f} MB -> 200 000 n ~ {tam/N*2e5/1e9:.0f} GB")
print("TODO CORRECTO" if ok else "HAY PROBLEMAS")
