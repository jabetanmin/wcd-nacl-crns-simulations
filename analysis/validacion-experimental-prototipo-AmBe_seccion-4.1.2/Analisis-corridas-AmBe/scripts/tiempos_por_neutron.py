#!/usr/bin/env python3
"""Tiempo de CPU/real por neutrón en las corridas AmBe, leído de los registros de MEIGA dentro del zip del
TOSHIBA (una línea 'User=..s Real=..s' por neutrón, en el orden del archivo de entrada).
-> resultados/tiempos_<medio>.npz (real, user por evento)"""
import os, re, zipfile
import numpy as np
ZIP = os.path.join(os.environ.get("TOSHIBA", os.path.join("/media", os.environ.get("USER", "ubuntu"), "TOSHIBA EXT")), "Documentos-antiguos", "Tesis-doctorado", "Mterial-faltante-mejorar", "Simulacion-fuente-241AmBe.zip")
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados")
LOGS = {"nacl25": "Simulacion-fuente-241AmBe/Tipos-medios/Agua+2.5NaCl/Datos-simulacion/Flujo-AmBe241-A25NaCl.txt",
        "nacl10": "Simulacion-fuente-241AmBe/Tipos-medios/Agua+10NaCl/Agua+10NaCl/Datos-simulacion/Flujo-AmBe241-A10NaCl.txt"}
pat = re.compile(rb"User=([0-9.eE+-]+)s Real=([0-9.eE+-]+)s")
z = zipfile.ZipFile(ZIP)
for m, n in LOGS.items():
    real, user, resto = [], [], b""
    with z.open(n) as f:
        while True:
            b = f.read(256 * 1024 * 1024)
            if not b:
                break
            b = resto + b
            corte = b.rfind(b"\n")
            bloque, resto = b[:corte], b[corte:]
            for u, r in pat.findall(bloque):
                user.append(float(u)); real.append(float(r))
            print(m, len(real), flush=True)
    for u, r in pat.findall(resto):
        user.append(float(u)); real.append(float(r))
    np.savez_compressed(os.path.join(RES, f"tiempos_{m}.npz"), real=np.array(real), user=np.array(user))
    print(m, "FIN", len(real), "suma real [h]", sum(real) / 3600, flush=True)
