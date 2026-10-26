#!/usr/bin/env python3
"""Baja el PMT de la tapa a la posición de las otras corridas: zPMT = 0.3*fWaterHalfHeight.

La cara plana del semielipsoide (la parte superior del PMT) queda a 0.3 x 66.5 = 19.95 cm sobre el centro
del agua: 86.45 cm sobre el fondo del agua y 46.55 cm bajo la tapa. Solo cambia la posición: la forma del
PMT de Sidelnik (10.16 x 10.16 x 5 cm, en OptDevice.cc) se mantiene.

Parte del MEIGA con el PMT de Sidelnik (línea "zPMT = fWaterHalfHeight - 0.1*mm;  // SIDELNIK: PMT en la
tapa"). La línea original se guarda en SaltyWCD.cc.linea-zPMT-tapa (y una copia de respaldo del archivo),
y --revertir la restaura exactamente.

Uso (dentro del contenedor):
    python3 bajar_pmt.py /opt/meiga/src              # bajar el PMT
    python3 bajar_pmt.py /opt/meiga/src --revertir   # volver al PMT de Sidelnik en la tapa
Después hay que recompilar MEIGA (preparar_meiga.sh lo hace).
"""
import argparse, re, shutil, sys
from datetime import datetime
from pathlib import Path

MARCA = "// PMT-BAJO:"
NUEVA = "const G4double zPMT = 0.3*fWaterHalfHeight;  " + MARCA + " cara plana a 86.45 cm del fondo, 46.55 cm bajo la tapa"
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("src", type=Path, help="carpeta src de MEIGA (contiene G4Models/)")
ap.add_argument("--revertir", action="store_true")
a = ap.parse_args()
salty = a.src / "G4Models" / "SaltyWCD.cc"
guardada = salty.with_name("SaltyWCD.cc.linea-zPMT-tapa")
if not salty.is_file():
    sys.exit(f"ERROR: no existe {salty}")
ls = salty.read_text().split("\n")
act = [i for i, l in enumerate(ls) if re.match(r"\s*const G4double zPMT = [^;]+;", l)]
if len(act) != 1:
    sys.exit(f"ERROR: se esperaba 1 línea activa 'const G4double zPMT = ...;' y hay {len(act)}. No se cambió nada.")
i = act[0]; linea = ls[i]; sangria = linea[:len(linea) - len(linea.lstrip())]
respaldo = lambda: shutil.copy2(salty, salty.with_name(salty.name + ".respaldo-" + datetime.now().strftime("%Y%m%d-%H%M%S")))

if not a.revertir:
    if MARCA in linea:
        print("El PMT ya está bajado (0.3*fWaterHalfHeight); no se hizo ningún cambio."); sys.exit(0)
    if "fWaterHalfHeight - 0.1*mm" not in linea or "SIDELNIK: PMT en la tapa" not in linea:
        sys.exit(f"ERROR: la línea zPMT no es la del PMT de Sidelnik en la tapa:\n  {linea.strip()}\nNo se cambió nada.")
    respaldo()
    guardada.write_text(linea + "\n")
    ls[i] = sangria + NUEVA
    print(f"PMT BAJADO: zPMT = 0.3*fWaterHalfHeight (línea {i + 1}). Línea original guardada en {guardada.name}.")
else:
    if MARCA not in linea:
        print("El PMT no está bajado; no se hizo ningún cambio."); sys.exit(0)
    if not guardada.is_file():
        sys.exit(f"ERROR: no está {guardada}; restaure SaltyWCD.cc desde su respaldo.")
    respaldo()
    ls[i] = guardada.read_text().rstrip("\n")
    guardada.unlink()
    print(f"PMT REVERTIDO a la tapa (Sidelnik): {ls[i].strip()}")
salty.write_text("\n".join(ls))
print("Recompile MEIGA para aplicar el cambio.")
