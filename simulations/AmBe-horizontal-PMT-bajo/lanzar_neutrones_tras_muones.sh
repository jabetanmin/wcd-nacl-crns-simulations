#!/usr/bin/env bash
# Espera a que termine la corrida de muones de este paquete y lanza, una tras otra, las corridas completas de
# neutrones (500 000 por medio) en agua pura, 2.5 % y 10 % NaCl. No hace falta estar pendiente.
#   Lanzar desde el portatil (sale del contenedor de inmediato y sigue en segundo plano):
#   sudo docker exec -d silly_roentgen bash -ic 'cd /opt/Corrida-AmBe-horizontal-PMT-bajo && ./lanzar_neutrones_tras_muones.sh > cadena-neutrones.log 2>&1'
# Si la corrida de muones no termina con "== Listo", no lanza nada (avisa en el registro).
set -uo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"; cd "$AQUI"
LOGMU="$AQUI/corrida-muones-pmtbajo.log"
echo "== $(date): esperando a que termine la corrida de muones ($LOGMU)"
while pgrep -x G4WCDSimulator > /dev/null; do sleep 60; done
sleep 30                                             # deja que ejecutar_muones.sh mueva sus resultados
if ! grep -q "== Listo" "$LOGMU" 2>/dev/null; then
    echo "ERROR: la corrida de muones no termino con '== Listo'. Revise $LOGMU; no se lanza ningun neutron."; exit 1
fi
echo "== $(date): muones terminados: $(grep '== Listo' "$LOGMU")"
for m in agua-pura nacl-2.5 nacl-10; do
    echo "== $(date): neutrones $m (${N_NEUTRONES:-500000}, 4 partes)"
    if ./ejecutar_corrida.sh "$m" completa 4 > "corrida-horizontal-$m.log" 2>&1; then
        echo "   $(tail -1 corrida-horizontal-$m.log)"
    else
        echo "ERROR en $m; vea corrida-horizontal-$m.log. Se detiene la cadena."; exit 1
    fi
done
echo "== $(date): cadena terminada. Copie los resultados al ADATA y despues ejecute ./preparar_meiga.sh revertir"
