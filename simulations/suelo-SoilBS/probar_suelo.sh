#!/usr/bin/env bash
# Prueba del suelo SoilBS: 30 neutrones termicos (25 meV) que caen verticalmente sobre el suelo, fuera del tanque,
# en cuatro casos: sin suelo (MEIGA_SUELO_W sin definir), suelo seco (w = 0), suelo con 10 % de agua (w = 0.10) y
# suelo con 25 % de agua SIN tanque (MEIGA_SIN_TANQUE=1, el caso de los estudios de albedo) y suelo con 10 % de
# agua con el tanque a 2 m sobre el suelo (MEIGA_SUELO_SEPARACION=2, como en los experimentos).
# Comprueba en el registro de MEIGA la linea del suelo (material, densidad, tamano) y, en los pasos de los
# neutrones, que el material del suelo aparezca. La geometria se revisa con CheckOverlaps = true.
set -uo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
SRC="${MEIGA_SRC:-/opt/meiga/src}"; BUILD="${MEIGA_BUILD:-/opt/meiga/build}"
EXE="$BUILD/Applications/G4WCDSimulator/G4WCDSimulator"
pgrep -x G4WCDSimulator > /dev/null && { echo "ERROR: hay otra simulacion corriendo; espere."; exit 1; }
python3 "$AQUI/agregar_suelo.py" "$SRC" --estado | grep -q APLICADO || { echo "ERROR: el parche no esta aplicado (./preparar_suelo.sh aplicar)."; exit 1; }
FL=30N-termicos-sobre-suelo.txt; cp "$AQUI/prueba/$FL" "$SRC/Documentation/SampleFlux/$FL"
RUN="$BUILD/Applications/G4WCDSimulator-prueba-suelo"; OK=1
for caso in sin-suelo seco humedo-0.10 sin-tanque-0.25 tanque-a-2m-0.10; do
    rm -rf "$RUN"; mkdir -p "$RUN/Datos-simulacion"; cd "$RUN"
    cp "$AQUI/configuracion/DetectorList.xml" .; sed "s|__FLUJO__|$FL|" "$AQUI/configuracion/plantilla.json" > G4WCDSimulator.json
    unset MEIGA_SIN_TANQUE MEIGA_SUELO_SEPARACION
    case "$caso" in sin-suelo) unset MEIGA_SUELO_W ;; seco) export MEIGA_SUELO_W=0 ;; humedo-0.10) export MEIGA_SUELO_W=0.10 ;;
                    sin-tanque-0.25) export MEIGA_SUELO_W=0.25 MEIGA_SIN_TANQUE=1 ;;
                    tanque-a-2m-0.10) export MEIGA_SUELO_W=0.10 MEIGA_SUELO_SEPARACION=2 ;; esac
    "$EXE" -c G4WCDSimulator.json > registro.txt 2>&1; st=$?
    lin=$(grep "\[INFO\] Suelo SoilBS" registro.txt | head -1)
    pasos=$(awk -F'\t' '$9 ~ /^SoilBS/ {n++} END{print n+0}' Datos-simulacion/pasos-neutrones.tsv 2>/dev/null)
    solap=$(grep -c "Overlap is detected" registro.txt); exc=$(grep -c "G4Exception" registro.txt); runs=$(grep -c "Run terminated" registro.txt)
    echo "== $caso: salida=$st, corridas=$runs/30, pasos de neutrones en el suelo=$pasos, avisos de solapamiento=$solap, G4Exception=$exc"
    echo "   ${lin:-(sin linea de suelo)}"
    case "$caso" in
      sin-suelo)   [[ -z "$lin" && "$pasos" == 0 ]] || { echo "   [MAL] sin MEIGA_SUELO_W no deberia haber suelo"; OK=0; } ;;
      seco)        [[ "$lin" == *"material = SoilBS,"* && "$lin" == *"densidad = 2.7 "* && "$pasos" -gt 0 ]] || { echo "   [MAL] suelo seco"; OK=0; } ;;
      humedo-0.10) [[ "$lin" == *"SoilBS_agua0.100"* && "$lin" == *"densidad = 2.3"* && "$pasos" -gt 0 ]] || { echo "   [MAL] suelo humedo"; OK=0; } ;;
      sin-tanque-0.25) [[ "$lin" == *"SoilBS_agua0.250"* && "$pasos" -gt 0 ]] && grep -q "SIN TANQUE" registro.txt || { echo "   [MAL] suelo sin tanque"; OK=0; }
                       grep -q "SIN TANQUE" registro.txt && echo "   $(grep -m1 'SIN TANQUE' registro.txt)" ;;
      tanque-a-2m-0.10) [[ "$lin" == *"superficie en z = -2 m (tanque a 2 m sobre el suelo)"* && "$pasos" -gt 0 ]] || { echo "   [MAL] tanque a 2 m"; OK=0; } ;;
    esac
    (( st == 0 && runs == 30 )) || { echo "   [MAL] la corrida no termino bien (vea $RUN/registro.txt)"; OK=0; }
    (( solap == 0 )) || { echo "   [MAL] Geant4 detecto solapamiento de volumenes:"; grep -m3 -A2 "Overlap is detected" registro.txt | sed 's/^/   /'; OK=0; }
    mkdir -p "$AQUI/resultados-prueba/$caso"; cp registro.txt "$AQUI/resultados-prueba/$caso/"; cp Datos-simulacion/capturas-neutrones.tsv "$AQUI/resultados-prueba/$caso/" 2>/dev/null
done
unset MEIGA_SUELO_W MEIGA_SIN_TANQUE MEIGA_SUELO_SEPARACION
(( OK == 1 )) && echo "TODO CORRECTO" || echo "HAY PROBLEMAS: mande la salida"
