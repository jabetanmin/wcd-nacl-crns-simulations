# Espectro de la fuente de ²⁴¹Am-Be: revisión, referencia ISO 8529 y archivos de entrada de MEIGA

Revisión de la cadena con la que se construyó la fuente de neutrones de la simulación (carpeta hermana
[`../fuente-AmBe/`](../fuente-AmBe/)), corrección de sus defectos y generación de todos los archivos de entrada de
las corridas Am-Be de octubre de 2026. Informe: [`informe/Informe-fuente-AmBe241.pdf`](informe/Informe-fuente-AmBe241.pdf);
cuaderno: `Analisis-fuente-AmBe.ipynb` (generado con `scripts/construir_notebook.py`).

## Resultados principales

- La fuente original (1 637 458 neutrones, ⟨E⟩ = 4.06 MeV) tiene cuatro defectos: el número de neutrones por
  intervalo sigue la densidad de puntos digitalizados (sesgos de −46 % a +35 % en bins de 0.25 MeV), 28 puntos
  espurios (6.2 % de los neutrones), un peine de 437 energías y un archivo ordenado por la digitalización.
- Espectro limpio ⟨E⟩ = 4.15 MeV (ISO 8529-1: 4.16 MeV) y fuente corregida validada con χ²/ndf = 218/214.
- Espectro ISO 8529 digitalizado de la figura de la norma publicada por el IAEA (47 grupos, ⟨E⟩ = 4.21 MeV).
- Montaje blindado modelado con tres componentes (haz 35 %, halo 45 %, fondo 20 %) y espectro Am-Be moderado en agua
  (10 meV – 10 eV) tomado de la corrida del montaje.

## Scripts

| Script | Qué hace |
|---|---|
| `analizar_fuente.py` | diagnóstico de la digitalización y de la fuente cargada en MEIGA; espectro limpio (`resultados/espectro_AmBe_limpio.txt`, `resumen.json`) |
| `generar_fuente.py`, `validar_fuente.py` | fuente corregida (1 637 458 n) y su validación (`resultados/validacion.json`) |
| `digitalizar_iso8529.py`, `comparar_iso8529.py` | digitalización de la figura ISO 8529 y comparación con la digitalización previa |
| `generar_irradiacion.py`, `validar_irradiacion.py` | irradiación de 1 Ci durante 5 min a 10 cm (sin blindaje) |
| `blindaje_fuga.py`, `colimador_area.py` | fuga del blindaje y área del colimador |
| `generar_irradiacion_compuesta.py`, `validar_irradiacion_compuesta.py` | montaje blindado: haz + halo + fondo. El archivo de las corridas del montaje se genera con `--N-total 1000000 --semilla 20261021` |
| `generar_ambe_moderado.py` | espectro Am-Be moderado (10 meV – 10 eV) desde `resultados/AmBe-moderado-MEIGA/flujo_pura.tsv` y archivo de entrada lateral; el de las corridas con el PMT bajado se genera con `--N 500000 --semilla 20261025 --horizontal --radio-haz 2` |

## Datos de entrada

`datos-entrada/` contiene los archivos originales de la carpeta de la fuente que leen `analizar_fuente.py` y
`validar_fuente.py`. Los dos grandes van comprimidos con gzip: `Espectro-completo-neutrones-fuente-AmBe241.txt.gz`,
la fuente original de MEIGA (57 MB sin comprimir), y `Espectro-energia-neutrones-AmBe-241.txt.gz`. Otra carpeta se
elige con `FUENTE_AMBE_DATOS`.

## No incluido

- **La figura de la norma ISO 8529** (`referencia_ISO8529/IAEA_SSDL_lamina26_espectro_AmBe_ISO8529.jpg`): es
  material del IAEA. `digitalizar_iso8529.py` la necesita; se obtiene de la lámina 26 de la presentación del IAEA
  *Establishing neutron calibrations at SSDL using ISO 8529 radionuclide sources*. La digitalización está en
  `resultados/ISO8529_AmBe_digitalizado.txt`.
- **Archivos de neutrones de más de 1 MB.** Son la fuente corregida, las 203 partes de la irradiación sin blindaje
  (77 MB cada una) y los flujos moderados. Se regeneran con los scripts y su semilla; sus sha256 están en
  [`data/manifiestos/excluidos-v0.8.0.sha256`](../../../data/manifiestos/excluidos-v0.8.0.sha256).
