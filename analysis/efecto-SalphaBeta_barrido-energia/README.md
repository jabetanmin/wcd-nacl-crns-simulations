# Efecto de S(α,β) en el WCD: transporte de neutrones y respuesta electromagnética

Análisis del barrido en energía de 1 meV a 1 keV con dos físicas (QGSP_BERT_HP con y sin
S(α,β)), agua pura, geometría de la Campaña 2 y 10 000 neutrones por punto. Los datos los produce el
kit [`simulations/barrido-SalphaBeta_1meV-1keV/`](../../simulations/barrido-SalphaBeta_1meV-1keV/).

**Informe técnico completo:**
[`informe/Informe-tecnico-Efecto-SalphaBeta-Barrido-Energia.pdf`](informe/Informe-tecnico-Efecto-SalphaBeta-Barrido-Energia.pdf)
(21 páginas).

## Resultados principales

- El efecto de S(α,β) sobre la captura en el agua **cambia de signo en ≈ 0.34 eV**: la reduce hasta
  8.6 puntos por debajo (25 meV: 19.70 % frente a 28.31 %) y la aumenta hasta 8.4 puntos por encima
  (1 keV: 41.90 % frente a 33.54 %).
- Mecanismo: S(α,β) acorta la difusión térmica. Las capturas son más superficiales, la vida media
  térmica efectiva sube de 140.7 ± 1.5 a 161.8 ± 1.5 µs y la fuga térmica baja ≈ 40 %.
- El máximo de captura entre 0.3 y 10 eV de la Campaña 1 es propio del gas libre; con S(α,β) la
  captura crece de forma monótona hasta ≈ 42 %.
- Eficiencia de detección (Q ≥ 1 pe): 8–19 % por neutrón incidente; −34 % a 25 meV y +21 % a 1 keV
  con S(α,β); cruce en ≈ 0.7 eV.
- Cuellos de botella geométricos: solo el 54–64 % de los γ de 2.2 MeV interactúa en el agua y solo el
  1.30 % de los fotones Cherenkov produce un fotoelectrón.

## Figuras

| Figura | Archivo |
|---|---|
| Captura en el agua y ⟨N⟩ frente a la energía | `fig_captura_N_vs_energia` |
| Destinos de los neutrones y profundidad media | `fig_destinos_vs_energia` |
| Distribución de la profundidad de captura | `fig_profundidad_captura` |
| Tiempo, vida media térmica y energía de captura | `fig_tiempo_energia_captura` |
| Eficiencia de detección | `fig_eficiencia_deteccion` |
| Contención de los γ de 2.2 MeV | `fig_contencion_gamma` |
| Procesos γ y origen de la luz | `fig_procesos_luz` |
| Electrones Compton y umbral Cherenkov | `fig_electrones_cherenkov` |
| Luz creada, probabilidad de señal y carga | `fig_luz_carga` |

Cada figura existe en PDF (vectorial, para la tesis) y PNG.

## Tablas de resultados

| Archivo | Contenido |
|---|---|
| `balance_destinos.tsv` | Destino de los neutrones por energía y física (conteos) |
| `resumen_barrido.tsv` | Porcentajes de destino, ⟨N⟩ y profundidad media |
| `resumen_capturas.tsv` | Profundidad, tiempo, vida media y energía de captura |
| `resumen_em.tsv` | Eficiencia de detección y contención de los γ |
| `resumen_em2.tsv` | Procesos γ, origen de la luz, fotones y carga |
| `em_procesos.tsv` | Interacciones γ por proceso y material, por corrida |

## Reproducción

Los scripts leen la carpeta de datos del barrido (`<carpeta>`, fuera del repositorio):

```bash
./balance_destinos.sh <carpeta> > balance_destinos.tsv
./capturas_detalle.sh <carpeta> > capturas_detalle.tsv
./em_detalle.sh <carpeta>        # em_eventos.tsv, em_gammas.tsv
./em_cadena.sh <carpeta>         # em_procesos.tsv, em_electrones.tsv, em_luz.tsv
python3 figuras_barrido.py && python3 figuras_capturas.py
python3 figuras_em.py && python3 figuras_em2.py
cd informe && python3 generar_tablas.py && latexmk -pdf Informe-tecnico-Efecto-SalphaBeta-Barrido-Energia.tex
```

Todo el proceso tarda alrededor de un minuto. Los archivos intermedios por evento
(`capturas_detalle.tsv`, `em_eventos.tsv`, `em_gammas.tsv`, `em_electrones.tsv`, `em_luz.tsv`;
85 MB en total) no se versionan porque se regeneran con los scripts anteriores.

Las tablas del informe se generan desde los TSV con `informe/generar_tablas.py`, de modo que no hay
cifras copiadas a mano.
