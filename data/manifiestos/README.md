# Manifiestos de datos fuera de git

| Archivo | Contenido |
|---|---|
| `corridas-v0.8.0.tsv` | una línea por corrida MEIGA de la v0.8.0: número de archivos, bytes y md5 del listado ordenado (tamaño y ruta). Sirve para verificar una copia o el depósito en Zenodo con [`tools/manifiesto.sh`](../../tools/manifiesto.sh) |
| `flujos-regenerables.sha256` | sha256 de los archivos de entrada grandes que no se versionan, con el comando que los regenera byte a byte |
| `excluidos-v0.8.0.sha256` | sha256, tamaño y motivo de cada archivo de las carpetas de trabajo que se dejó fuera de git (datos de más de 5 MB, material de terceros) |
