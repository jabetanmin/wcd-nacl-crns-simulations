#!/usr/bin/env python3
"""
Carga por pulso de las tomas experimentales del detector prototipo (archivos LAGO raw v5 en
TOSHIBA .../Detector-prototipo/Nuevo-analisis/datos/), con el MISMO algoritmo del notebook
analisis-datos-Flujo-Completo-Bga.ipynb (PASOS 1-3):
  * trazas de 32 muestras (un disparo), canal 1;
  * ventana = tramo contiguo con ADC > 0 que contiene la muestra 8 (TRIGGER_INDEX);
  * se conserva si el máximo de la ventana supera 1200 ADC; carga = suma de la ventana.
Además se mide la duración de cada toma (líneas GPS '# x h', una por segundo) y se cuentan los
disparos y los errores. -> resultados/experimento_cargas.npz, experimento_tomas.json
"""
import json, os, subprocess
import numpy as np

DATOS = os.path.join(os.environ.get("TOSHIBA", os.path.join("/media", os.environ.get("USER", "ubuntu"), "TOSHIBA EXT")), "Simulaciones-Jaime-2024", "Detector-prototipo", "Nuevo-analisis", "datos")
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
TOMAS = ["pura_fondo", "pura_neutrones", "2.5_fondo", "2.5_neutrones", "10_fondo", "10_neutrones"]
SEGMENT_LENGTH, TRIGGER_INDEX, PEAK_THRESHOLD = 32, 8, 1200


def find_signal_window(segment, trigger_index=TRIGGER_INDEX):     # copia literal del notebook (PASO 2)
    start = trigger_index
    end = trigger_index
    while start >= 0 and segment[start] > 0:
        start -= 1
    while end < len(segment) and segment[end] > 0:
        end += 1
    if start == -1 and end == len(segment):
        return np.array([])
    if segment[start] < 0:
        start += 1
    if segment[end - 1] < 0:
        end -= 1
    return segment[start:end]


cargas, info = {}, {}
for t in TOMAS:
    f = os.path.join(DATOS, f"{t}.dat")
    meta = subprocess.run(["mawk", r"/^# t /{t++} /^# x h /{h++; s=$5; if(!a) a=s} /^# E [0-9]/{e++} "
                           r"END{print t, h, e, a, s}", f], capture_output=True, text=True,
                          env={"LC_ALL": "C", "PATH": os.environ["PATH"]}).stdout.split()
    n_trig, n_gps, n_err = int(meta[0]), int(meta[1]), int(meta[2])
    col = subprocess.run(["mawk", r"/^#/{next} {print $1}", f], capture_output=True, text=True,
                         env={"LC_ALL": "C", "PATH": os.environ["PATH"]}).stdout
    data = np.array(col.split(), dtype=np.int32)
    nseg = len(data) // SEGMENT_LENGTH
    seg = data[:nseg * SEGMENT_LENGTH].reshape(nseg, SEGMENT_LENGTH)
    seg = seg[seg.sum(axis=1) > 0]                                   # como slice_segments
    q = []
    for s in seg:
        w = find_signal_window(s)
        if w.size > 0 and w.max() > PEAK_THRESHOLD:
            q.append(float(w.sum()))
    cargas[t] = np.array(q)
    info[t] = {"disparos": n_trig, "lineas_datos": int(len(data)), "segmentos_32": int(nseg),
               "alineado": bool(len(data) == 32 * n_trig), "segundos_gps": n_gps,
               "duracion_s": n_gps, "errores_lectura": n_err, "pulsos_carga": len(q),
               "tasa_disparo_s": n_trig / n_gps, "tasa_pulsos_s": len(q) / n_gps}
    print(t, info[t], flush=True)
np.savez_compressed(os.path.join(RES, "experimento_cargas.npz"), **cargas)
json.dump(info, open(os.path.join(RES, "experimento_tomas.json"), "w"), indent=2)
