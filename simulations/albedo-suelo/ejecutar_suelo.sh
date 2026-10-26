#!/usr/bin/env bash
# Albedo de neutrones de un suelo SoilBS (tesis): el flujo que BAJA sobre Bucaramanga (all_bga_neutron_35.shw de la
# tesis, 200 000 neutrones muestreados al azar, con su energia y direccion) incide de forma uniforme sobre un suelo de
# 20 x 20 x 1 m, SIN TANQUE (MEIGA_SIN_TANQUE=1), seco o humedo (fraccion masica de agua de la tesis). Un plano contador a 5 cm sobre el suelo se evalua despues con los
# pasos de cada neutron (pasos-neutrones.tsv): neutrones que bajan y que suben, su energia y el proceso que los creo.
# Requiere el parche Parche-suelo-SoilBS aplicado (./preparar_suelo.sh aplicar). Fisica QGSP_BERT_HP_NoThermal.
#
#   ./ejecutar_suelo.sh <suelo> prueba               # 30 neutrones (de todo el rango de energia)
#   ./ejecutar_suelo.sh <suelo> completa [PARTES]    # 200 000 neutrones, en PARTES corridas paralelas (1-4)
#   ./ejecutar_suelo.sh <suelo> validacion [PARTES]  # los primeros 50 000 de esos 200 000 (= la parte 1 de una corrida
#                                                    #   completa en 4 partes); para validar el suelo seco frente a la tesis
#   <suelo> = seco (w = 0) | humedo-5 | humedo-10 | humedo-15 | humedo-25 | humedo-30   (w = 0.05 ... 0.30)
set -euo pipefail
SUELO="${1:-}"; MODO="${2:-}"; PARTES="${3:-1}"
case "$SUELO" in
    seco)      W="0";    ETQ="SoilBS-seco" ;;
    humedo-5)  W="0.05"; ETQ="SoilBS-agua05" ;;
    humedo-10) W="0.10"; ETQ="SoilBS-agua10" ;;
    humedo-15) W="0.15"; ETQ="SoilBS-agua15" ;;
    humedo-25) W="0.25"; ETQ="SoilBS-agua25" ;;
    humedo-30) W="0.30"; ETQ="SoilBS-agua30" ;;
    *) echo "Uso: $0 seco|humedo-5|humedo-10|humedo-15|humedo-25|humedo-30 prueba|completa [PARTES]"; exit 1 ;;
esac
[[ "$MODO" == "prueba" || "$MODO" == "completa" || "$MODO" == "validacion" ]] || { echo "Uso: $0 $SUELO prueba|completa|validacion [PARTES]"; exit 1; }
[[ "$PARTES" =~ ^[1-4]$ ]] || { echo "ERROR: PARTES debe ser 1, 2, 3 o 4"; exit 1; }
[[ "$MODO" == "prueba" ]] && PARTES=1
AQUI="$(cd "$(dirname "$0")" && pwd)"
SRC="${MEIGA_SRC:-/opt/meiga/src}"; BUILD="${MEIGA_BUILD:-/opt/meiga/build}"
EXE="$BUILD/Applications/G4WCDSimulator/G4WCDSimulator"
CC="$SRC/Applications/G4WCDSimulator/G4WCDConstruction.cc"
if [[ "$MODO" == "prueba" ]]; then FLUJO="$AQUI/flujos/prueba/30N-Bga-baja-sobre-suelo.txt"; N=30
elif [[ "$MODO" == "validacion" ]]; then
    # las lineas 1-50 000 del archivo de 200 000 (los mismos neutrones que la parte 1 de las corridas completas)
    N=50000; mkdir -p "$AQUI/flujos/validacion"; FLUJO="$AQUI/flujos/validacion/50000N-Bga-baja-sobre-suelo.txt"
    head -n "$N" "$AQUI/flujos/200000N-Bga-baja-sobre-suelo.txt" > "$FLUJO"
    head -n "$((N + 1))" "$AQUI/flujos/200000N-Bga-baja-sobre-suelo-componentes.txt" > "${FLUJO%.txt}-componentes.txt"
else FLUJO="$AQUI/flujos/200000N-Bga-baja-sobre-suelo.txt"; N=200000; fi
FECHA="$(date +%Y%m%d-%H%M%S)"
DEST="$AQUI/resultados/${N}N-Bga-sobre-${ETQ}-sinSab-$FECHA"

echo "== Comprobaciones previas ($SUELO: w = $W, $N neutrones, $PARTES parte(s))"
grep -q "SUELO-SoilBS" "$CC" || { echo "ERROR: el parche del suelo no esta aplicado (Parche-suelo-SoilBS: ./preparar_suelo.sh aplicar)."; exit 1; }
[[ -x "$EXE" ]] || { echo "ERROR: no existe $EXE"; exit 1; }
[[ "$EXE" -nt "$CC" ]] || { echo "ERROR: G4WCDConstruction.cc es mas reciente que el ejecutable: recompile MEIGA."; exit 1; }
grep -q '"PhysicsName" : "QGSP_BERT_HP_NoThermal"' "$AQUI/configuracion/plantilla.json" || { echo "ERROR: la plantilla no usa QGSP_BERT_HP_NoThermal."; exit 1; }
NLIN=$(grep -c . "$FLUJO"); (( NLIN == N )) || { echo "ERROR: $FLUJO tiene $NLIN lineas (se esperaban $N)."; exit 1; }
if [[ "$MODO" != "prueba" ]]; then
    pgrep -x G4WCDSimulator > /dev/null && { echo "ERROR: ya hay otra simulacion G4WCDSimulator corriendo."; exit 1; }
    MIN_DEF=100; [[ "$MODO" == "validacion" ]] && MIN_DEF=20    # 50 000 neutrones: unos 10 GB
    MIN_GB="${MIN_GB:-$MIN_DEF}"
    LIBRE_GB=$(df -BG --output=avail "$BUILD" | tail -1 | tr -dc '0-9')
    echo "   Espacio libre: ${LIBRE_GB} GB"
    (( LIBRE_GB >= ${MIN_GB:-100} )) || { echo "ERROR: hay ${LIBRE_GB} GB libres; se piden al menos ${MIN_GB:-100} GB."; exit 1; }
fi
echo "   OK: parche del suelo aplicado y compilado; QGSP_BERT_HP_NoThermal; suelo $ETQ (MEIGA_SUELO_W=$W), 20 x 20 x 1 m, sin tanque."

mkdir -p "$DEST"; TMPF="$(mktemp -d)"
if (( PARTES == 1 )); then cp "$FLUJO" "$TMPF/parte1.txt"
else split -n "l/$PARTES" -d -a 1 "$FLUJO" "$TMPF/p"; for k in $(seq 1 "$PARTES"); do mv "$TMPF/p$((k-1))" "$TMPF/parte$k.txt"; done; fi
export MEIGA_SUELO_W="$W" MEIGA_SUELO_XY=20 MEIGA_SUELO_Z=1 MEIGA_SIN_TANQUE=1 MEIGA_SUELO_SEPARACION=0
lanzar() {
    local k="$1" run nombre log ini
    run="$BUILD/Applications/G4WCDSimulator-suelo-$SUELO-parte$k"
    nombre="$(basename "$FLUJO" .txt)-$SUELO-parte$k-de$PARTES.txt"
    cp "$TMPF/parte$k.txt" "$SRC/Documentation/SampleFlux/$nombre"
    mkdir -p "$run"; cd "$run"; rm -rf Datos-simulacion output.json.gz output.json; mkdir -p Datos-simulacion
    cp "$AQUI/configuracion/DetectorList.xml" DetectorList.xml
    sed "s|__FLUJO__|$nombre|" "$AQUI/configuracion/plantilla.json" > G4WCDSimulator.json
    log="Flujo-parte$k-$(basename "$FLUJO" .txt)-${ETQ}.txt"; ini=$(date +%s)
    if "$EXE" -c G4WCDSimulator.json > "$log" 2>&1; then echo "   parte $k terminada en $(( $(date +%s) - ini )) s"
    else echo "   ERROR en la parte $k; vea $run/$log"; fi
    mkdir -p "$DEST/parte$k"; mv Datos-simulacion "$log" "$DEST/parte$k/"
    [[ -f output.json.gz ]] && mv output.json.gz "$DEST/parte$k/"
    cp DetectorList.xml G4WCDSimulator.json "$TMPF/parte$k.txt" "$DEST/parte$k/"
}
echo "== Ejecutando G4WCDSimulator ($(date))"; INI=$(date +%s)
for k in $(seq 1 "$PARTES"); do lanzar "$k" & sleep 3; done; wait
echo "   Duracion total: $(( $(date +%s) - INI )) s"
cp "$FLUJO" "${FLUJO%.txt}-componentes.txt" "$DEST/"; rm -rf "$TMPF"
if [[ "$MODO" == "prueba" ]]; then
    echo "== Verificando la prueba"; python3 "$AQUI/verificar_suelo.py" "$DEST/parte1" "$W" "$N"
elif [[ "$MODO" == "validacion" ]]; then
    echo "== Verificando las partes"
    for k in $(seq 1 "$PARTES"); do
        echo "-- parte $k"; python3 "$AQUI/verificar_suelo.py" "$DEST/parte$k" "$W" "$(grep -c . "$DEST/parte$k/parte$k.txt")"
    done
fi
echo "== Listo: $DEST   (tamano: $(du -sh "$DEST" | cut -f1))"
