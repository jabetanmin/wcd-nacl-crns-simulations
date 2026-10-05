#!/usr/bin/env python3
"""Cálculos sin datos de simulación usados en la revisión de la tesis (octubre de 2026).

  Tabla 3.2  contenido volumétrico de agua del suelo, theta_w = (w/rho_agua)/(w/rho_agua + (1-w)/rho_suelo)
  Tabla 4.13 coeficiente de atenuación másico mu/rho de las soluciones (coeficientes elementales de NIST,
             tablas de Hubbell y Seltzer) con la concentración como fracción en masa de la solución,
             igual que en el simulador (SaltyWCD.cc); la masa es rho * V del volumen activo (Tabla 4.7)
  Tabla 4.18 energía cinética umbral Cherenkov, E = m_e c^2 (1/sqrt(1 - 1/n^2) - 1), y su diferencia
             relativa con el máximo del espectro de electrones de Geant4 (0.26410-0.26411 MeV en los
             cuatro medios; véase umbral_cherenkov.py)
"""
import math

print("Tabla 3.2 (rho_suelo = 2.7, rho_agua = 1.0 g/cm3)")
for w in (0.05, 0.10, 0.15, 0.25, 0.30):
    a, b = w / 1.0, (1 - w) / 2.7
    print(f"  w = {w:.2f}: theta_w = {a/(a+b):.4f}, rho_mezcla = {1/(a+b):.4f} g/cm3")

mH, mO, mNa, mCl = 1.00794, 15.9994, 22.98977, 35.453
Mw, Ms = 2 * mH + mO, mNa + mCl
mu = {0.02: {"H": 0.3695, "O": 0.8651, "Na": 2.057, "Cl": 7.739},
      0.10: {"H": 0.2944, "O": 0.1551, "Na": 0.1585, "Cl": 0.2050}}   # cm2/g, NIST
print("\nTabla 4.13 (mu/rho en cm2/g y contribución de cada elemento en %)")
for w, masa in ((0.0, 960.96), (0.025, 978.14), (0.05, 995.44), (0.10, 1030.57)):
    fr = {"H": (1 - w) * 2 * mH / Mw, "O": (1 - w) * mO / Mw, "Na": w * mNa / Ms, "Cl": w * mCl / Ms}
    for E in (0.02, 0.10):
        c = {k: fr[k] * mu[E][k] for k in fr}
        t = sum(c.values())
        print(f"  w = {w:5.3f}, M = {masa} kg, E = {E} MeV: mu/rho = {t:.6f}  "
              + "  ".join(f"{k} {100*c[k]/t:.2f}" for k in ("H", "O", "Na", "Cl")))

me = 0.51099895
print("\nTabla 4.18 (umbral calculado y diferencia con el máximo simulado)")
for medio, n, pico in (("Agua pura", 1.3330, 0.26410), ("2.5 % NaCl", 1.3397, 0.26411),
                       ("5 % NaCl", 1.3436, 0.26411), ("10 % NaCl", 1.3594, 0.26411)):
    E = me * (1 / math.sqrt(1 - 1 / n**2) - 1)
    print(f"  {medio:11s} n = {n}: E_umbral = {E:.5f} MeV, pico = {pico:.5f} MeV, "
          f"diferencia = {100*abs(pico-round(E,5))/round(E,5):.5f} %")
