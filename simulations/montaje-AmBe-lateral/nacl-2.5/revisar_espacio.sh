#!/usr/bin/env bash
# Revisa el espacio del portátil y del contenedor de MEIGA, y qué resultados del contenedor ya tienen
# copia IDÉNTICA (mismos archivos y mismos bytes) en el ADATA. NO BORRA NADA: solo imprime los comandos
# de borrado de lo que está verificado, para que el usuario los ejecute si quiere.
#
# Uso (en el portátil, FUERA del contenedor):
#   ./revisar_espacio.sh "/media/jaime/ADATA HD330"          (ruta donde está montado el ADATA)
# Variables: CONTENEDOR (silly_roentgen)
set -uo pipefail
ADATA="${1:-}"
CT="${CONTENEDOR:-silly_roentgen}"
[[ -n "$ADATA" && -d "$ADATA" ]] || { echo "Uso: $0 <ruta del ADATA montado>"; exit 1; }

echo "================ Espacio en el portátil"
df -h / "$ADATA" | sed 's/^/  /'
echo
echo "================ Espacio dentro del contenedor $CT"
sudo docker exec "$CT" df -h /opt | sed 's/^/  /'
echo
echo "================ Lo que más ocupa en el contenedor"
sudo docker exec "$CT" bash -c 'du -sh /opt/meiga/build/Applications/* /opt/corrida-sidelnik/*/resultados/* /opt/Corrida-AmBe-montaje-agua-pura/resultados/* 2>/dev/null | sort -h | tail -25' | sed 's/^/  /'
echo
echo "================ Resultados del contenedor con copia en el ADATA"
# carpetas de resultados (una por corrida) dentro del contenedor
mapfile -t CARPETAS < <(sudo docker exec "$CT" bash -c 'ls -d /opt/corrida-sidelnik/*/resultados/*/ /opt/Corrida-AmBe-montaje-agua-pura/resultados/*/ 2>/dev/null')
BORRAR=()
for c in "${CARPETAS[@]}"; do
    c="${c%/}"; nombre="$(basename "$c")"
    # buscar en el ADATA una carpeta con el mismo nombre (hasta 3 niveles)
    copia="$(find "$ADATA" -maxdepth 3 -type d -name "$nombre" 2>/dev/null | head -1)"
    # bytes de los archivos (sin el tamaño de las carpetas, que depende del sistema de archivos)
    tam_ct=$(sudo docker exec "$CT" bash -c "find '$c' -type f -printf '%s\n' | awk '{s+=\$1} END{printf \"%.0f\", s}'")
    gb=$(awk -v b="$tam_ct" 'BEGIN{printf "%.1f", b/1e9}')
    if [[ -z "$copia" ]]; then
        echo "  [SIN COPIA]   $nombre  ($gb GB)  -> NO borrar; primero copiar al ADATA"
        continue
    fi
    tam_ad=$(find "$copia" -type f -printf '%s\n' | awk '{s+=$1} END{printf "%.0f", s}')
    n_ct=$(sudo docker exec "$CT" bash -c "find '$c' -type f | wc -l")
    n_ad=$(find "$copia" -type f | wc -l)
    if [[ "$tam_ct" == "$tam_ad" && "$n_ct" == "$n_ad" ]]; then
        echo "  [COPIA OK]    $nombre  ($gb GB, $n_ct archivos)  = $copia"
        BORRAR+=("$c")
    else
        echo "  [DIFERENTE]   $nombre  contenedor $tam_ct B / $n_ct archivos  vs  ADATA $tam_ad B / $n_ad archivos -> NO borrar"
    fi
done
echo
if (( ${#BORRAR[@]} )); then
    echo "================ Comandos para liberar espacio (solo carpetas con copia verificada)"
    echo "  Revíselos y ejecútelos usted mismo, uno por uno:"
    for c in "${BORRAR[@]}"; do echo "  sudo docker exec $CT rm -rf '$c'"; done
else
    echo "No hay resultados en el contenedor con copia verificada en el ADATA."
fi
echo
echo "Carpetas de trabajo de MEIGA (G4WCDSimulator-sidelnik-*, -ambe-*) solo contienen datos si una corrida"
echo "se interrumpió; las corridas terminadas mueven todo a resultados/. Para revisar una:"
echo "  sudo docker exec $CT du -sh /opt/meiga/build/Applications/G4WCDSimulator-sidelnik-nacl-10"
echo
echo "La corrida de agua pura necesita ~75 GB (el script de la corrida exige >= 100 GB libres en /opt)."
