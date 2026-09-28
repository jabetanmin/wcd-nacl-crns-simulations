import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

ARCHIVO_ENTRADA = "S3_bga_003600_neutrons.shw"

OUTDIR = "Flujo-neutrones-energia-MeV-ARTI"
os.makedirs(OUTDIR, exist_ok=True)

ARCHIVO_NEUTRONES = os.path.join(
    OUTDIR,
    "Neutrones_con_energia_cinetica_MeV.txt"
)

# Archivo detallado para verificar, neutrón por neutrón,
# las componentes del momento y el cálculo de la energía.
ARCHIVO_VERIFICACION_NEUTRONES = os.path.join(
    OUTDIR,
    "Verificacion_componentes_momento_y_energia_neutrones.txt"
)

# Resumen de las comprobaciones numéricas globales.
ARCHIVO_RESUMEN_VERIFICACION = os.path.join(
    OUTDIR,
    "Resumen_verificacion_momento_energia.txt"
)

ARCHIVO_ESPECTRO = os.path.join(
    OUTDIR,
    "Flujo_neutrones_en_funcion_energia_MeV.txt"
)

ARCHIVO_PDF = os.path.join(
    OUTDIR,
    "Flujo-neutrones-energia-MeV-ARTI.pdf"
)

ARCHIVO_PNG = os.path.join(
    OUTDIR,
    "Flujo-neutrones-energia-MeV-ARTI.png"
)


# ==========================================================
# PARÁMETROS FÍSICOS
# ==========================================================

# Masa en reposo del neutrón:
# m_n c² = 939.565 MeV
MASA_NEUTRON_MEV = 939.565

# Conversión de GeV a MeV
GEV_A_MEV = 1000.0

# Identificador del neutrón en el archivo CORSIKA/ARTI
CORSIKA_ID_NEUTRON = 13


# ==========================================================
# PARÁMETROS DE NORMALIZACIÓN
# ==========================================================

# Tiempo de exposición de la simulación
TIEMPO_EXPOSICION_S = 30.0

# Área efectiva de muestreo.
#
# IMPORTANTE:
# reemplaza 1.0 por el área real utilizada en ARTI.
AREA_EFECTIVA_M2 = 1.0


# ==========================================================
# INTERVALO ENERGÉTICO
# ==========================================================

# Límites del espectro en MeV.
#
# Para neutrones atmosféricos puedes modificar estos valores
# según el intervalo realmente contenido en el archivo.
ENERGIA_MIN_MEV = 1.0e-3
ENERGIA_MAX_MEV = 1.0e4

# Número de bins logarítmicos
NUM_BINS = 80


# ==========================================================
# NOMBRES DE LAS COLUMNAS DEL ARCHIVO
# ==========================================================

NOMBRES_COLUMNAS = [
    "CorsikaId",
    "px",
    "py",
    "pz",
    "x",
    "y",
    "z",
    "shower_id",
    "prm_id",
    "prm_energy",
    "prm_theta",
    "prm_phi"
]


# ==========================================================
# CONFIGURACIÓN TIPOGRÁFICA
# ==========================================================

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",

    "font.size": 16,
    "axes.labelsize": 23,
    "xtick.labelsize": 18,
    "ytick.labelsize": 18,
    "legend.fontsize": 15,

    "axes.linewidth": 1.0,

    # Mantener fuentes editables en PDF
    "pdf.fonttype": 42,
    "ps.fonttype": 42
})


# ==========================================================
# COMPROBAR ARCHIVO DE ENTRADA
# ==========================================================

if not os.path.exists(ARCHIVO_ENTRADA):
    raise FileNotFoundError(
        f"No se encontró el archivo: {ARCHIVO_ENTRADA}"
    )


# ==========================================================
# LEER EL ARCHIVO ARTI/CORSIKA
# ==========================================================

datos = pd.read_csv(
    ARCHIVO_ENTRADA,
    sep=r"\s+",
    comment="#",
    header=None
)

numero_columnas = datos.shape[1]

if numero_columnas != len(NOMBRES_COLUMNAS):
    raise ValueError(
        f"El archivo contiene {numero_columnas} columnas, "
        f"pero se esperaban {len(NOMBRES_COLUMNAS)}."
    )

datos.columns = NOMBRES_COLUMNAS


# ==========================================================
# CONVERTIR COLUMNAS A FORMATO NUMÉRICO
# ==========================================================

for columna in NOMBRES_COLUMNAS:

    datos[columna] = pd.to_numeric(
        datos[columna],
        errors="coerce"
    )

# Eliminar filas sin información válida
datos = datos.dropna(
    subset=[
        "CorsikaId",
        "px",
        "py",
        "pz"
    ]
).copy()


# ==========================================================
# SELECCIONAR NEUTRONES
# ==========================================================

datos_neutrones = datos[
    datos["CorsikaId"] == CORSIKA_ID_NEUTRON
].copy()

if datos_neutrones.empty:
    raise ValueError(
        f"No se encontraron partículas con "
        f"CorsikaId = {CORSIKA_ID_NEUTRON}."
    )


# ==========================================================
# CALCULAR EL MOMENTO TOTAL
# ==========================================================
#
# Se supone que px, py y pz están en GeV/c.
# ==========================================================

datos_neutrones["momento_GeV_c"] = np.sqrt(
    datos_neutrones["px"]**2
    + datos_neutrones["py"]**2
    + datos_neutrones["pz"]**2
)

# Eliminar valores no físicos
datos_neutrones = datos_neutrones[
    np.isfinite(datos_neutrones["momento_GeV_c"])
    & (datos_neutrones["momento_GeV_c"] > 0)
].copy()


# ==========================================================
# CONVERTIR MOMENTO DE GeV/c A MeV/c
# ==========================================================

datos_neutrones["momento_MeV_c"] = (
    datos_neutrones["momento_GeV_c"]
    * GEV_A_MEV
)


# ==========================================================
# CALCULAR ENERGÍA TOTAL Y ENERGÍA CINÉTICA EN MeV
# ==========================================================
#
# E_total = sqrt(p² + m²)
#
# E_cinética = E_total - m
#
# p debe estar en MeV/c
# m c² debe estar en MeV
# ==========================================================

momento_MeV_c = datos_neutrones[
    "momento_MeV_c"
].to_numpy()

energia_total_MeV = np.sqrt(
    momento_MeV_c**2
    + MASA_NEUTRON_MEV**2
)

energia_cinetica_MeV = (
    energia_total_MeV
    - MASA_NEUTRON_MEV
)

datos_neutrones["energia_total_MeV"] = (
    energia_total_MeV
)

datos_neutrones["energia_cinetica_MeV"] = (
    energia_cinetica_MeV
)


# ==========================================================
# COMPONENTES DEL MOMENTO EN GeV/c Y MeV/c
# ==========================================================
#
# Las columnas px, py y pz se conservan como fueron leídas
# del archivo ARTI/CORSIKA y se duplican con unidades explícitas.
# El archivo de verificación se genera antes de normalizar por
# área, tiempo o ancho de bin.
# ==========================================================

datos_neutrones["px_GeV_c"] = datos_neutrones["px"]
datos_neutrones["py_GeV_c"] = datos_neutrones["py"]
datos_neutrones["pz_GeV_c"] = datos_neutrones["pz"]

datos_neutrones["px_MeV_c"] = datos_neutrones["px_GeV_c"] * GEV_A_MEV
datos_neutrones["py_MeV_c"] = datos_neutrones["py_GeV_c"] * GEV_A_MEV
datos_neutrones["pz_MeV_c"] = datos_neutrones["pz_GeV_c"] * GEV_A_MEV


# ==========================================================
# COMPROBAR EL MÓDULO DEL MOMENTO
# ==========================================================

datos_neutrones["momento_recalculado_GeV_c"] = np.sqrt(
    datos_neutrones["px_GeV_c"]**2
    + datos_neutrones["py_GeV_c"]**2
    + datos_neutrones["pz_GeV_c"]**2
)

datos_neutrones["momento_recalculado_MeV_c"] = np.sqrt(
    datos_neutrones["px_MeV_c"]**2
    + datos_neutrones["py_MeV_c"]**2
    + datos_neutrones["pz_MeV_c"]**2
)

datos_neutrones["diferencia_momento_GeV_c"] = (
    datos_neutrones["momento_recalculado_GeV_c"]
    - datos_neutrones["momento_GeV_c"]
)

datos_neutrones["diferencia_momento_MeV_c"] = (
    datos_neutrones["momento_recalculado_MeV_c"]
    - datos_neutrones["momento_MeV_c"]
)


# ==========================================================
# COMPROBACIÓN INDEPENDIENTE DE LA ENERGÍA CINÉTICA
# ==========================================================
# Método 1: cálculo directo en MeV.
# Método 2: cálculo en GeV y conversión posterior a MeV.
# ==========================================================

MASA_NEUTRON_GEV = MASA_NEUTRON_MEV / GEV_A_MEV

energia_cinetica_comprobacion_MeV = GEV_A_MEV * (
    np.sqrt(
        datos_neutrones["momento_GeV_c"].to_numpy()**2
        + MASA_NEUTRON_GEV**2
    )
    - MASA_NEUTRON_GEV
)

datos_neutrones["energia_cinetica_comprobacion_MeV"] = (
    energia_cinetica_comprobacion_MeV
)

datos_neutrones["diferencia_energia_cinetica_MeV"] = (
    datos_neutrones["energia_cinetica_MeV"]
    - datos_neutrones["energia_cinetica_comprobacion_MeV"]
)


# ==========================================================
# COMPROBAR LA RELACIÓN RELATIVISTA ENERGÍA-MOMENTO
# ==========================================================
# Debe cumplirse E_total² - p² - m² = 0.
# ==========================================================

datos_neutrones["residuo_relativista_MeV2"] = (
    datos_neutrones["energia_total_MeV"]**2
    - datos_neutrones["momento_MeV_c"]**2
    - MASA_NEUTRON_MEV**2
)


# ==========================================================
# GUARDAR ARCHIVO DETALLADO DE VERIFICACIÓN
# ==========================================================

columnas_verificacion = [
    "CorsikaId",
    "shower_id",
    "prm_id",
    "prm_energy",
    "prm_theta",
    "prm_phi",
    "px_GeV_c",
    "py_GeV_c",
    "pz_GeV_c",
    "momento_GeV_c",
    "momento_recalculado_GeV_c",
    "px_MeV_c",
    "py_MeV_c",
    "pz_MeV_c",
    "momento_MeV_c",
    "momento_recalculado_MeV_c",
    "energia_total_MeV",
    "energia_cinetica_MeV",
    "energia_cinetica_comprobacion_MeV",
    "diferencia_momento_GeV_c",
    "diferencia_momento_MeV_c",
    "diferencia_energia_cinetica_MeV",
    "residuo_relativista_MeV2"
]

tabla_verificacion = datos_neutrones[columnas_verificacion].copy()

tabla_verificacion.to_csv(
    ARCHIVO_VERIFICACION_NEUTRONES,
    sep="\t",
    index=False,
    float_format="%.12e"
)


# ==========================================================
# ESTADÍSTICAS DE LAS COMPROBACIONES
# ==========================================================

def estadisticas_absolutas(serie):
    valores = np.abs(np.asarray(serie, dtype=float))
    return {
        "maximo": float(np.max(valores)),
        "media": float(np.mean(valores)),
        "mediana": float(np.median(valores)),
        "rms": float(np.sqrt(np.mean(valores**2)))
    }

est_momento_GeV = estadisticas_absolutas(
    datos_neutrones["diferencia_momento_GeV_c"]
)
est_momento_MeV = estadisticas_absolutas(
    datos_neutrones["diferencia_momento_MeV_c"]
)
est_energia = estadisticas_absolutas(
    datos_neutrones["diferencia_energia_cinetica_MeV"]
)
est_relativista = estadisticas_absolutas(
    datos_neutrones["residuo_relativista_MeV2"]
)


# ==========================================================
# GUARDAR RESUMEN DE VERIFICACIÓN
# ==========================================================

lineas_resumen = [
    "RESUMEN DE VERIFICACIÓN DEL MOMENTO Y LA ENERGÍA",
    "================================================",
    f"Archivo de entrada: {ARCHIVO_ENTRADA}",
    f"Número total de neutrones válidos: {len(datos_neutrones)}",
    f"Masa del neutrón utilizada: {MASA_NEUTRON_MEV:.9f} MeV/c^2",
    "",
    "1. Diferencia del módulo del momento en GeV/c",
    f"   Máximo absoluto: {est_momento_GeV['maximo']:.12e}",
    f"   Media absoluta:  {est_momento_GeV['media']:.12e}",
    f"   Mediana absoluta:{est_momento_GeV['mediana']:.12e}",
    f"   RMS:             {est_momento_GeV['rms']:.12e}",
    "",
    "2. Diferencia del módulo del momento en MeV/c",
    f"   Máximo absoluto: {est_momento_MeV['maximo']:.12e}",
    f"   Media absoluta:  {est_momento_MeV['media']:.12e}",
    f"   Mediana absoluta:{est_momento_MeV['mediana']:.12e}",
    f"   RMS:             {est_momento_MeV['rms']:.12e}",
    "",
    "3. Diferencia entre métodos de energía cinética [MeV]",
    f"   Máximo absoluto: {est_energia['maximo']:.12e}",
    f"   Media absoluta:  {est_energia['media']:.12e}",
    f"   Mediana absoluta:{est_energia['mediana']:.12e}",
    f"   RMS:             {est_energia['rms']:.12e}",
    "",
    "4. Residuo E_total^2 - p^2 - m^2 [MeV^2]",
    f"   Máximo absoluto: {est_relativista['maximo']:.12e}",
    f"   Media absoluta:  {est_relativista['media']:.12e}",
    f"   Mediana absoluta:{est_relativista['mediana']:.12e}",
    f"   RMS:             {est_relativista['rms']:.12e}",
    "",
    "Los valores deben ser próximos a cero y compatibles con",
    "la precisión numérica de punto flotante."
]

with open(
    ARCHIVO_RESUMEN_VERIFICACION,
    "w",
    encoding="utf-8"
) as archivo_resumen:
    archivo_resumen.write("\n".join(lineas_resumen) + "\n")


# ==========================================================
# GUARDAR TABLA GENERAL DE NEUTRONES
# ==========================================================

datos_neutrones.to_csv(
    ARCHIVO_NEUTRONES,
    sep="\t",
    index=False,
    float_format="%.12e"
)


# ==========================================================
# MOSTRAR COMPROBACIONES EN TERMINAL
# ==========================================================

print("\nComprobaciones numéricas")
print("-------------------------")
print(
    "Diferencia máxima del módulo del momento: "
    f"{est_momento_MeV['maximo']:.12e} MeV/c"
)
print(
    "Diferencia máxima entre métodos de energía: "
    f"{est_energia['maximo']:.12e} MeV"
)
print(
    "Residuo relativista máximo: "
    f"{est_relativista['maximo']:.12e} MeV²"
)
print(f"Archivo detallado: {ARCHIVO_VERIFICACION_NEUTRONES}")
print(f"Resumen: {ARCHIVO_RESUMEN_VERIFICACION}")
print("\nPrimeras filas de la tabla de verificación:")
print(tabla_verificacion.head().to_string(index=False))


# ==========================================================
# FILTRAR EL INTERVALO ENERGÉTICO
# ==========================================================

mascara_energia = (
    np.isfinite(energia_cinetica_MeV)
    & (energia_cinetica_MeV >= ENERGIA_MIN_MEV)
    & (energia_cinetica_MeV <= ENERGIA_MAX_MEV)
)

energia_filtrada_MeV = energia_cinetica_MeV[
    mascara_energia
]

if energia_filtrada_MeV.size == 0:
    raise ValueError(
        "No quedaron neutrones dentro del intervalo energético. "
        "Revisa ENERGIA_MIN_MEV y ENERGIA_MAX_MEV."
    )


# ==========================================================
# CREAR BINS LOGARÍTMICOS EN MeV
# ==========================================================

bordes_energia_MeV = np.logspace(
    np.log10(ENERGIA_MIN_MEV),
    np.log10(ENERGIA_MAX_MEV),
    NUM_BINS + 1
)

# Para bins logarítmicos, el centro geométrico es más adecuado
centros_energia_MeV = np.sqrt(
    bordes_energia_MeV[:-1]
    * bordes_energia_MeV[1:]
)

anchos_energia_MeV = np.diff(
    bordes_energia_MeV
)


# ==========================================================
# CALCULAR EL HISTOGRAMA
# ==========================================================

conteos, _ = np.histogram(
    energia_filtrada_MeV,
    bins=bordes_energia_MeV
)


# ==========================================================
# NORMALIZACIÓN POR ÁREA Y TIEMPO
# ==========================================================

factor_area_tiempo = (
    AREA_EFECTIVA_M2
    * TIEMPO_EXPOSICION_S
)

if factor_area_tiempo <= 0:
    raise ValueError(
        "El producto AREA_EFECTIVA_M2 × "
        "TIEMPO_EXPOSICION_S debe ser positivo."
    )


# ==========================================================
# FLUJO INTEGRADO POR BIN
# ==========================================================
#
# Phi_i = N_i / (A T)
#
# Unidades:
# m^-2 s^-1
# ==========================================================

flujo_por_bin = (
    conteos
    / factor_area_tiempo
)


# ==========================================================
# FLUJO DIFERENCIAL EN MeV
# ==========================================================
#
# dPhi/dE = N_i / (A T DeltaE_i)
#
# Como DeltaE está en MeV:
#
# unidades:
# m^-2 s^-1 MeV^-1
# ==========================================================

flujo_diferencial_MeV = (
    conteos
    / (
        factor_area_tiempo
        * anchos_energia_MeV
    )
)


# ==========================================================
# INCERTIDUMBRE ESTADÍSTICA DE POISSON
# ==========================================================
#
# sigma_N = sqrt(N)
#
# sigma_dPhi/dE =
# sqrt(N) / (A T DeltaE)
# ==========================================================

incertidumbre_conteos = np.sqrt(
    conteos.astype(float)
)

incertidumbre_flujo_MeV = (
    incertidumbre_conteos
    / (
        factor_area_tiempo
        * anchos_energia_MeV
    )
)


# ==========================================================
# PREPARAR VALORES PARA ESCALA LOGARÍTMICA
# ==========================================================

flujo_visible = np.where(
    flujo_diferencial_MeV > 0,
    flujo_diferencial_MeV,
    np.nan
)

limite_inferior = np.where(
    flujo_diferencial_MeV
    - incertidumbre_flujo_MeV
    > 0,
    flujo_diferencial_MeV
    - incertidumbre_flujo_MeV,
    np.nan
)

limite_superior = np.where(
    flujo_diferencial_MeV > 0,
    flujo_diferencial_MeV
    + incertidumbre_flujo_MeV,
    np.nan
)


# ==========================================================
# GUARDAR EL ESPECTRO
# ==========================================================

resultados = np.column_stack([
    bordes_energia_MeV[:-1],
    bordes_energia_MeV[1:],
    centros_energia_MeV,
    anchos_energia_MeV,
    conteos,
    flujo_por_bin,
    flujo_diferencial_MeV,
    incertidumbre_flujo_MeV
])

encabezado = (
    "E_min_MeV "
    "E_max_MeV "
    "E_centro_MeV "
    "DeltaE_MeV "
    "Conteos "
    "Flujo_por_bin_m-2_s-1 "
    "Flujo_diferencial_m-2_s-1_MeV-1 "
    "Incertidumbre_m-2_s-1_MeV-1"
)

np.savetxt(
    ARCHIVO_ESPECTRO,
    resultados,
    header=encabezado,
    fmt=[
        "%.8e",
        "%.8e",
        "%.8e",
        "%.8e",
        "%d",
        "%.8e",
        "%.8e",
        "%.8e"
    ]
)


# ==========================================================
# MOSTRAR INFORMACIÓN EN TERMINAL
# ==========================================================

print("\nResumen del espectro")
print("--------------------")

print(
    f"Archivo de entrada: {ARCHIVO_ENTRADA}"
)

print(
    f"Neutrones encontrados: "
    f"{len(datos_neutrones):,}"
)

print(
    f"Neutrones dentro del intervalo: "
    f"{len(energia_filtrada_MeV):,}"
)

print(
    f"Momento mínimo: "
    f"{np.min(momento_MeV_c):.6e} MeV/c"
)

print(
    f"Momento máximo: "
    f"{np.max(momento_MeV_c):.6e} MeV/c"
)

print(
    f"Energía cinética mínima total: "
    f"{np.min(energia_cinetica_MeV):.6e} MeV"
)

print(
    f"Energía cinética máxima total: "
    f"{np.max(energia_cinetica_MeV):.6e} MeV"
)

print(
    f"Tiempo de exposición: "
    f"{TIEMPO_EXPOSICION_S:.2f} s"
)

print(
    f"Área efectiva: "
    f"{AREA_EFECTIVA_M2:.6f} m²"
)

print(
    f"Número de bins: {NUM_BINS}"
)


# ==========================================================
# CREAR FIGURA
# ==========================================================

fig, ax = plt.subplots(
    figsize=(13.5, 8.5),
    constrained_layout=True
)


# ==========================================================
# GRAFICAR EL FLUJO DIFERENCIAL
# ==========================================================

ax.stairs(
    flujo_diferencial_MeV,
    bordes_energia_MeV,
    linewidth=1.55,
    color="firebrick",
    label="Neutrones secundarios",
    zorder=5
)


# ==========================================================
# BANDA DE INCERTIDUMBRE
# ==========================================================

ax.fill_between(
    centros_energia_MeV,
    limite_inferior,
    limite_superior,
    step="mid",
    alpha=0.20,
    linewidth=0,
    label=r"Incertidumbre estadística, $\sqrt{N}$",
    zorder=3
)


# ==========================================================
# ESCALAS Y LÍMITES
# ==========================================================

ax.set_xscale("log")
ax.set_yscale("log")

ax.set_xlim(
    ENERGIA_MIN_MEV,
    ENERGIA_MAX_MEV
)

valores_positivos = flujo_diferencial_MeV[
    flujo_diferencial_MeV > 0
]

if valores_positivos.size > 0:

    ax.set_ylim(
        np.min(valores_positivos) * 0.55,
        np.max(valores_positivos) * 2.0
    )


# ==========================================================
# ETIQUETAS DE LOS EJES
# ==========================================================

ax.set_xlabel(
    r"Energía cinética del neutrón, $E_{k,n}$ [MeV]",
    labelpad=18
)

ax.set_ylabel(
    r"Flujo diferencial de neutrones, "
    r"$\mathrm{d}\Phi_n/\mathrm{d}E$ "
    r"[$\mathrm{m}^{-2}\,\mathrm{s}^{-1}\,\mathrm{MeV}^{-1}$]",
    labelpad=20
)


# ==========================================================
# CONFIGURACIÓN DE LOS TICKS DEL EJE X
# ==========================================================

ax.xaxis.set_major_locator(
    ticker.LogLocator(
        base=10,
        numticks=12
    )
)

ax.xaxis.set_minor_locator(
    ticker.LogLocator(
        base=10,
        subs=np.arange(2, 10) * 0.1,
        numticks=100
    )
)

ax.xaxis.set_major_formatter(
    ticker.LogFormatterMathtext(
        base=10
    )
)

ax.xaxis.set_minor_formatter(
    ticker.NullFormatter()
)


# ==========================================================
# CONFIGURACIÓN DE LOS TICKS DEL EJE Y
# ==========================================================

ax.yaxis.set_major_locator(
    ticker.LogLocator(
        base=10,
        numticks=12
    )
)

ax.yaxis.set_minor_locator(
    ticker.LogLocator(
        base=10,
        subs=np.arange(2, 10) * 0.1,
        numticks=100
    )
)

ax.yaxis.set_major_formatter(
    ticker.LogFormatterMathtext(
        base=10
    )
)

ax.yaxis.set_minor_formatter(
    ticker.NullFormatter()
)


# ==========================================================
# APARIENCIA DE LOS TICKS
# ==========================================================

ax.tick_params(
    axis="both",
    which="major",
    direction="in",
    length=7,
    width=1.0,
    labelsize=19,
    top=True,
    right=True
)

ax.tick_params(
    axis="both",
    which="minor",
    direction="in",
    length=3.5,
    width=0.6,
    top=True,
    right=True
)


# ==========================================================
# CUADRÍCULA
# ==========================================================

ax.grid(
    visible=True,
    which="major",
    axis="both",
    linestyle="--",
    linewidth=0.55,
    color="0.55",
    alpha=0.35
)

ax.grid(
    visible=True,
    which="minor",
    axis="both",
    linestyle=":",
    linewidth=0.32,
    color="0.65",
    alpha=0.13
)

ax.set_axisbelow(True)


# ==========================================================
# INFORMACIÓN DE LA SIMULACIÓN
# ==========================================================

texto_simulacion = (
    "Simulación ARTI\n"
    "Bucaramanga, Colombia\n"
    f"Tiempo de exposición: {TIEMPO_EXPOSICION_S:g} s\n"
    f"Área efectiva: {AREA_EFECTIVA_M2:g} m²"
)

ax.text(
    0.025,
    0.965,
    texto_simulacion,
    transform=ax.transAxes,
    fontsize=15.5,
    ha="left",
    va="top",
    color="0.25",
    bbox=dict(
        facecolor="white",
        edgecolor="0.65",
        linewidth=0.7,
        boxstyle="round,pad=0.35",
        alpha=0.92
    ),
    zorder=15
)


# ==========================================================
# LEYENDA
# ==========================================================

leyenda = ax.legend(
    loc="upper right",
    fontsize=15,
    frameon=True,
    framealpha=0.94,
    facecolor="white",
    edgecolor="0.65",
    borderpad=0.70,
    labelspacing=0.50,
    handlelength=2.5
)

leyenda.get_frame().set_linewidth(0.8)


# ==========================================================
# ESTILO DE LOS BORDES
# ==========================================================

for spine in ax.spines.values():

    spine.set_linewidth(1.0)
    spine.set_color("0.20")


# ==========================================================
# GUARDAR FIGURA
# ==========================================================

fig.savefig(
    ARCHIVO_PDF,
    format="pdf",
    bbox_inches="tight",
    pad_inches=0.06
)

fig.savefig(
    ARCHIVO_PNG,
    format="png",
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.06
)


# ==========================================================
# MOSTRAR Y CERRAR
# ==========================================================

plt.show()
plt.close(fig)

print("\nArchivos generados correctamente.")
print(f"Neutrones:    {ARCHIVO_NEUTRONES}")
print(f"Verificación: {ARCHIVO_VERIFICACION_NEUTRONES}")
print(f"Resumen:      {ARCHIVO_RESUMEN_VERIFICACION}")
print(f"Espectro:     {ARCHIVO_ESPECTRO}")
print(f"PDF:          {ARCHIVO_PDF}")
print(f"PNG:          {ARCHIVO_PNG}")