#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cuenta neutrones por intervalos energéticos y estima el número detectado
por un WCD con agua pura y con NaCl al 2.5 %, 5 % y 10 %.

Formato esperado del archivo .shw:
neutron px py pz x y z ...

Suposición física:
- px, py, pz están expresados en MeV/c.
- La energía cinética se obtiene relativísticamente con la masa del neutrón.
"""

from pathlib import Path
import math
import numpy as np
import pandas as pd


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

ARCHIVO_ENTRADA = Path("filtered_neutrons(1).shw")
ARCHIVO_SALIDA = Path("conteo_neutrones_por_intervalo.csv")

MASA_NEUTRON_MEV = 939.56542052

# Energías representativas solicitadas [meV]
ENERGIAS_OBJETIVO_MEV = np.array([
    2.5,
    5.0,
    7.0,
    10.0,
    25.0,
    80.0,
    100.0,
    300.0,
    500.0,
    700.0,
    1_000.0,
    10_000.0,
    100_000.0,
    1_000_000.0
], dtype=float)

# Puntos donde se simuló la eficiencia [meV]
ENERGIAS_EFICIENCIA_MEV = np.array([
    1_000_000,
    100_000,
    10_000,
    1_000,
    700,
    500,
    300,
    100,
    80,
    50,
    25,
    10,
    7,
    5,
    2.5,
    1
], dtype=float)

EFICIENCIAS_PORCENTAJE = {
    "Agua_pura": np.array([
        17.583, 17.765, 17.871, 17.984,
        17.704, 17.743, 17.149, 16.157,
        15.942, 15.244, 13.962, 11.829,
        11.103, 10.396, 9.350, 8.021
    ]),
    "NaCl_2.5": np.array([
        21.971, 22.641, 23.417, 22.927,
        22.756, 22.817, 22.512, 21.349,
        20.761, 19.929, 18.457, 15.948,
        15.184, 14.132, 12.530, 11.027
    ]),
    "NaCl_5": np.array([
        25.048, 26.144, 26.396, 26.631,
        26.377, 26.628, 25.922, 24.710,
        24.103, 23.397, 21.563, 18.638,
        17.793, 16.786, 14.982, 13.083
    ]),
    "NaCl_10": np.array([
        29.259, 30.635, 31.653, 31.753,
        31.467, 31.610, 31.204, 30.107,
        29.661, 28.552, 26.474, 23.417,
        22.377, 21.183, 19.047, 16.384
    ])
}


# ==========================================================
# FUNCIONES
# ==========================================================

def energia_cinetica_mev(px: float, py: float, pz: float) -> float:
    """Calcula la energía cinética del neutrón en MeV."""
    p2 = px * px + py * py + pz * pz
    energia_total = math.sqrt(p2 + MASA_NEUTRON_MEV**2)

    # Forma numéricamente estable de E_c = sqrt(p²+m²)-m
    return p2 / (energia_total + MASA_NEUTRON_MEV)


def leer_energias_shw(ruta: Path) -> np.ndarray:
    """Lee el archivo .shw y devuelve energías cinéticas en meV."""
    energias = []
    lineas_invalidas = 0

    with ruta.open("r", encoding="utf-8", errors="replace") as archivo:
        for numero_linea, linea in enumerate(archivo, start=1):
            columnas = linea.split()

            if not columnas or columnas[0].lower() != "neutron":
                continue

            if len(columnas) < 4:
                lineas_invalidas += 1
                continue

            try:
                px, py, pz = map(float, columnas[1:4])
            except ValueError:
                lineas_invalidas += 1
                continue

            energia_mev = energia_cinetica_mev(px, py, pz)

            # 1 MeV = 10^9 meV
            energias.append(energia_mev * 1.0e9)

    if not energias:
        raise RuntimeError(
            "No se encontraron líneas válidas de neutrones en el archivo."
        )

    if lineas_invalidas:
        print(f"Advertencia: se omitieron {lineas_invalidas} líneas inválidas.")

    return np.asarray(energias, dtype=float)


def construir_bordes_logaritmicos(centros: np.ndarray) -> np.ndarray:
    """
    Construye bordes como medias geométricas entre energías representativas.

    El primer y último borde se extrapolan conservando el mismo espaciado
    logarítmico local. Así, cada intervalo queda centrado aproximadamente
    en la energía objetivo.
    """
    centros = np.asarray(centros, dtype=float)

    if np.any(centros <= 0) or np.any(np.diff(centros) <= 0):
        raise ValueError(
            "Las energías objetivo deben ser positivas y estar ordenadas."
        )

    bordes_internos = np.sqrt(centros[:-1] * centros[1:])

    borde_inferior = centros[0]**2 / bordes_internos[0]
    borde_superior = centros[-1]**2 / bordes_internos[-1]

    return np.concatenate([
        [borde_inferior],
        bordes_internos,
        [borde_superior]
    ])


def interpolar_eficiencia_log(
    energias_consulta_mev: np.ndarray,
    energias_tabla_mev: np.ndarray,
    eficiencias_porcentaje: np.ndarray
) -> np.ndarray:
    """
    Interpola la eficiencia linealmente en log10(E).

    Fuera del intervalo simulado se fija el valor del extremo más cercano.
    Esto evita extrapolaciones no controladas.
    """
    orden = np.argsort(energias_tabla_mev)
    x = np.log10(energias_tabla_mev[orden])
    y = eficiencias_porcentaje[orden] / 100.0

    return np.interp(
        np.log10(energias_consulta_mev),
        x,
        y,
        left=y[0],
        right=y[-1]
    )


def analizar_archivo(
    archivo_entrada: Path,
    archivo_salida: Path
) -> pd.DataFrame:
    energias_neutrones = leer_energias_shw(archivo_entrada)
    bordes = construir_bordes_logaritmicos(ENERGIAS_OBJETIVO_MEV)

    conteos, _ = np.histogram(energias_neutrones, bins=bordes)

    tabla = pd.DataFrame({
        "energia_representativa_meV": ENERGIAS_OBJETIVO_MEV,
        "borde_inferior_meV": bordes[:-1],
        "borde_superior_meV": bordes[1:],
        "neutrones_incidentes": conteos
    })

    for nombre, valores in EFICIENCIAS_PORCENTAJE.items():
        eficiencia = interpolar_eficiencia_log(
            ENERGIAS_OBJETIVO_MEV,
            ENERGIAS_EFICIENCIA_MEV,
            valores
        )

        tabla[f"eficiencia_{nombre}"] = eficiencia
        tabla[f"detectados_{nombre}"] = (
            tabla["neutrones_incidentes"] * eficiencia
        )

    tabla.to_csv(archivo_salida, index=False)

    print(f"Archivo analizado: {archivo_entrada}")
    print(f"Neutrones leídos: {len(energias_neutrones):,}")
    print(
        "Rango energético del archivo: "
        f"{energias_neutrones.min():.6g}–"
        f"{energias_neutrones.max():.6g} meV"
    )
    print(f"Neutrones clasificados: {conteos.sum():,}")
    print(f"Archivo generado: {archivo_salida.resolve()}")

    columnas_totales = [
        columna for columna in tabla.columns
        if columna.startswith("detectados_")
    ]

    print("\nTotales esperados detectados:")
    for columna in columnas_totales:
        print(f"  {columna}: {tabla[columna].sum():,.2f}")

    return tabla


if __name__ == "__main__":
    if not ARCHIVO_ENTRADA.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ARCHIVO_ENTRADA.resolve()}"
        )

    resultado = analizar_archivo(
        ARCHIVO_ENTRADA,
        ARCHIVO_SALIDA
    )

    print("\nResumen por intervalo:")
    print(resultado.to_string(index=False))
