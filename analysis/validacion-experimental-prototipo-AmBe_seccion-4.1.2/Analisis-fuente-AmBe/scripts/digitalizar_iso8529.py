#!/usr/bin/env python3
"""
Digitalización automática (por píxeles) del espectro de referencia 241Am-Be de ISO 8529
mostrado en la lámina 26 de la presentación IAEA "Establishing neutron calibrations at SSDL
using ISO 8529 radionuclide sources" (figura tomada de ISO 8529; histograma B_E·E vs E, eje x log).

La imagen embebida (1191x790 px) se guarda en referencia_ISO8529/. El histograma se reconstruye
como escalones: bordes = saltos en la altura de la línea, nivel = centro del trazo.
Calibración:
  y: marcas 0 / 0,2 / 0,4 / 0,6 / 0,8 del eje (ajuste lineal);
  x: interpolación lineal de log10(E) entre TODAS las marcas detectadas (el dibujo original
     tiene décadas de ancho desigual: 297, 273 y 284 px).
Salida: resultados/ISO8529_AmBe_digitalizado.txt (grupos E_inf, E_sup, B_E·E relativo) y fig09.
"""
import os
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(AQUI, ".."))
IMG = os.path.join(BASE, "referencia_ISO8529", "IAEA_SSDL_lamina26_espectro_AmBe_ISO8529.jpg")
RES, FIG = os.path.join(BASE, "resultados"), os.path.join(BASE, "figuras")

g = np.asarray(Image.open(IMG).convert("L"))
neg = g < 110                                    # trazo negro

# --- calibración (posiciones medidas sobre la imagen; centros de las marcas) ---
Y_PX = np.array([691.5, 539.0, 385.5, 232.5, 80.5]); Y_VAL = np.array([0, 0.2, 0.4, 0.6, 0.8])
ay, by = np.polyfit(Y_PX, Y_VAL, 1)
X_TICKS = [(152.5, 0.01), (238, 0.02), (288, 0.03), (351.5, 0.04), (373.5, 0.05), (393, 0.06),
           (409.5, 0.07), (424, 0.08), (436.5, 0.09), (449.5, 0.1), (522.5, 0.2), (572.5, 0.3),
           (608.5, 0.4), (635.5, 0.5), (658.5, 0.6), (677.5, 0.7), (694, 0.8), (708.5, 0.9),
           (722.5, 1.0), (808, 2), (858, 3), (893, 4), (921, 5), (943.5, 6), (963, 7),
           (979.5, 8), (994, 9), (1006.5, 10), (1092.5, 20)]
XP = np.array([p for p, _ in X_TICKS]); XL = np.log10([e for _, e in X_TICKS])
px_a_E = lambda x: 10 ** np.interp(x, XP, XL)
px_a_y = lambda r: ay * r + by

# --- trazo: intervalo vertical [arriba, abajo] del trazo en cada columna ---
# El trazo tiene 4 filas de grueso en los tramos horizontales (h = 1.5 px desde el centro) y
# ~5 columnas en los verticales (hw = 2). Por encima de 5 MeV muchos escalones son más angostos
# que el trazo. Modelo: el intervalo de la columna c es [min S, max S] de la escalera S(x) en
# x ∈ [c-hw, c+hw]. Por tanto, para cada x, S(x) está en la intersección de los intervalos de
# todas las columnas c con |c - x| <= hw. Eso recupera también los escalones angostos.
X0, X1, FILA_MAX, BASE_FILA, h, hw = 440, 1026, 676, 691.5, 1.5, 2
lo = np.full(g.shape[1], np.nan); hi = np.full(g.shape[1], np.nan)
for x in range(X0, X1):
    r = np.where(neg[60:FILA_MAX, x])[0] + 60
    trozos = [t for t in np.split(r, np.where(np.diff(r) > 1)[0] + 1) if len(t) >= 2] if len(r) else []
    if not trozos:                                # curva sobre el eje
        lo[x] = hi[x] = BASE_FILA
        continue
    t = trozos[0]                                 # el trazo es el tramo más alto; debajo, marcas del eje
    lo[x], hi[x] = t[0] + h, t[-1] - h
    if t[-1] >= FILA_MAX - 2:                     # desciende hasta el eje
        hi[x] = BASE_FILA
        if t[0] >= FILA_MAX - 8:                  # solo una marca del eje: curva en cero
            lo[x] = BASE_FILA

S = np.full(g.shape[1], np.nan)
for x in range(X0 + hw, X1 - hw):
    a = np.max(lo[x - hw:x + hw + 1]); b = np.min(hi[x - hw:x + hw + 1])
    S[x] = 0.5 * (a + b) if a <= b + 2.5 else np.nan
# Máximos y mínimos angostos: si un tramo de columnas con el mismo 'lo' es un mínimo local del
# perfil lo (pico de la escalera), el escalón ocupa [c1+hw, c2-hw]; igual para 'hi' (valles).
fijo = np.zeros(g.shape[1], bool)
def extremos(perfil, signo):
    c = X0
    tr = []
    while c < X1:
        d = c
        while d + 1 < X1 and abs(perfil[d + 1] - perfil[c]) <= 1:
            d += 1
        tr.append((c, d, float(np.median(perfil[c:d + 1]))))
        c = d + 1
    for k in range(1, len(tr) - 1):
        c1, c2, v = tr[k]
        if signo * (tr[k - 1][2] - v) > 1.5 and signo * (tr[k + 1][2] - v) > 1.5:
            a1, a2 = c1 + hw, c2 - hw
            if a2 < a1:
                a1 = a2 = (c1 + c2) // 2
            S[a1:a2 + 1] = v
            fijo[a1:a2 + 1] = True
extremos(lo, +1)      # picos (fila menor que los vecinos)
extremos(hi, -1)      # valles
xs = np.arange(X0 + hw, X1 - hw)
Sv = S[xs]
ok = ~np.isnan(Sv)
Sv = np.interp(xs, xs[ok], Sv[ok])
# escalones: tramos de S constante (tolerancia 1.5 px)
tramos = [[xs[0], xs[0], [Sv[0]]]]
for x, v in zip(xs[1:], Sv[1:]):
    if abs(v - np.median(tramos[-1][2])) <= 1.5:
        tramos[-1][1] = x; tramos[-1][2].append(v)
    else:
        tramos.append([x, x, [v]])
tramos = [(a, b, float(np.median(v))) for a, b, v in tramos]
# quita tramos espurios de 1 columna entre dos niveles (transición), salvo picos/valles fijados
tramos = [t for k, t in enumerate(tramos) if t[1] > t[0] or fijo[t[0]] or k in (0, len(tramos) - 1)]
# une tramos contiguos que quedaron al mismo nivel tras quitar los espurios
uni = [list(tramos[0])]
for t in tramos[1:]:
    if abs(t[2] - uni[-1][2]) <= 1.5:
        uni[-1][1] = t[1]
    else:
        uni.append(list(t))
tramos = [tuple(t) for t in uni]
tramos = [t for t in tramos if abs(t[2] - BASE_FILA) > 3]          # fuera los tramos en cero
bordes = np.array([tramos[0][0] - 0.5] + [0.5 * (t1[1] + t2[0]) for t1, t2 in zip(tramos[:-1], tramos[1:])]
                  + [tramos[-1][1] + 0.5])
niv = [t[2] for t in tramos]
nivel = px_a_y(np.array(niv))
E_b = px_a_E(bordes)
salida = os.path.join(RES, "ISO8529_AmBe_digitalizado.txt")
np.savetxt(salida, np.column_stack([E_b[:-1], E_b[1:], nivel]), fmt="%.5f %.5f %.5f",
           header="E_inf[MeV] E_sup[MeV] B_E*E (relativo, por unidad de letargia) "
                  "- digitalizado de ISO 8529 (lamina 26 IAEA SSDL)")

# --- validación: energía media de fluencia ---
L = np.log(E_b[1:] / E_b[:-1])
peso = nivel * L                                  # fracción por grupo
Em = np.sum(nivel * (E_b[1:] - E_b[:-1])) / np.sum(peso)
print(f"{len(nivel)} grupos, E de {E_b[0]:.4f} a {E_b[-1]:.3f} MeV, <E> = {Em:.3f} MeV")

# --- figura de control: superposición sobre la imagen ---
fig, ax = plt.subplots(figsize=(9, 6))
ax.imshow(g, cmap="gray")
xs = np.repeat(bordes, 2)[1:-1]; ys = np.repeat(niv, 2)
ax.plot(xs, ys, color="red", lw=1.0)
ax.set_xlim(400, 1060); ax.set_ylim(700, 50)
ax.set_title(f"Digitalización: {len(nivel)} grupos, $\\langle E\\rangle$ = {Em:.2f} MeV", fontsize=11)
ax.axis("off")
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"fig09_digitalizacion_ISO8529.{ext}"), dpi=200)
