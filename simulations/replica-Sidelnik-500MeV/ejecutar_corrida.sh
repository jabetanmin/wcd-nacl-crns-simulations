#!/usr/bin/env bash
# Corridas tipo Sidelnik (2020) en MEIGA para la Sec. 4.1.1 de la tesis:
# neutrones de 500 MeV horizontales a media altura, tanque de acero (Tyvek 0,12 mm + acero 0,5 mm),
# PMT en la tapa, SIN S(alpha,beta). Mismo detector y fuente para los cuatro medios.
#
# Uso (dentro del contenedor de MEIGA):
#   ./ejecutar_corrida.sh <medio> prueba               # 10 neutrones, verifica fisica, medio, geometria, fuente y PMT
#   nohup ./ejecutar_corrida.sh <medio> completa > corrida-<medio>.log 2>&1 &     # 150000 neutrones
#   <medio> = agua-pura | nacl-2.5 | nacl-5 | nacl-10
#
# Cada medio corre en su propia carpeta de trabajo ($BUILD/Applications/G4WCDSimulator-sidelnik-<medio>),
# asi una corrida no puede mezclar sus archivos con otra.
# Variables opcionales: MEIGA_SRC (/opt/meiga/src), MEIGA_BUILD (/opt/meiga/build),
#                       MIN_GB (espacio libre minimo para la completa, 250), PERMITIR_PARALELO=1
set -euo pipefail

MEDIO="${1:-}"; MODO="${2:-}"
case "$MEDIO" in
    agua-pura) ETQ="H2O-pura";    W="0";     MAT="Water_TS_H_of_Water";    RHO="0.9982";  N589="1.3329872" ;;
    nacl-2.5)  ETQ="H2O-2.5NaCl"; W="0.025"; MAT="SaltyWater_NaCl_2.5pct"; RHO="1.01604"; N589="1.3396866" ;;
    nacl-5)    ETQ="H2O-5NaCl";   W="0.05";  MAT="SaltyWater_NaCl_5.0pct"; RHO="1.03401"; N589="1.3435767" ;;
    nacl-10)   ETQ="H2O-10NaCl";  W="0.1";   MAT="SaltyWater_NaCl_10.0pct"; RHO="1.07051"; N589="1.3593505" ;;
    *) echo "Uso: $0 agua-pura|nacl-2.5|nacl-5|nacl-10 prueba|completa"; exit 1 ;;
esac
[[ "$MODO" == "prueba" || "$MODO" == "completa" ]] || { echo "Uso: $0 $MEDIO prueba|completa"; exit 1; }

AQUI="$(cd "$(dirname "$0")" && pwd)"
SRC="${MEIGA_SRC:-/opt/meiga/src}"
BUILD="${MEIGA_BUILD:-/opt/meiga/build}"
EXE="$BUILD/Applications/G4WCDSimulator/G4WCDSimulator"
# misma profundidad que la carpeta original: "../../../src/..." del JSON sigue apuntando a $SRC
RUN="$BUILD/Applications/G4WCDSimulator-sidelnik-$MEDIO"
CONF="$AQUI/configuracion/$MEDIO"
if [[ "$MODO" == "prueba" ]]; then FLUJO="10N-500MeV-Sidelnik.txt"; N=10; else FLUJO="150000N-500MeV-Sidelnik.txt"; N=150000; fi
FECHA="$(date +%Y%m%d-%H%M%S)"
DEST="$AQUI/resultados/${N}N-500MeV-Sidelnik-${ETQ}-sinSab-$FECHA"

echo "== Comprobaciones previas ($MEDIO: w_NaCl = $W)"
FIS="$SRC/G4Models/G4MPhysicsList.cc"; MATS="$SRC/G4Models/Materials.cc"; SAL="$SRC/G4Models/SaltyWCD.cc"
OPT="$SRC/Framework/Detector/OptDevice.cc"
for f in "$FIS" "$MATS" "$SAL" "$OPT" "$CONF/DetectorList.xml" "$CONF/G4WCDSimulator-$MODO.json"; do
    [[ -f "$f" ]] || { echo "ERROR: no existe $f"; exit 1; }
done
grep -q "noThermal" "$FIS" || { echo "ERROR: este MEIGA no tiene la opcion QGSP_BERT_HP_NoThermal."; exit 1; }
grep -q '"QGSP_BERT_HP_NoThermal"' "$CONF/G4WCDSimulator-$MODO.json" || { echo "ERROR: el JSON no usa QGSP_BERT_HP_NoThermal."; exit 1; }
grep -q "SelectWCDMedium" "$SAL" || { echo "ERROR: SaltyWCD.cc no es la version integrada esperada."; exit 1; }
grep -q "<impuritiesFraction> $W </impuritiesFraction>" "$CONF/DetectorList.xml" || { echo "ERROR: DetectorList.xml no tiene impuritiesFraction = $W."; exit 1; }
# densidad (Tabla 3.6) y RINDEX a 589,3 nm (n_G4 de la Tabla 3.6) definidos en el codigo que se compila
grep -q "${RHO}0* \* g/cm3\|${RHO} \* g/cm3" "$MATS" || { echo "ERROR: Materials.cc no define la densidad $RHO g/cm3 de la Tabla 3.6."; exit 1; }
grep -q "$N589" "$MATS" || { echo "ERROR: Materials.cc no contiene el RINDEX $N589 (n a 589,3 nm de la Tabla 3.6)."; exit 1; }
if ! grep -q "SIDELNIK: PMT en la tapa" "$SAL" || ! grep -q "SetSemiAxisZ(5.0);  // SIDELNIK" "$OPT"; then
    echo "ERROR: el PMT no esta en la configuracion de Sidelnik. Ejecute: python3 $AQUI/ajustar_pmt_sidelnik.py $SRC  y recompile."
    exit 1
fi
[[ -x "$EXE" ]] || { echo "ERROR: no existe $EXE (compile MEIGA)"; exit 1; }
for f in "$SAL" "$OPT" "$MATS"; do
    [[ "$f" -nt "$EXE" ]] && { echo "ERROR: $(basename "$f") es mas reciente que el ejecutable: recompile MEIGA."; exit 1; }
done
if [[ "$MODO" == "completa" ]]; then
    if pgrep -x G4WCDSimulator > /dev/null && [[ "${PERMITIR_PARALELO:-0}" != "1" ]]; then
        echo "ERROR: ya hay otra simulacion G4WCDSimulator corriendo. Espere a que termine"
        echo "       (o use PERMITIR_PARALELO=1 si hay espacio en disco para ambas)."
        exit 1
    fi
    LIBRE_GB=$(df -BG --output=avail "$BUILD" | tail -1 | tr -dc '0-9')
    echo "   Espacio libre: ${LIBRE_GB} GB"
    (( LIBRE_GB >= ${MIN_GB:-250} )) || { echo "ERROR: hay ${LIBRE_GB} GB libres; se recomiendan al menos ${MIN_GB:-250} GB (mueva resultados anteriores fuera del contenedor)."; exit 1; }
fi
echo "   OK: sin S(alpha,beta); medio $MAT (w = $W, rho = $RHO g/cm3, n(589 nm) = $N589); PMT de Sidelnik; ejecutable actualizado."

echo "== Preparando la corrida ($MEDIO, $MODO, $N neutrones) en $RUN"
cp "$AQUI/$FLUJO" "$SRC/Documentation/SampleFlux/$FLUJO"
mkdir -p "$RUN"
cd "$RUN"
if [[ -d Datos-simulacion ]] && [[ -n "$(ls -A Datos-simulacion)" ]]; then
    mv Datos-simulacion "Datos-simulacion-respaldo-$FECHA"
    echo "   Datos-simulacion anterior movido a Datos-simulacion-respaldo-$FECHA"
fi
mkdir -p Datos-simulacion
rm -f output.json.gz
cp "$CONF/DetectorList.xml" DetectorList.xml
cp "$CONF/G4WCDSimulator-$MODO.json" "G4WCDSimulator-$MODO.json"
LOG="Flujo-${N}N-500MeV-Sidelnik-${ETQ}-sinSab.txt"

echo "== Ejecutando G4WCDSimulator (registro en $RUN/$LOG)"
INI=$(date +%s)
"$EXE" -c "G4WCDSimulator-$MODO.json" > "$LOG" 2>&1 || { echo "ERROR: la simulacion termino con error; vea $RUN/$LOG"; exit 1; }
echo "   Duracion: $(( $(date +%s) - INI )) s"

echo "== Guardando resultados en $DEST"
mkdir -p "$DEST"
mv Datos-simulacion "$LOG" "$DEST/"
[[ -f output.json.gz ]] && mv output.json.gz "$DEST/"
cp DetectorList.xml "G4WCDSimulator-$MODO.json" "$DEST/"

if [[ "$MODO" == "prueba" ]]; then
    echo "== Verificando la prueba"
    python3 "$AQUI/verificar_prueba.py" "$DEST" "$MEDIO"
fi
echo "== Listo: $DEST"
