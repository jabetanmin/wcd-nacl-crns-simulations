#!/usr/bin/env python3
"""Activa o desactiva el termino termico S(alpha,beta) en MEIGA, sin tocar nada mas.

El unico cambio es en G4Models/G4MPhysicsList.cc:
    RegisterPhysics(new G4ThermalNeutrons());
queda comentado, y el mensaje del registro pasa a decir que esta DESACTIVADO.
Sin G4ThermalNeutrons, Geant4 trata el H por debajo de 4 eV como gas libre,
como en la primera campana. Materiales, geometria, PMT y salidas no cambian.

Uso (dentro del contenedor, donde se compila MEIGA):
    python3 desactivar_termico.py /opt/meiga/src/G4Models/G4MPhysicsList.cc            # desactivar
    python3 desactivar_termico.py /opt/meiga/src/G4Models/G4MPhysicsList.cc --activar  # volver a S(alpha,beta)
Despues hay que recompilar MEIGA para que el cambio tenga efecto.
"""
import argparse, shutil, sys
from datetime import datetime
from pathlib import Path

REG = "RegisterPhysics(new G4ThermalNeutrons());"
MARCA = "// DESACTIVADO: corrida sin S(alpha,beta)"
MSG_ON = 'G4cout << "RegisterPhysics: G4ThermalNeutrons "'
MSG_OFF = 'G4cout << "[AVISO] G4ThermalNeutrons DESACTIVADO, H como gas libre "'

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("archivo", type=Path)
ap.add_argument("--activar", action="store_true", help="revertir: volver a registrar G4ThermalNeutrons")
a = ap.parse_args()
if not a.archivo.is_file():
    sys.exit(f"ERROR: no existe {a.archivo}")
lineas = a.archivo.read_text().split("\n")
activas = [i for i, l in enumerate(lineas) if l.strip() == REG]
inactivas = [i for i, l in enumerate(lineas) if l.strip().startswith("// " + REG) and MARCA in l]
if len(activas) + len(inactivas) != 1:
    sys.exit(f"ERROR: se esperaba exactamente 1 registro de G4ThermalNeutrons (activo o desactivado) "
             f"y hay {len(activas)} activos y {len(inactivas)} desactivados. Revise el archivo; no se cambio nada.")
if (not a.activar and inactivas) or (a.activar and activas):
    print("El archivo ya esta en el estado pedido; no se hizo ningun cambio.")
    sys.exit(0)
copia = a.archivo.with_name(a.archivo.name + ".respaldo-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
shutil.copy2(a.archivo, copia)
if a.activar:
    i = inactivas[0]; sangria = lineas[i][:len(lineas[i]) - len(lineas[i].lstrip())]
    lineas[i] = sangria + REG
    lineas = [l.replace(MSG_OFF, MSG_ON) for l in lineas]
else:
    i = activas[0]; sangria = lineas[i][:len(lineas[i]) - len(lineas[i].lstrip())]
    lineas[i] = sangria + "// " + REG + "  " + MARCA
    lineas = [l.replace(MSG_ON, MSG_OFF) for l in lineas]
a.archivo.write_text("\n".join(lineas))
print(f"Respaldo: {copia}")
print("S(alpha,beta) " + ("ACTIVADO" if a.activar else "DESACTIVADO") + ". Recompile MEIGA para aplicar el cambio.")
