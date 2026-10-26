"""
Regiones de energía del neutrón: la clasificación operativa de la tesis (Tabla 2.2, cap. 2), basada en Krane (1988,
cap. 12), Podgoršak (2010, cap. 9), Köhli et al. (2015, sec. 2.2, fig. 1) y la IAEA (2023, fuentes de neutrones fríos).
Energías en MeV. Todos los límites caen en la malla de 10 intervalos por década de analizar_albedo.py.
Colores: ninguno coincide con los de los medios (rojo, verde, púrpura, naranja).
"""
REGIONES = [  # nombre, E_min, E_max [MeV], texto LaTeX del rango, color de la curva, color de fondo
    ("Ultrafríos",   1e-14, 2e-10, "$<0.2$~meV",          "#7f7f7f", "#f2f2f2"),
    ("Fríos",        2e-10, 1e-8,  "0.2--10~meV",         "#1b2a6b", "#e9ecf7"),
    ("Térmicos",     1e-8,  1e-7,  "10--100~meV",         "#1f77d4", "#e6f0fb"),
    ("Epitérmicos",  1e-7,  1e-6,  "0.1--1~eV",           "#17becf", "#e5f7f9"),
    ("Intermedios",  1e-6,  1e-2,  "1~eV--10~keV",        "#bcbd22", "#f6f6e2"),
    ("Rápidos",      1e-2,  20.0,  "10~keV--20~MeV",      "#8c564b", "#f6ede9"),
    ("Alta energía", 20.0,  1e6,   "$>20$~MeV",           "#e377c2", "#fcedf7"),
]
NOMBRES = [r[0] for r in REGIONES]
LIMITES = {r[0]: (r[1], r[2]) for r in REGIONES}
TEXTO = {r[0]: r[3] for r in REGIONES}
COLOR = {r[0]: r[4] for r in REGIONES}
FONDO = {r[0]: r[5] for r in REGIONES}
CLAVE = {"Ultrafríos": "Ufr", "Fríos": "Fri", "Térmicos": "Ter", "Epitérmicos": "Epi", "Intermedios": "Int",
         "Rápidos": "Rap", "Alta energía": "Alt"}            # para las macros de cifras.tex
AJUSTE = ["Intermedios", "Rápidos"]                       # regiones sensibles al agua en las que se ajusta Desilets


def sombrear(ax, xmin, xmax, etiquetas=True, y=None, fontsize=8):
    """Fondo de color por región y, si se pide, el nombre vertical de cada región en la parte alta del eje."""
    import numpy as np
    for n, lo, hi, _, _, fondo in REGIONES:
        a, b = max(lo, xmin), min(hi, xmax)
        if a >= b: continue
        ax.axvspan(a, b, color=fondo, zorder=0)
        if etiquetas:
            yy = y if y is not None else 0.97
            ax.text(np.sqrt(a * b), yy, n, ha="center", va="top", fontsize=fontsize, color="0.35", rotation=90,
                    transform=ax.get_xaxis_transform())
