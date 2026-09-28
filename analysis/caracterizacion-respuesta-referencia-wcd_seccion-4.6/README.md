# Respuesta de referencia del WCD al flujo emergente de un suelo seco — sección 4.6 de la tesis

La carpeta cubre la sección 4.6 del capítulo 4 (páginas impresas 253–263): la caracterización de la respuesta de
referencia del WCD, el apartado 4.6.0.1 (construcción de una curva de calibración para distintos contenidos de
humedad) y la subsección 4.6.1 (alcance científico e incertidumbres).

Informe corto: [`informe/Informe-tecnico-Respuesta-Referencia-WCD-Suelo-Seco-Seccion-4.6.pdf`](informe/Informe-tecnico-Respuesta-Referencia-WCD-Suelo-Seco-Seccion-4.6.pdf)

**Datos existentes:** sólo la **Tabla 4.23**, es decir, N_inc(E) del espectro seco (207 969 n, 12 h, 1 m²) y
ε_j(E) en 4 medios. El resto de 4.6.0.1 es metodología propuesta: humedades θ_v > 0, R_j(θ_v), ajuste de la
función de calibración, sensibilidad S_j y calibración de campo. Nada de eso está simulado.

| Medio | N_0,j (detectados, suelo seco) | ε efectiva | Δ vs agua |
|---|---|---|---|
| Agua pura | 32 931 | 15.8 % | — |
| NaCl 2.5 % | 43 073 | 20.7 % | +30.8 % |
| NaCl 5 % | 49 887 | 24.0 % | +51.5 % |
| NaCl 10 % | 60 665 | 29.2 % | +84.2 % |

## Contenido

- `informe/`: informe LaTeX + PDF y la figura `tabla_4_23_eficiencia_y_conteos.{png,pdf}`.
- `scripts/verificar_tabla_4_23.py`: reconstruye la Tabla 4.23 a partir de sus propios valores. Verifica los
  totales y Δ% y calcula ε efectiva, σ Poisson, fracción térmica y ε(10 eV)/ε(10 meV). No lee datos de simulación.
- `resultados/`: `tabla_4_23_reconstruida.csv` y `resumen_respuesta_referencia_seca.csv`.

El notebook original que genera la Tabla 4.23 es `Medicion-humedad.ipynb` (celda 2). Está en
[`../flujo-bucaramanga_secciones-4.3-4.5/notebooks/4.5_suelo-seco/`](../flujo-bucaramanga_secciones-4.3-4.5/notebooks/4.5_suelo-seco/).

## Puntos a corregir en la tesis (detalle en el informe, §3)

1. El texto dice que N_inc,0 = 207 969 está "entre 1 meV y 1 keV". El espectro cubre **10 meV–10 eV**; lo que
   llega a 1 keV es la tabla de eficiencias.
2. Falta de respuesta: con este espectro faltan los neutrones de 10 eV–1 keV, no sólo los de más de 1 keV.
3. Las ε provienen de haces monoenergéticos a incidencia normal. N_0,j es una estimación por convolución, no una
   simulación directa del espectro en el WCD.
4. "4.6.0.1" es una `\subsubsection` sin subsección padre. Conviene renumerar.
