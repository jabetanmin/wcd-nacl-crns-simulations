# Réplica de Sidelnik et al. (2020) con MEIGA — neutrones de 500 MeV (Sección 4.1.1)

Corridas de MEIGA que reproducen la configuración de Sidelnik et al., *Adv. Space Res.* **65** (2020) 2216:
150 000 neutrones de 500 MeV que entran horizontalmente a media altura del WCD (radio 48 cm, altura 133 cm,
Tyvek 0,12 mm + acero 0,5 mm, PMT de 10,16 × 10,16 × 5 cm en la tapa), con Geant4 10.7.p04,
`QGSP_BERT_HP_NoThermal` (sin S(α,β), como la Campaña 1) y modo óptico `eFast`.

| Medio | Corrida (fuera del repositorio) | Neutrones |
|---|---|---|
| Agua pura | `150000N-500MeV-Sidelnik-H2O-pura-sinSab-20261012-061022` (124 GB) | 150 000 |
| Agua + 2,5 % NaCl | `42649N-parcial-...-20261013` (43 GB, interrumpida) + `107351N-...-20261013-135213` (108 GB), unidas con `unir_tramos.py` | 150 000 |
| Agua + 5 % NaCl | `150000N-500MeV-Sidelnik-H2O-5NaCl-sinSab-20261014-065724` (162 GB) | 150 000 |
| Agua + 10 % NaCl | `150000N-500MeV-Sidelnik-H2O-10NaCl-sinSab-20261015-081303` (166 GB) | 150 000 |

Todos los scripts aceptan los medios `pura`, `nacl25`, `nacl5`, `nacl10` y corridas interrumpidas. La configuración
y los scripts de las corridas están en [`simulations/replica-Sidelnik-500MeV/`](../../simulations/replica-Sidelnik-500MeV/).

## Contenido

```text
Analisis-Sidelnik-500MeV.ipynb   Notebook (generado por scripts/construir_notebook.py): código de los scripts y, en la sección 8, el texto, tablas y figuras del informe
scripts/                         Procesamiento, análisis, figuras e informe
datos/                           Digitalizaciones de las Figs. 2–6 de Sidelnik (las imágenes del artículo no se versionan)
resultados/                      Resúmenes procesados (.npz, .json, .csv)
figuras/                         fig00–fig24 (png y pdf)
informe/                         Informe-Sidelnik-500MeV.pdf: informe técnico (49 páginas) con el mismo contenido que la Sec. 4.1.1 de la tesis
                                 fuente común con la tesis: seccion_4_1_1.tex + apendice_procesos.tex; construir_informe.py genera
                                 cuerpo_informe.tex y apendice_informe.tex (secciones 1–11 y Apéndice A); Figuras/, bibliografia-1.bib
                                 Informe-Sidelnik-500MeV-tecnico.pdf: notas técnicas (corridas, procedimientos, diagnósticos, reproducibilidad), generado por escribir_informe.py
```

## Uso

```bash
python3 scripts/construir_notebook.py          # regenera el notebook a partir de los scripts
jupyter notebook Analisis-Sidelnik-500MeV.ipynb
```

Sin las corridas, el notebook regenera todas las figuras y los informes a partir de `resultados/`. Para reprocesar,
indique la carpeta de las corridas en la celda de configuración o con `export CORRIDAS_SIDELNIK=/ruta/a/Corridas-Sidelnik-500MeV`.

**Informe.** El texto del informe es el de la Sec. 4.1.1 de la tesis: se edita en `informe/seccion_4_1_1.tex` (y
`informe/apendice_procesos.tex`), `scripts/construir_informe.py` genera `cuerpo_informe.tex` y `apendice_informe.tex`
con la jerarquía de títulos del informe y `latexmk -pdf Informe-Sidelnik-500MeV.tex` lo compila (biber). Para compilar
hacen falta las figuras 3 y 5 de Sidelnik et al. (2020) en `informe/Figuras/` (`espectro-gamma-ivan.png`,
`espectro-e-ivan.png`), que no se versionan por los derechos de la revista; el PDF del informe sí está incluido.
Por la misma razón, `digitalizar_fig3.py` y `digitalizar_fig5.py` necesitan las imágenes del artículo en `datos/`;
sus resultados (`datos/*_digitalizada.csv`) están en el repositorio.

No se versionan `resultados/elasticas_<medio>.npz` (vértices elásticos, ~300–400 MB por medio; se regeneran con
`elasticas_vertices.py`) ni `resultados/<medio>_fotones.npz` (destino de cada fotón óptico, 360–490 MB por medio; se
regeneran con `destino_fotones.py` desde `pasos-particulas.tsv`). Sin ellos se conservan las figuras y los `.json`
derivados (`diagnostico_<medio>.json`, `destino_fotones_medios.json`, `elasticas_resumen.json`).

## Resultados principales

- **Tabla 2 (captura).** El 25,18 % de Sidelnik corresponde a capturas en el agua divididas por todos los neutrones
  del evento (primario + cascada): MEIGA da 24.08 % (agua pura), 24.59 %, 25.19 % y 26.08 % (2.5, 5 y 10 % NaCl).
- **Fig. 6 (luz).** Con el mismo observable (fotones aceptados por la eficiencia cuántica, antes del transporte óptico)
  MEIGA reproduce la figura entre 0 y 500 fotones; la cola superior es 2–3 veces mayor por la producción de piones.
- **Figs. 3–5 (gammas y electrones).** El espectro de electrones coincide en escala absoluta (bines de 20 keV) y en forma;
  las líneas del Cl de 1,165–7,79 MeV coinciden. MEIGA produce ≈ 1,6–1,8 veces más gammas de desexcitación nuclear
  por captura en H y unas 6 veces más gammas de > 20 MeV (piones).
- **Capturas en ³⁵Cl y ¹⁶O.** Las intensidades por captura de las transiciones reales coinciden con ENSDF (13 de 15 en ³⁶Cl),
  pero en ≈ 24 % de las capturas Geant4 emite un único gamma con toda la energía de separación (8579,8 keV en ³⁶Cl,
  4143,09 keV en ¹⁷O, sin retroceso) y en el resto sortea los gammas de forma independiente: la energía por captura
  en el Cl promedia 10,2 MeV en lugar de 8,58 MeV. Esquemas de niveles en `fig18`/`fig19`.
- **Efecto del NaCl.** Captura +2.1/+4.6/+8.3 % (2.5/5/10 % NaCl; Sidelnik +6.2/+9.8/+16.2 %), τ de captura 192 → 140/109/75 µs
  (teoría 205/147/114/78 µs); las curvas de razón NaCl/agua pura de la Fig. 6 coinciden en forma (r = 0.88–0.91).
  Los piones explican solo 3–6 puntos del menor efecto con 2.5 y 5 %; el resto, el fondo de desexcitación nuclear y el
  menor aumento de captura.
- **Carga en el PMT.** Aporte de este trabajo; su escala depende del modelo óptico del Tyvek (el factor 0.94 de
  `scaleLinerRef` aporta ~6 de los 9.8 puntos de absorción por choque; incertidumbre de la escala hasta ×2.5).
