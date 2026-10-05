"""Regenera la figura de la Sec. 4.4: flujo por unidad de letargía de los neutrones de ARTI (> 20 MeV).

Entrada: S3_bga_003600_neutrons.shw (salida de ARTI para Bucaramanga, momento en GeV/c).
Normalización: área de 1 m2 y tiempo de integración de 3600 s, según la convención de ARTI
(opción -t; el número del nombre del archivo es ese tiempo en segundos). El archivo corresponde
al flujo en el nivel de inyección del bloque atmosférico de MEIGA, 2000 m sobre el suelo.

Uso: python3 regenerar_flujo_ARTI_seccion_4_4.py <archivo .shw> <directorio de salida>
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

M_N = 939.56542052          # MeV
AREA_CM2 = 1.0e4            # 1 m2
T_S = 3600.0                # s
BINS_POR_DECADA = 20

entrada = Path(sys.argv[1])
salida = Path(sys.argv[2])

p = []
for linea in entrada.open():
    c = linea.split()
    if not c or c[0].startswith("#"):
        continue
    p.append([float(v) for v in c[1:4]])
p = np.array(p) * 1000.0                                  # MeV/c
E = np.sqrt((p**2).sum(axis=1) + M_N**2) - M_N            # MeV
N = len(E)

bordes = 10 ** np.arange(np.floor(np.log10(E.min())), np.ceil(np.log10(E.max())) + 1e-9, 1 / BINS_POR_DECADA)
cuentas, _ = np.histogram(E, bins=bordes)
du = np.log(bordes[1:] / bordes[:-1])
dphi_du = cuentas / (AREA_CM2 * T_S * du)
phi_total = N / (AREA_CM2 * T_S)

fig, ax = plt.subplots(figsize=(9.5, 5.6))
ax.step(bordes[:-1], dphi_du, where="post", color="#0b3d91", lw=1.6,
        label="Neutrones de ARTI (> 20 MeV) en el nivel de inyección, Bucaramanga")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(10, 2e5)
positivos = dphi_du[dphi_du > 0]
ax.set_ylim(10 ** np.floor(np.log10(positivos.min())), 10 ** np.ceil(np.log10(positivos.max()) + 0.3))
ax.set_xlabel("Energía cinética del neutrón [MeV]", fontsize=13)
ax.set_ylabel(r"Flujo por unidad de letargía, $\frac{d\Phi}{du}$  [n cm$^{-2}$ s$^{-1}$]", fontsize=12)
ax.grid(True, which="both", ls=":", color="0.8")
ax.legend(loc="upper right", fontsize=10)
texto = (r"$A = 1$ m$^2$" "\n" r"$T = 3600$ s" "\n"
         rf"$N_\mathrm{{total}} = {N}$" "\n"
         rf"$\Phi_\mathrm{{total}} = {phi_total:.3e}$" "\n" r"[n cm$^{-2}$ s$^{-1}$]")
ax.text(0.02, 0.04, texto, transform=ax.transAxes, fontsize=9, va="bottom",
        bbox=dict(boxstyle="round", fc="white", ec="0.6"))
fig.tight_layout()
salida.mkdir(parents=True, exist_ok=True)
fig.savefig(salida / "Flujo-letargico-neutrones-ARTI-Bucaramanga.pdf")
fig.savefig(salida / "Flujo-letargico-neutrones-ARTI-Bucaramanga.png", dpi=300)
print(f"N = {N}, E = {E.min():.3f}-{E.max():.4g} MeV, Phi_total = {phi_total:.4e} n cm^-2 s^-1")
