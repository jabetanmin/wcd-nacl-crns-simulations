# Transporte óptico y conversión de la luz Cherenkov en fotoelectrones (Sec. 4.2.5)

Kit y resultados de la Sección 4.2.5 de la tesis (Tablas 4.26 y 4.27). Usa las corridas del barrido de
S(α,β) ([`simulations/barrido-SalphaBeta_1meV-1keV/`](../../simulations/barrido-SalphaBeta_1meV-1keV/)),
en las que `G4WCDSteppingAction` registra todos los pasos de los fotones ópticos en
`Datos-simulacion/pasos-particulas.tsv`.

| Archivo | Función |
|---|---|
| `destino_fotones.sh` | Clasifica el último paso de cada fotón transportado: detectado (Pyrex del PMT), absorbido en el agua o absorbido en el Tyvek de la pared, la tapa o el fondo; recorrido medio, llegadas a fronteras y cara del PMT por la que entran los detectados. |
| `qe_efectiva.sh`, `diagnostico_cherenkov.sh`, `diagnostico_madres.sh` | Diagnósticos de la eficiencia cuántica efectiva y del origen del factor 0.70 (`fPMTCollectionEfficiency`). |
| `destino_fotones_1keV_4medios.tsv` | Tabla 4.27: destino de los fotones a 1 keV con S(α,β) en los cuatro medios (agua pura: 41 911 fotones; 2.5 %: 117 045; 5 %: 162 088; 10 %: 214 087). |
| `qe_recoleccion.tsv` | Factores ⟨QE⟩ y ε_opt por medio (Tabla 4.26). |

Resultado: f_pe = ⟨QE⟩ · ε_col · ε_opt ≈ 0.154 · 0.70 · 0.12 ≈ 1.3 % en los cuatro medios; el Tyvek
absorbe ≈ 72 % de los fotones transportados. Los valores absolutos corresponden a la posición del PMT
de estas corridas (cara plana a 86.5 cm del fondo, unos 46 cm bajo la superficie; véase
[`docs/GEOMETRIA_Y_FISICA_CAMPANAS.md`](../../docs/GEOMETRIA_Y_FISICA_CAMPANAS.md)).

Uso dentro del contenedor:
`./destino_fotones.sh <ruta a pasos-particulas.tsv> [salida.tsv]`
