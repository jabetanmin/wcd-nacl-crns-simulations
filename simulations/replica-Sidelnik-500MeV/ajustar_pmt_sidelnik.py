#!/usr/bin/env python3
"""Pone el PMT como en Sidelnik et al. (2020): arriba y en el centro, con la forma del articulo.

Cambios (reversibles con --revertir; se guarda un respaldo de cada archivo):
  1. G4Models/SaltyWCD.cc   : zPMT = fWaterHalfHeight - 0.1*mm
       (la cara plana del semielipsoide queda 0,1 mm bajo la tapa del agua y el domo
        cuelga dentro del agua, como en la Fig. 1 del articulo)
  2. Framework/Detector/OptDevice.cc (caso ePMT): semiejes 10.1, 10.1, 6.5 cm -> 10.16, 10.16, 5.0 cm
       (casquete de radio 10,16 cm y altura h = 5 cm, Sec. 2 del articulo)
Afecta a todos los detectores con ePMT (SaltyWCD y WCD); por eso conviene revertir al terminar.

Uso (dentro del contenedor, sobre el codigo que se compila):
    python3 ajustar_pmt_sidelnik.py /opt/meiga/src              # aplicar
    python3 ajustar_pmt_sidelnik.py /opt/meiga/src --revertir   # volver al MEIGA original
Despues hay que recompilar MEIGA.
"""
import argparse, re, shutil, sys
from datetime import datetime
from pathlib import Path

MARCA = "// SIDELNIK:"
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("src", type=Path, help="carpeta src de MEIGA (contiene G4Models/ y Framework/)")
ap.add_argument("--revertir", action="store_true")
a = ap.parse_args()
salty = a.src / "G4Models" / "SaltyWCD.cc"
optdev = a.src / "Framework" / "Detector" / "OptDevice.cc"
for f in (salty, optdev):
    if not f.is_file():
        sys.exit(f"ERROR: no existe {f}")


def respaldo(f):
    c = f.with_name(f.name + ".respaldo-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    shutil.copy2(f, c)
    return c


def sangria(l):
    return l[:len(l) - len(l.lstrip())]


ls = salty.read_text().split("\n")
lo = optdev.read_text().split("\n")
z_act = [i for i, l in enumerate(ls) if re.match(r"\s*const G4double zPMT = [^;]+;", l)]
z_ori = [i for i, l in enumerate(ls) if l.strip().startswith(MARCA + " original: const G4double zPMT")]
# lineas activas (no comentadas) del caso ePMT; los bloques comentados empiezan con //
ejes = {}
for eje in "XYZ":
    ejes[eje] = [i for i, l in enumerate(lo) if re.match(rf"\s*SetSemiAxis{eje}\([\d.]+\);", l)]
if len(z_act) != 1 or any(len(v) != 1 for v in ejes.values()):
    sys.exit(f"ERROR: se esperaba 1 linea zPMT y 1 SetSemiAxis por eje activas; hay zPMT={len(z_act)}, "
             f"ejes={ {k: len(v) for k, v in ejes.items()} }. No se cambio nada.")
aplicado = MARCA in ls[z_act[0]]

if not a.revertir:
    if aplicado:
        print("El PMT ya esta en la configuracion de Sidelnik; no se hizo ningun cambio.")
        sys.exit(0)
    print("Respaldos:", respaldo(salty), respaldo(optdev))
    i = z_act[0]; s = sangria(ls[i])
    ls[i:i + 1] = [s + MARCA + " original: " + ls[i].strip(),
                   s + "const G4double zPMT = fWaterHalfHeight - 0.1*mm;  " + MARCA + " PMT en la tapa"]
    nuevos = {"X": "10.16", "Y": "10.16", "Z": "5.0"}
    for eje, (j,) in ejes.items():
        s = sangria(lo[j])
        lo[j] = s + f"SetSemiAxis{eje}({nuevos[eje]});  {MARCA} original: {lo[j].strip()}"
    print("PMT de Sidelnik APLICADO: en la tapa (cara plana 0,1 mm bajo el agua), semiejes 10,16 x 10,16 x 5 cm.")
else:
    if not aplicado:
        print("El PMT ya esta como en el MEIGA original; no se hizo ningun cambio.")
        sys.exit(0)
    if len(z_ori) != 1:
        sys.exit("ERROR: no se encontro la linea original de zPMT guardada; restaure desde el respaldo.")
    print("Respaldos:", respaldo(salty), respaldo(optdev))
    s = sangria(ls[z_ori[0]])
    original = ls[z_ori[0]].strip()[len(MARCA + " original: "):]
    del ls[z_act[0]]
    ls[z_ori[0]] = s + original
    for eje, (j,) in ejes.items():
        if MARCA in lo[j]:
            lo[j] = sangria(lo[j]) + lo[j].split(MARCA + " original: ")[1]
    print("PMT REVERTIDO al MEIGA original.")
salty.write_text("\n".join(ls))
optdev.write_text("\n".join(lo))
print("Recompile MEIGA para aplicar el cambio.")
