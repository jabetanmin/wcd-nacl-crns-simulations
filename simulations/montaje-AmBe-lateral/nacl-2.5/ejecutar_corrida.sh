#!/usr/bin/env bash
# Corrida MEIGA del montaje blindado con la fuente 241Am-Be (detector prototipo):
# 1 000 000 neutrones que entran por el costado del tanque, mezcla haz 35 % (ISO 8529, 0.1-11 MeV) /
# halo 45 % (0.5 eV-100 keV) / fondo 20 % (1e-4-0.5 eV). Tanque SaltyWCD R = 48 cm, H = 133 cm,
# Tyvek 0.12 mm + acero 0.5 mm, PMT de Sidelnik (en la tapa), SIN S(alpha,beta).
#
# Uso (dentro del contenedor de MEIGA):
#   ./ejecutar_corrida.sh <medio> prueba               # 30 neutrones; verifica fisica, medio, inyeccion y PMT
#   ./ejecutar_corrida.sh <medio> completa [PARTES]    # 1 000 000 neutrones, en PARTES corridas paralelas (1-4)
#   <medio> = nacl-2.5    (este paquete trae la configuracion de agua + 2.5 % NaCl)
#
# Cada parte corre en su propia carpeta: $BUILD/Applications/G4WCDSimulator-ambe-<medio>-parte<k>.
# Variables opcionales: MEIGA_SRC (/opt/meiga/src), MEIGA_BUILD (/opt/meiga/build), MIN_GB (100),
#                       PERMITIR_PARALELO=1 (si ya hay otra simulacion corriendo)
set -euo pipefail

MEDIO="${1:-}"; MODO="${2:-}"; PARTES="${3:-1}"
case "$MEDIO" in
    agua-pura) ETQ="H2O-pura";    W="0";     GB_ESP=51 ;;
    nacl-2.5)  ETQ="H2O-2.5NaCl"; W="0.025"; GB_ESP=66 ;;
    nacl-10)   ETQ="H2O-10NaCl";  W="0.1";   GB_ESP=78 ;;
    *) echo "Uso: $0 agua-pura|nacl-2.5|nacl-10 prueba|completa [PARTES]"; exit 1 ;;
esac
[[ "$MODO" == "prueba" || "$MODO" == "completa" ]] || { echo "Uso: $0 $MEDIO prueba|completa [PARTES]"; exit 1; }
[[ "$PARTES" =~ ^[1-4]$ ]] || { echo "ERROR: PARTES debe ser 1, 2, 3 o 4"; exit 1; }
[[ "$MODO" == "prueba" ]] && PARTES=1

AQUI="$(cd "$(dirname "$0")" && pwd)"
SRC="${MEIGA_SRC:-/opt/meiga/src}"
BUILD="${MEIGA_BUILD:-/opt/meiga/build}"
EXE="$BUILD/Applications/G4WCDSimulator/G4WCDSimulator"
CONF="$AQUI/configuracion/$MEDIO"
if [[ "$MODO" == "prueba" ]]; then FLUJO="$AQUI/flujos/prueba/30N-AmBe-montaje-haz-halo-fondo.txt"; N=30
else FLUJO="$AQUI/flujos/1000000N-AmBe-montaje-haz-halo-fondo.txt"; N=1000000; fi
FECHA="$(date +%Y%m%d-%H%M%S)"
DEST="$AQUI/resultados/${N}N-AmBe-montaje-${ETQ}-sinSab-$FECHA"

echo "== Comprobaciones previas ($MEDIO: w_NaCl = $W, $N neutrones, $PARTES parte(s))"
FIS="$SRC/G4Models/G4MPhysicsList.cc"; SAL="$SRC/G4Models/SaltyWCD.cc"; OPT="$SRC/Framework/Detector/OptDevice.cc"
PF="$SRC/IO/ParticleFiller.cc"; SD="$SRC/Framework/SimData/SimData.cc"
for f in "$FIS" "$SAL" "$OPT" "$PF" "$SD" "$CONF/DetectorList.xml" "$AQUI/configuracion/plantilla.json" "$FLUJO"; do
    [[ -f "$f" ]] || { echo "ERROR: no existe $f"; exit 1; }
done
grep -q "noThermal" "$FIS" || { echo "ERROR: este MEIGA no tiene la opcion QGSP_BERT_HP_NoThermal."; exit 1; }
grep -q '"eFromFile"' "$SD" || { echo "ERROR: este MEIGA no reconoce injectionMode eFromFile."; exit 1; }
# el archivo de neutrones se escribio con pz invertido porque ParticleFiller guarda (px, py, -pz)
grep -q -- "-1\*pz" "$PF" || { echo "ERROR: ParticleFiller.cc no invierte pz; el archivo de neutrones no sirve tal cual (avise)."; exit 1; }
grep -q '<injectionMode type="eFromFile">' "$CONF/DetectorList.xml" || { echo "ERROR: DetectorList.xml no usa eFromFile."; exit 1; }
grep -q "<impuritiesFraction> $W </impuritiesFraction>" "$CONF/DetectorList.xml" || { echo "ERROR: DetectorList.xml no tiene impuritiesFraction = $W."; exit 1; }
if ! grep -q "SIDELNIK: PMT en la tapa" "$SAL" || ! grep -q "SetSemiAxisZ(5.0);  // SIDELNIK" "$OPT"; then
    echo "ERROR: el PMT no esta en la configuracion de Sidelnik (se eligio ese PMT). Ejecute:"
    echo "       python3 /opt/corrida-sidelnik/Corridas-Sidelnik-500MeV/ajustar_pmt_sidelnik.py $SRC   y recompile."
    exit 1
fi
[[ -x "$EXE" ]] || { echo "ERROR: no existe $EXE (compile MEIGA)"; exit 1; }
for f in "$SAL" "$OPT"; do
    [[ "$f" -nt "$EXE" ]] && { echo "ERROR: $(basename "$f") es mas reciente que el ejecutable: recompile MEIGA."; exit 1; }
done
NLIN=$(wc -l < "$FLUJO"); (( NLIN == N )) || { echo "ERROR: $FLUJO tiene $NLIN lineas (se esperaban $N)."; exit 1; }
if [[ "$MODO" == "completa" ]]; then
    if pgrep -x G4WCDSimulator > /dev/null && [[ "${PERMITIR_PARALELO:-0}" != "1" ]]; then
        echo "ERROR: ya hay otra simulacion G4WCDSimulator corriendo (use PERMITIR_PARALELO=1 si hay espacio)."
        exit 1
    fi
    LIBRE_GB=$(df -BG --output=avail "$BUILD" | tail -1 | tr -dc '0-9')
    echo "   Espacio libre: ${LIBRE_GB} GB (se esperan ~${GB_ESP} GB de salida para $MEDIO)"
    (( LIBRE_GB >= ${MIN_GB:-100} )) || { echo "ERROR: hay ${LIBRE_GB} GB libres; se piden al menos ${MIN_GB:-100} GB."; exit 1; }
fi
echo "   OK: sin S(alpha,beta); eFromFile; pz invertido en ParticleFiller; w = $W; PMT de Sidelnik; ejecutable actualizado."

echo "== Preparando $PARTES parte(s)"
mkdir -p "$DEST"
TMPF="$(mktemp -d)"
if (( PARTES == 1 )); then cp "$FLUJO" "$TMPF/parte1.txt"
else split -n "l/$PARTES" -d -a 1 "$FLUJO" "$TMPF/p" ; for k in $(seq 1 "$PARTES"); do mv "$TMPF/p$((k-1))" "$TMPF/parte$k.txt"; done; fi

lanzar() {   # $1 = numero de parte
    local k="$1" run nombre log ini
    run="$BUILD/Applications/G4WCDSimulator-ambe-$MEDIO-parte$k"
    nombre="$(basename "$FLUJO" .txt)-$MEDIO-parte$k-de$PARTES.txt"     # nombre propio de cada medio
    cp "$TMPF/parte$k.txt" "$SRC/Documentation/SampleFlux/$nombre"
    mkdir -p "$run"; cd "$run"
    if [[ -d Datos-simulacion ]] && [[ -n "$(ls -A Datos-simulacion)" ]]; then mv Datos-simulacion "Datos-simulacion-respaldo-$FECHA"; fi
    mkdir -p Datos-simulacion; rm -f output.json.gz output.json
    cp "$CONF/DetectorList.xml" DetectorList.xml
    sed "s|__FLUJO__|$nombre|" "$AQUI/configuracion/plantilla.json" > G4WCDSimulator.json
    log="Flujo-parte$k-$(basename "$FLUJO" .txt)-${ETQ}.txt"
    ini=$(date +%s)
    if "$EXE" -c G4WCDSimulator.json > "$log" 2>&1; then echo "   parte $k terminada en $(( $(date +%s) - ini )) s"
    else echo "   ERROR en la parte $k; vea $run/$log"; fi
    mkdir -p "$DEST/parte$k"
    mv Datos-simulacion "$log" "$DEST/parte$k/"
    [[ -f output.json.gz ]] && mv output.json.gz "$DEST/parte$k/"
    [[ -f output.json ]] && mv output.json "$DEST/parte$k/"
    cp DetectorList.xml G4WCDSimulator.json "$TMPF/parte$k.txt" "$DEST/parte$k/"
}

echo "== Ejecutando G4WCDSimulator ($(date))"
INI=$(date +%s)
for k in $(seq 1 "$PARTES"); do
    lanzar "$k" &
    sleep 3            # semillas distintas: MEIGA usa time(NULL)
done
wait
echo "   Duracion total: $(( $(date +%s) - INI )) s"
cp "$FLUJO" "$DEST/"; cp "${FLUJO%.txt}-componentes.txt" "$DEST/" 2>/dev/null || true
rm -rf "$TMPF"

if [[ "$MODO" == "prueba" ]]; then
    echo "== Verificando la prueba"
    python3 "$AQUI/verificar_prueba.py" "$DEST/parte1" "$FLUJO" "$W"
fi
echo "== Listo: $DEST   (tamano: $(du -sh "$DEST" | cut -f1))"
