#!/usr/bin/env python3
"""
Balance de destinos del neutrón incidente en el barrido rápido (1 keV a 1 GeV), con la misma clasificación de la
Tabla 4.8 y las Tablas C.3--C.5 de la tesis (balance_caras_tanque.py del repositorio):

  Cap    el último paso del neutrón primario es nCapture (dentro o fuera del volumen activo);
  Refle  entra al volumen activo y lo abandona por la cara superior (último cruce);
  Trans  lo abandona por el fondo o por la pared lateral;
  Otros  no entra al volumen activo, o su historia termina en neutronInelastic (u otro proceso).

Volumen activo: |x|, |y| <= 48 cm y el agua en z (133 cm de altura, como los 0--1330 mm de la tesis; en la geometría
del barrido el agua va de z = 0.062 a 133.062 cm, bajo el Tyvek y la tapa de acero). Se comprueba en los datos que
ningún paso en el agua queda fuera de ese intervalo. Solo cuenta la traza del neutrón primario (track_id 1) de cada evento.
Lee <carpeta>/<energía>-<medio>-<N>N/Datos-simulacion/pasos-neutrones.tsv del paquete Barrido-rapidos-WCD.
Uso: balance_rapidos.py <carpeta de resultados del barrido> [<otra carpeta> ...]
-> resultados/balance_rapidos.tsv (mismas columnas que balance_caras_tanque.tsv)
"""
import os, re, subprocess, sys

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(BASE, "resultados", "balance_rapidos.tsv")
MEDIO = {"AguaPura": "Agua-pura", "Agua25NaCl": "Agua+2.5NaCl", "Agua5NaCl": "Agua+5NaCl", "Agua10NaCl": "Agua+10NaCl"}
UNID = {"eV": 1, "keV": 1e3, "MeV": 1e6, "GeV": 1e9}
# por evento, la traza 1: estado de entrada/salida del volumen activo y el último paso
AWK = r'''BEGIN { FS = "\t" }
/^#/ { next }
$9 ~ /Water/ { if (zmin == "" || $12 < zmin) zmin = $12; if (zmax == "" || $12 > zmax) zmax = $12 }
$4 != 1 { next }
{ r = $1; s = $6 + 0
  a = (($10 < 0 ? -$10 : $10) <= 48 && ($11 < 0 ? -$11 : $11) <= 48 && $12 >= ZB && $12 <= ZT)
  b = (($13 < 0 ? -$13 : $13) <= 48 && ($14 < 0 ? -$14 : $14) <= 48 && $15 >= ZB && $15 <= ZT)
  if (!(r in ult) || s >= ult[r]) { ult[r] = s; proc[r] = $8; fin[r] = b }
  if (b) entro[r] = 1
  if (a && !b && s >= tsal[r]) { tsal[r] = s; sal[r] = ($15 > ZT ? "arriba" : ($15 < ZB ? "abajo" : "lateral")) }
  if (!a && b && s >= tent[r]) tent[r] = s }
END {
  for (r in ult) {
    if (proc[r] == "nCapture") c = fin[r] ? "cap_dentro" : "cap_fuera"
    else if (proc[r] == "neutronInelastic") c = fin[r] ? "inel_dentro" : "inel_fuera"
    else if (!(r in entro)) c = "no_entra"
    else if ((r in sal) && tsal[r] > tent[r]) c = sal[r]
    else c = "otro"
    n[c]++ }
  printf "#zagua %s %s\n", zmin, zmax
  for (c in n) printf "%s %d\n", c, n[c] }'''
# agua del SaltyWCD en la geometría del barrido: H = 133 cm con la superficie en z = 133.062 cm (bajo el Tyvek y la tapa)
ZB, ZT = 0.062, 133.062
CLAVES = ["cap_dentro", "cap_fuera", "arriba", "abajo", "lateral", "no_entra", "inel_dentro", "inel_fuera", "otro"]

filas = []
for raiz in sys.argv[1:]:
    for d in sorted(os.listdir(raiz)):
        m = re.fullmatch(r"([0-9.]+)(eV|keV|MeV|GeV)-(\w+)-(\d+)N", d)
        f = os.path.join(raiz, d, "Datos-simulacion", "pasos-neutrones.tsv")
        if not m or int(m.group(4)) < 1000 or m.group(3) not in MEDIO or not os.path.isfile(f): continue
        txt = subprocess.run(["mawk", "-v", f"ZB={ZB}", "-v", f"ZT={ZT}", AWK, f], capture_output=True, text=True, check=True,
                             env={"LC_ALL": "C", "PATH": os.environ["PATH"]}).stdout.split("\n")
        z = txt[0].split()[1:]; c = {l.split()[0]: int(l.split()[1]) for l in txt[1:] if l.strip()}
        N = int(m.group(4)); n = sum(c.values())
        assert n == N, f"{d}: {n} historias del primario para {N} neutrones"
        assert z and float(z[0]) >= ZB - 1e-6 and abs(float(z[1]) - ZT) < 1e-3, f"{d}: el agua va de {z} cm, no de {ZB} a {ZT}"
        E_meV = float(m.group(1)) * UNID[m.group(2)] * 1e3
        g = lambda *k: sum(c.get(x, 0) for x in k) / n
        filas.append((E_meV, d, MEDIO[m.group(3)], N, c, g("cap_dentro", "cap_fuera"), g("arriba"), g("abajo", "lateral"),
                      g("no_entra", "inel_dentro", "inel_fuera", "otro")))
        print(f"{d:28s} Cap {100 * filas[-1][5]:6.2f}  Refle {100 * filas[-1][6]:6.2f}  Trans {100 * filas[-1][7]:6.2f}  Otros {100 * filas[-1][8]:6.2f}")
if not filas: raise SystemExit("no se encontraron corridas del barrido rápido con pasos-neutrones.tsv")
with open(OUT, "w") as fo:
    fo.write("energia\tmedio\tN\t" + "\t".join(CLAVES) + "\teta_cap\teta_refle\teta_trans\teta_otros\tE_meV\n")
    for E, d, mc, N, c, *eta in sorted(filas, key=lambda x: (x[2], x[0])):
        fo.write(f"{d.split('-')[0]}\t{mc}\t{N}\t" + "\t".join(str(c.get(k, 0)) for k in CLAVES) +
                 "\t" + "\t".join(f"{x:.6f}" for x in eta) + f"\t{E:g}\n")
print("->", OUT)
