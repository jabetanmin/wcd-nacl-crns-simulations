# Flujo de neutrones sobre Bucaramanga — secciones 4.3, 4.4 y 4.5 de la tesis

Esta carpeta contiene el material de las secciones 4.3 a 4.5 del capítulo 4 (páginas impresas 222–251,
páginas 248–277 del PDF de la tesis corregida):

- **4.3** Caracterización del campo de neutrones atmosféricos sobre la superficie de Bucaramanga.
- **4.4** Aplicación del modelo Monte Carlo al flujo atmosférico de neutrones rápidos y de alta energía.
- **4.5** Aplicación del modelo Monte Carlo al flujo de neutrones emergentes de un suelo seco.

Informe de revisión: [`informe/Informe-tecnico-Flujo-Bucaramanga-Secciones-4.3-4.5.pdf`](informe/Informe-tecnico-Flujo-Bucaramanga-Secciones-4.3-4.5.pdf)

Los notebooks se copiaron **tal como están en las carpetas de trabajo**, con sus salidas incluidas.
Leen los datos crudos con rutas relativas a su carpeta original. Esos datos pesan varios GB y no se
replican aquí. Para volver a ejecutar un notebook hay que ponerlo junto a sus datos, en la carpeta de
origen indicada abajo. En `resultados/` sólo hay CSV/TXT pequeños y las figuras de espectro finales.

## Archivos de partículas (fuera del repositorio)

| Archivo | Neutrones | Qué es |
|---|---|---|
| `Flujo-diferencial-sobre-Bucaramanga/flujo_neutrones_completo_Bga.shw` (= `all_bga_neutron_35.shw`) | 1 891 124 | Campo total en superficie (ARTI + suelo), ambos sentidos, p en MeV/c |
| `Flujo-diferencial-sobre-Bucaramanga/flujo_neutrons_rapidos_Bga.shw` (= `S3_bga_003600_neutrons_MeV.shw`) | 317 537 | Salida ARTI de **3600 s**, sólo n descendentes con E ≥ 20 MeV |
| `Flujo-diferencial-sobre-Bucaramanga/flujo_neutrones_suelo_seco_Bga.shw` (= `filtered_neutrons.shw`) | 207 969 | Subconjunto ascendente (pz>0) del archivo completo, 10 meV–10 eV |

## Mapa sección → figura → notebook

Rutas de origen relativas a `Documetos-Jaime-Betancourt/`.

### 4.3 — `notebooks/4.3_campo-atmosferico/`

| Contenido | Notebook | Origen |
|---|---|---|
| Fig. 4.52, Ecs. 4.40–4.63 (también Figs. 4.53 y 4.61) | `Flujos-neutrones-Bga.ipynb` (celda 6 = versión final) | `Flujo-diferencial-sobre-Bucaramanga/` |
| Versiones previas del espectro (12 h, térmico) | `Flujo-neutrones-termicos.ipynb` | `Flujo-sobre-Bucaramnga/Flujo-termico-suelo-seco/` |
| Reanálisis de verificación (grupos de energía, sentidos, ajuste maxwelliano, comparación con ARTI S3) | `analisis_flujo_superficie_bga.ipynb` / `.py` | `Flujo-sobre-Bucaramnga/Flujo-completo-Bga/Analisis-flujo-superficie-Bga/` |

> `resultados/4.3/resumen_flujo_superficie_bga.txt` y los CSV que lo acompañan vienen del reanálisis.
> Están normalizados con **t = 3600 s**, un supuesto de trabajo y no un valor confirmado. La tesis
> usa 12 h. Véase el informe, §4.3.1.

### 4.4 — `notebooks/4.4_flujo-rapido-alta-energia/`

| Subsección / figura | Notebook | Origen |
|---|---|---|
| 4.4.1–4.4.2, Fig. 4.53 | `Flujos-neutrones-Bga.ipynb` (en 4.3), `Analisis-Flujo.ipynb`, `generar_espectros_neutrones_bucaramanga.py`, `flujo_neutrones_energia_MeV_verificacion.py` | `Flujo-sobre-Bucaramnga/Flujo-completo-Bga/Flujo-Arti-BGA/` |
| 4.4.5, Fig. 4.54a (espectro γ) | `Analisis-gamma.ipynb` | `.../Flujo-completo-Bga/Flujo-Arti-BGA/` (datos en `expectro-gamma/`) |
| 4.4.5, Fig. 4.55 (diferencias γ) | `Analisis-gamma-AP-Flujo-completo.ipynb` (celda 20) | `Imagenes-radiacion-EM/imagenes-resultados/Gammas/1000000meV/espectro-gama-completo/` |
| 4.4.5, Fig. 4.54b (electrones) | `Analisis-Espectro-Electrones.ipynb` | `.../Flujo-completo-Bga/Espectr-e/` |
| 4.4.6, Fig. 4.56 y Apéndice F | `distribucion-espacial/*.ipynb` (4 medios) | `.../Flujo-completo-Bga/Distribucion-espacial-capturas/<medio>/` |
| 4.4.7, Fig. 4.57 | `Histogramas_dispersiones_cita_flujo_completo_Bga.ipynb` (celdas 8–11 y 19–21) | `.../Flujo-completo-Bga/Analisis-neutrones/Histogramas_cita_n_tremicos_Bga.ipynb` |
| 4.4.8, Fig. 4.59 | `Distancias-capturas-neutrones.ipynb` | `.../Flujo-completo-Bga/Distancia-captura/` |
| Fig. 4.58 (ξ, flujo completo) y Fig. 4.60 (fotoelectrones) | **no localizados** | — |

### 4.5 — `notebooks/4.5_suelo-seco/`

| Subsección / figura | Notebook | Origen |
|---|---|---|
| 4.5.1–4.5.6, Fig. 4.61 | `Flujos-neutrones-Bga.ipynb` (en 4.3) | `Flujo-diferencial-sobre-Bucaramanga/` |
| 4.5.7, Apéndice G | `Histogramas-coordenada.ipynb` | `Flujo-sobre-Bucaramnga/Flujo-termico-suelo-seco/Distribucion-espacial-neutrones/` |
| 4.5.8, Figs. 4.62–4.63 | `Histogramas_dispersiones_cita_suelo_seco_Bga.ipynb` | `Neutrones-termicos/Neutrones-termico-Bga/Distribuciones-cita/Histogramas_cita_n_tremicos_Bga.ipynb` |
| 4.5.9, Fig. 4.64 | `Comparacion_Histogramas_Carga_Termicos.ipynb` | `.../Flujo-termico-suelo-seco/Histograma-carga/` |
| Tabla 4.23 (conteo y detectados por intervalo) | `Medicion-humedad.ipynb` (celda 2), `contar_neutrones_y_detectados.py` | `.../Flujo-termico-suelo-seco/` |

> La sección 4.6 (respuesta de referencia y curva de calibración, basada en la Tabla 4.23) tiene su propio informe en
> [`../caracterizacion-respuesta-referencia-wcd_seccion-4.6/`](../caracterizacion-respuesta-referencia-wcd_seccion-4.6/).

## Advertencias (detalle en el informe)

1. **Normalización del conjunto de 4.4.** `flujo_neutrons_rapidos_Bga.shw` es la salida ARTI de 3600 s,
   pero en la tesis está normalizada a 12 h. Con 3600 s, Φ = 8.82×10⁻³ n cm⁻² s⁻¹ y no 7.35×10⁻⁴.
   Además, el conjunto empieza en **20 MeV**, no en 1 MeV.
2. **Las 12 h del archivo completo no están confirmadas.** Sus neutrones descendentes con E > 20 MeV
   son sólo entre 2.0 y 4.3 veces los del archivo ARTI de 1 h, cuando con 12 h se esperaría un factor ≈ 12.
3. `Histogramas_dispersiones_cita_flujo_completo_Bga.ipynb`, celda 18: la figura
   `numero-dispersion-elastica-neutron-termicos-NORMALIZADO-Bga.*` se hizo con datos del flujo completo
   normalizados con las capturas del suelo seco (ΣP ≈ 2.9). **No es la Fig. 4.62 de la tesis** y no debe
   reutilizarse.
