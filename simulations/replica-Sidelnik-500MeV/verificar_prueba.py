#!/usr/bin/env python3
"""Verifica la corrida de prueba (10 neutrones) antes de lanzar la completa.

Comprueba en el registro y en Datos-simulacion/ que:
  1. Fisica QGSP_BERT_HP sin S(alpha,beta) (opcion QGSP_BERT_HP_NoThermal de MEIGA).
  2. El medio es el pedido (material, w_NaCl de la Ec. 3.12 y densidad de la Tabla 3.6 de la tesis)
     y la geometria es la esperada (R = 48 cm, H = 133 cm, Tyvek 0,12 mm, acero 0,5 mm).
  3. Cada neutron primario arranca en (-49,062; 0; 66,562) cm con 500 MeV y viaja en +x.
  4. El primario atraviesa aire -> acero -> Tyvek -> agua.
  5. El PMT (Pyrex) esta en la tapa: z entre 128,05 y 133,05 cm.
Uso: python3 verificar_prueba.py <carpeta de resultados de la prueba> [agua-pura|nacl-2.5|nacl-5|nacl-10]
"""
import sys, glob, os, csv

D = sys.argv[1]
MEDIO = sys.argv[2] if len(sys.argv) > 2 else "agua-pura"
# material de MEIGA, fraccion masica final w_NaCl (Ec. 3.12) y densidad (Tabla 3.6) esperados
ESPERADO = {"agua-pura": ("Water_TS_H_of_Water", 0.0, 0.99820),
            "nacl-2.5": ("SaltyWater_NaCl_2.5pct", 0.025, 1.01604),
            "nacl-5": ("SaltyWater_NaCl_5.0pct", 0.05, 1.03401),
            "nacl-10": ("SaltyWater_NaCl_10.0pct", 0.10, 1.07051)}[MEDIO]
ok = True


def check(cond, msg):
    global ok
    print(("  OK    " if cond else "  FALLA ") + msg)
    ok &= bool(cond)


log = open(glob.glob(os.path.join(D, "Flujo-*.txt"))[0], errors="replace").read()
print("1. Fisica")
check("without S(alpha,beta)" in log, "MEIGA anuncia QGSP_BERT_HP sin S(alpha,beta) (gas libre, fisica de la campana 1)")
check("RegisterPhysics: G4ThermalNeutrons" not in log, "G4ThermalNeutrons no aparece registrado")
check("Physics List simulation engine: QGSP_BERT_HP" in log, "la lista base es QGSP_BERT_HP (no FTFP_BERT)")

print("2. Medio y geometria")
def valor(clave):
    l = next((l for l in log.splitlines() if clave in l), "")
    return l.split("=", 1)[1].strip() if l else "no encontrado"


mat, w, rho = ESPERADO
check(valor("Active medium =") == mat, f"medio activo = {valor('Active medium =')} (esperado {mat})")
try:
    check(abs(float(valor("NaCl final mass fraction =")) - w) < 1e-9, f"fraccion masica final w_NaCl = {valor('NaCl final mass fraction =')} (esperado {w}, Ec. 3.12)")
except ValueError:
    check(False, "no se encontro la fraccion masica de NaCl en el registro")
try:
    check(abs(float(valor("Active-medium density =").split()[0]) - rho) < 1e-5, f"densidad = {valor('Active-medium density =')} (esperado {rho} g/cm3, Tabla 3.6)")
except ValueError:
    check(False, "no se encontro la densidad del medio en el registro")
for clave, valor in [("Water radius =", "48"), ("Water height =", "133"), ("Steel thickness =", "0.5"), ("Tyvek thickness =", "0.12")]:
    linea = next((l for l in log.splitlines() if clave in l), "")
    check(valor in linea, f"{clave} {linea.split('=')[-1].strip() if linea else 'no encontrado'} (esperado {valor})")

print("3. Fuente")
DS = os.path.join(D, "Datos-simulacion")
inc = os.path.join(DS, "neutrones-incidentes.tsv")
filas = [r for r in csv.reader(open(inc), delimiter="\t") if r and not r[0].startswith("#")]
check(len(filas) == 10, f"{len(filas)} neutrones incidentes (esperado 10)")
for r in filas[:10]:
    x0, y0, z0, x1, y1, z1 = map(float, r[9:15]); e0 = float(r[15])
    bien = abs(x0 + 49.062) < 1e-3 and abs(y0) < 1e-3 and abs(z0 - 66.562) < 1e-3 and abs(e0 - 500) < 0.01 \
        and x1 > x0 and abs(y1 - y0) < 1e-6 and abs(z1 - z0) < 1e-6
    if not bien:
        check(False, f"evento {r[1]}: inicio ({x0}, {y0}, {z0}) cm, {e0} MeV, fin del paso ({x1}, {y1}, {z1})")
        break
else:
    check(True, "todos arrancan en (-49,062; 0; 66,562) cm con 500 MeV (±0,01) y su primer paso va en +x")

print("4. Recorrido del primer neutron primario (track 1)")
mats = []
for r in csv.reader(open(os.path.join(DS, "pasos-neutrones.tsv")), delimiter="\t"):
    # MEIGA lanza cada particula como una corrida (run) aparte con event_id 0: se filtra por (run, evento)
    if r and not r[0].startswith("#") and (r[0], r[1]) == (filas[0][0], filas[0][1]) and r[3] == "1":
        if not mats or mats[-1] != r[8]:
            mats.append(r[8])
print("   materiales (pre-paso):", " -> ".join(mats[:8]))
check(len(mats) >= 2 and "STAINLESS" in mats[1].upper(), "tras el aire, el primario entra al acero inoxidable")
check(any("Water" in m for m in mats), "el primario llega al agua")

print("5. PMT (pasos en Pyrex de pasos-particulas.tsv)")
# PMT de Sidelnik: semielipsoide con la cara plana 0,1 mm bajo la tapa del agua -> z entre 128,05 y 133,05 cm
zs = []
pp = os.path.join(DS, "pasos-particulas.tsv")
if os.path.exists(pp):
    for r in csv.reader(open(pp), delimiter="\t"):
        if r and not r[0].startswith("#") and r[8] == "Pyrex":
            zs.append(float(r[11]))
if zs:
    check(min(zs) >= 128.0 and max(zs) <= 133.1, f"pasos en el PMT entre z = {min(zs):.2f} y {max(zs):.2f} cm (esperado 128,05-133,05: PMT en la tapa)")
else:
    print("  AVISO ninguna particula paso por el PMT en esta prueba; no se pudo comprobar su posicion")

print("\nRESULTADO: " + ("TODO CORRECTO, puede lanzar la corrida completa." if ok else "HAY FALLAS: no lance la corrida completa."))
sys.exit(0 if ok else 1)
