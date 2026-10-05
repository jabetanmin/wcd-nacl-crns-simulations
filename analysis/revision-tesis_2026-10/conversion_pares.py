#!/usr/bin/env python3
"""Porcentaje de conversiones de pares de la tabla tab:conversion_pares del Cap. 4.

El denominador que reproduce la tabla es N_Int(gamma_Tanque) de la Tabla N-intera-gamma-cap (registros
de interacción dentro del tanque, incluidos los pasos de transporte), no N_Total-int. Los valores
publicados antes de la revisión estaban truncados en seis celdas; aquí se redondean.

Uso: python3 conversion_pares.py <carpeta Gammas de la Campaña 1>
"""
import glob
import sys

base = sys.argv[1]
ENERGIAS = ["1meV", "10meV", "100meV", "1000meV", "1000000meV"]
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
N_TANQUE = [[108898, 213878, 275135, 363278], [159194, 306048, 392804, 514877],
            [216088, 409145, 517145, 664137], [239947, 440039, 561933, 704066],
            [238505, 428752, 541513, 667270]]   # columna N_Int(gamma_Tanque) de la tesis
for i, e in enumerate(ENERGIAS):
    fila = []
    for j, m in enumerate(MEDIOS):
        f = glob.glob(f"{base}/{e}/{m}/gamma-completo-*.txt")[0]
        conv = sum(1 for l in open(f) if l.split()[4:5] == ["conv"])
        fila.append(f"{100*conv/N_TANQUE[i][j]:.2f} ({conv})")
    print(e, " | ".join(fila))
