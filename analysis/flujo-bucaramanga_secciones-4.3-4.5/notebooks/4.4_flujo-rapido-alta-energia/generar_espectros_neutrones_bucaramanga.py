import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path

INPUT_FILE = Path("S3_bga_003600_neutrons.shw")
OUTPUT_DIR = Path("analisis_neutrones_bucaramanga")
OUTPUT_DIR.mkdir(exist_ok=True)

EXPOSURE_TIME_S = 3600.0
AREA_M2 = 1.0
NEUTRON_MASS_GEV = 0.9395654205
N_BINS = 120

COLUMNS = [
    "CorsikaId", "px", "py", "pz", "x", "y", "z",
    "shower_id", "prm_id", "prm_energy", "prm_theta", "prm_phi"
]

df = pd.read_csv(INPUT_FILE, sep=r"\s+", header=None, names=COLUMNS)
df = df[df["CorsikaId"] == 13].copy()

p_gev_c = np.sqrt(df["px"]**2 + df["py"]**2 + df["pz"]**2)
ekin_mev = (
    np.sqrt(p_gev_c**2 + NEUTRON_MASS_GEV**2)
    - NEUTRON_MASS_GEV
) * 1.0e3
ekin_mev = ekin_mev[np.isfinite(ekin_mev) & (ekin_mev > 0)].to_numpy()

edges = np.logspace(
    np.log10(ekin_mev.min()),
    np.log10(ekin_mev.max()),
    N_BINS + 1
)
centers = np.sqrt(edges[:-1] * edges[1:])
delta_e = np.diff(edges)
delta_u = np.log(edges[1:] / edges[:-1])
counts, _ = np.histogram(ekin_mev, bins=edges)

dphi_dE = counts / (AREA_M2 * EXPOSURE_TIME_S * delta_e)
dphi_du = counts / (AREA_M2 * EXPOSURE_TIME_S * delta_u)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 15,
    "axes.labelsize": 19,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 13,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

def format_axes(ax):
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.grid(True, which="major", linestyle="--", linewidth=0.6, alpha=0.30)
    ax.grid(True, which="minor", linestyle=":", linewidth=0.35, alpha=0.12)
    ax.tick_params(which="both", direction="in", top=True, right=True)
    ax.xaxis.set_major_formatter(ticker.LogFormatterMathtext())
    ax.yaxis.set_major_formatter(ticker.LogFormatterMathtext())

fig, ax = plt.subplots(figsize=(11.5, 7.2), constrained_layout=True)
ax.stairs(dphi_dE, edges, linewidth=2.0, label="ARTI/CORSIKA – Bucaramanga")
ax.set_xlabel(r"Energía cinética del neutrón, $E_n$ [MeV]")
ax.set_ylabel(
    r"Flujo diferencial, $\mathrm{d}\Phi_n/\mathrm{d}E$ "
    r"[$\mathrm{n\,m^{-2}\,s^{-1}\,MeV^{-1}}$]"
)
format_axes(ax)
ax.legend()
fig.savefig(OUTPUT_DIR / "flujo_diferencial_neutrones_bucaramanga.pdf",
            bbox_inches="tight")
fig.savefig(OUTPUT_DIR / "flujo_diferencial_neutrones_bucaramanga.png",
            dpi=600, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(11.5, 7.2), constrained_layout=True)
ax.stairs(dphi_du, edges, linewidth=2.0, label="ARTI/CORSIKA – Bucaramanga")
ax.set_xlabel(r"Energía cinética del neutrón, $E_n$ [MeV]")
ax.set_ylabel(
    r"Flujo por unidad de letargía, $\mathrm{d}\Phi_n/\mathrm{d}u$ "
    r"[$\mathrm{n\,m^{-2}\,s^{-1}}$]"
)
format_axes(ax)
ax.legend()
fig.savefig(OUTPUT_DIR / "flujo_letargico_neutrones_bucaramanga.pdf",
            bbox_inches="tight")
fig.savefig(OUTPUT_DIR / "flujo_letargico_neutrones_bucaramanga.png",
            dpi=600, bbox_inches="tight")
plt.close(fig)

pd.DataFrame({
    "E_min_MeV": edges[:-1],
    "E_max_MeV": edges[1:],
    "E_center_MeV": centers,
    "counts": counts,
    "dPhi_dE_n_m2_s_MeV": dphi_dE,
    "dPhi_du_n_m2_s": dphi_du,
}).to_csv(OUTPUT_DIR / "espectros_neutrones_bucaramanga.csv", index=False)

print(f"N = {len(ekin_mev):,}")
print(f"Fluencia = {len(ekin_mev)/AREA_M2:.6e} n/m²")
print(
    "Flujo integrado promedio = "
    f"{len(ekin_mev)/(AREA_M2*EXPOSURE_TIME_S):.6e} n/(m² s)"
)
