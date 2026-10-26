# Corridas MEIGA con la fuente de ²⁴¹Am-Be inyectada por la tapa

Análisis de las tres corridas recuperadas del disco TOSHIBA (agua pura, 2.5 % y 10 % NaCl; 1 637 458 neutrones cada
una, inyección vertical por la tapa con la fuente original). Informe:
[`informe/Informe-corridas-AmBe.pdf`](informe/Informe-corridas-AmBe.pdf) (escrito por `scripts/escribir_informe.py`);
cuaderno: `Analisis-corridas-AmBe.ipynb`.

## Resultados principales

- Con 10 % NaCl, por neutrón incidente, la eficiencia de señal (Q ≥ 1 p.e.) sube de 36.4 % a 49.4 % y la carga
  media de 3.54 a 11.16 p.e.; el ³⁵Cl recibe el 67 % de las capturas.
- Cada evento se repondera por su energía inicial para pasar del espectro sesgado al ISO 8529.
- Escalado al montaje blindado (haz con estas corridas; halo y fondo con la Campaña 1): 88 287, 107 258 y 136 065
  eventos con señal en 5 min. Vale para la inyección por la tapa; el montaje real irradia por el costado (ver
  [`../Analisis-montaje-MEIGA/`](../Analisis-montaje-MEIGA/)).

## Datos del experimento

`resultados/experimento_cargas.npz` (ventana del disparo) y `resultados/cargas_robustas.npz` contienen la carga de
cada pulso de las seis tomas del prototipo, extraída de los datos crudos: la primera con `procesar_experimento.py` (que también escribe la duración de cada toma en
`experimento_tomas.json`) y la segunda con `histogramas_sin_fondo.py` (`carga_robusta.awk`). Los análisis
[`../Analisis-montaje-MEIGA/`](../Analisis-montaje-MEIGA/) y [`../Analisis-PMT-bajo-horizontal/`](../Analisis-PMT-bajo-horizontal/)
los usan.

## Rutas de los datos

Los scripts leen las corridas y los datos crudos de los discos externos: `ADATA` y `TOSHIBA` (por defecto
`/media/$USER/ADATA HD330` y `/media/$USER/TOSHIBA EXT`). La ruta del repositorio la toman de `REPO_TESIS` y el flujo
térmico de `FLUJO_TERMICO_SHW`. Las tablas por evento de las corridas (`capturas_*`, `eventos_*`, `gammas_captura_*`,
`residuos_*`, `inelasticos_*`, `carga_*.npz`, `tiempos_*.npz`) no se versionan. Sus sha256 están en
[`data/manifiestos/excluidos-v0.8.0.sha256`](../../../data/manifiestos/excluidos-v0.8.0.sha256).
