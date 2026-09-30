# Espectro de la fuente de ²⁴¹AmBe usada en la simulación

Construcción del espectro de energía de los neutrones de la fuente de ²⁴¹AmBe que se inyecta en
Geant4 para simular el prototipo, y su comparación con el espectro de referencia (figura
`Espectro-AmBe-Geant4-vs-IAEA` de la Sección 4.1.2).

## Cadena de construcción (`notebooks/simulacion-241-AmBe.ipynb`, celdas 1–9)

| Paso | Entrada | Salida |
|---|---|---|
| Espectro digitalizado de la literatura con WebPlotDigitizer | figura publicada | `datos/Default-Dataset-2.csv`, `datos/espectro-neutrones-Am-Be-241.txt` (coma decimal) |
| Limpieza y conversión a función de dos columnas | `datos/Datos-originales-espectro-AmBe-241.txt` | `datos/Funcion-espectro-AmBe-241-final.txt` |
| Conversión a frecuencias y redondeo | `espectro-neutrones-Am-Be-241.txt` | `datos/espectro_procesado_frecuencia_redondeado.txt` |
| Expansión a una energía por neutrón | frecuencias redondeadas | `datos/Espectro-energia-neutrones-AmBe-241.txt.gz` (1 637 458 energías en MeV) |

El resto de ese notebook (celdas 10 en adelante) contiene cálculos auxiliares que no forman parte de
la construcción del espectro: conversión energía–momento con entrada interactiva (`input()`),
absorción en acero SS304 y conteos de procesos frente a la energía copiados como listas.

## Comparación con la referencia (`notebooks/Espectro-energia-AmBe-241.ipynb`)

Histograma normalizado por área de las energías generadas, suavizado con un filtro gaussiano
(σ = 1.5 intervalos), frente al espectro de referencia `datos/AmBe_IAEA.txt`. Produce
`figuras/Espectro-AmBe-Geant4-vs-IAEA.{pdf,png}`. También se incluye `datos/AmBe_ISO8529_spectrum.txt`
(espectro de referencia ISO 8529 tabulado, flujo relativo normalizado).

Para ejecutarlo, descomprimir primero la lista de energías:

```bash
gunzip -k datos/Espectro-energia-neutrones-AmBe-241.txt.gz
```

y colocar los archivos de `datos/` junto al notebook (usa rutas relativas).

## Pendiente de trazabilidad

- Referencia bibliográfica exacta de la figura digitalizada y del espectro `AmBe_IAEA.txt`
  (en la carpeta de trabajo hay un informe IAEA-NDS-0127, pero no se ha confirmado que sea la fuente).
