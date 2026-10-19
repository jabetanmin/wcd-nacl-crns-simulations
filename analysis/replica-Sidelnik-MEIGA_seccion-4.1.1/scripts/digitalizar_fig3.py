#!/usr/bin/env python3
"""Digitalizacion automatica (por color de pixel) de la Fig. 3 de Sidelnik et al. (2020), espectro gamma.
Marco: columna 220 = 0 MeV, columna 1000 = 20 MeV; fila 552 = 1e0, fila 54 = 1e6 (escala log).
Por columna (25,6 keV) guarda, para cada medio, la fila mas alta (envolvente superior = picos) y la mediana
de los pixeles de su color (continuo). La curva roja (agua pura) queda tapada en parte por las otras: su
mediana es fiable en el continuo; las otras series son nubes de marcadores.
Salida: datos/fig3_sidelnik_digitalizada.csv"""
import os
import numpy as np, pandas as pd
from PIL import Image
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
im = np.asarray(Image.open(os.path.join(R, "datos", "fig3_sidelnik_espectro_gamma.png")).convert("RGB")).astype(int)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
COLS = {"pura": (r > 190) & (g < 70) & (b < 70),
        "nacl25": (r < 60) & (g > 120) & (g < 190) & (b > 80) & (b < 150),
        "nacl5": (r > 110) & (r < 190) & (g < 60) & (b > 170),
        "nacl10": (r > 200) & (g > 130) & (g < 190) & (b < 60)}
X0, X1, Y0, Y1 = 220, 1000, 552, 54
filas = []
for c in range(X0 + 1, X1):
    E = (c - X0) / (X1 - X0) * 20
    d = {"E_MeV": E}
    for m, mk in COLS.items():
        rows = np.flatnonzero(mk[Y1 + 1:Y0, c]) + Y1 + 1
        if c > 850:  # recuadro de la leyenda (filas 54-190, E > 16,5 MeV)
            rows = rows[rows > 190]
        for nom, val in (("max", rows.min() if len(rows) else np.nan), ("mediana", np.median(rows) if len(rows) else np.nan)):
            d[f"{m}_{nom}"] = 10 ** (6 * (Y0 - val) / (Y0 - Y1)) if np.isfinite(val) else np.nan
    filas.append(d)
t = pd.DataFrame(filas); t.to_csv(os.path.join(R, "datos", "fig3_sidelnik_digitalizada.csv"), index=False)
print(t.describe().T[["count", "min", "max"]])
