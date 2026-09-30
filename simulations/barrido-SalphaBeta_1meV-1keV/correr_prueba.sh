#!/bin/bash
# Prueba de fisica del WCD: neutrones monoenergeticos en agua pura, geometria de la Campana 2.
# Uso (dentro del contenedor, con el entorno de Geant4 cargado):
#   ./correr_prueba.sh <PhysicsName> <energia en eV> [numero de neutrones, por defecto 10000]
# Ejemplos:
#   ./correr_prueba.sh QGSP_BERT_HP           1
#   ./correr_prueba.sh QGSP_BERT_HP_NoThermal 0.025
# PhysicsName: QGSP_BERT_HP            -> QGSP_BERT_HP + S(alpha,beta) (actua por debajo de 4 eV)
#              QGSP_BERT_HP_NoThermal  -> QGSP_BERT_HP sin S(alpha,beta) (gas libre)
set -euo pipefail

FISICA=${1:?Indique PhysicsName: QGSP_BERT_HP o QGSP_BERT_HP_NoThermal}
E_EV=${2:?Indique la energia del neutron en eV, por ejemplo 1 o 0.025}
N=${3:-10000}
BASE=$(cd "$(dirname "$0")" && pwd)
EXE=/opt/meiga/build/Applications/G4WCDSimulator/G4WCDSimulator

case "$FISICA" in
  QGSP_BERT_HP)           ESPERADA="RegisterPhysics: G4ThermalNeutrons" ;;
  QGSP_BERT_HP_NoThermal) ESPERADA="RegisterPhysics: QGSP_BERT_HP without S(alpha,beta)" ;;
  *) echo "PhysicsName no reconocido: $FISICA"; exit 1 ;;
esac

# Momento del neutron (CORSIKA id 13) en GeV/c: p = sqrt(E^2 + 2 m E), m = 939.565420 MeV.
# Para 0.025 eV da 6.85407e-06, igual que el archivo 100000N-25meV.txt de la Campana 2.
PZ=$(awk -v e="$E_EV" 'BEGIN { if (e <= 0) exit 1; m = 939565420.0; printf "%.6g", sqrt(e * e + 2 * m * e) / 1e9 }') \
  || { echo "Energia no valida: $E_EV"; exit 1; }
# Etiqueta legible: 0.025 -> 25meV, 1 -> 1eV, 10 -> 10eV
ETIQ=$(awk -v e="$E_EV" 'BEGIN { if (e < 1) printf "%gmeV", e * 1000; else printf "%geV", e }')
D="$BASE/$ETIQ-AguaPura-$FISICA-${N}N"

[ -x "$EXE" ] || { echo "No se encuentra el ejecutable $EXE"; exit 1; }
[ -e "$D" ] && { echo "Ya existe $D. Borrela o renombrela antes de repetir la prueba."; exit 1; }

mkdir -p "$D/Datos-simulacion"
cd "$D"

awk -v n="$N" -v p="$PZ" 'BEGIN { for (i = 0; i < n; i++) print "13 0 0 " p " 0 0 0 0 0 0 0 0" }' > flujo.txt
cp "$BASE/DetectorList-AguaPura.xml" DetectorList.xml
sed "s|@FISICA@|$FISICA|" "$BASE/G4WCDSimulator-prueba.json" > config.json

echo "Carpeta : $D"
echo "Fisica  : $FISICA"
echo "Energia : $E_EV eV (pz = $PZ GeV/c), $N neutrones"
echo "Inicio  : $(date '+%F %T')" | tee ejecucion.log

"$EXE" -c config.json >> ejecucion.log 2>&1 || { echo "El simulador termino con error; revise $D/ejecucion.log"; exit 1; }

echo "Fin     : $(date '+%F %T')" | tee -a ejecucion.log

# Comprobaciones: fisica registrada, energia inyectada, medio y geometria leidos por el simulador
echo
echo "== Comprobaciones"
grep -m1 "PhysicsList =" ejecucion.log || true
if grep -q "$ESPERADA" ejecucion.log; then
  echo "OK: $ESPERADA"
else
  echo "ATENCION: no aparece \"$ESPERADA\" en el registro. La corrida NO usa la fisica pedida."
fi
awk -F'\t' '!/^#/ && $4 == 1 { printf "Energia inyectada (primer neutron): %.6g eV\n", $16 * 1e6; exit }' Datos-simulacion/neutrones-incidentes.tsv
grep -m6 -E "SaltyWCD: (Active medium|NaCl final mass fraction|Water radius|Water height|Tyvek thickness|Steel thickness)" ejecucion.log || true

echo
echo "== Resultados"
"$BASE/resumen_prueba.sh" "$D/Datos-simulacion"
