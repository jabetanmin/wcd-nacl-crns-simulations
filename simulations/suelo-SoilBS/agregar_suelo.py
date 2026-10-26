#!/usr/bin/env python3
"""Agrega a G4WCDSimulator (MEIGA) el suelo modelo SoilBS de la tesis, seco o húmedo, con el tanque apoyado encima.

Solo cambia Applications/G4WCDSimulator/G4WCDConstruction.cc (se guarda una copia exacta del original para revertir).
El suelo se crea ÚNICAMENTE si está definida la variable de entorno MEIGA_SUELO_W; sin ella MEIGA se comporta
exactamente igual que antes, así que los demás paquetes de corrida no se ven afectados.

  MEIGA_SUELO_W   fracción másica de agua del suelo: 0 = seco; 0.05, 0.10, 0.15, 0.25, 0.30 (tesis, Tabla de humedad)
  MEIGA_SUELO_XY  (opcional) lado del suelo en m (por defecto groundSizeX/Y de MEIGA, 5 m)
  MEIGA_SUELO_Z   (opcional) profundidad en m (por defecto groundSizeZ de MEIGA, 1 m, como en la tesis)
  MEIGA_SIN_TANQUE (opcional) si está definida, no se construye el tanque: solo el suelo (estudios de albedo)
  MEIGA_SUELO_SEPARACION (opcional) altura en m del fondo del tanque sobre el suelo; 0 por defecto (apoyado).
                  En los experimentos del prototipo el tanque está a 2 m: MEIGA_SUELO_SEPARACION=2.
                  El tanque no se mueve (su fondo sigue en z = 0); el suelo baja a z = -separación.

Material (tesis, cap. 3, Etapa III; Ariza Gómez y Carrillo Moreno 2020, Tabla 3, a partir de Juárez Sanz et al. 2006):
  SoilBS, 2.7 g/cm3, fracciones másicas O 0.4900, Si 0.3300, Al 0.0713, Na 0.0063, K 0.0136, Ca 0.0137, Fe 0.0380,
  Mg 0.0060, C 0.0200, S 0.0008, N 0.0010, P 0.0009, Ti 0.0046, H 0.0038.
  Suelo húmedo: mezcla SoilBS (1-w) + agua (w), densidad (w/1.0 + (1-w)/2.7)^-1 g/cm3 (volúmenes aditivos).
  El hidrógeno del agua del suelo usa el elemento TS_H_of_Water de MEIGA (si existe), como el agua del tanque.
Geometría: caja de suelo centrada en x = y = 0, con su cara superior en z = -separación (por defecto 0: el tanque queda
  apoyado sobre el suelo; con MEIGA_SUELO_SEPARACION=2, a 2 m como en los experimentos). El mundo se agranda si hace falta.

Uso (dentro del contenedor):
    python3 agregar_suelo.py /opt/meiga/src              # aplicar
    python3 agregar_suelo.py /opt/meiga/src --revertir   # volver al original
    python3 agregar_suelo.py /opt/meiga/src --estado     # ¿está aplicado?
Después hay que recompilar (preparar_suelo.sh lo hace).
"""
import argparse, re, shutil, sys
from datetime import datetime
from pathlib import Path

MARCA = "SUELO-SoilBS"
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("src", type=Path)
g = ap.add_mutually_exclusive_group()
g.add_argument("--revertir", action="store_true")
g.add_argument("--estado", action="store_true")
a = ap.parse_args()
f = a.src / "Applications" / "G4WCDSimulator" / "G4WCDConstruction.cc"
orig = f.with_name(f.name + ".original-suelo")
if not f.is_file():
    sys.exit(f"ERROR: no existe {f}")
s = f.read_text()
aplicado = MARCA in s

if a.estado:
    print("Suelo SoilBS: APLICADO" if aplicado else "Suelo SoilBS: no aplicado"); sys.exit(0)

if a.revertir:
    if not aplicado:
        print("El parche del suelo no está aplicado; no se hizo ningún cambio."); sys.exit(0)
    if not orig.is_file():
        sys.exit(f"ERROR: no está la copia original {orig}; no se puede revertir con seguridad.")
    shutil.copy2(f, f.with_name(f.name + ".con-suelo-" + datetime.now().strftime("%Y%m%d-%H%M%S")))
    shutil.copy2(orig, f); orig.unlink()
    print("Parche del suelo REVERTIDO: G4WCDConstruction.cc es otra vez el original. Recompile MEIGA.")
    sys.exit(0)

if aplicado:
    print("El parche del suelo ya está aplicado; no se hizo ningún cambio."); sys.exit(0)

# --- 1. llamadas en CreateDetector: CreateWorld(); //CreateGround(); PlaceDetector(fEvent);
patron_llamadas = re.compile(r"(?P<i>[ \t]*)CreateWorld\(\);\s*\n[ \t]*//\s*CreateGround\(\);\s*\n(?P<j>[ \t]*)PlaceDetector\(fEvent\);")
m = patron_llamadas.search(s)
if not m:
    sys.exit("ERROR: no se encontró en CreateDetector() la secuencia 'CreateWorld(); //CreateGround(); PlaceDetector(fEvent);'.\n"
             "El código del contenedor es distinto del esperado: no se cambió nada (mande G4WCDConstruction.cc para revisarlo).")
i = m.group("i")
nuevo_llamadas = f"""{i}// {MARCA}: suelo bajo el tanque solo si esta definida la variable de entorno MEIGA_SUELO_W
{i}if (const char* sw = std::getenv("MEIGA_SUELO_W")) {{
{i}	char* fin = nullptr;
{i}	gSueloW = std::strtod(sw, &fin);
{i}	if (fin == sw || gSueloW < 0. || gSueloW > 0.5) {{
{i}		G4cerr << "[ERROR] MEIGA_SUELO_W = '" << sw << "' no es una fraccion masica de agua valida (0 a 0.5)" << G4endl;
{i}		std::exit(1);
{i}	}}
{i}	gSueloActivo = true;
{i}	const G4double gx = fEvent.GetDetector(0).GetGroundSizeX();
{i}	const G4double gy = fEvent.GetDetector(0).GetGroundSizeY();
{i}	const G4double gz = fEvent.GetDetector(0).GetGroundSizeZ();
{i}	if (gx > 0.) fGroundSizeX = gx;
{i}	if (gy > 0.) fGroundSizeY = gy;
{i}	if (gz > 0.) fGroundSizeZ = gz;
{i}	if (const char* sxy = std::getenv("MEIGA_SUELO_XY")) fGroundSizeX = fGroundSizeY = std::atof(sxy) * CLHEP::m;
{i}	if (const char* sz = std::getenv("MEIGA_SUELO_Z")) fGroundSizeZ = std::atof(sz) * CLHEP::m;
{i}	if (const char* ss = std::getenv("MEIGA_SUELO_SEPARACION")) {{   // altura del fondo del tanque sobre el suelo
{i}		char* fin2 = nullptr;
{i}		gSueloSep = std::strtod(ss, &fin2) * CLHEP::m;
{i}		if (fin2 == ss || gSueloSep < 0. || gSueloSep > 50. * CLHEP::m) {{
{i}			G4cerr << "[ERROR] MEIGA_SUELO_SEPARACION = '" << ss << "' no es una altura valida en m (0 a 50)" << G4endl;
{i}			std::exit(1);
{i}		}}
{i}	}}
{i}	fWorldSizeX = std::max(fWorldSizeX, fGroundSizeX + 0.5 * CLHEP::m);
{i}	fWorldSizeY = std::max(fWorldSizeY, fGroundSizeY + 0.5 * CLHEP::m);
{i}	fWorldSizeZ = std::max(fWorldSizeZ, 2. * (gSueloSep + fGroundSizeZ + 0.5 * CLHEP::m));
{i}}}
{i}CreateWorld();
{i}if (gSueloActivo) CreateGround();   // {MARCA}
{i}if (std::getenv("MEIGA_SIN_TANQUE")) {{   // {MARCA}: solo el suelo, sin construir el tanque
{i}	G4cout << "[INFO] Suelo SoilBS: SIN TANQUE (MEIGA_SIN_TANQUE definida): no se construye ningun detector" << G4endl;
{i}}} else {{
{m.group('j')}	PlaceDetector(fEvent);
{i}}}"""
s = s[:m.start()] + nuevo_llamadas + s[m.end():]

# --- 2. cuerpo de CreateGround()
patron_suelo = re.compile(r"void\s*\n\s*G4WCDConstruction::CreateGround\(\)\s*\{.*?\n\}\n", re.S)
m = patron_suelo.search(s)
if not m:
    sys.exit("ERROR: no se encontró la función G4WCDConstruction::CreateGround(); no se cambió nada.")
nuevo_suelo = f"""void
G4WCDConstruction::CreateGround()
{{
	// {MARCA}: suelo seco modelo de la tesis (cap. 3, Etapa III; Ariza Gomez y Carrillo Moreno 2020, Tabla 3,
	// a partir de Juarez Sanz et al. 2006), 2.7 g/cm3; suelo humedo = SoilBS (1-w) + agua (w), volumenes aditivos.
	G4NistManager* nist = G4NistManager::Instance();
	G4Material* seco = G4Material::GetMaterial("SoilBS", false);
	if (!seco) {{
		const char* el[14] = {{"O", "Si", "Al", "Na", "K", "Ca", "Fe", "Mg", "C", "S", "N", "P", "Ti", "H"}};
		const G4double fr[14] = {{0.4900, 0.3300, 0.0713, 0.0063, 0.0136, 0.0137, 0.0380,
		                          0.0060, 0.0200, 0.0008, 0.0010, 0.0009, 0.0046, 0.0038}};
		seco = new G4Material("SoilBS", 2.7 * CLHEP::g / CLHEP::cm3, 14);
		for (int k = 0; k < 14; k++) seco->AddElement(nist->FindOrBuildElement(el[k]), fr[k]);
	}}
	G4Material* suelo = seco;
	if (gSueloW > 0.) {{
		char nombre[64];
		std::snprintf(nombre, sizeof(nombre), "SoilBS_agua%.3f", gSueloW);
		suelo = G4Material::GetMaterial(nombre, false);
		if (!suelo) {{
			G4Element* hAgua = G4Element::GetElement("TS_H_of_Water", false);
			if (!hAgua) hAgua = nist->FindOrBuildElement("H");
			G4Material* agua = G4Material::GetMaterial("AguaSuelo", false);
			if (!agua) {{
				agua = new G4Material("AguaSuelo", 1.0 * CLHEP::g / CLHEP::cm3, 2);
				agua->AddElement(hAgua, 2);
				agua->AddElement(nist->FindOrBuildElement("O"), 1);
			}}
			const G4double rho = 1. / (gSueloW / (1.0 * CLHEP::g / CLHEP::cm3) + (1. - gSueloW) / (2.7 * CLHEP::g / CLHEP::cm3));
			suelo = new G4Material(nombre, rho, 2);
			suelo->AddMaterial(seco, 1. - gSueloW);
			suelo->AddMaterial(agua, gSueloW);
		}}
	}}
	G4cout << "[INFO] Suelo SoilBS: material = " << suelo->GetName()
	       << ", fraccion masica de agua = " << gSueloW
	       << ", densidad = " << suelo->GetDensity() / (CLHEP::g / CLHEP::cm3) << " g/cm3"
	       << ", tamano = (" << fGroundSizeX / CLHEP::m << ", " << fGroundSizeY / CLHEP::m << ", " << fGroundSizeZ / CLHEP::m << ") m"
	       << ", superficie en z = " << (gSueloSep > 0. ? -gSueloSep / CLHEP::m : 0.) << " m (tanque a " << gSueloSep / CLHEP::m << " m sobre el suelo)"
	       << ", mundo = (" << fWorldSizeX / CLHEP::m << ", " << fWorldSizeY / CLHEP::m
	       << ", " << fWorldSizeZ / CLHEP::m << ") m" << G4endl;
	solidGround = new G4Box("Ground", fGroundSizeX/2, fGroundSizeY/2, fGroundSizeZ/2);
	G4VisAttributes brown(G4Colour::Brown());
	logicGround = new G4LogicalVolume(solidGround, suelo, "Ground");
	logicGround->SetVisAttributes(brown);
	physGround  = new G4PVPlacement(nullptr, G4ThreeVector(0, 0, -gSueloSep - fGroundSizeZ/2), logicGround, "Ground", logicWorld, false, 0, fCheckOverlaps);
}}
"""
s = s[:m.start()] + nuevo_suelo + s[m.end():]

# --- 3. includes y variables del archivo
if "using namespace std;" not in s:
    sys.exit("ERROR: no se encontró 'using namespace std;'; no se cambió nada.")
s = s.replace("using namespace std;", f"""using namespace std;

// {MARCA}: configuracion del suelo (variables de entorno MEIGA_SUELO_W, MEIGA_SUELO_XY, MEIGA_SUELO_Z)
namespace {{
	bool gSueloActivo = false;
	G4double gSueloW = 0.;
	G4double gSueloSep = 0.;   // distancia entre la superficie del suelo y el fondo exterior del tanque (z = 0)
}}""", 1)
inc = f'\n#include <cstdio>    // {MARCA}\n#include <cstdlib>\n#include <algorithm>'
for ancla in ('#include "G4UnitsTable.hh"', '#include "Materials.h"', '#include "G4WCDConstruction.h"'):
    if ancla in s:
        s = s.replace(ancla, ancla + inc, 1); break
else:
    sys.exit("ERROR: no se encontró dónde agregar los #include; no se cambió nada.")

shutil.copy2(f, orig)
f.write_text(s)
print(f"Parche del suelo APLICADO en {f}. Original guardado en {orig.name}. Recompile MEIGA.")
