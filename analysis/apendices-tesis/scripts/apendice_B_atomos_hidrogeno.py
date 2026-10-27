#!/usr/bin/env python3
"""
Apéndice B de la tesis: número de átomos de hidrógeno en 1 m³ (≈ 1000 kg) de solución al agregar NaCl.

Como en la tesis, se toman 1000 kg de solución para todos los medios: con una fracción en masa f de NaCl quedan
1000 (1 − f) kg de agua, y N_H = 2 N_A m_agua / M_H2O. La reducción relativa de N_H es exactamente f.
Uso: apendice_B_atomos_hidrogeno.py   (imprime la tabla; no lee datos)
"""
M_H2O = 0.01801528          # kg/mol
N_A = 6.02214076e23         # 1/mol
M_SOL = 1000.0              # kg de solución (≈ 1 m³)

n0 = M_SOL / M_H2O
NH0 = 2 * n0 * N_A
print(f"{'f NaCl':>8} {'m_agua [kg]':>12} {'n_H2O [mol]':>13} {'N_H':>11} {'ΔN_H':>10} {'ΔN_H/N_H':>9}")
for f in (0.0, 0.025, 0.05, 0.10):
    m = M_SOL * (1 - f); n = m / M_H2O; NH = 2 * n * N_A
    print(f"{f:8.3f} {m:12.1f} {n:13.5e} {NH:11.4e} {NH0 - NH:10.3e} {100 * (NH0 - NH) / NH0:8.2f} %")
