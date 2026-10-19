#!/usr/bin/env python3
"""Digitalizacion por color de pixel de la Fig. 5 de Sidelnik et al. (2020): espectro de electrones producidos
por gammas en el volumen activo. Marco: columna 384 = 0 MeV, columna 1167 = 10 MeV; fila 634 = 1e1 y
98,6 pixeles por decada (marcas en 634, 535 y 338). Se excluye la leyenda (filas < 275, columnas > 850).
Por columna (12,8 keV) guarda la fila mas alta y la mediana de cada color. Salida: datos/fig5_sidelnik_digitalizada.csv"""
import os
import numpy as np, pandas as pd
from PIL import Image
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
im = np.asarray(Image.open(os.path.join(R, "datos", "fig5_sidelnik_espectro_electrones.png")).convert("RGB")).astype(int)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
COLS = {"pura": (r > 190) & (g < 80) & (b < 80),
        "nacl25": (r < 80) & (g > 120) & (g < 190) & (b > 80) & (b < 150),
        "nacl5": (r > 100) & (r < 190) & (g < 70) & (b > 170),
        "nacl10": (r > 200) & (g > 130) & (g < 200) & (b < 80)}
X0, X1, Y0, DEC = 384, 1167, 634, 98.6
filas = []
for c in range(X0 + 2, X1 - 1):
    d = {"E_MeV": (c - X0) / (X1 - X0) * 10}
    for m, mk in COLS.items():
        rows = np.flatnonzero(mk[130:Y0, c]) + 130
        if c > 850:
            rows = rows[rows > 275]
        for nom, f in (("max", np.min), ("mediana", np.median)):
            d[f"{m}_{nom}"] = 10 ** (1 + (Y0 - f(rows)) / DEC) if len(rows) else np.nan
    filas.append(d)
t = pd.DataFrame(filas); t.to_csv(os.path.join(R, "datos", "fig5_sidelnik_digitalizada.csv"), index=False)
print(t.notna().sum().to_dict())
for E in (0.5, 1, 1.5, 1.9, 2.1, 3, 4, 5, 5.8, 6.1, 7, 8, 9):
    i = (t.E_MeV - E).abs().idxmin(); print(E, {k: round(t.loc[i, k]) if np.isfinite(t.loc[i, k]) else None for k in ("pura_mediana", "nacl25_mediana")})
