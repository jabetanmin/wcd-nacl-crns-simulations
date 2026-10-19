#!/usr/bin/env python3
"""Genera informe/Informe-Sidelnik-500MeV.tex a partir de resultados/resumen.json (medios disponibles)."""
import json, os
import numpy as np

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
S = json.load(open(os.path.join(R, "resultados", "resumen.json")))
CORR10 = os.environ.get("CORRIDA_NACL10", "150000N-500MeV-Sidelnik-H2O-10NaCl-sinSab-20261015-081303")
M = [m for m in ["pura", "nacl25", "nacl5", "nacl10"] if m in S]
ET = {"pura": "Agua pura", "nacl25": "2,5\\,\\% NaCl", "nacl5": "5\\,\\% NaCl", "nacl10": "10\\,\\% NaCl"}
SID = {"pura": (25.18, 8.4), "nacl25": (26.73, 8.0), "nacl5": (27.65, 7.7), "nacl10": (29.26, 7.3)}


def f(x, d=2):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", "\\,")


def pct(v, d=1):
    return f(100 * v, d) + "\\,\\%"


def row(c):
    return " & ".join(c) + " \\\\\n"


def tabla(filas, cap, cols_extra=None):
    t = "\\begin{table}[H]\\centering\\small\\begin{tabular}{l" + "c" * len(M) + "}\\toprule\n & " + " & ".join(ET[m] for m in M) + " \\\\\\midrule\n"
    for nom, fn in filas:
        t += row([nom] + [fn(m) for m in M])
    return t + "\\bottomrule\\end{tabular}\\caption{" + cap + "}\\end{table}\n"


def fig(n, cap):
    return f"\\begin{{figure}}[H]\\centering\\includegraphics[width=\\linewidth]{{../figuras/{n}.pdf}}\\caption{{{cap}}}\\end{{figure}}\n"


p = S["pura"] if "pura" in S else S[M[0]]
BLOQ = []; _cur = ["pre", 0]


def ir(sec, orden=0):
    """Los bloques siguientes van a la seccion 'sec' de la tesis (Sec. 4.1.1), en el orden 'orden'."""
    _cur[0], _cur[1] = sec, orden


def w(t):
    BLOQ.append((_cur[0], _cur[1], len(BLOQ), t))
w(r"""\documentclass[11pt,a4paper]{article}
\usepackage[spanish,es-noshorthands,es-tabla]{babel}
\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[margin=2.2cm]{geometry}\usepackage{graphicx}\usepackage{booktabs}\usepackage{amsmath}\usepackage{float}\usepackage{xcolor}
\usepackage[colorlinks=true,linkcolor=blue!50!black,urlcolor=blue!50!black]{hyperref}
\usepackage{caption}\captionsetup{font=small,labelfont=bf}\usepackage{pdflscape}\usepackage{longtable}\usepackage{colortbl}
\newcommand{\aviso}[1]{\begin{center}\fcolorbox{orange!70!black}{orange!6}{\parbox{0.93\linewidth}{\small #1}}\end{center}}
\sloppy
\title{Réplica de Sidelnik et al. (2020) en MEIGA \\ \large Neutrones de 500\,MeV horizontales en el WCD de acero: """ + ", ".join(ET[m] for m in M).replace("\\,\\%", "\\,\\%") + r"""}
\author{Informe técnico preparado para Jaime Betancourt}
\date{13 de octubre de 2026}
\begin{document}\maketitle
\begin{abstract}
Se analizan las corridas de MEIGA preparadas para la Sec.~4.1.1 de la tesis: 150\,000 neutrones de 500\,MeV que entran horizontalmente,
a media altura, a un WCD de 96\,cm $\times$ 133\,cm con Tyvek de 0,12\,mm, acero de 0,5\,mm y el PMT en la tapa, sin dispersión térmica $S(\alpha,\beta)$.
Se comparan con la Tabla~2 y las Figs.~2--6 de Sidelnik et al., \textit{Adv. Space Res.} 65 (2020) 2216.
Este informe se regenera automáticamente cuando se agregan los demás medios.
\end{abstract}
\tableofcontents
""")
ir("conf")
w(r"""\section{Parámetros de la simulación}
\begin{table}[H]\centering\small\begin{tabular}{ll}\toprule
Parámetro & Valor en MEIGA (igual que en Sidelnik et al.\ 2020) \\\midrule
Tanque & cilindro de agua de 48\,cm de radio y 133\,cm de altura \\
Paredes & Tyvek de 0,12\,mm y acero inoxidable de 0,5\,mm (lados, tapa y fondo) \\
Fotomultiplicador & 10,16 $\times$ 10,16 $\times$ 5\,cm, en la tapa \\
Medios & agua pura; agua + 2,5, 5 y 10\,\% NaCl (Ec.~3.12; densidad y $n$ de la Tabla~3.6) \\
Fuente & neutrones de 500\,MeV, horizontales, a media altura (66,562\,cm), 1\,cm fuera de la pared \\
Neutrones por medio & 150\,000 \\
Física & Geant4 10.7.p04, \texttt{QGSP\_BERT\_HP\_NoThermal} (sin $S(\alpha,\beta)$), G4NDL\,4.6 \\
Óptica & modo \texttt{eFast}: eficiencia cuántica del R5912 aplicada al crearse cada fotón \\\bottomrule
\end{tabular}\caption{Parámetros de las corridas (equivalente a la Tabla~4.1 de la tesis).}\end{table}
""")
if os.path.exists(os.path.join(R, "figuras", "fig00_esquema_detector.pdf")):
    EVJ = json.load(open(os.path.join(R, "resultados", "evento_ejemplo_nacl25.json")))
    w(r"""\begin{figure}[H]\centering\includegraphics[width=0.92\linewidth]{../figuras/fig00_esquema_detector.pdf}\caption{Esquema del WCD simulado (corte $y = 0$, a escala; el espesor de las paredes está exagerado) con un evento real de la corrida de agua + 2,5\,\% NaCl (\texttt{run\_id} """ + str(EVJ["run"]) + r"""):
el neutrón de 500\,MeV entra a media altura y tiene una interacción inelástica; los neutrones secundarios se moderan y dos de ellos se capturan, uno en $^1$H (gamma de 2224\,keV, azul) y otro en $^{35}$Cl,
con la cascada 6111 + 1951 + 517\,keV que conserva la energía de separación (8,579\,MeV; rojo; véase el esquema de niveles de la Sec.~\ref{sec:esquemas}). Los electrones de los gammas (violeta) recorren pocos milímetros y emiten la luz Cherenkov.
Equivalente a la Fig.~1 de Sidelnik et al.\ (2020), pero con la geometría y las trayectorias de MEIGA. La versión de agua pura (captura en H) está en \texttt{figuras/fig00\_esquema\_detector\_pura}.}\label{fig:esquema}\end{figure}
""")
w(r"""\section{Corridas analizadas}
Corrida de agua pura: \texttt{Corridas-Sidelnik-500MeV/150000N-500MeV-Sidelnik-H2O-pura-sinSab-20261012-061022} (disco ADATA, 124\,GB, 20,2\,h de cómputo).
Cada neutrón primario es una corrida de MEIGA (\texttt{run\_id} 0--149\,999); la carga de \texttt{Carga-total.txt} coincide evento por evento con \texttt{output.json.gz}.
Se leyeron todos los archivos salvo \texttt{pasos-particulas.tsv} (78\,GB), que no se necesita para estos observables.
""" + ("" if "nacl25" not in S else r"""\par Corrida de agua + 2,5\,\% NaCl, en dos tramos: \texttt{42649N-parcial-500MeV-Sidelnik-H2O-2.5NaCl-sinSab-20261013} (43\,GB), interrumpida al detenerse el contenedor (se usan los 42\,649 neutrones terminados y se descartan las filas del incompleto),
y su complemento \texttt{107351N-500MeV-Sidelnik-H2O-2.5NaCl-sinSab-20261013-135213} (108\,GB, 16,6\,h), lanzado con otra semilla (MEIGA la toma de la hora). Los dos tramos se unen en 150\,000 neutrones (\texttt{unir\_tramos.py}: los números de evento del complemento se desplazan en 42\,649 y los histogramas se suman);
sus resultados son compatibles dentro del error (neutrones con al menos una captura: $43{,}42\pm0{,}24$ y $43{,}25\pm0{,}15$\,\%; carga media: $11{,}45\pm0{,}15$ y $11{,}35\pm0{,}09$\,p.e.).""") + ("" if "nacl5" not in S else r"""
\par Corrida de agua + 5\,\% NaCl: \texttt{150000N-500MeV-Sidelnik-H2O-5NaCl-sinSab-20261014-065724} (162\,GB, 24,4\,h de cómputo).""") + ("" if "nacl10" not in S else r"""
\par Corrida de agua + 10\,\% NaCl: \texttt{""" + CORR10 + r"""} (166\,GB, 26,8\,h de cómputo).""") + r"""

""")
ir("captura", 1)
w(r"""\section{Captura de neutrones (Tabla 2 de Sidelnik)}
""")
FC = {m_: json.load(open(os.path.join(R, "resultados", f"fraccion_captura_{m_}.json"))) for m_ in M
      if os.path.exists(os.path.join(R, "resultados", f"fraccion_captura_{m_}.json"))}
w(tabla([("Capturas en el agua por neutrón primario", lambda m: f(S[m]["capturas_por_neutron_agua"], 3)),
         ("Neutrones en el evento por primario (primario + cascada)", lambda m: f(FC[m]["neutrones_por_primario"], 2) if m in FC else "--"),
         ("\\textbf{Capturas en el agua / todos los neutrones}", lambda m: "\\textbf{" + pct(FC[m]["P_b_capturas_sobre_todos_los_neutrones"], 2) + "}" if m in FC else "--"),
         ("Neutrones con $\\geq 1$ captura en el agua", lambda m: pct(S[m]["P_al_menos_1_captura_agua"][0], 2)),
         ("Primario de 500\\,MeV capturado (la misma traza)", lambda m: pct(S[m]["P_primario_capturado"][0], 2)),
         ("\\textit{Sidelnik: probabilidad de captura}", lambda m: f"\\textit{{{f(SID[m][0], 2)}\\,\\%}}"),
         ("Capturas fuera del agua (acero, Tyvek, aire)", lambda m: f(S[m]["capturas_total"] - S[m]["capturas_en_agua"], 0)),
         ("Capturas en H", lambda m: pct(S[m]["capturas_agua_por_nucleo"].get("H", [0, 0])[1], 2)),
         ("Capturas en $^{35}$Cl", lambda m: pct(S[m]["capturas_agua_por_nucleo"].get("Cl35", [0, 0])[1], 2)),
         ("Tiempo de captura $\\tau$ [µs]", lambda m: f(S[m]["tau_captura_us"], 0)),
         ("Energía de captura, mediana [meV]", lambda m: f(S[m]["E_captura_mediana_meV"], 1))],
        "Captura de neutrones en el volumen activo."))
w(r"""\aviso{Qué mide el 25,18\,\% de Sidelnik. El artículo lo describe como ``la fracción de capturas de neutrones dentro del volumen activo'' sin decir sobre qué total.
Las tres definiciones posibles dan, en agua pura:
(i) capturas por neutrón primario: """ + f(p["capturas_por_neutron_agua"], 3) + r""" (un mismo primario de 500\,MeV produce en promedio """ + (f(FC["pura"]["neutrones_por_primario"], 1) if "pura" in FC else "3,4") + r""" neutrones y varios se capturan);
(ii) captura de la traza primaria: """ + pct(p["P_primario_capturado"][0], 2) + r""", porque en Geant4 el neutrón de 500\,MeV desaparece casi siempre en su primera interacción inelástica y los neutrones que salen de ella son trazas nuevas; no es comparable con el artículo;
(iii) capturas divididas por todos los neutrones del evento (primario + cascada): """ + (pct(FC["pura"]["P_b_capturas_sobre_todos_los_neutrones"], 2) if "pura" in FC else "--") + r""",
que coincide con el 25,18\,\% de Sidelnik dentro de 1\,punto. Esta es la interpretación adoptada: de cada cuatro neutrones que existen en el tanque, uno termina capturado en el agua; los demás escapan o se pierden en interacciones inelásticas.""" +
  ("" if "nacl25" not in FC else r""" Con 2,5\,\% NaCl la fracción sube a """ + pct(FC["nacl25"]["P_b_capturas_sobre_todos_los_neutrones"], 2) + r""" (""" + f"{100 * (FC['nacl25']['P_b_capturas_sobre_todos_los_neutrones'] / FC['pura']['P_b_capturas_sobre_todos_los_neutrones'] - 1):+.1f}".replace(".", ",") + r"""\,\% relativo; Sidelnik: 26,73\,\%, +6,2\,\%).""") + r"""}

""")
ir("captura", 2)
w(r"""\section{Distancia de máxima absorción (Fig. 2 de Sidelnik)}
""")
w(tabla([("Borde de entrada $\\to$ captura, a lo largo del haz: máximo [cm]", lambda m: f(S[m]["distancia_max_absorcion_cm"], 1)),
         ("Vértice del neutrón capturado $\\to$ captura: máximo [cm]", lambda m: f(S[m].get("d_vertice_max_cm", float("nan")), 1)),
         ("Inelástica del primario $\\to$ captura: máximo [cm]", lambda m: f(S[m].get("d_inel_primario_max_cm", float("nan")), 1)),
         ("\\textit{Sidelnik: distancia de máxima absorción [cm]}", lambda m: f"\\textit{{{f(SID[m][1], 1)}}}")],
        "Distancia de máxima absorción con tres definiciones (máximo del histograma suavizado de 0,5\\,cm)."))
w(r"""Medida a lo largo del haz desde la cara de entrada, la distribución de capturas de MEIGA es una joroba ancha con máximo cerca del centro del tanque
(""" + f(p["distancia_max_absorcion_cm"], 1) + r"""\,cm): el primario de 500\,MeV hace su primera inelástica en promedio a """ + f(p["profundidad_inelastica_primario_media_cm"], 0) + r"""\,cm de profundidad,
y los neutrones de la cascada se capturan en todo el volumen. La forma de la Fig.~2 de Sidelnik (máximo cercano y cola larga hasta $\sim$96\,cm) sí aparece
si la distancia se mide desde el punto donde nace el neutrón capturado (máximo a """ + f(p.get("d_vertice_max_cm", 0), 1) + r"""\,cm) o desde la inelástica del primario
(""" + f(p.get("d_inel_primario_max_cm", 0), 1) + r"""\,cm). Esto sugiere que la ``distancia desde el borde'' de Sidelnik describe en realidad la escala de moderación.
La curva de agua pura de Sidelnik se digitalizó de la figura del artículo; solo se recuperan los 43 puntos rojos visibles (en la cola los tapan los de las otras curvas).
""")
w(fig("fig01_distancia_captura", "Izquierda: capturas en función de la distancia a lo largo del haz desde la cara de entrada. Derecha: tres definiciones de distancia, normalizadas, frente a la curva de agua pura digitalizada de Sidelnik (puntos)."))

ir("gamma", 1)
w(r"""\section{Gammas creados en el agua (Figs. 3 y 4 de Sidelnik)}
""")
w(tabla([("Gammas creados en el agua por neutrón", lambda m: f(S[m]["gammas_creados_agua_por_neutron"], 2)),
         ("\\quad de inelásticas de neutrones", lambda m: f(S[m]["gammas_creados_por_proceso"].get("neutronInelastic", 0), 2)),
         ("\\quad de captura", lambda m: f(S[m]["gammas_creados_por_proceso"].get("nCapture", 0), 2)),
         ("\\quad bremsstrahlung / aniquilación", lambda m: f(S[m]["gammas_creados_por_proceso"].get("eBrem", 0), 2) + " / " + f(S[m]["gammas_creados_por_proceso"].get("annihil", 0), 2)),
         ("Energía gamma de captura por neutrón [MeV]", lambda m: f(S[m]["E_gamma_captura_por_neutron_MeV"], 3)),
         ("e$^\\pm$ creados por gammas por neutrón", lambda m: f(S[m]["e_de_gammas_por_neutron"], 1)),
         ("\\quad Compton / fotoeléctrico", lambda m: f(S[m]["e_de_gammas_por_proceso"].get("compt|e-", 0), 1) + " / " + f(S[m]["e_de_gammas_por_proceso"].get("phot|e-", 0), 2)),
         ("\\quad fracción sobre umbral Cherenkov (0,264\\,MeV)", lambda m: pct(S[m]["e_de_gammas_frac_sobre_umbral"], 1))],
        "Gammas y electrones creados dentro del agua."))
w(fig("fig02_espectro_gamma", "Espectro de energía de los gammas creados en el agua (como la Fig.~3 de Sidelnik) y cuentas acumuladas de derecha a izquierda (como su Fig.~4)."))
# --- exceso de cuentas acumuladas entre 2,2 y 8,6 MeV con NaCl: descomposicion por proceso creador
GA = {m_: np.load(os.path.join(R, "resultados", f"{m_}_gammas_hasta600.npz")) for m_ in M
      if os.path.exists(os.path.join(R, "resultados", f"{m_}_gammas_hasta600.npz"))}
MS_ = [m_ for m_ in M if m_ in GA and m_ != "pura"]
if "pura" in GA and MS_:
    def acum_(m_, clave, E1, E2=1e9):
        d_ = GA[m_]; c_ = 0.5 * (d_["EB"][1:] + d_["EB"][:-1]); h_ = d_[clave] if clave in d_.files else np.zeros(c_.size)
        return h_[(c_ >= E1) & (c_ < E2)].sum() / float(d_["N"])
    ncl_ = lambda m_: S[m_]["capturas_agua_por_nucleo"].get("Cl35", [0])[0] / S[m_]["N"]
    filas_ = [("$N(\\geq 4\\,$MeV$)$ total", lambda m_: f(acum_(m_, "todos", 4.0), 3)),
              ("\\quad de captura (nCapture)", lambda m_: f(acum_(m_, "cre|nCapture", 4.0), 3)),
              ("\\quad de inelásticas de neutrones", lambda m_: f(acum_(m_, "cre|neutronInelastic", 4.0), 3)),
              ("Exceso sobre el agua pura en $N(\\geq 4\\,$MeV$)$", lambda m_: "--" if m_ == "pura" else f(acum_(m_, "todos", 4.0) - acum_("pura", "todos", 4.0), 3)),
              ("\\quad fracción del exceso debida a la captura", lambda m_: "--" if m_ == "pura" else pct(acum_(m_, "cre|nCapture", 4.0) / (acum_(m_, "todos", 4.0) - acum_("pura", "todos", 4.0)), 0)),
              ("Gammas de captura entre 2,3 y 8,7\\,MeV por neutrón", lambda m_: f(acum_(m_, "cre|nCapture", 2.3, 8.7), 3)),
              ("\\quad por captura en $^{35}$Cl", lambda m_: "--" if ncl_(m_) == 0 else f(acum_(m_, "cre|nCapture", 2.3, 8.7) / ncl_(m_), 2)),
              ("Escalón de 8,58\\,MeV (gamma único, por neutrón)", lambda m_: f(acum_(m_, "cre|nCapture", 8.50, 8.65), 3)),
              ("\\quad fracción de las capturas en $^{35}$Cl", lambda m_: "--" if ncl_(m_) == 0 else pct(acum_(m_, "cre|nCapture", 8.50, 8.65) / ncl_(m_), 0)),
              ("$N(\\geq 8{,}7\\,$MeV$)$ total", lambda m_: f(acum_(m_, "todos", 8.7), 3))]
    MM_g = ["pura"] + MS_
    w(r"""\paragraph{¿Por qué las curvas acumuladas con NaCl tienen una protuberancia entre 2,2 y 8,6\,MeV?}
$N(\geq E)$ cuenta, por neutrón, los gammas de energía mayor o igual que $E$: cada línea produce un escalón en su energía y los gammas comprendidos entre dos energías forman la meseta que las separa.
En agua pura casi todos los gammas de captura proceden del H y tienen 2,22\,MeV, de modo que por encima del escalón de 2,22\,MeV no queda ninguno.
Con NaCl, el $^{35}$Cl emite su cascada entre 2,3 y 8,58\,MeV: esos gammas forman una meseta adicional que termina en un escalón abrupto en 8,58\,MeV, la energía de separación del neutrón en el $^{36}$Cl, por encima de la cual no puede haber gammas de captura.
Por encima de 8,6\,MeV las curvas coinciden, porque allí solo quedan gammas de las inelásticas, del bremsstrahlung y de las desintegraciones de $\pi^0$ y muones, que no dependen de la sal (Tabla~\ref{tab:protuberancia}).
""")
    w(r"""\begin{table}[H]\centering\small\begin{tabular}{l""" + "c" * len(MM_g) + r"""}\toprule
Gammas creados en el agua por neutrón incidente & """ + " & ".join(ET[m_] for m_ in MM_g) + r""" \\\midrule
""" + "".join(row([et_] + [fn_(m_) for m_ in MM_g]) for et_, fn_ in filas_) + r"""\bottomrule\end{tabular}
\caption{Descomposición de las cuentas acumuladas $N(\geq E)$ de la figura anterior (derecha) por proceso creador (\texttt{gammas\_acumulados.py}).}\label{tab:protuberancia}\end{table}
""")
    m_u = MS_[-1]
    w(r"""La captura explica el """ + " y el ".join(pct(acum_(m_, "cre|nCapture", 4.0) / (acum_(m_, "todos", 4.0) - acum_("pura", "todos", 4.0)), 0) + " (" + ET[m_] + ")" for m_ in MS_) + r""" del exceso sobre el agua pura a 4\,MeV;
las inelásticas apenas cambian con la sal. Cada captura en $^{35}$Cl aporta unos """ + f(acum_(m_u, "cre|nCapture", 2.3, 8.7) / ncl_(m_u), 1) + r""" gammas entre 2,3 y 8,7\,MeV, y los escalones de la meseta son las líneas del $^{36}$Cl
(2,86, 5,72, 6,12, 6,62, 7,41 y 7,79\,MeV; Sec.~\ref{sec:cl_lineas}). El escalón mayor, en 8,57\,MeV, corresponde al """ + pct(acum_(m_u, "cre|nCapture", 8.50, 8.65) / ncl_(m_u), 0) + r""" de las capturas en $^{35}$Cl:
es el defecto de \texttt{G4NeutronHP} discutido en la Sec.~\ref{sec:cascadas_cl}, que en una cuarta parte de las capturas emite un único gamma con toda la energía de separación.
Con cascadas realistas el escalón de 8,58\,MeV sería mucho menor y la meseta tendría más gammas de menor energía.
Las caídas pequeñas cerca de 6--7\,MeV presentes también en el agua pura son las líneas de desexcitación del $^{16}$O (6,13, 6,92 y 7,12\,MeV) producidas por las inelásticas, iguales en todos los medios.
""")
ir("elec", 1); w(r"\section{Electrones creados por gammas}" + "\n")
w(fig("fig03_espectro_electrones", "Electrones creados por gammas en el agua (como la Fig.~5 de Sidelnik), con el borde Compton de 1,994\\,MeV de la línea de 2,223\\,MeV; derecha, en escala logarítmica."))
gj = os.path.join(R, "resultados", "espectro_gamma_tipo_sidelnik.json")
ir("gamma", 2)
if os.path.exists(gj):
    G = json.load(open(gj)); po = G["positrones_por_proceso"]; tp = sum(po.values())
    r1, r6, pc = G["cociente_0511_2223"], G["cociente_6130_2223"], G["pico_sobre_continuo"]
    l6 = G["linea_6130_por_creador"]
    w(r"""\subsection{Comparación con la Fig. 3 de Sidelnik}\label{sec:fig3}
\paragraph{Procedimiento.} Se histogramó la energía de creación de los """ + f"{G['gammas_creados_en_agua']:,}".replace(",", "\\,") + r""" gammas creados en el agua
(primer paso de cada gamma en \texttt{pasos-gamma.tsv}) con bines de 1\,keV, y se agruparon en bines de """ + str(G["ancho_bin_keV"]) + r"""\,keV para el formato de la figura.
La Fig.~3 del artículo se digitalizó automáticamente por el color de los píxeles (\texttt{digitalizar\_fig3.py}); la curva roja de agua pura queda tapada en parte por las de NaCl,
por lo que su lectura es fiable en las líneas y en el continuo inferior, y aproximada por encima de 10\,MeV, donde hay pocas cuentas.
\paragraph{Normalización.} El eje de Sidelnik está en unidades arbitrarias: su línea de 2,223\,MeV tiene unas $""" + f"{G['pico_2223']['Sidelnik_cuentas_aprox']:.1e}".replace("e+0", r"\times10^{").replace(".", "{,}") + r"""}$ cuentas, más que el número de neutrones
(150\,000) y unas diez veces más que las capturas que reporta (25\,\%). En MEIGA la línea tiene """ + f"{G['pico_2223']['MEIGA_cuentas']:,.0f}".replace(",", "\\,") + r""" cuentas, una por captura en H;
contar todos los pasos de los gammas en vez de un gamma por entrada solo la sube a $1{,}8\times10^5$. Por eso la comparación se hace con magnitudes que no dependen de la normalización:
(i) cocientes entre alturas de líneas, que tampoco dependen del ancho de bin, y (ii) la forma del continuo con el pico de 2,223\,MeV igualado.
Con bines de """ + str(G["ancho_bin_keV"]) + r"""\,keV el cociente pico/continuo de MEIGA entre 3 y 5\,MeV (""" + f(pc["3"]["MEIGA"], 0) + "--" + f(pc["5"]["MEIGA"], 0) + r""") coincide con el de Sidelnik (""" + f(pc["3"]["Sidelnik"], 0) + "--" + f(pc["5"]["Sidelnik"], 0) + r"""), lo que sugiere que el artículo usó bines de ese orden.
""")
    w(fig("fig11_espectro_gamma_tipo_sidelnik", "(a) Espectro de energía de los gammas creados en el agua pura, en el formato de la Fig.~3 de Sidelnik. (b) MEIGA con el pico de 2,223\\,MeV igualado frente a la Fig.~3 digitalizada. (c) Composición del espectro de MEIGA por proceso creador. (d) Cocientes de líneas."))
    fj = os.path.join(R, "resultados", "fig4_gammas_acumulados.json")
    if os.path.exists(fj):
        F4 = json.load(open(fj)); q4 = F4["cociente_Sidelnik_MEIGA_pura"]; r4 = F4["N2menosN3_sobre_N3"]; t4 = F4["N20_sobre_N3"]; n4 = F4["NaCl_sobre_pura"]
        w(r"""\paragraph{Fig. 4 de Sidelnik: gammas acumulados.} La Fig.~4 del artículo muestra los mismos gammas acumulados de derecha a izquierda, $N(\geq E)$, en bines de 1\,MeV hasta 100\,MeV (Fig.~\ref{fig:fig4}).
Se digitalizaron sus marcadores (\texttt{fig4\_gammas\_acumulados.py}); por encima de 9\,MeV las cuatro curvas del artículo se superponen y se usa su valor común.
Tres cocientes, independientes de la normalización, resumen la comparación:
\begin{itemize}
\item \textbf{Línea de 2,223\,MeV frente a los gammas de más de 3\,MeV}, $[N(\geq2)-N(\geq3)]/N(\geq3)$: """ + f(r4["pura"]["Sidelnik"], 2) + " en el artículo y " + f(r4["pura"]["MEIGA"], 2) + r""" en MEIGA (agua pura), un factor """ + f(r4["pura"]["Sidelnik"] / r4["pura"]["MEIGA"], 1) + r""".
Es la misma conclusión que el salto en el borde Compton (Sec.~\ref{sec:interp_fig5}): por cada captura en H, MEIGA produce $\approx$\,1,6--1,8 veces más gammas de desexcitación nuclear. Entre 3 y 6\,MeV, donde dominan esos gammas, el cociente Sidelnik/MEIGA de las cuentas es constante ($\approx$\,""" + f(q4["4"], 2) + r""").
\item \textbf{Gammas de más de 20\,MeV}, $N(\geq20)/N(\geq3)$: """ + f(t4["pura"]["Sidelnik"], 3) + " en el artículo, " + f(t4["pura"]["MEIGA"], 3) + r""" en MEIGA y """ + f(t4["pura"]["MEIGA_sin_piones"], 4) + r""" en MEIGA sin los eventos con piones. Los gammas de alta energía vienen casi solo de los piones
(desintegración $\pi^0\to\gamma\gamma$, con gammas de $\approx$\,70\,MeV, y bremsstrahlung de sus cascadas). El artículo queda entre las dos curvas de MEIGA: tiene piones, pero $\approx$\,""" + f(t4["pura"]["MEIGA"] / t4["pura"]["Sidelnik"], 0) + r""" veces menos que Bertini en Geant4\,10.7 en esta observable, lo que concuerda con la cola de la Fig.~6.
""" + ("" if not n4 else r"""\item \textbf{Efecto del NaCl}, $N(\geq E)_{\rm NaCl}/N(\geq E)_{\rm pura}$: entre 3 y 6\,MeV vale """ + f(n4["3"]["MEIGA"], 2) + "--" + f(n4["6"]["MEIGA"], 2) + " en MEIGA y " + f(n4["3"]["Sidelnik"], 2) + "--" + f(n4["5"]["Sidelnik"], 2) + r""" en el artículo (el fondo mayor de MEIGA diluye la contribución del Cl); a 8\,MeV MEIGA queda por encima (""" + f(n4["8"]["MEIGA"], 2) + " frente a " + f(n4["8"]["Sidelnik"], 2) + r""") por la línea de 8,58\,MeV, y desde 9\,MeV ambos valen 1: la sal no cambia los gammas de alta energía.""") + r"""
\end{itemize}
""")
        w(r"""\begin{figure}[H]\centering\includegraphics[width=\linewidth]{../figuras/fig17_gammas_acumulados.pdf}\caption{Gammas creados en el medio acumulados de derecha a izquierda (formato de la Fig.~4 de Sidelnik): (a) hasta 100\,MeV y (b) por debajo de 10\,MeV, MEIGA (lleno) y artículo (vacío), cuentas por 150\,000 neutrones; (c) forma normalizada a $N(\geq3\,{\rm MeV})$, con y sin los eventos con piones; (d) cociente 2,5\,\% NaCl/agua pura.}\label{fig:fig4}\end{figure}
""")
    w(r"""\begin{table}[H]\centering\small\begin{tabular}{lccc}\toprule
Cociente de alturas & Sidelnik & MEIGA & MEIGA sin decaimiento radiactivo \\\midrule
""" + row(["0,511\\,MeV / 2,223\\,MeV", f(r1["Sidelnik"], 3), f(r1["MEIGA"], 3), f(r1["MEIGA_sin_decaimiento_radiactivo"], 3) + "$^*$"])
      + row(["6,13\\,MeV / 2,223\\,MeV", f(r6["Sidelnik"], 3), f(r6["MEIGA"], 3), f(r6["MEIGA_sin_decaimiento_radiactivo"], 3)]) + r"""\bottomrule
\end{tabular}\caption{Cocientes entre las alturas de las líneas principales (agua pura). $^*$Estimado restando la fracción de positrones que vienen de desintegraciones $\beta^+$.}\end{table}
\paragraph{Línea de 2,223\,MeV y línea de 6,13\,MeV.} La línea de 6,13\,MeV del $^{16}$O la producen la dispersión inelástica de neutrones (""" + f"{l6.get('neutronInelastic', 0):,}".replace(",", "\\,") + r""" gammas)
y la desintegración del $^{16}$N ($T_{1/2}=7{,}1$\,s, """ + f"{l6.get('RadioactiveDecayBase', 0):,}".replace(",", "\\,") + r""" gammas), producido por $^{16}$O$(n,p)$. Sin esta última, el cociente con la línea de captura en H
es """ + f(r6["MEIGA_sin_decaimiento_radiactivo"], 3) + r""", igual al del artículo (""" + f(r6["Sidelnik"], 3) + r"""): la captura en H y la dispersión inelástica en O se reproducen con la misma proporción.
\paragraph{Línea de aniquilación (0,511\,MeV).} En MEIGA es unas """ + f(r1["MEIGA"] / r1["Sidelnik"], 0) + r""" veces más intensa, relativa a la de 2,223\,MeV, que en el artículo.
Los positrones que la producen vienen de desintegraciones $\beta^+$ de núcleos producidos por espalación del oxígeno ($^{15}$O, $^{13}$N, $^{11}$C, con vidas medias de minutos; """ + pct(po.get("RadioactiveDecayBase", 0) / tp, 0) + r"""),
de conversión de gammas de alta energía en pares (""" + pct(po.get("conv", 0) / tp, 0) + r""") y de la desintegración de muones positivos procedentes de $\pi^+$ (""" + pct((po.get("DecayWithSpin", 0) + po.get("Decay", 0)) / tp, 0) + r""").
Geant4 simula las desintegraciones radiactivas sin límite de tiempo; si la simulación de Sidelnik no las incluía, o las cortaba en tiempo, el cociente de MEIGA bajaría a """ + f(r1["MEIGA_sin_decaimiento_radiactivo"], 2) + r""",
y el exceso restante (unas """ + f(r1["MEIGA_sin_decaimiento_radiactivo"] / r1["Sidelnik"], 1) + r""" veces) es coherente con la mayor producción de piones encontrada en la Sec.~\ref{sec:fig6}.
\paragraph{Continuo.} Entre 2,5 y 9\,MeV la forma del continuo coincide (es la cola de la dispersión inelástica de neutrones). Por debajo de 1,5\,MeV el continuo de MEIGA es varias veces más alto,
dominado por el bremsstrahlung de electrones y positrones de alta energía, que de nuevo apunta a la producción de piones y sus cascadas.
Por encima de 10\,MeV el artículo muestra un continuo que llega hasta $\approx$\,17\,MeV, más alto que el de MEIGA, cuya componente de dispersión inelástica termina hacia 11\,MeV; con la precisión de la digitalización en esa zona
(decenas de cuentas y la curva roja parcialmente tapada) esta diferencia debe tomarse con cautela.
\aviso{En resumen: las líneas y el continuo ligados a la moderación, la captura y la dispersión inelástica de neutrones (2,223 y 6,13\,MeV, continuo de 2,5--9\,MeV) se reproducen;
las diferencias (línea de 0,511\,MeV y continuo de baja energía) se explican por el decaimiento radiactivo de larga vida y por la mayor producción de piones a 500\,MeV en el modelo de Bertini, igual que en la cola de la Fig.~6.}
""")

ej = os.path.join(R, "resultados", "espectro_electrones_tipo_sidelnik.json")
ir("elec", 2)
if os.path.exists(ej):
    EL = json.load(open(ej)); cq = EL["cociente_Sidelnik_MEIGA"]; sb = EL["saltos_bordes"]; ns = EL.get("NaCl_sobre_pura", {})
    ES = EL; SIDP = {"pura": 25.18, "nacl25": 26.73, "nacl5": 27.65, "nacl10": 29.26}
    PM_ = [100 * (1 - 1 / ES["cociente_Sidelnik_MEIGA"][m_]["mediana"]) for m_ in ES["cociente_Sidelnik_MEIGA"]]
    w(r"""\subsection{Comparación con la Fig. 5 de Sidelnik: electrones producidos por gammas}\label{sec:fig5}
Se sumaron los electrones que crean los gammas en el agua por efecto Compton, fotoeléctrico y producción de pares (\texttt{secundarias-interaccion-gamma.tsv}),
con bines de """ + str(EL["ancho_bin_keV"]) + r"""\,keV y cuentas escaladas a 150\,000 neutrones, y se compararon con la Fig.~5 del artículo digitalizada por color (\texttt{digitalizar\_fig5.py}).
\paragraph{Escala absoluta.} A diferencia de las Figs.~3 y 6, aquí no hace falta ninguna normalización: ambas figuras son electrones por 150\,000 neutrones con bines de 20\,keV.
El factor $k$ de la figura siguiente (panel b) es la mediana del cociente Sidelnik/MEIGA en 11 energías entre 0,5 y 7\,MeV: """ + ", ".join(f(ES["cociente_Sidelnik_MEIGA"][m_]["mediana"], 2) + " (" + {"pura": "agua pura", "nacl25": "2,5\\,\\%", "nacl5": "5\\,\\%", "nacl10": "10\\,\\%"}[m_] + ")" for m_ in ES["cociente_Sidelnik_MEIGA"]) + r""".
Es decir, MEIGA produce entre un """ + f(min(PM_), 0) + " y un " + f(max(PM_), 0) + r"""\,\% menos de electrones que la simulación del artículo, y su forma coincide desde 0,3 hasta 10\,MeV.
Este factor vale solo para los electrones: el de la Fig.~3 (3,40) es una normalización, porque el eje de Sidelnik está en unidades arbitrarias (Sec.~\ref{sec:fig3}).
\paragraph{Por qué MEIGA tiene menos electrones.} (i) La causa principal es que Sidelnik tiene más capturas: el cociente de probabilidades de captura Sidelnik/MEIGA es
""" + ", ".join(f(SIDP[m_] / (100 * FC[m_]["P_b_capturas_sobre_todos_los_neutrones"]), 2) for m_ in ES["cociente_Sidelnik_MEIGA"] if m_ in FC) + r""" (mismo orden de medios), prácticamente igual a $k$ en agua pura y con 2,5\,\%.
Con 5 y 10\,\% $k$ queda por debajo de ese cociente porque cada captura en Cl de MEIGA emite más energía de la real (10,1 frente a 8,58\,MeV; Sec.~\ref{sec:cascadas_cl}) y produce más electrones, lo que compensa en parte las capturas que faltan.
(ii) $k$ es un promedio: punto a punto el cociente va de """ + f(ES["cociente_Sidelnik_MEIGA"]["pura"]["min"], 2) + " a " + f(ES["cociente_Sidelnik_MEIGA"]["pura"]["max"], 2) + r""" en agua pura; Sidelnik está más alto justo debajo del borde de 1,994\,MeV y MEIGA entre 2 y 3\,MeV, donde domina el fondo de desexcitación nuclear (Sec.~\ref{sec:interp_fig5}),
y con NaCl MEIGA queda muy por encima entre 7,4 y 8,3\,MeV por el gamma único de 8,58\,MeV. (iii) La digitalización por color en escala logarítmica tiene una incertidumbre del 5--10\,\%.
(iv) Las versiones de Geant4 y las listas físicas son distintas y el artículo no las especifica. La diferencia de amplitud es, por tanto, pequeña y se explica casi por completo por la probabilidad de captura;
las diferencias físicamente relevantes están en la forma (fondo de desexcitación nuclear y gamma único de 8,58\,MeV).
\paragraph{Bordes Compton.} Se ven en ambas simulaciones los bordes de la línea de aniquilación (0,34\,MeV), de la captura en H (1,994\,MeV) y de la línea de 6,13/6,11\,MeV (5,87\,MeV).
El salto en el borde de 1,994\,MeV (nivel antes/después) es """ + f(sb["pura"]["2,223 (H)"]["MEIGA"], 1) + " en MEIGA y " + f(sb["pura"]["2,223 (H)"]["Sidelnik"], 1) + r""" en el artículo; el de 5,87\,MeV, """ + f(sb["pura"]["6,13 (O) / 6,11 (Cl)"]["MEIGA"], 2) + " y " + f(sb["pura"]["6,13 (O) / 6,11 (Cl)"]["Sidelnik"], 2) + r""".
""" + ("" if "nacl25" not in ns else r"""\paragraph{Efecto del NaCl.} El cociente 2,5\,\% NaCl/agua pura no depende de la normalización. Por debajo de 1,9\,MeV es $\approx$\,1,1 en ambas simulaciones; entre 2 y 6\,MeV, donde contribuyen los electrones Compton de las líneas del Cl,
vale """ + f(ns["nacl25"]["3.0"]["MEIGA"], 2) + "--" + f(ns["nacl25"]["5.8"]["MEIGA"], 2) + " en MEIGA y " + f(ns["nacl25"]["3.0"]["Sidelnik"], 2) + "--" + f(ns["nacl25"]["5.8"]["Sidelnik"], 2) + r""" en el artículo.
Las diferencias aparecen por encima de 7\,MeV: el borde Compton de la línea de 8,58\,MeV (8,33\,MeV) produce en MEIGA un salto de """ + f(sb["nacl25"]["8,58 (Cl)"]["MEIGA"], 1) + r""" frente a """ + f(sb["nacl25"]["8,58 (Cl)"]["Sidelnik"], 1) + r""" en el artículo,
consecuencia directa del exceso de transiciones directas al fundamental en las cascadas del $^{35}$Cl de Geant4 (Sec.~\ref{sec:nacl25}). Los bordes de 7,17 y 7,54\,MeV (líneas de 7,41 y 7,79\,MeV) tienen saltos parecidos en las dos simulaciones.
"""))
    w(fig("fig13_espectro_electrones_tipo_sidelnik", "Electrones producidos por gammas en el agua: (a) formato de la Fig.~5 de Sidelnik (bines de 20\\,keV, 150\\,000 neutrones); (b) MEIGA frente a la figura digitalizada, con los bordes Compton; (c) cociente NaCl/agua pura; (d) saltos en los bordes Compton."))
ij = os.path.join(R, "resultados", "interpretacion_electrones.json")
if os.path.exists(ij):
    IE = json.load(open(ij)); cp_ = IE["composicion"]["pura"]; ns_ = IE["NaCl_sobre_pura"]
    w(r"""\subsection{Interpretación física de las diferencias con la Fig. 5}\label{sec:interp_fig5}
Para entender las diferencias se clasificó cada electrón según el origen del gamma que lo produce (\texttt{origen\_electrones.py}): el electrón se enlaza con su gamma padre
(\texttt{pasos-gamma.tsv}), el gamma con su proceso creador y, si es de captura, con el núcleo que capturó el neutrón (\texttt{capturas-neutrones.tsv}). Fig.~\ref{fig:origen}.
\paragraph{El salto en el borde de 1,994\,MeV mide la razón captura en H / fondo.} Por debajo del borde, el """ + pct(cp_["antes_borde"]["captura H"] / sum(cp_["antes_borde"].values()), 0) + r""" de los electrones viene de la línea de 2,223\,MeV;
por encima, el """ + pct(cp_["frac_inelastica_despues"], 0) + r""" viene de gammas de la dispersión inelástica de neutrones en el oxígeno (desexcitación de $^{16}$O$^*$, $^{12}$C$^*$, $^{15}$N$^*$: líneas de 4,44, 6,13, 6,92, 7,12\,MeV y su continuo).
El salto vale, por tanto, $J \approx 1 + C_H/F$, con $C_H$ los electrones de la captura en H y $F$ ese fondo. Los piones no son la causa: sin los eventos con piones el salto apenas pasa de """ + f(cp_["salto"], 2) + " a " + f(cp_["salto_sin_piones"], 2) + r""".
Para obtener el salto de Sidelnik (""" + f(cp_["salto_Sidelnik"], 1) + r""") habría que dividir el fondo de MEIGA por """ + f(cp_["k_fondo"], 2) + r""" en agua pura y por """ + f(IE["composicion"]["nacl25"]["k_fondo"], 2) + r""" con 2,5\,\% NaCl:
el mismo factor en los dos medios, como corresponde a un fondo que no depende de la sal. Es decir, por cada captura en H, MEIGA produce $\approx$\,1,6 veces más gammas de desexcitación nuclear que la simulación del artículo.
Esto concuerda con el espectro gamma: respecto a la línea de 2,223\,MeV, las líneas de 6,13\,MeV ($^{16}$O) y 4,44\,MeV ($^{12}$C) son 1,35 y 1,40 veces más intensas en MEIGA (las demás quedan tapadas en la figura digitalizada),
y Sidelnik tiene además $\approx$\,5\,\% más capturas (25,18 frente a 24,08\,\%). El salto en el borde de 5,87\,MeV, que mide justamente la línea de 6,13\,MeV, es por la misma razón algo mayor en MEIGA (1,74 frente a 1,63).
La producción de gammas en la dispersión inelástica de neutrones de 10--500\,MeV depende del modelo de cascada (Bertini por encima de $\approx$\,20\,MeV) y de la desexcitación de los núcleos residuales (\texttt{G4PhotonEvaporation}, datos G4NDL por debajo de 20\,MeV),
que cambiaron entre versiones de Geant4; sin conocer la versión y la lista física de Sidelnik no se puede atribuir la diferencia a un componente concreto.
\paragraph{El cociente NaCl/agua pura.} Con NaCl el cociente vale $1 + C_{Cl}/F$ en la región de 2--6\,MeV, donde solo contribuyen las capturas en Cl y el fondo. Hay tres efectos:
\begin{enumerate}
\item Debajo del borde de 1,994\,MeV el cociente baja a $\approx$\,0,84 en las dos simulaciones: el Cl compite con el H y las capturas en H por neutrón caen de 0,83 a 0,55. Que el valor coincida indica que la competencia H/Cl es parecida en ambas.
\item Entre 2 y 6\,MeV el fondo más alto de MEIGA diluye la contribución del Cl, y el cociente queda por debajo del de Sidelnik (""" + f(ns_["2.05-4.0"]["MEIGA"], 2) + " frente a " + f(ns_["2.05-4.0"]["Sidelnik"], 2) + r""" entre 2 y 4\,MeV).
Si se divide el fondo por el mismo factor """ + f(cp_["k_fondo"], 2) + r""", el cociente pasa a """ + f(ns_["2.05-4.0"]["MEIGA_fondo_entre_k"], 2) + " y " + f(ns_["4.0-5.85"]["MEIGA_fondo_entre_k"], 2) + r""", algo por encima del artículo (""" + f(ns_["2.05-4.0"]["Sidelnik"], 2) + " y " + f(ns_["4.0-5.85"]["Sidelnik"], 2) + r"""):
una vez corregido el fondo, los electrones de las capturas en Cl de MEIGA son $\approx$\,1,2--1,4 veces los del artículo. Es lo esperado de los dos defectos de Geant4 ya identificados: $\approx$\,1,27 veces más capturas en Cl que las secciones eficaces térmicas
y cascadas con 10,2\,MeV en promedio en vez de 8,58\,MeV.
\item Entre 7 y 8,3\,MeV el cociente de MEIGA (""" + f(ns_["7.0-8.3"]["MEIGA"], 2) + r""") supera al del artículo (""" + f(ns_["7.0-8.3"]["Sidelnik"], 2) + r""") por los electrones Compton de la línea de 8,58\,MeV: el """ + "24" + r"""\,\% de las capturas en $^{35}$Cl emite un único gamma de 8,58\,MeV, frente a $\approx$\,3\,\% en la naturaleza.
\end{enumerate}
\aviso{Las intensidades relativas de las líneas intermedias del Cl (1,165, 6,11, 7,41, 7,79\,MeV) coinciden con Sidelnik porque los dos defectos se compensan: hay $\approx$\,1,27 veces más capturas en Cl,
pero solo $\approx$\,76\,\% de ellas siguen una cascada (el resto va directo al fundamental); $1{,}27 \times 0{,}76 \approx 0{,}97$. En la luz total, en cambio, los defectos se suman, porque cada captura en Cl deposita más energía de la debida.}
""")
    w(r"""\begin{figure}[H]\centering\includegraphics[width=\linewidth]{../figuras/fig14_origen_electrones.pdf}\caption{Origen del gamma que produce cada electrón (agua pura y 2,5\,\% NaCl; áreas apiladas) y cociente NaCl/agua pura en cuatro intervalos: Sidelnik, MEIGA y MEIGA con el fondo no debido a capturas dividido por el factor que reproduce el salto de 1,994\,MeV del artículo.}\label{fig:origen}\end{figure}
""")
ir("luz", 1)
w(r"""\section{Fotones Cherenkov y carga en el PMT (Fig. 6 de Sidelnik)}
""")
w(tabla([("Fotones Cherenkov creados por neutrón", lambda m: f(S[m]["fotones_cherenkov_por_neutron"][0], 0)),
         ("Carga media [p.e.]", lambda m: f(S[m]["Q_media"][0], 2)),
         ("Eventos con $Q\\geq 1$", lambda m: pct(S[m]["eficiencia_Q_ge1"][0], 1)),
         ("p.e. por fotón creado", lambda m: f(100 * S[m]["Q_sobre_fotones"], 2) + "\\,\\%"),
         ("Carga $<1$\\,µs", lambda m: pct(S[m]["carga_por_ventana"]["<1 us"]["frac"], 1)),
         ("Carga 1\\,µs--1\\,ms (capturas)", lambda m: pct(S[m]["carga_por_ventana"]["1 us-1 ms"]["frac"], 1)),
         ("Carga $>1$\\,ms (desintegraciones)", lambda m: pct(S[m]["carga_por_ventana"][">1 ms"]["frac"], 2))],
        "Producción de luz Cherenkov y respuesta del PMT."))
w(r"""\aviso{La distribución de fotoelectrones de MEIGA es mucho más estrecha que la Fig.~6 de Sidelnik: la media es """ + f(p["Q_media"][0], 1) + r"""\,p.e.
y casi no hay eventos por encima de 400\,p.e., mientras que la curva del artículo se extiende hasta $\sim$1000. Se crean unos """ + f(p["fotones_cherenkov_por_neutron"][0], 0) + r""" fotones Cherenkov por neutrón
y llega al PMT (tras la eficiencia cuántica) el """ + f(100 * p["Q_sobre_fotones"], 2) + r"""\,\%. La Sec.~\ref{sec:diag} muestra que la diferencia indica que la Fig.~6 del artículo no incluye la colección óptica (el artículo no lo especifica); la Fig.~6 digitalizada tiene además los problemas descritos en el informe v0.6.0.
Como en las corridas anteriores, Geant4 simula desintegraciones radiactivas sin límite de tiempo: el """ + pct(p["carga_por_ventana"][">1 ms"]["frac"], 2) + r""" de la carga llega después de 1\,ms.}
""")
w(fig("fig04_carga_y_tiempos", "Distribución de fotoelectrones en el PMT frente a la Fig.~6 de Sidelnik (digitalizada) y tiempos de llegada de los fotoelectrones."))
w(fig("fig05_tiempo_energia_captura", "Tiempo de captura y energía del neutrón al capturarse."))
dj = os.path.join(R, "resultados", "diagnostico_pura.json")
ir("carga", 2)

if os.path.exists(dj):
    g = json.load(open(dj)); de = g["destino"]; c6 = g["comparacion_fig6"]
    w(r"""\section{Diagnóstico: por qué la carga es baja (agua pura)}\label{sec:diag}
Se reconstruyó la historia de los """ + f(g["fotones_seguidos_por_neutron"] * p["N"] / 1e6, 1) + r""" millones de fotones ópticos seguidos (archivo \texttt{pasos-particulas.tsv}, 78\,GB).
En el modo rápido de MEIGA (\texttt{eFast}) cada fotón Cherenkov se acepta o descarta según la eficiencia cuántica del R5912 en el momento de crearse;
solo los aceptados se transportan, y cada uno que entra al PMT es un fotoelectrón.
\begin{table}[H]\centering\small\begin{tabular}{lr}\toprule
Etapa & Por neutrón \\\midrule
Fotones Cherenkov creados & """ + f(g["fotones_creados_por_neutron"], 1) + r""" \\
Aceptados por la eficiencia cuántica al crearse (se transportan) & """ + f(g["fotones_seguidos_por_neutron"], 1) + " (" + pct(g["fraccion_seguidos"], 1) + r""") \\
Llegan al PMT = carga & """ + f(g["llegan_PMT_por_neutron"], 2) + " (" + pct(de["PMT"]["frac"], 1) + r""" de los transportados) \\\bottomrule
\end{tabular}\caption{Balance de luz. La carga registrada coincide con los fotones que entran al PMT en el """ + pct(g["eventos_Q_igual_llegadas"], 2) + r""" de los eventos.}\end{table}
\begin{table}[H]\centering\small\begin{tabular}{lccc}\toprule
Destino del fotón transportado & Fracción & Rebotes medios & Camino medio [cm] \\\midrule
""")
    for k, nom in [("PMT", "Llega al PMT"), ("absorcion_agua", "Absorbido en el agua"), ("pared", "Absorbido al chocar con la pared (Tyvek)"), ("tyvek", "Perdido dentro del Tyvek/acero")]:
        if k in de:
            w(row([nom, pct(de[k]["frac"], 1), f(de[k]["rebotes_medios"], 1), f(de[k]["camino_medio_cm"], 0)]))
    w(r"""\bottomrule\end{tabular}\caption{Destino de los fotones transportados.}\end{table}
Los pasos de fotones ``dentro del Tyvek'' son de longitud cero: son las reflexiones en la superficie \texttt{groundbackpainted}, que funciona.
La pérdida dominante es la absorción en la pared. Con un modelo de rebotes ajustado a las trayectorias (\texttt{sensibilidad\_tyvek.py}): en cada encuentro con la pared el fotón alcanza el PMT con probabilidad $s$, si no choca con el Tyvek y se absorbe con probabilidad $a$, y entre encuentros se absorbe en el agua con probabilidad $w$; la fracción que llega al PMT es $P = s/[s + (1-s)a + w]$.
En agua pura $s = 0{,}8$\,\%, $a = 9{,}8$\,\% y $w = 2{,}0$\,\%, que dan $P = 6{,}3$\,\%, igual al valor observado: un fotón sobrevive en promedio $1/a \approx 10$ choques, pero necesitaría del orden de $1/s \approx 130$ encuentros para dar con el PMT.
\paragraph{El factor 0,94 del Tyvek.} En \texttt{Materials.cc} la reflectividad medida del Tyvek ($R_{\rm tabla}$: 0,99--1,00 en el azul, 0,78--0,85 en el ultravioleta) se multiplica por \texttt{scaleLinerRef}\,=\,0,94. De los 9,8 puntos de absorción por choque, $\approx$\,2,1 corresponden a $1 - R_{\rm tabla}$, $\approx$\,5,9 al factor 0,94 (una pérdida mínima del 6\,\% por choque aun donde el Tyvek tabulado refleja el 100\,\%) y $\approx$\,1,9 a una pérdida adicional del modelo de superficie \texttt{groundbackpainted}.
El factor es un parámetro del modelo sin justificación documentada (se usa a veces para representar un revestimiento envejecido) y es el principal responsable de la baja colección. Carga media estimada con otros modelos ópticos (agua pura):
\begin{table}[H]\centering\small\begin{tabular}{lcc}\toprule
Modelo óptico & Carga media [p.e.] & Factor \\\midrule
""" + "".join(row([nom, f(json.load(open(os.path.join(R, "resultados", "sensibilidad_tyvek_pura.json")))["carga_media_estimada"][k], 1), f(json.load(open(os.path.join(R, "resultados", "sensibilidad_tyvek_pura.json")))["carga_media_estimada"][k] / json.load(open(os.path.join(R, "resultados", "sensibilidad_tyvek_pura.json")))["carga_media_estimada"]["MEIGA actual (tabla x 0,94)"], 1)]) for nom, k in [
    ("Actual: $R = 0{,}94\\,R_{\\rm tabla}$", "MEIGA actual (tabla x 0,94)"), ("Tabla sin el factor 0,94", "tabla sin factor (x 1,00)"),
    ("$R = 0{,}985$ (LHAASO)", "LHAASO R = 0,985"), ("Actual + agua de 100\\,m", "MEIGA actual + agua de 100 m"),
    ("$R = 0{,}985$ + agua de 100\\,m", "LHAASO: R = 0,985 + 100 m")]) + r"""\bottomrule\end{tabular}\caption{Sensibilidad de la carga en el PMT al modelo óptico (modelo de rebotes aplicado por intervalos de energía del fotón; se conserva la pérdida adicional de \texttt{groundbackpainted}).}\label{tab:sens_tyvek}\end{table}
La escala absoluta de la carga es incierta en un factor de hasta $\approx$\,2,5, pero ni la comparación con la Fig.~6 (fotones aceptados antes del transporte) ni las diferencias entre medios dependen de ella. El Tyvek se mantuvo en esta campaña para que todas las corridas sean comparables; su revisión queda como trabajo futuro.
La luz roja ($<2{,}3$\,eV) se pierde sobre todo por absorción en el agua (longitud de absorción de 3--9\,m), y la ultravioleta por la menor reflectividad del Tyvek.
""")
    w(fig("fig07_destino_fotones", "Destino de los fotones transportados en los cuatro medios (\\texttt{figura\\_destino\\_fotones\\_medios.py}): (a) destino final; (b) rebotes en el Tyvek antes del destino; (c) fracción que llega al PMT según la energía del fotón; (d) fracción absorbida en la pared y en el agua según la energía.").replace("\\end{figure}", "\\label{fig:destino}\\end{figure}"))
    w(r"""\paragraph{Qué cuenta la Fig. 6 de Sidelnik.} Su eje dice ``número de fotones Cherenkov aceptados por la eficiencia cuántica''. La distribución de MEIGA que mejor
la reproduce es precisamente la de fotones aceptados por la eficiencia cuántica al crearse, antes del transporte óptico (correlación de la forma en escala logarítmica """ + f(c6["fotones aceptados por la QE al crearse"]["corr_log"], 3) + r""",
frente a """ + f(c6["p.e. en el PMT (tras transporte)"]["corr_log"], 3) + r""" para la carga en el PMT), incluido el quiebre a 400--450 fotones.
Esto indica que la Fig.~6 del artículo no incluye la eficiencia de colección óptica, aunque el artículo no lo especifica: la carga en el PMT de MEIGA es del orden de 16 veces menor, y ni con la reflectividad de LHAASO (0,985) y 100\,m de longitud de absorción subiría más de unas 2,5 veces.
""")
    w(fig("fig06_balance_luz_y_fig6", "Izquierda: tres distribuciones de MEIGA frente a la Fig.~6 de Sidelnik. Derecha: balance de luz por neutrón."))
hj, pj, cj = (os.path.join(R, "resultados", n) for n in ("histograma_tipo_sidelnik.json", "piones_cola.json", "figura6_cuentas_por_intervalo.csv"))
ir("luz", 2)
if all(os.path.exists(x) for x in (hj, pj, cj)):
    import pandas as pd
    hs = json.load(open(hj))["pura"]; pi = json.load(open(pj))["pura"]
    ci = pd.read_csv(cj); ci = ci[(ci.medio == "pura") & ci.Sidelnik_cuentas.notna()]
    ac, qc = hs["aceptados_QE"], hs["carga_pe"]
    w(r"""\section{La Fig. 6 de Sidelnik reproducida con MEIGA y el histograma de carga}\label{sec:fig6}
\subsection{Procedimiento}
Para comparar con la Fig.~6 del artículo se usa su mismo observable. Para cada uno de los 150\,000 neutrones:
\begin{enumerate}
\item Se cuentan los fotones Cherenkov aceptados por la eficiencia cuántica del PMT en el momento de crearse, sin transporte óptico. En el modo \texttt{eFast} de MEIGA son exactamente los fotones que el simulador transporta, por lo que se obtienen de \texttt{pasos-particulas.tsv}.
\item Se descartan los eventos sin ningún fotón aceptado (""" + pct(ac["frac_0"], 1) + r""" de los neutrones), porque la Fig.~6 no muestra el pico en cero.
\item Se histograma como en el artículo: bines de 10 fotones, eje de 0 a 2500 fotones, escala logarítmica y cuentas absolutas, sin normalizar ni reescalar.
\end{enumerate}
Las curvas digitalizadas de la Fig.~6 se limpiaron de dos artefactos de la digitalización: la leyenda capturada entre 1590 y 1800 fotones y el borde final del eje en las curvas con NaCl.
""")
    w(fig("fig10_figura6_sidelnik_vs_meiga", "Izquierda: Fig.~6 de Sidelnik et al.\\ (2020), digitalizada. Derecha: la misma figura construida con MEIGA para agua pura (150\\,000 neutrones de 500\\,MeV), con la curva de Sidelnik superpuesta y los eventos separados según haya o no producción de piones en una interacción inelástica del neutrón."))
    w(r"""\begin{table}[H]\centering\small\begin{tabular}{lrrr}\toprule
Fotones aceptados & MEIGA & Sidelnik (digitalizada) & MEIGA/Sidelnik \\\midrule
""")
    for _, r_ in ci.iterrows():
        w(row([r_.intervalo.replace("-", "--"), f"{int(r_.MEIGA_cuentas):,}".replace(",", "\\,"), f"{int(r_.Sidelnik_cuentas):,}".replace(",", "\\,"), f(r_.cociente, 2)]))
    w(r"""\bottomrule\end{tabular}\caption{Cuentas absolutas por intervalo de fotones aceptados (agua pura, eventos con al menos un fotón). Además, MEIGA tiene """ + f"{int((pd.read_csv(cj).query('medio == \"pura\" and intervalo == \">2500\"').MEIGA_cuentas).iloc[0]):,}".replace(",", "\\,") + r""" eventos por encima de 2500 fotones, fuera del eje del artículo.}\end{table}
\subsection{Resultado: coincidencia hasta 500 fotones}
Entre 0 y 500 fotones la distribución de MEIGA coincide con la de Sidelnik sin ningún reescalamiento: la pendiente es la misma, el quiebre aparece en 400--500 fotones como en el artículo,
y las cuentas absolutas coinciden dentro del 6--23\,\%. La correlación de la forma en escala logarítmica entre 0 y 1000 fotones es """ + f(ac["corr_forma_Sidelnik_0_1000"], 3) + r""".
Esto indica que el número de neutrones, la eficiencia cuántica y la producción de luz Cherenkov son comparables en las dos simulaciones.
La mediana de MEIGA es de """ + f(ac["mediana"], 0) + r""" fotones aceptados por neutrón y la media de """ + f(ac["media"], 0) + r""" (la media está dominada por la cola).
\subsection{La cola por encima de 500 fotones: producción de piones}
Por encima de 500 fotones MEIGA tiene entre 2 y 3 veces más eventos que el artículo. Para identificar su origen se marcó cada evento según el archivo
\texttt{secundarias-inelastica-neutron.tsv}: un evento ``con piones'' es aquel en que alguna interacción inelástica de un neutrón produjo un $\pi^\pm$ o un $\pi^0$.
\begin{table}[H]\centering\small\begin{tabular}{lrccc}\toprule
Fotones aceptados & Eventos & Con $\pi^\pm$ & Con $\pi^0$ & Con algún pion \\\midrule
""")
    for it in pi["intervalos"]:
        w(row([it["intervalo"].replace("-None", "").replace(">=", "$\\geq$").replace("-", "--"), f"{it['n']:,}".replace(",", "\\,"), pct(it["pi_cargado"], 1), pct(it["pi0"], 1), pct(it["algun_pion"], 1)]))
    w(r"""\bottomrule\end{tabular}\caption{Fracción de eventos con producción de piones según el número de fotones aceptados (agua pura). Un mismo evento puede tener piones cargados y neutros.}\end{table}
Solo el """ + pct(pi["frac_eventos_con_piones"], 1) + r""" de los neutrones produce piones (""" + pct(pi["frac_con_pi_cargado"], 1) + r""" con $\pi^\pm$ y """ + pct(pi["frac_con_pi0"], 1) + r""" con $\pi^0$),
pero esos eventos forman la cola: el """ + pct(pi["frac_ge500_con_piones_entre_ge500"], 1) + r""" de los eventos con 500 fotones o más tiene piones. Un evento con piones produce en promedio
""" + f(pi["media_aceptados_con_piones"], 0) + r""" fotones aceptados, frente a """ + f(pi["media_aceptados_sin_piones"], 0) + r""" en uno sin piones. Los $\pi^\pm$ emiten luz Cherenkov directamente a lo largo de su trayectoria
y, al desintegrarse, dan muones que también la emiten; los $\pi^0$ se desintegran en dos gammas de unos 70\,MeV que inician cascadas electromagnéticas. Entre 500 y 1000 fotones dominan los $\pi^\pm$ y por encima de 1000 los $\pi^0$.
Sin los eventos con piones, la distribución cae a cero hacia 600 fotones (la fracción de eventos con 500 fotones o más pasa de """ + pct(pi["frac_ge500_todos"], 1) + r""" a """ + pct(pi["frac_ge500_sin_piones"], 2) + r""").

\aviso{Interpretación de la cola. La energía de 500\,MeV está apenas por encima del umbral de producción de piones en colisiones nucleón--nucleón ($\approx$\,290\,MeV),
donde la sección eficaz de producción depende mucho del modelo hadrónico. MEIGA usa el modelo de cascada de Bertini (\texttt{QGSP\_BERT\_HP}, Geant4 10.7.p04).
La explicación más probable es que la simulación de Sidelnik usara otra lista física u otra versión de Geant4 que produce entre 2 y 3 veces menos piones a esta energía.
Esto no se ha comprobado: habría que conocer la versión de Geant4 y la lista física que se usaron en el artículo. En cualquier caso, la cola no afecta el tramo de 0 a 500 fotones,
que corresponde a la moderación y la captura, el objeto de estudio.}
""")
    RZ_ = os.path.join(R, "resultados", "razon_histogramas.json")
    if os.path.exists(RZ_):
        RZ = json.load(open(RZ_))["medios"]
        ETR = {"nacl25": "2,5\\,\\%", "nacl5": "5\\,\\%", "nacl10": "10\\,\\%"}
        def ep_(x):
            e_ = int(np.floor(np.log10(x))); return f(x / 10 ** e_, 1) + r"$\times10^{" + str(e_) + "}$"
        ir("carga", 0)
        w(r"""\section{Curvas de razón NaCl / agua pura (validación cuantitativa)}\label{sec:razon}
Para cuantificar el efecto del NaCl se dividió el histograma de fotones aceptados de cada medio con sal por el de agua pura, en MEIGA y en las curvas digitalizadas de la Fig.~6
(\texttt{razon\_histogramas.py}). Ambos conjuntos tienen el mismo número de neutrones por medio, de modo que se usan cuentas absolutas; los histogramas se agrupan en bines de 50 fotones
y se excluye el primero (0--50 fotones), afectado por la digitalización. Las métricas se calculan en los 19 bines entre 50 y 1000 fotones (Fig.~\ref{fig:razon}).
\begin{table}[H]\centering\small\begin{tabular}{lcccccc}\toprule
NaCl & Pearson $r$ & $p$ & Spearman $\rho$ & RMSE & MAE & Razón media 100--500 (MEIGA / Sidelnik) \\\midrule
""" + "".join(row([ETR[m_], f(v["pearson"], 3), ep_(v["p_pearson"]), f(v["spearman"], 3), f(v["RMSE"], 3), f(v["MAE"], 3),
                   f(v["media_MEIGA_100_500"], 2) + " / " + f(v["media_Sidelnik_100_500"], 2)]) for m_, v in RZ.items()) + r"""\bottomrule\end{tabular}
\caption{Concordancia entre las curvas de razón NaCl / agua pura de MEIGA y de la Fig.~6 de Sidelnik digitalizada.}\label{tab:razon}\end{table}
Las curvas de los dos trabajos tienen la misma forma: la razón es menor que 1 por debajo de $\approx$\,150 fotones (la captura en Cl desplaza eventos hacia más luz), crece hasta un máximo
(MEIGA: """ + ", ".join(f(v["max_MEIGA"], 2) + " en " + f(v["N_max_MEIGA"], 0) + " fotones" for v in RZ.values()) + r"""; Sidelnik: """ + ", ".join(f(v["max_Sidelnik"], 2) + " en " + f(v["N_max_Sidelnik"], 0) for v in RZ.values()) + r""")
y tiende a 1 por encima de $\approx$\,700 fotones, donde dominan los piones. La razón de MEIGA crece de forma monótona con la concentración; en la figura digitalizada, en cambio,
la razón media entre 100 y 500 fotones con 10\,\% es prácticamente igual a la de 5\,\%, aunque su máximo es mayor.
El máximo de MEIGA es algo más alto y está desplazado 0--50 fotones hacia más luz, coherente con el exceso de energía de las cascadas del Cl (Sec.~\ref{sec:cascadas_cl}).
""" + fig("fig22_razon_histogramas", "Razón entre los histogramas de fotones aceptados de cada medio con NaCl y el de agua pura: MEIGA (puntos con error estadístico) y Fig.~6 de Sidelnik digitalizada (líneas discontinuas), bines de 50 fotones.").replace("\\end{figure}", "\\label{fig:razon}\\end{figure}"))
    ir("carga", 1)
    w(r"""\section{Aporte: el histograma de carga en el PMT}
El eje de la Fig.~6 del artículo corresponde a los fotones Cherenkov aceptados por la eficiencia cuántica. Su escala y su forma coinciden con los fotones aceptados al crearse, antes del transporte óptico, y no con la carga en el PMT, unas 16 veces menor: la figura no parece incluir la colección óptica, aunque el artículo no lo especifica (Sec.~\ref{sec:diag}). La magnitud que mide el detector es la carga en el PMT,
que incluye el transporte de cada fotón por el agua y sus reflexiones en el Tyvek hasta llegar al fotocátodo (Sec.~\ref{sec:diag}).
Ese histograma es el aporte de este trabajo (Fig.~\ref{fig:fig09}, paneles c y d):
\begin{itemize}
\item El """ + pct(qc["frac_ge1"], 1) + r""" de los neutrones deja al menos un fotoelectrón; la mediana es """ + f(qc["mediana"], 0) + r"""\,p.e. y la media """ + f(qc["media"], 1) + r"""\,p.e. (""" + f(hs["MEIGA_carga_media_0_1000"], 1) + r"""\,p.e. contando solo los eventos con carga).
\item Solo el """ + pct(qc["frac_ge100"], 1) + r""" de los eventos supera 100\,p.e. Como llega al PMT alrededor del 6\,\% de los fotones transportados, la distribución se comprime hacia valores bajos y desaparece la cola de cientos de fotones.
\end{itemize}
\aviso{La escala del histograma de carga depende del modelo óptico del Tyvek y de la longitud de absorción del agua: con la reflectividad de LHAASO (0,985) y una longitud de absorción de 100\,m,
la carga media subiría hasta unas 2,5 veces. El histograma de fotones aceptados (comparación con la Fig.~6) no depende del transporte óptico y no cambia.
La carga debe tomarse como definitiva solo después de fijar el modelo del Tyvek.}
""")
    w(r"""\begin{figure}[H]\centering\includegraphics[width=\linewidth]{../figuras/fig09_histograma_tipo_sidelnik.pdf}\caption{(a, b) Fotones aceptados por la eficiencia cuántica antes del transporte óptico, frente a la Fig.~6 de Sidelnik (área igualada y normalizado en escala logarítmica).
(c) Histograma de carga en el PMT, con transporte óptico. (d) Efecto del transporte óptico: fotones aceptados frente a fotoelectrones. Eventos con al menos un fotón o fotoelectrón.}\label{fig:fig09}\end{figure}
""")
ir("captura", 0)
IP = {m_: json.load(open(os.path.join(R, "resultados", f"inelasticas_primario_{m_}.json"))) for m_ in M
      if os.path.exists(os.path.join(R, "resultados", f"inelasticas_primario_{m_}.json"))}
if "pura" in IP:
    a_ = IP["pura"]; b_ = IP.get("nacl25", a_); dp, db = a_["destino_primario"], b_["destino_primario"]
    mu = a_["multiplicidad_media"]; ea = a_["energia_total_media_MeV"]
    w(r"""\section{Interacciones del neutrón primario}\label{sec:primario}
Antes de la captura conviene seguir al neutrón de 500\,MeV (la traza 1 de Geant4; \texttt{inelasticas\_primario.py}, que lee \texttt{interacciones-neutrones.tsv} y \texttt{secundarias-inelastica-neutron.tsv}).
El núcleo blanco de cada inelástica se deduce por conservación de la carga y del número bariónico de los productos; los isótopos $^{17}$O (""" + pct(a_["blanco_en_medio"].get("O17", 0), 2) + r""") y $^{18}$O (""" + pct(a_["blanco_en_medio"].get("O18", 0), 2) + r""") aparecen con su abundancia natural, lo que valida la reconstrucción.
\begin{table}[H]\centering\small\begin{tabular}{l""" + "c" * len(IP) + r"""}\toprule
Destino del neutrón primario & """ + " & ".join({"pura": "Agua pura", "nacl25": "2,5\\,\\%", "nacl5": "5\\,\\%", "nacl10": "10\\,\\%"}[m_] for m_ in IP) + r""" \\\midrule
""" + row(["Atraviesa el tanque sin interactuar"] + [pct(IP[m_]["destino_primario"]["sin interacción"], 1) for m_ in IP])
      + row(["Interacción inelástica (la traza termina)"] + [pct(IP[m_]["destino_primario"]["neutronInelastic"], 1) for m_ in IP])
      + row(["Solo dispersiones elásticas y sale"] + [pct(IP[m_]["destino_primario"]["solo elásticas"], 1) for m_ in IP])
      + row(["Solo elásticas y es capturado (misma traza)"] + [pct(IP[m_]["destino_primario"]["nCapture"], 2) for m_ in IP])
      + r"""\midrule """ + row(["Inelástica en el medio"] + [pct(sum(v for k, v in IP[m_]["material"].items() if k.startswith(("Water", "SaltyWater"))), 1) for m_ in IP])
      + row(["Inelástica en el acero"] + [pct(IP[m_]["material"].get("G4_STAINLESS-STEEL", 0), 2) for m_ in IP])
      + row(["Inelástica en el aire"] + [pct(IP[m_]["material"].get("Air", 0), 2) for m_ in IP])
      + row(["Blanco en el medio: $^{16}$O"] + [pct(IP[m_]["blanco_en_medio"]["O16"], 1) for m_ in IP])
      + row(["Blanco en el medio: $^{1}$H"] + [pct(IP[m_]["blanco_en_medio"]["H1"], 1) for m_ in IP])
      + row(["Blanco en el medio: $^{35}$Cl + $^{37}$Cl + $^{23}$Na"] + [pct(sum(IP[m_]["blanco_en_medio"].get(k, 0) for k in ("Cl35", "Cl37", "Na23")), 2) if m_ != "pura" else "--" for m_ in IP])
      + row(["Profundidad media de la inelástica [cm]"] + [f(IP[m_]["prof_media_cm"], 1) for m_ in IP])
      + r"""\bottomrule\end{tabular}\caption{Qué le ocurre al neutrón primario de 500\,MeV y dónde y con quién tiene su interacción inelástica (150\,000 neutrones por medio).}\label{tab:primario}\end{table}
\paragraph{Proceso.} El primario solo sufre tres procesos: dispersión elástica (\texttt{hadElastic}), interacción inelástica (\texttt{neutronInelastic}) y, raramente, captura.
En la inelástica, el modelo de cascada intranuclear de Bertini (\texttt{QGSP\_BERT\_HP}, por encima de $\approx$\,20\,MeV) destruye la traza del primario y crea trazas nuevas para todos los productos;
por eso el primario como tal solo se captura en el """ + pct(dp["nCapture"], 2) + r""" de los casos (Sec.~\ref{sec:nacl25} y la definición de la probabilidad de captura de Sidelnik).
Ocurre casi siempre a la energía inicial (mediana """ + f(a_["E_primario_mediana_MeV"], 0) + r"""\,MeV): las elásticas previas son pocas (el """ + pct(a_["elasticas_antes_de_la_inelastica"].get("0", 0) / a_["inelasticas"], 0) + r""" no tiene ninguna) y casi no frenan al neutrón.
\paragraph{Dónde y con quién.} El """ + pct(a_["material"].get("Water_TS_H_of_Water", 0), 0) + r""" de las inelásticas ocurre en el agua, distribuidas en todo el tanque y decreciendo con la profundidad (camino libre medio inelástico $\approx$\,1\,m, Fig.~\ref{fig:primario}a);
el resto, en el acero de la pared de entrada ($^{56}$Fe, $^{52}$Cr, $^{58}$Ni) y en el aire. En el agua el blanco es $^{16}$O en el """ + pct(a_["blanco_en_medio"]["O16"], 0) + r""" de los casos y $^{1}$H en el """ + pct(a_["blanco_en_medio"]["H1"], 1) + r"""
(la colisión n--p inelástica requiere producir un pion). Con NaCl, el Cl y el Na son el blanco en solo el """ + ", ".join(pct(sum(IP[m_]["blanco_en_medio"].get(k, 0) for k in ("Cl35", "Cl37", "Na23")), 1) for m_ in IP if m_ != "pura") + r""" de las inelásticas (""" + ", ".join({"nacl25": "2,5", "nacl5": "5", "nacl10": "10"}[m_] for m_ in IP if m_ != "pura") + r"""\,\% NaCl): la sal no cambia la fase de alta energía, solo la captura.
\paragraph{Resultados.} Cada inelástica produce en promedio """ + f(mu["neutron"], 2) + r""" neutrones, """ + f(mu["proton"], 2) + r""" protones, """ + f(mu["alpha"], 2) + r""" partículas $\alpha$, """ + f(mu["deuteron"], 2) + r""" deuterones, """ + f(mu["gamma"], 1) + r""" gammas de desexcitación
y """ + f(mu["pi+"] + mu["pi-"] + mu["pi0"], 2) + r""" piones, y deja un núcleo residual en el """ + pct(mu["núcleo residual"], 0) + r""" de los casos ($^{12}$C, $^{15}$N, $^{15}$O, $^{14}$N, $^{8}$Be; Fig.~\ref{fig:primario}d).
La energía se reparte sobre todo en neutrones (""" + f(ea["neutron"], 0) + r"""\,MeV por inelástica) y protones (""" + f(ea["proton"], 0) + r"""\,MeV): el neutrón más energético se lleva en mediana el """ + pct(a_["neutron_lider_frac_E_mediana"], 0) + r""" de la energía incidente
y puede producir a su vez otra inelástica (de ahí, junto con los demás neutrones rápidos, los """ + f(FC["pura"]["neutrones_por_primario"], 2) + r""" neutrones por evento). Los neutrones que terminan capturados son los de evaporación, de pocos MeV, que se moderan en el agua.
Los núcleos residuales $\beta^+$ ($^{15}$O, """ + pct(a_["nucleos_residuales"].get("O15", 0), 0) + r"""; $^{13}$N y $^{11}$C) son la fuente de la línea de 0,511\,MeV de larga vida discutida en la Sec.~\ref{sec:fig3},
y los gammas de desexcitación del $^{12}$C, $^{15}$N y $^{16}$O forman el fondo de 4--7\,MeV de la Sec.~\ref{sec:interp_fig5}.
Las multiplicidades y los núcleos residuales son iguales en los dos medios dentro del 2\,\%.
""")
    w(r"""\begin{figure}[H]\centering\includegraphics[width=\linewidth]{../figuras/fig20_inelasticas_primario.pdf}\caption{Interacciones inelásticas del neutrón primario de 500\,MeV: (a) profundidad a lo largo del haz en el medio; (b) multiplicidad media de los productos; (c) espectro de energía de los productos en agua pura; (d) núcleos residuales más frecuentes.}\label{fig:primario}\end{figure}
""")
    PC = {m_: json.load(open(os.path.join(R, "resultados", f"primario_y_captura_{m_}.json"))) for m_ in M
          if os.path.exists(os.path.join(R, "resultados", f"primario_y_captura_{m_}.json"))}
    if "pura" in PC and "nacl25" in PC and "nacl25" in FC:
        c0, c1, f0, f1 = PC["pura"], PC["nacl25"], FC["pura"], FC["nacl25"]
        pb0, pb1 = f0["P_b_capturas_sobre_todos_los_neutrones"], f1["P_b_capturas_sobre_todos_los_neutrones"]
        sg = lambda p_, n_: np.sqrt(p_ * (1 - p_) / n_)
        MM_ = [m_ for m_ in ("pura", "nacl25", "nacl5", "nacl10") if m_ in PC and m_ in FC and m_ in IP]
        ETQ_ = {"pura": "agua pura", "nacl25": "2,5\\,\\% NaCl", "nacl5": "5\\,\\% NaCl", "nacl10": "10\\,\\% NaCl"}

        def lista_m(fn):
            """'a (agua pura), b (2,5 % NaCl) y c (5 % NaCl)' con los medios disponibles"""
            t = [f"{fn(m_)} ({ETQ_[m_]})" for m_ in MM_]
            return t[0] if len(t) == 1 else ", ".join(t[:-1]) + " y " + t[-1]

        def inel_(m_):
            return IP[m_]["destino_primario"]["neutronInelastic"]

        def sale_(m_):
            return IP[m_]["destino_primario"]["sin interacción"] + IP[m_]["destino_primario"]["solo elásticas"]
        d_ = (pb1 - pb0) / np.hypot(sg(pb0, f0["neutrones_totales"]), sg(pb1, f1["neutrones_totales"]))
        w(r"""\section{¿Desaparece el primario? Consecuencias para la comparación con Sidelnik}\label{sec:primario_captura}
\paragraph{El primario casi nunca es el neutrón capturado.} De los primarios, el """ + lista_m(lambda m_: pct(inel_(m_), 1)) + r""" desaparece en una inelástica y el """ + lista_m(lambda m_: pct(sale_(m_), 1)) + r""" sale del tanque;
solo el """ + lista_m(lambda m_: pct(PC[m_]["primario_capturado"], 2)) + r""" se captura como la misma traza, después de frenarse únicamente por dispersiones elásticas.
En cambio, en el """ + lista_m(lambda m_: pct(PC[m_]["frac_eventos_captura_con_inel_primario"], 1)) + r""" de los eventos con captura el primario tuvo antes una inelástica: los neutrones capturados son los secundarios, sobre todo los de evaporación, que se moderan en el agua;
por cada primario hay """ + lista_m(lambda m_: f(FC[m_]["neutrones_por_primario"] - 1, 2)) + r""" neutrones secundarios. Los eventos con captura tienen en promedio """ + lista_m(lambda m_: f(PC[m_]["capturas_por_evento_con_captura"], 2)) + r""" capturas.
Las diferencias entre medios son pequeñas (menos de 1,5 puntos porcentuales): con más sal el primario sufre algo más de inelásticas y escapa menos, hay algo más de neutrones secundarios y aumenta el número de capturas por evento, en parte porque el cloro captura neutrones que en agua pura escaparían del tanque.
Este comportamiento no es propio de MEIGA: es el de cualquier simulación con Geant4, incluida la de Sidelnik, porque los modelos de cascada intranuclear terminan la traza incidente y crean trazas nuevas para todos los productos.
Físicamente, además, los neutrones son indistinguibles: después de la inelástica no tiene sentido preguntar si se capturó ``el primario''.
\paragraph{Por eso nuestros resultados no contradicen a Sidelnik.} El """ + pct(c0["primario_capturado"], 2) + r""" mide la numeración de las trazas, no la física, y no es comparable con el 25,18\,\% del artículo.
La magnitud comparable es el número de capturas en el agua dividido por todos los neutrones del evento (primario + secundarios):
\begin{table}[H]\centering\small\begin{tabular}{l""" + "c" * len([m_ for m_ in ("pura", "nacl25", "nacl5", "nacl10") if m_ in PC and m_ in FC]) + r"""}\toprule
 & """ + " & ".join({"pura": "Agua pura", "nacl25": "2,5\\,\\% NaCl", "nacl5": "5\\,\\% NaCl", "nacl10": "10\\,\\% NaCl"}[m_] for m_ in [m_ for m_ in ("pura", "nacl25", "nacl5", "nacl10") if m_ in PC and m_ in FC]) + r""" \\\midrule
""" + row(["Primario capturado (misma traza)"] + [pct(PC[m_]["primario_capturado"], 2) for m_ in [m_ for m_ in ("pura", "nacl25", "nacl5", "nacl10") if m_ in PC and m_ in FC]])
      + row(["Neutrones incidentes con $\\geq 1$ captura en el agua"] + [pct(PC[m_]["eventos_con_captura"], 1) for m_ in [m_ for m_ in ("pura", "nacl25", "nacl5", "nacl10") if m_ in PC and m_ in FC]])
      + row(["\\textbf{Capturas / neutrones del evento (MEIGA)}"] + ["\\textbf{" + pct(FC[m_]["P_b_capturas_sobre_todos_los_neutrones"], 2) + "}" for m_ in [m_ for m_ in ("pura", "nacl25", "nacl5", "nacl10") if m_ in PC and m_ in FC]])
      + row(["\\textit{Sidelnik: probabilidad de captura}"] + ["\\textit{" + f(SID[m_][0], 2) + "\\,\\%}" for m_ in [m_ for m_ in ("pura", "nacl25", "nacl5", "nacl10") if m_ in PC and m_ in FC]])
      + row(["Aumento relativo con NaCl (MEIGA)"] + ["--" if m_ == "pura" else f"{100 * (FC[m_]['P_b_capturas_sobre_todos_los_neutrones'] / pb0 - 1):+.1f}".replace(".", ",") + "\\,\\%" for m_ in [m_ for m_ in ("pura", "nacl25", "nacl5", "nacl10") if m_ in PC and m_ in FC]])
      + row(["\\textit{Aumento relativo con NaCl (Sidelnik)}"] + ["--" if m_ == "pura" else "\\textit{" + f"{100 * (SID[m_][0] / SID['pura'][0] - 1):+.1f}".replace(".", ",") + "\\,\\%}" for m_ in [m_ for m_ in ("pura", "nacl25", "nacl5", "nacl10") if m_ in PC and m_ in FC]])
      + r"""\bottomrule\end{tabular}\caption{Tres formas de medir la captura. Solo la tercera es comparable con la Tabla~2 de Sidelnik.}\label{tab:defs_captura}\end{table}
En agua pura MEIGA queda """ + f(100 * (0.2518 - pb0), 1) + r""" puntos por debajo del artículo (un """ + f(100 * (0.2518 / pb0 - 1), 0) + r"""\,\% relativo), una diferencia razonable entre dos simulaciones con versiones y modelos hadrónicos distintos
(Bertini produce más piones y más gammas de desexcitación nuclear, Secs.~\ref{sec:fig6} y \ref{sec:interp_fig5}).
La diferencia que sí debe discutirse es el efecto de la sal: la fracción aumenta un """ + ", ".join(f(100 * (FC[m_]["P_b_capturas_sobre_todos_los_neutrones"] / pb0 - 1), 1) + "\\,\\% (" + {"nacl25": "2,5", "nacl5": "5", "nacl10": "10"}[m_] + "\\,\\%)" for m_ in ("nacl25", "nacl5", "nacl10") if m_ in FC) + r""" en MEIGA (con 2,5\,\%, significativo a $\approx$\,""" + f(d_, 0) + r"""\,$\sigma$) frente al """ + ", ".join(f(100 * (SID[m_][0] / SID["pura"][0] - 1), 1) + "\\,\\%" for m_ in ("nacl25", "nacl5", "nacl10") if m_ in FC) + r""" del artículo: la tendencia es la misma, pero unas dos veces más débil.
No es un error de nuestros datos: todos los medios usan la misma física y la misma geometría, y el tiempo de captura con NaCl sigue el valor teórico de las secciones eficaces térmicas (Sec.~\ref{sec:nacl25}; con 2,5\,\% NaCl, """ + f(S["nacl25"]["tau_captura_us"], 0) + r"""\,µs frente a 147\,µs).
Puede deberse a diferencias en las secciones eficaces del Cl o en la moderación entre las dos simulaciones, o a la normalización de Sidelnik, que el artículo no detalla.
\aviso{Recomendación para la tesis: reportar dos magnitudes y dejar el """ + pct(c0["primario_capturado"], 2) + r""" solo como nota metodológica:
(i) capturas por neutrón del evento, comparable con Sidelnik (""" + lista_m(lambda m_: pct(FC[m_]["P_b_capturas_sobre_todos_los_neutrones"], 1)) + r"""), y
(ii) fracción de neutrones incidentes que producen al menos una captura, que es la relevante para la eficiencia del detector (""" + lista_m(lambda m_: pct(PC[m_]["eventos_con_captura"], 1)) + r""").}
""")
ir("captura", 0.5)
EL = {m_: json.load(open(os.path.join(R, "resultados", f"elasticas_{m_}.json"))) for m_ in M if os.path.exists(os.path.join(R, "resultados", f"elasticas_{m_}.json"))}
if "pura" in EL:
    e0 = EL["pura"]; e1 = EL.get("nacl25", e0); r0 = e0["por_rango"]; r1 = e1["por_rango"]
    MEL = [m_ for m_ in ("pura", "nacl25", "nacl5", "nacl10") if m_ in EL]
    na_cl = lambda m_: sum(v for k, v in EL[m_]["blanco_cin_global"].items() if k in ("Na", "Cl")) / sum(v for k, v in EL[m_]["blanco_cin_global"].items() if k in ("H", "O", "Na", "Cl"))
    ER = json.load(open(os.path.join(R, "resultados", "elasticas_resumen.json")))
    bc = lambda r_, k_: pct(r_["blanco_cin"].get(k_, 0), 1)
    w(r"""\section{Dispersiones elásticas: reconstrucción de los vértices}\label{sec:elasticas}
Las dispersiones elásticas (\texttt{hadElastic}) son las que moderan los neutrones antes de la captura. Se reconstruyeron todos los vértices elásticos de todos los neutrones
(\texttt{elasticas\_vertices.py}): """ + ", ".join(f"{EL[m_]['vertices']:,}".replace(",", "\\,") + " " + {"pura": "en agua pura", "nacl25": "con 2,5\\,\\% NaCl", "nacl5": "con 5\\,\\% NaCl", "nacl10": "con 10\\,\\% NaCl"}[m_] + " (" + f(EL[m_]["elasticas_por_neutron_primario"], 0) + " por neutrón incidente)" for m_ in MEL[:-1]) + (" y " if len(MEL) > 1 else "") + (f"{EL[MEL[-1]]['vertices']:,}".replace(",", "\\,") + " " + {"pura": "en agua pura", "nacl25": "con 2,5\\,\\% NaCl", "nacl5": "con 5\\,\\% NaCl", "nacl10": "con 10\\,\\% NaCl"}[MEL[-1]] + " (" + f(EL[MEL[-1]]["elasticas_por_neutron_primario"], 0) + " por neutrón incidente)" if len(MEL) > 1 else "") + r""".
Con sal hay menos vértices porque el Cl captura antes a los neutrones térmicos: la fracción de vértices por debajo de 1\,eV es del """ + ", ".join(pct(EL[m_]["por_rango"]["< 1 eV"]["vertices"] / EL[m_]["vertices"], 0) for m_ in MEL[:-1]) + " y " + pct(EL[MEL[-1]]["por_rango"]["< 1 eV"]["vertices"] / EL[MEL[-1]]["vertices"], 0) + r""" (""" + ", ".join({"pura": "agua pura", "nacl25": "2,5\\,\\% NaCl", "nacl5": "5\\,\\% NaCl", "nacl10": "10\\,\\% NaCl"}[m_] for m_ in MEL) + r""", respectivamente).
La cinemática (masas reconstruidas, decrementos $\xi$ y conservación) coincide en """ + ("los tres medios" if len(MEL) == 3 else "todos los medios") + r""" dentro de 0,002, por lo que las cifras que siguen son las del agua pura. Cada vértice es $n(E_{\rm in},\hat d_{\rm in}) + (A,Z) \to n(E_{\rm out},\hat d_{\rm out}) + (A,Z)_{\rm retroceso}$:
el neutrón entrante y el saliente se toman de \texttt{pasos-neutrones.tsv} (el vértice es el extremo del paso \texttt{hadElastic} y la dirección de salida, la del paso siguiente)
y el núcleo de retroceso, de \texttt{pasos-particulas.tsv} (partícula creada por \texttt{hadElastic}), enlazado por evento, traza madre y posición.
\paragraph{Con quién: el blanco reconstruido solo con el neutrón.} Con la transferencia de impulso $\vec q = \vec p_{\rm in} - \vec p_{\rm out}$ y la de energía $T = E_{\rm in} - E_{\rm out}$, la masa del blanco es $M = (q^2 - T^2)/(2T)$, sin usar el retroceso.
Por encima de 20\,MeV la mediana es """ + f(r0["> 20 MeV"]["M_cin_mediana_H"], 2) + r"""\,MeV para el H (masa del protón: 938,27) y """ + f(r0["> 20 MeV"]["M_cin_mediana_O16"], 1) + r"""\,MeV para el O (masa nuclear del $^{16}$O: 14\,895,1);
por debajo de 20\,MeV resulta """ + f(r0["1 - 20 MeV"]["M_cin_mediana_H"], 2) + " y " + f(r0["1 - 20 MeV"]["M_cin_mediana_O16"], 1) + r"""\,MeV, las masas \emph{atómicas} del $^1$H y del $^{16}$O (núcleo + electrones):
el modelo de alta precisión (\texttt{G4NeutronHP}, $<20$\,MeV) usa masas atómicas y el de alta energía, masas nucleares. Donde hay retroceso registrado, el blanco cinemático coincide con la partícula de retroceso en el """ + pct(r0["1 - 20 MeV"]["acuerdo_cin_retroceso"], 2) + r""" de los vértices.
La composición por energía (Fig.~\ref{fig:elasticas}a) sigue las secciones eficaces: el H domina por debajo de 1\,MeV (""" + bc(r0["1 keV - 1 MeV"], "H") + r""" de las colisiones entre 1\,keV y 1\,MeV), el O gana peso por encima (""" + bc(r0["> 20 MeV"], "O") + r""" sobre 20\,MeV),
y con sal el Na y el Cl son el blanco en solo el """ + ", ".join(pct(na_cl(m_), 1) + " (" + {"nacl25": "2,5\\,\\%", "nacl5": "5\\,\\%", "nacl10": "10\\,\\%"}[m_] + ")" for m_ in MEL if m_ != "pura") + r""" de las colisiones: la sal cambia la captura, no la moderación.
\paragraph{Energía y ángulo.} Para el H la fracción de energía perdida es uniforme entre 0 y 1 y para el $^{16}$O, uniforme entre 0 y """ + f(ER["perdida_max_O_teoria"], 3) + r""" (Fig.~\ref{fig:elasticas}c), lo que corresponde a una dispersión isótropa en el centro de masas.
El decremento logarítmico medio $\xi = \langle\ln(E/E')\rangle$ medido es """ + f(r0["1 keV - 1 MeV"]["xi_H_cin"], 3) + r""" para el H (teoría: 1) y """ + f(r0["1 keV - 1 MeV"]["xi_O_cin"], 3) + r""" para el O (teoría: """ + f(ER["xi_O_teoria"], 3) + r""") entre 1\,keV y 1\,MeV.
Por encima de unos MeV la dispersión en el O se vuelve hacia adelante (difracción) y $\xi_O$ cae a """ + f(r0["> 20 MeV"]["xi_O_cin"], 3) + r""" sobre 20\,MeV (Fig.~\ref{fig:elasticas}d,e): el neutrón de 500\,MeV apenas se frena en el O y se modera casi solo en el H.
\paragraph{Neutrones térmicos.} El """ + pct(r0["< 1 eV"]["vertices"] / e0["vertices"], 0) + r""" de los vértices ocurre por debajo de 1\,eV, donde los neutrones difunden hasta capturarse. Allí el blanco no está en reposo (modelo de gas libre; esta corrida no usa $S(\alpha,\beta)$):
el """ + pct(r0["< 1 eV"]["frac_ganan_energia"], 0) + r""" de las colisiones aumenta la energía del neutrón y la reconstrucción con el blanco en reposo no es válida. Geant4 no registra el núcleo de retroceso por debajo de $\approx$\,1\,keV.
\paragraph{Leyes de conservación.} En cada vértice con retroceso la energía se conserva dentro de una parte en $10^3$ en el """ + pct(e0["conservacion"]["energia_|dE|/Ein<1e-3"], 3) + r""" de los casos (el residuo de $\sim$\,$5\times10^{-4}$ proviene de la convención de masas atómicas)
y el impulso, dentro del 1\,\% en el """ + pct(e0["conservacion"]["impulso_|dp|/p<1e-2"], 1) + r""" (mediana $""" + f"{e0['conservacion']['impulso_mediana']:.1e}".replace(".", "{,}").replace("e-0", r"\times10^{-") + r"""}$; el resto tiene la dirección del retroceso mal definida por un primer paso muy corto; Fig.~\ref{fig:elasticas}f).
La carga, el número bariónico y el leptónico se conservan exactamente: el estado inicial y el final son el mismo neutrón y el mismo núcleo ($A$ y $Z$ iguales, sin leptones),
y no aparecen núcleos de retroceso distintos de los del medio ($p$, $^{16,17,18}$O, $^{23}$Na, $^{35,37}$Cl) salvo en el Tyvek ($^{12}$C), en el acero ($^{56}$Fe, $^{52}$Cr), en el aire ($^{14}$N) y algunos deuterones del $^2$H natural del agua.
\begin{table}[H]\centering\small\begin{tabular}{lcccc}\toprule
Energía del neutrón & Vértices (agua pura) & Blanco H / O & $\xi_H$ & $\xi_O$ \\\midrule
""")
    for k_ in ["1 eV - 1 keV", "1 keV - 1 MeV", "1 - 20 MeV", "> 20 MeV"]:
        v_ = r0[k_]
        w(row([k_.replace(" - ", "--").replace("> ", "$>$\\,"), f"{v_['vertices']:,}".replace(",", "\\,"), bc(v_, "H") + " / " + bc(v_, "O"), f(v_["xi_H_cin"], 3), f(v_["xi_O_cin"], 3)]))
    w(r"""\midrule """ + row(["Teoría (dispersión isótropa en el CM)", "", "", "1,000", f(ER["xi_O_teoria"], 3)]) + r"""\bottomrule\end{tabular}
\caption{Vértices elásticos por intervalo de energía, blanco reconstruido por cinemática y decremento logarítmico medio. Por debajo de 1\,eV (""" + f"{r0['< 1 eV']['vertices']:,}".replace(",", "\\,") + r""" vértices) el blanco térmico no está en reposo y no se reconstruye.}\label{tab:elasticas}\end{table}
""")
    w(r"""\begin{figure}[H]\centering\includegraphics[width=\linewidth]{../figuras/fig21_elasticas.pdf}\caption{Reconstrucción de los vértices de dispersión elástica: (a) blanco según la energía del neutrón; (b) masa del blanco deducida solo de la cinemática del neutrón; (c) fracción de energía perdida por colisión en H y $^{16}$O frente a la teoría; (d) ángulo de dispersión en el laboratorio; (e) decremento logarítmico medio $\xi$; (f) balance de energía e impulso en cada vértice.}\label{fig:elasticas}\end{figure}
""")
    if os.path.exists(os.path.join(R, "figuras", "fig23_esquema_cinematica_elastica.pdf")):
        w(r"""\paragraph{Esquema de la cinemática.} La Fig.~\ref{fig:esquema_cin} explica gráficamente estos resultados: con el H (masa casi igual a la del neutrón) neutrón y protón salen perpendiculares y el neutrón nunca retrocede; con el $^{16}$O el neutrón puede rebotar pero conserva al menos el 78\,\% de su energía.
El diagrama de velocidades muestra el porqué: la velocidad final es $\vec V_{CM} + \vec u\,'$, con $\vec u\,'$ isótropa sobre un círculo de radio $u' = Av/(A+1)$; para el H el círculo pasa por el origen y para el O lo encierra.
Por encima de 20\,MeV solo el O dispersa hacia adelante (difracción); el H sigue cercano a la dispersión isótropa en el CM.
\begin{figure}[H]\centering\includegraphics[width=\linewidth]{../figuras/fig23_esquema_cinematica_elastica.pdf}\caption{Cinemática de la dispersión elástica: (a) colisión con $^1$H; (b) colisión con $^{16}$O (velocidad del retroceso $\times$3); (c) diagrama de velocidades; (d) energía final uniforme entre $\alpha E$ y $E$; (e) $\cos\theta_{\rm lab}$ entre 1\,keV y 1\,MeV, teoría frente a MEIGA (agua pura); (f) por encima de 20\,MeV.}\label{fig:esquema_cin}\end{figure}
""")
ir("captura", 0.6)
CN = {m_: json.load(open(os.path.join(R, "resultados", f"canales_{m_}.json"))) for m_ in M if os.path.exists(os.path.join(R, "resultados", f"canales_{m_}.json"))}
if CN and EL:
    import re as _re
    SUP = lambda t: _re.sub(r"([A-Z][a-z]?)(\d+)", r"$^{\2}$\1", t)
    def ecu(c):                                      # O16(n,np)N15 -> 16O(n,np)15N con superindices
        mm = _re.match(r"([A-Za-z]+\d+)\(n,([^)]*)\)(.*)", c)
        if not mm:
            return c
        x = mm.group(2).replace("π⁺", r"$\pi^+$").replace("π⁻", r"$\pi^-$").replace("π⁰", r"$\pi^0$").replace("α", r"$\alpha$").replace("³He", r"$^3$He")
        return SUP(mm.group(1)) + "(n," + x + ")" + (SUP(mm.group(3)) if mm.group(3) else "")
    CAPL = {"H": ("$^1$H(n,$\\gamma$)$^2$H", 2.2246, "2224 (MEIGA: 2224,4)"), "O16": ("$^{16}$O(n,$\\gamma$)$^{17}$O", 4.1431, "871, 1088, 2184; $\\gamma$ único 4143"),
            "Cl35": ("$^{35}$Cl(n,$\\gamma$)$^{36}$Cl", 8.5798, "517, 788, 1165, 1951, 6111, 7414; $\\gamma$ único 8580"),
            "Cl37": ("$^{37}$Cl(n,$\\gamma$)$^{38}$Cl", 6.1078, "638, 755, 1692; $\\gamma$ único 6108"), "Na23": ("$^{23}$Na(n,$\\gamma$)$^{24}$Na", 6.9594, "472 (0,9\\,\\%); $\\gamma$ único 6959")}
    w(r"""\section{Ecuaciones, energías y porcentajes de todos los procesos}\label{sec:procesos_resumen}
Las tablas completas de reacciones de cada medio (ecuación, valor $Q$, energía típica del neutrón, porcentaje y gammas emitidos) están en el Apéndice~\ref{sec:procesos}.
Explican de dónde vienen los gammas, y por tanto los electrones y la luz Cherenkov: la dispersión elástica en H modera ($\xi = 1$), la captura en H y en $^{35}$Cl produce los gammas de captura,
y las inelásticas en $^{16}$O (canales (n,n$'$), (n,n$\alpha$), (n,np), (n,2n) y los de fragmentación a más de 20\,MeV) producen el fondo de desexcitación nuclear y los emisores $\beta^+$.
""")
    ir("apx", 0)
    w(r"""\section{Ecuaciones, energías y porcentajes de todos los procesos}\label{sec:procesos}
Las Tablas~\ref{tab:procesos_pura}--\ref{tab:procesos_nacl10} reúnen, para cada medio, todas las reacciones de los neutrones en el volumen del detector (primario y secundarios): la ecuación,
el valor $Q$ del estado fundamental (calculado con los excesos de masa AME2020; $Q<0$ es la energía umbral que se gasta en romper el núcleo), la energía típica del neutrón incidente,
el porcentaje dentro de cada tipo de proceso y los gammas que emite (\texttt{canales\_reaccion.py}; el blanco de cada inelástica se deduce por conservación de la carga y del número bariónico).
En las inelásticas, las \emph{líneas} solo se atribuyen si pertenecen al núcleo residual o al blanco de esa misma reacción (ventana de $\pm10$\,keV).
""")
    for m_ in [x for x in ["pura", "nacl25", "nacl5", "nacl10"] if x in CN and x in EL]:
        C_, E_, S_ = CN[m_], EL[m_], S[m_]
        bcg = {k: v for k, v in E_["blanco_cin_global"].items() if k in ("H", "O", "Na", "Cl")}; tb = sum(bcg.values())
        nc = sum(v[0] for v in S_["capturas_agua_por_nucleo"].values())
        w(r"""{\footnotesize\begin{longtable}{p{4.4cm}rrrp{4.6cm}}
\caption{""" + ET.get(m_, m_) + r""": ecuaciones, energías y porcentajes de los procesos de los neutrones (150\,000 neutrones de 500\,MeV).}\label{tab:procesos_""" + m_ + r"""}\\\toprule
Reacción & $Q$ [MeV] & $E_n$ típica & \% & Gammas / resultado (keV) \\\midrule\endfirsthead
\toprule Reacción & $Q$ [MeV] & $E_n$ típica & \% & Gammas / resultado (keV) \\\midrule\endhead
\multicolumn{5}{l}{\textbf{Dispersión elástica} (""" + f(E_["elasticas_por_neutron_primario"], 0) + r""" por neutrón incidente; \% de las colisiones con blanco reconstruido, $E>1$\,eV)}\\
""")
        for k_, ec, perd in [("H", "$^1$H(n,n)$^1$H", "pierde 0--100\\,\\% de $E$; $\\xi = 1{,}00$"), ("O", "$^{16}$O(n,n)$^{16}$O", "pierde 0--22\\,\\%; $\\xi = 0{,}12$ ($<$\\,1\\,MeV)"),
                            ("Na", "$^{23}$Na(n,n)$^{23}$Na", "pierde 0--16\\,\\%"), ("Cl", "$^{35,37}$Cl(n,n)$^{35,37}$Cl", "pierde 0--11\\,\\%")]:
            if bcg.get(k_, 0) / tb > 0.0005 and (k_ in ("H", "O") or m_ != "pura"):
                w(ec + " & 0 & todas & " + pct(bcg[k_] / tb, 2) + " & " + perd + r" \\" + "\n")
        w(r"""\midrule\multicolumn{5}{l}{\textbf{Captura radiativa} (""" + f(S_["capturas_por_neutron_agua"], 3) + r""" por neutrón incidente; \% de las capturas en el agua)}\\
""")
        for k_, v_ in sorted(S_["capturas_agua_por_nucleo"].items(), key=lambda kv: -kv[1][0]):
            if k_ in CAPL:
                ec, q_, gl = CAPL[k_]
                w(ec + " & +" + f(q_, 3) + " & térmica & " + pct(v_[1], 2) + " & " + gl + r" \\" + "\n")
        w(r"""\midrule\multicolumn{5}{l}{\textbf{Inelástica} (""" + f(C_["inelasticas_por_neutron_incidente"], 2) + r""" por neutrón incidente; \% de las inelásticas; canales con más del 0,4\,\%""" + ("" if m_ == "pura" else r""" y los del Na y el Cl""") + r""")}\\
""")
        for c in C_["canales"]:
            sal = c["canal"].startswith(("Na", "Cl"))
            if (c["frac"] < 0.004 and not (sal and c["frac"] >= 0.0005)) or c["canal"].startswith(("incompleto", "?")):
                continue
            lin = ", ".join(f"{l.split()[0]} ({100 * fr:.0f}\\,\\%)" for l, fr in c["lineas"][:3]) if c["lineas"] else ("sin $\\gamma$ directos" if c["gammas_por_reaccion"] < 0.05 else "continuo")
            e_ = c["E_n_mediana_MeV"]
            En = (f(e_, 0) + "\\,MeV" if e_ >= 1 else (f(e_ * 1e3, 0) + "\\,keV" if e_ >= 1e-3 else ("térmica" if e_ < 1e-6 else f(e_ * 1e6, 1) + "\\,eV"))) + (f" ({100 * c['frac_E_menor_20MeV']:.0f}\\,\\% $<$\\,20)" if c["frac_E_menor_20MeV"] > 0.05 else "")
            w(ecu(c["canal"]) + " & " + (f(c["Q_MeV"], 2) if c["Q_MeV"] is not None else "--") + " & " + En + " & " + pct(c["frac"], 1)
              + " & " + f(c["gammas_por_reaccion"], 1) + r" $\gamma$/reacc.; " + lin + r" \\" + "\n")
        w(r"""\bottomrule\end{longtable}}
""")
    ir("captura", 0.6)
    c0 = CN["pura"]; r47 = c0["gammas_4_7_MeV_por_residual"]
    w(r"""\paragraph{De dónde salen los gammas de 4--7\,MeV.} Cada inelástica emite en promedio """ + f(c0["gammas_4_7_MeV_por_inelastica"], 2) + r""" gammas entre 4 y 7\,MeV.
Según el núcleo que los emite: $^{16}$O """ + pct(r47.get("O16", 0), 0) + r""" (dispersión inelástica $^{16}$O(n,n$'$)), $^{12}$C """ + pct(r47.get("C12", 0), 0) + r""" ($^{16}$O(n,n$\alpha$)$^{12}$C y canales de fragmentación),
$^{15}$N """ + pct(r47.get("N15", 0), 0) + r""" ($^{16}$O(n,np)$^{15}$N), $^{14}$N """ + pct(r47.get("N14", 0), 0) + r""" y $^{15}$O """ + pct(r47.get("O15", 0), 0) + r""" ($^{16}$O(n,2n)$^{15}$O).
Pero solo el """ + pct(1 - c0["gammas_4_7_MeV_lineas"].get("continuo / otras", 0), 0) + r""" son líneas discretas: 6130\,keV del $^{16}$O (""" + pct(c0["gammas_4_7_MeV_lineas"].get("6130 (O16)", 0), 1) + r"""), 4439\,keV del $^{12}$C (""" + pct(c0["gammas_4_7_MeV_lineas"].get("4439 (C12)", 0), 1) + r"""),
6917\,keV del $^{16}$O (""" + pct(c0["gammas_4_7_MeV_lineas"].get("6917 (O16)", 0), 1) + r""") y, con menos del 0,3\,\% cada una, las del $^{15}$N (5269, 5298, 6324\,keV), $^{15}$O (5183, 5241, 6176) y $^{14}$N (5106).
La razón es el modelo: el """ + pct(c0["gammas_4_7_MeV_frac_de_n_menor_20MeV"], 0) + r""" de estos gammas viene de neutrones de menos de 20\,MeV, tratados con los datos evaluados de \texttt{G4NeutronHP}, y entre ellos el """ + pct(c0["gammas_4_7_MeV_frac_lineas_si_En_menor_20"], 0) + r""" son líneas;
el resto viene de reacciones de más de 20\,MeV (cascada de Bertini), cuya desexcitación es estadística y produce un continuo (solo el """ + pct(c0["gammas_4_7_MeV_frac_lineas_si_En_mayor_20"], 0) + r""" son líneas).
Por eso el fondo de 4--7\,MeV de la Sec.~\ref{sec:interp_fig5} es sobre todo un continuo de desexcitación con unas pocas líneas encima, y su intensidad depende del modelo de cascada.
""")
ir("captura", 3)
if "nacl25" in S and os.path.exists(os.path.join(R, "resultados", "cascadas_cloro_nacl25.json")):
    import pandas as pd
    a0, a1 = S["pura"], S["nacl25"]
    G1 = json.load(open(os.path.join(R, "resultados", "espectro_gamma_tipo_sidelnik_nacl25.json")))
    K = json.load(open(os.path.join(R, "resultados", "cascadas_cloro_nacl25.json")))["Z17A35"]
    D0, D1 = (json.load(open(os.path.join(R, "resultados", f"diagnostico_{m_}.json"))) for m_ in ("pura", "nacl25"))
    H6 = json.load(open(os.path.join(R, "resultados", "histograma_tipo_sidelnik.json")))
    F6 = pd.read_csv(os.path.join(R, "resultados", "figura6_cuentas_por_intervalo.csv"))
    def c6(m_, iv):
        r_ = F6[(F6.medio == m_) & (F6.intervalo == iv)].iloc[0]; return r_.MEIGA_cuentas, r_.Sidelnik_cuentas
    rel = lambda x0, x1: f"{100 * (x1 / x0 - 1):+.1f}".replace(".", ",") + r"\,\%"
    P0, P1 = a0["P_al_menos_1_captura_agua"], a1["P_al_menos_1_captura_agua"]
    SAL = [m_ for m_ in ("nacl25", "nacl5", "nacl10") if m_ in S]
    WN = {"nacl25": (0.025, 1.01604), "nacl5": (0.05, 1.03401), "nacl10": (0.10, 1.07051)}
    def teoria(m_):
        """tau y fraccion de capturas en 35Cl con secciones eficaces termicas (1/v: independientes de la energia)"""
        w_, rho = WN.get(m_, (0.0, 0.9982)); NA = 6.02214e23
        nH = rho * (1 - w_) / 18.015 * NA * 2; nO = rho * (1 - w_) / 18.015 * NA; nS = rho * w_ / 58.443 * NA
        sig = {"H": 0.3326 * nH, "O": 0.00019 * nO, "Na": 0.530 * nS, "Cl35": 43.6 * 0.7576 * nS, "Cl37": 0.433 * 0.2424 * nS}
        tot = sum(sig.values()) * 1e-24                       # cm^-1
        return 1 / (tot * 2.2e5) * 1e6, sig["Cl35"] * 1e-24 / tot   # tau [us], fraccion en 35Cl
    cols = ["pura"] + SAL
    ETc = {"pura": "Agua pura", "nacl25": "2,5\\,\\%", "nacl5": "5\\,\\%", "nacl10": "10\\,\\%"}
    def fila(nombre, fn, rel_=True):
        v0 = fn("pura")
        celdas = [nombre, fn("pura", txt=True)]
        for m_ in SAL:
            celdas.append(fn(m_, txt=True) + ((" (" + rel(v0, fn(m_)) + ")") if rel_ and v0 else ""))
        return row(celdas)
    def g(clave, k=None, d=3, pc=False):
        def fn(m_, txt=False):
            v = S[m_][clave] if k is None else S[m_][clave][k]
            v = v[0] if isinstance(v, list) else v
            return (pct(v, d) if pc else f(v, d)) if txt else v
        return fn
    def sid(i_, d=2, unidad=""):
        def fn(m_, txt=False):
            v = SID[m_][i_]
            return f(v, d) + unidad if txt else v
        return fn
    def nuc(n_):
        def fn(m_, txt=False):
            v = S[m_]["capturas_agua_por_nucleo"].get(n_, [0, 0])[1]
            return pct(v, 1) if txt else v
        return fn
    def tau_t(m_, txt=False):
        v = teoria(m_)[0]; return f(v, 0) if txt else v
    def cl_t(m_, txt=False):
        v = teoria(m_)[1]; return pct(v, 1) if txt else v
    w(r"""\section{Efecto del NaCl en la captura}\label{sec:nacl25}
Las corridas con NaCl usan exactamente el mismo esquema que la de agua pura (física sin $S(\alpha,\beta)$, Tyvek y PMT iguales; 150\,000 neutrones cada una); solo cambia el medio
(composición de la Ec.~3.12 y densidad e índice de refracción de la Tabla~3.6). Por eso las diferencias entre medios se deben al NaCl, y su comparación con las tendencias de Sidelnik
es válida aunque el modelo óptico del Tyvek se revise después. Entre paréntesis, el cambio relativo respecto al agua pura.
\begin{table}[H]\centering\small\begin{tabular}{l""" + "c" * len(cols) + r"""}\toprule
 & """ + " & ".join(ETc[c_] for c_ in cols) + r""" \\\midrule
""" + fila("Capturas / neutrones del evento (MEIGA)", lambda m_, txt=False: (pct(FC[m_]["P_b_capturas_sobre_todos_los_neutrones"], 2) if txt else FC[m_]["P_b_capturas_sobre_todos_los_neutrones"]))
      + fila("\\textit{Sidelnik: probabilidad de captura}", sid(0, 2, "\\,\\%"))
      + fila("Neutrones incidentes con $\\geq 1$ captura", g("P_al_menos_1_captura_agua", d=2, pc=True))
      + fila("Capturas por neutrón incidente", g("capturas_por_neutron_agua"))
      + fila("Capturas en H", nuc("H"), False) + fila("Capturas en $^{35}$Cl (MEIGA)", nuc("Cl35"), False)
      + fila("\\quad teoría (secciones eficaces térmicas)", cl_t, False)
      + fila("Capturas en $^{23}$Na / $^{37}$Cl", lambda m_, txt=False: (nuc("Na23")(m_, True) + " / " + nuc("Cl37")(m_, True)) if txt else 0, False)
      + fila("Tiempo de captura $\\tau$ [µs] (MEIGA)", g("tau_captura_us", d=0))
      + fila("\\quad teoría [µs]", tau_t)
      + fila("Vértice $\\to$ captura, máximo [cm]", g("d_vertice_max_cm", d=1))
      + fila("\\textit{Sidelnik: distancia de máxima absorción [cm]}", sid(1, 1))
      + fila("Energía de gammas de captura por neutrón [MeV]", g("E_gamma_captura_por_neutron_MeV", d=2))
      + r"""\bottomrule\end{tabular}\caption{Captura en los distintos medios (MEIGA, 150\,000 neutrones de 500\,MeV por medio) frente a las tendencias de Sidelnik.}\label{tab:nacl}\end{table}
Las tendencias tienen el signo del artículo y son monótonas con la concentración: aumenta la fracción de captura y se acorta la distancia de captura. El aumento de la fracción de captura es menor que en el artículo
(""" + ", ".join(ETc[m_] + ": " + rel(FC["pura"]["P_b_capturas_sobre_todos_los_neutrones"], FC[m_]["P_b_capturas_sobre_todos_los_neutrones"]) + " frente a " + rel(SID["pura"][0], SID[m_][0]) for m_ in SAL) + r"""),
mientras que el tiempo de captura sigue la predicción de las secciones eficaces térmicas (""" + ", ".join(ETc[m_] + ": " + f(S[m_]["tau_captura_us"], 0) + " frente a " + f(teoria(m_)[0], 0) + "\\,µs" for m_ in SAL) + r""").
La fracción de capturas en $^{35}$Cl es mayor que la que dan esas secciones eficaces (""" + ", ".join(ETc[m_] + ": " + pct(S[m_]["capturas_agua_por_nucleo"]["Cl35"][1], 1) + " frente a " + pct(teoria(m_)[1], 1) for m_ in SAL) + r"""),
un exceso ya observado en las campañas anteriores con G4NDL\,4.6.
""")
    hf, sf = c6("nacl25", "100-500"); hp, sp_ = c6("pura", "100-500")
    ir("luz", 3)
    w(r"""\section{Efecto del NaCl en la luz Cherenkov (Fig. 6 de Sidelnik)}
Con el mismo observable de la Sec.~\ref{sec:fig6} (fotones aceptados por la eficiencia cuántica, antes del transporte óptico), MEIGA reproduce el efecto del NaCl que muestra la Fig.~6:
las curvas con NaCl quedan por encima de la de agua pura, más cuanto mayor es la concentración, entre $\approx$\,150 y 550 fotones (Fig.~\ref{fig:fig6nacl}), por la luz adicional de las capturas en Cl, y por encima de 600 fotones las dos curvas coinciden (piones).
Entre 100 y 500 fotones las cuentas aumentan """ + "; ".join(ETc[m_] + ": " + rel(hp, c6(m_, "100-500")[0]) + " en MEIGA y " + rel(sp_, c6(m_, "100-500")[1]) + " en el artículo" for m_ in SAL if (F6.medio == m_).any()) + r""";
la correlación de forma con la curva correspondiente de Sidelnik es """ + ", ".join(f(H6[m_]["aceptados_QE"]["corr_forma_Sidelnik_0_1000"], 3) for m_ in SAL if m_ in H6) + r""".
Los fotones Cherenkov creados por neutrón pasan de """ + f(S["pura"]["fotones_cherenkov_por_neutron"][0], 0) + " (agua pura) a " + ", ".join(f(S[m_]["fotones_cherenkov_por_neutron"][0], 0) + " (" + ETc[m_] + ")" for m_ in SAL) + r""",
y la carga media de """ + f(a0["Q_media"][0], 2) + " a " + ", ".join(f(S[m_]["Q_media"][0], 2) for m_ in SAL) + r"""\,p.e. (""" + ", ".join(rel(a0["Q_media"][0], S[m_]["Q_media"][0]) for m_ in SAL) + r""").
\begin{figure}[H]\centering\includegraphics[width=\linewidth]{../figuras/fig10_figura6_sidelnik_vs_meiga.pdf}\caption{Fig.~6 de Sidelnik (izquierda) y MEIGA (derecha) en todos los medios simulados; 150\,000 neutrones en cada medio.}\label{fig:fig6nacl}\end{figure}
""")
    PE_ = os.path.join(R, "resultados", "piones_efecto_nacl.json")
    if os.path.exists(PE_):
        PE = json.load(open(PE_))["medios"]; MS_ = [m_ for m_ in ("nacl25", "nacl5", "nacl10") if m_ in PE]
        ETP = {"nacl25": "2,5\\,\\%", "nacl5": "5\\,\\%", "nacl10": "10\\,\\%"}
        w(r"""\paragraph{¿Cuánto del déficit se debe a los piones?} Se marcó cada neutrón cuyo árbol contiene una inelástica con producción de $\pi^\pm$ o $\pi^0$ (\texttt{piones\_efecto\_nacl.py}): son el """ + ", ".join(pct(PE[m_]["frac_eventos_con_piones"], 1) for m_ in ["pura"] + MS_) + r""" de los eventos (agua pura, """ + ", ".join(ETP[m_] for m_ in MS_) + r"""), igual en todos los medios.
Sin esos eventos el aumento de cuentas entre 100 y 500 fotones pasa de """ + ", ".join(f(PE[m_]["aumento_todos_pct"], 1) + " a " + f(PE[m_]["aumento_sin_piones_pct"], 1) + "\\,\\% (" + ETP[m_] + ")" for m_ in MS_) + r""", frente a """ + ", ".join(f(PE[m_]["aumento_Sidelnik_pct"], 1) + "\\,\\%" for m_ in MS_) + r""" en el artículo.
Los piones explican, por tanto, solo una parte del déficit con 2,5 y 5\,\% (unos 3 y 6 puntos de los 23 y 24 que faltan): el exceso de cuentas que aporta la sal casi no cambia al quitarlos, lo que cambia es el fondo de agua pura con el que se divide.
El resto del déficit debe atribuirse al fondo de desexcitación nuclear tras las inelásticas, $\approx$\,1,6 veces mayor por captura en H en MEIGA (Sec.~\ref{sec:interp_fig5}), y al menor aumento de la probabilidad de captura con la sal (Sec.~\ref{sec:nacl25}); ambos dependen del modelo hadrónico y de los datos de captura, y solo pueden probarse con nuevas corridas.
Con 10\,\% MEIGA ya supera al artículo y la diferencia crece sin piones, consistente con la anomalía de la curva de 10\,\% del artículo (que apenas supera a la de 5\,\%).
""" + fig("fig24_piones_efecto_nacl", "Efecto del NaCl en la Fig.~6 con y sin los eventos con producción de piones: (a) razón NaCl/agua pura de los fotones aceptados; (b) aumento de cuentas entre 100 y 500 fotones respecto al agua pura, MEIGA (todos los eventos y sin piones) frente a Sidelnik."))
    L = G1["lineas_sobre_2223"]
    GL = {m_: json.load(open(os.path.join(R, "resultados", f"espectro_gamma_tipo_sidelnik_{m_}.json")))["lineas_sobre_2223"] for m_ in SAL
          if os.path.exists(os.path.join(R, "resultados", f"espectro_gamma_tipo_sidelnik_{m_}.json"))}
    ir("gamma", 3)
    w(r"""\section{Líneas del cloro (Fig. 3 de Sidelnik)}\label{sec:cl_lineas}
\begin{table}[H]\centering\small\begin{tabular}{l""" + "cc" * len(GL) + r"""}\toprule
 & """ + " & ".join(r"\multicolumn{2}{c}{" + ETc[m_] + "}" for m_ in GL) + r""" \\
Línea [MeV] / 2,223\,MeV & """ + " & ".join(["Sidelnik & MEIGA"] * len(GL)) + r""" \\\midrule
""")
    for k_ in L:
        w(row([k_.replace(",", "{,}")] + [x for m_ in GL for x in (f(GL[m_][k_]["Sidelnik"], 3), f(GL[m_][k_]["MEIGA"], 3))]))
    w(r"""\bottomrule\end{tabular}\caption{Altura de las líneas respecto a la de 2,223\,MeV en los medios con NaCl. La digitalización (25,6\,keV por píxel) no separa 0,511/0,517 ni 6,11/6,13\,MeV.}\end{table}
Las líneas de la cascada del $^{36}$Cl de 1,165, 6,11, 7,41 y 7,79\,MeV coinciden con el artículo dentro del 3--10\,\%: la proporción de capturas en Cl respecto a H y la intensidad de esas transiciones
son las mismas en las dos simulaciones. La línea de 1,951\,MeV queda algo por debajo (en la figura del artículo se superpone con la de 1,959\,MeV).
Hay dos diferencias: la línea de 0,511\,MeV, más intensa por las mismas causas que en agua pura (emisores $\beta^+$ de larga vida y piones), y la de 8,58\,MeV, unas """ + f(L["8,58 (Cl)"]["MEIGA"] / L["8,58 (Cl)"]["Sidelnik"], 0) + r""" veces más intensa en MEIGA.
""")
    w(fig("fig11_espectro_gamma_tipo_sidelnik_nacl25", "Espectro gamma en agua + 2,5\\,\\% NaCl: (a) formato de la Fig.~3 de Sidelnik; (b) comparación con su curva digitalizada; (c) composición por proceso; (d) cocientes de las líneas con la de 2,223\\,MeV."))
    ir("captura", 7)
    w(r"""\section{Las cascadas del $^{35}$Cl en Geant4 no conservan la energía}\label{sec:cascadas_cl}
La captura en $^{35}$Cl libera $Q=8{,}579$\,MeV, que en la naturaleza se reparte en una cascada de 3--4 gammas; la transición directa al estado fundamental (un solo gamma de 8,58\,MeV) ocurre en $\approx$\,3\,\% de las capturas.
En MEIGA (Geant4 10.7.p04, G4NDL\,4.6) las """ + f"{K['capturas']:,}".replace(",", "\\,") + r""" capturas en $^{35}$Cl emiten en promedio """ + f(K["gammas_por_captura"], 2) + r""" gammas con una energía total media de """ + f(K["suma_media_MeV"], 2) + r"""\,MeV
(percentiles 5--95: """ + f(K["suma_p5_p50_p95"][0], 1) + "--" + f(K["suma_p5_p50_p95"][2], 1) + r"""\,MeV): solo el """ + pct(K["frac_suma_igual_Q_1pct"], 0) + r""" de las cascadas suma $Q$ (dentro del 1\,\%), el """ + pct(K["frac_suma_mayor_Q"], 0) + r""" emite más energía y el """ + pct(K["frac_suma_menor_Q"], 0) + r""" menos,
y el """ + pct(K["frac_un_solo_gamma"], 0) + r""" de las capturas emite un único gamma de 8,58\,MeV. Esto explica el exceso de la línea de 8,58\,MeV. Las capturas en H, en cambio, emiten siempre un gamma de 2,224\,MeV.
\aviso{Consecuencia: en los medios con NaCl la luz de las capturas en Cl tiene, en promedio, un """ + f(100 * (K["suma_media_MeV"] / 8.579 - 1), 0) + r"""\,\% más de energía de la que corresponde, y con una dispersión que no es física.
Es un defecto del modelo de captura de Geant4/G4NDL, independiente del Tyvek; afecta a la escala de luz y de carga de los medios con NaCl y debe declararse en la tesis. Las intensidades de las líneas intermedias (1,165, 6,11, 7,41, 7,79\,MeV) sí coinciden con Sidelnik.}
""")
    w(fig("fig12_cascadas_cloro_nacl25", "Energía total emitida por captura y multiplicidad de la cascada en $^{35}$Cl, $^{23}$Na y $^{1}$H (agua + 2,5\\,\\% NaCl, MEIGA)."))
    lc = os.path.join(R, "resultados", "lineas_captura_nucleo.csv")
    ir("captura", 4)
    if os.path.exists(lc):
        import pandas as pd
        LC = pd.read_csv(lc); cl = LC[LC.reaccion == "35Cl(n,g)36Cl"]
        KC = json.load(open(os.path.join(R, "resultados", "cascadas_cloro_nacl25.json")))["Z17A35"]
        fsn = float(cl[cl.E_keV.between(8579, 8581)].por_100_capturas.iloc[0]) / 100      # fraccion con el gamma unico de S_n
        C_sin_sn = (KC["suma_media_MeV"] - fsn * 8.5798) / (1 - fsn)
        REF = {1164.86: 26.8, 517.07: 22.8, 6110.98: 19.8, 1951.13: 19.1, 788.42: 16.3, 1959.34: 12.3, 7414.09: 9.9, 786.30: 10.3, 7790.45: 8.0, 8578.70: 2.7}   # ENSDF (Nica et al. 2012)
        w(r"""\section{Espectros de captura por núcleo (Fig. 4.1 de la tesis)}\label{sec:captura_nucleo}
La Fig.~\ref{fig:captnucleo} reproduce la Fig.~4.1 de la tesis con estas corridas: gammas emitidos en cada captura, enlazados con el núcleo que capturó el neutrón.
La línea del H se ajusta a una gaussiana con $\mu = """ + f"{float(LC[LC.reaccion == '1H(n,g)2H'].E_keV.iloc[0]):.5f}".replace(".", "{,}") + r"""$\,keV y $\sigma \approx 0{,}013$\,keV, los mismos valores de la Fig.~4.1 (2224,37301\,keV; 0,01285\,keV). El gamma de Geant4 tiene $E_\gamma \approx S_n(^2{\rm H}) = 2224{,}57$\,keV menos 0,2\,keV, mientras que el valor medido es 2223,25\,keV ($S_n$ menos el retroceso del deuterón, 1,32\,keV):
la línea de MEIGA está 1,1\,keV por encima de la real y, como el deuterón recibe además su energía de retroceso (Sec.~\ref{sec:deut}), cada captura en H libera $\approx$\,1,1\,keV más que $S_n$. El efecto es irrelevante para la luz, pero conviene citarlo junto a la Fig.~4.1(b).
\begin{table}[H]\centering\small\begin{tabular}{rcc}\toprule
Línea del $^{35}$Cl(n,$\gamma$) [keV] & MEIGA [por 100 capturas] & Referencia ENSDF [por 100 capturas] \\\midrule
""")
        for _, r_ in cl.sort_values("por_100_capturas", ascending=False).head(10).iterrows():
            rf = min(REF, key=lambda e: abs(e - r_.E_keV))
            w(row([f(r_.E_keV, 1), f(r_.por_100_capturas, 1), f(REF[rf], 1) if abs(rf - r_.E_keV) < 0.5 else "-- (no existe)"]))
        w(r"""\bottomrule\end{tabular}\caption{Intensidad de las líneas principales de la captura en $^{35}$Cl (""" + f"{int(cl.capturas.iloc[0]):,}".replace(",", "\\,") + r""" capturas). Referencia: evaluación ENSDF (Nica et al.~2012), intensidades PGAA/OIEA por 100 capturas.}\end{table}
Las líneas de la cascada (517, 788, 1165, 1951, 6111, 7414\,keV) tienen, por captura, intensidades muy cercanas a las de referencia; la excepción es un gamma de 8579,8\,keV, presente en el """ + f(float(cl[cl.E_keV.between(8579, 8581)].por_100_capturas.iloc[0]), 0) + r"""\,\% de las capturas, que no es la transición real al fundamental (8578,70\,keV, 2,7\,\%, bien reproducida) sino un gamma único con toda la energía $S_n$ (Sec.~\ref{sec:esquemas}).
En esas capturas el gamma sale solo (y conserva la energía), mientras que en las demás los gammas de la cascada se sortean de forma independiente: su suma vale en promedio """ + f(C_sin_sn, 1) + r"""\,MeV y menos del 1\,\% suma $Q$.
Es el comportamiento del modelo de captura de alta precisión de Geant4 (\texttt{G4NeutronHP}), que toma los gammas de las tablas de producción de fotones de la evaluación (ENDF/G4NDL) sin imponer la conservación de la energía en cada captura;
Geant4 permite en cambio usar \texttt{G4PhotonEvaporation}, que genera cascadas que sí la conservan (variable de entorno \texttt{G4NEUTRONHP\_USE\_ONLY\_PHOTONEVAPORATION}). En la Fig.~4.1(c) de la tesis, obtenida con otra simulación, la línea de 8,58\,MeV es pequeña.
Los paneles (a) y (d) tienen poca estadística (""" + str(int(LC[LC.reaccion == "16O(n,g)17O"].capturas.iloc[0])) + r""" capturas en $^{16}$O en agua pura y """ + str(int(LC[LC.reaccion == "37Cl(n,g)38Cl"].capturas.iloc[0])) + r""" en $^{37}$Cl con 2,5\,\% NaCl).
""")
        w(r"""\begin{figure}[H]\centering\includegraphics[width=\linewidth]{../figuras/fig15_espectros_captura_nucleo.pdf}\caption{Espectros gamma de la captura de neutrones por núcleo (formato de la Fig.~4.1 de la tesis): (a) $^{16}$O(n,$\gamma$)$^{17}$O en agua pura; (b) $^{1}$H(n,$\gamma$)$^{2}$H con ajuste gaussiano; (c) $^{35}$Cl(n,$\gamma$)$^{36}$Cl y (d) $^{37}$Cl(n,$\gamma$)$^{38}$Cl en agua + 2,5\,\% NaCl. Intensidad en fotones por 100 capturas; los rombos son los valores de referencia (Firestone y Révay 2016 para $^{16}$O; ENSDF, Nica et al.~2012, para $^{35}$Cl) y las marcas negras en (d) las energías de la Tabla~4.2. Las etiquetas dan, en keV, la energía de referencia de cada línea (las de la Tabla~4.2 unificada, Sec.~\ref{sec:tabla42}); en magenta, el gamma único de $S_n$ que emite Geant4.}\label{fig:captnucleo}\end{figure}
""")
        tj = os.path.join(R, "resultados", "tabla_parametros_nucleares.json")
        ir("captura", 6)
        if os.path.exists(tj):
            TN = json.load(open(tj))
            NOM = {"1H": "$^{1}$H", "16O": "$^{16}$O", "35Cl": "$^{35}$Cl", "23Na": "$^{23}$Na", "37Cl": "$^{37}$Cl"}
            w(r"""\section{Parámetros nucleares y líneas de captura (Tabla 4.2 de la tesis)}\label{sec:tabla42}
La Tabla~\ref{tab:tabla42} reproduce la Tabla~4.2 de la tesis (abundancias, sección eficaz térmica de captura radiativa $\sigma_0$ y energías de las líneas $\gamma$, contrastadas con CapGam/NNDC;
para $^{16}$O, Firestone y Révay 2016). Las energías marcadas con $^\dagger$ se corrigieron para que coincidan con las de las figuras de este informe (ver la leyenda). La última columna da la misma transición en MEIGA (a menos de 0,4\,keV; para el H, la línea de Geant4 está 1,1\,keV por encima) y su intensidad por 100 capturas en ese isótopo.
\begin{table}[H]\centering\footnotesize
\begin{tabular}{cccrr}\toprule
\multicolumn{5}{c}{\textbf{Parámetros nucleares y líneas $\gamma$ de captura}}\\\midrule
\textbf{Isótopo} & \textbf{\shortstack{Abundancia\\isotópica (\%)}} & \textbf{$\sigma_0$ (mb)} & \textbf{$E_\gamma$ (keV)} & \textbf{\shortstack{MEIGA: $E_\gamma$ (keV)\\(por 100 capturas)}}\\\midrule
""")
            corr = []
            for k_, (iso, v) in enumerate(TN.items()):
                fondo = r"\rowcolor{gray!15}" if k_ % 2 == 0 else ""
                for i_, l in enumerate(v["lineas"]):
                    mg = "--" if l["MEIGA"] is None else f(l["MEIGA"], 2) + r" \;(" + f(l["por_100"], 1) + r"\,\%)"
                    et = f(l["tabla"], 2)
                    if l.get("original"):
                        et += r"$^\dagger$"
                        corr.append(f"{NOM[iso]} {f(l['tabla'], 2)}" + (r"\,keV (añadida)" if l["original"] == "nueva" else r"\,keV (" + f(l["original"], 2) + ")"))
                    col = [NOM[iso], v["abundancia"].replace(".", ","), "$" + v["sigma0_mb"].replace(".", "{,}") + "$"] if i_ == 0 else ["", "", ""]
                    w(fondo + " & ".join(col + [et, mg]) + r" \\" + "\n")
                sn = v.get("gamma_unico_Sn")
                if sn and iso != "1H":
                    w(fondo + r" & \multicolumn{3}{r}{\textcolor{magenta!70!black}{$\gamma$ único de $S_n$ (solo MEIGA)}} & \textcolor{magenta!70!black}{" + f(sn["MEIGA"], 2) + r" \;(" + f(sn["por_100"], 1) + r"\,\%)} \\" + "\n")
                w(r"\midrule" + "\n" if k_ < len(TN) - 1 else "")
            w(r"""\bottomrule\end{tabular}
\caption{Parámetros nucleares de los principales isótopos del volumen activo y energías de las líneas $\gamma$ de captura de neutrones térmicos (Tabla~4.2 de la tesis), y la línea correspondiente en MEIGA
(capturas en el agua de las corridas de todos los medios: """ + ", ".join(f"{NOM[i]} {v['capturas_MEIGA']:,}".replace(",", "\\,") for i, v in TN.items()) + r"""). $\sigma_0$ es la sección eficaz total de captura radiativa térmica del isótopo, no la de producción de cada línea.
$^\dagger$Energías unificadas con las figuras de este informe (Firestone y Révay 2016 para $^{16}$O, como en la Fig.~4.2; ENSDF, Nica et al.~2012, para $^{35}$Cl, como en el esquema de $^{36}$Cl); entre paréntesis, el valor de la Tabla~4.2 original: """ + "; ".join(corr) + r""". En magenta, el gamma único con toda la energía de separación que emite Geant4 (no existe en la naturaleza).}\label{tab:tabla42}\end{table}
{\small\textit{Nota de la tesis:} para $^{16}$O, Firestone y Révay reportan $\sigma_0 = 0{,}170\pm0{,}003$\,mb (2016, Sec.~II.B.1); la transición de $870{,}76\pm0{,}08$\,keV tiene una probabilidad absoluta de emisión $P_\gamma = 96{,}6\pm0{,}5$\,\%
(Tabla~III), mientras que su sección eficaz individual de producción es $\sigma_\gamma = 0{,}164\pm0{,}003$\,mb (Sec.~II.A, Tabla~I). Por tanto $\sigma_0$ y $\sigma_\gamma$ son magnitudes diferentes.}

\paragraph{Observaciones para la tesis.}
\begin{itemize}
\item \textbf{$^{1}$H:} la línea medida es 2223,25\,keV; MEIGA la emite a 2224,37\,keV (1,1\,keV más; Sec.~\ref{sec:captura_nucleo}).
\item \textbf{$^{16}$O:} en la Tabla~4.2 original las energías (1087,86; 2184,44; 3272,15; 4142,73\,keV) no coincidían con las de la Fig.~4.2 (1087,89; 2184,49; 3272,02; 4142,60\,keV), aunque ambas citan a Firestone y Révay (2016); aquí se usan las de la figura.
La transición real de 4142,60\,keV no aparece en MEIGA; en su lugar, el """ + f(TN["16O"]["gamma_unico_Sn"]["por_100"], 1) + r"""\,\% de las capturas emite el gamma único de 4143,09\,keV ($S_n$).
\item \textbf{$^{35}$Cl:} el valor 1959,13\,keV de la tabla original mezclaba dos líneas reales, 1951,13\,keV (19,1 por 100 capturas) y 1959,34\,keV (12,3), que ahora figuran por separado; la transición al fundamental pasa de 8578,21 a 8578,70\,keV (ENSDF)
y la de 6110,84 a 6110,98\,keV. Con estas energías MEIGA reproduce las siete líneas, incluida la del fundamental (2,4 frente a 2,7 por 100 capturas); aparte, el 24\,\% de las capturas emite el gamma único de 8579,81\,keV.
\item \textbf{$^{23}$Na:} MEIGA prácticamente no produce la línea de 472,20\,keV (""" + f(TN["23Na"]["lineas"][0]["por_100"], 1) + r"""\,\%, frente a una línea dominante en la naturaleza): en el """ + f(TN["23Na"]["gamma_unico_Sn"]["por_100"], 0) + r"""\,\% de las capturas emite el gamma único de 6959,4\,keV ($S_n$ de $^{24}$Na) y en el resto gammas de energías dispersas, sin líneas definidas.
\item \textbf{$^{37}$Cl:} también aquí el """ + f(TN["37Cl"]["gamma_unico_Sn"]["por_100"], 0) + r"""\,\% de las capturas emite el gamma único de $S_n$ (6107,9\,keV). Con """ + str(TN["37Cl"]["capturas_MEIGA"]) + r""" capturas aparecen las líneas de 637,5, 755,5 y 1692,2\,keV; las de 788,42, 2166,90 y 4134,13\,keV no aparecen.
\end{itemize}
""")
        oj, cj = (os.path.join(R, "resultados", n) for n in ("intensidades_O17.json", "intensidades_Cl36.json"))
        ir("captura", 5)
        if os.path.exists(oj) and os.path.exists(cj):
            O = json.load(open(oj)); TO = O["transiciones"]; C = json.load(open(cj)); TC = C["transiciones"]
            w(r"""\section{Esquemas de niveles: $^{35}$Cl(n,$\gamma$)$^{36}$Cl y $^{16}$O(n,$\gamma$)$^{17}$O}\label{sec:esquemas}
La Fig.~\ref{fig:Cl36} muestra el esquema de niveles de $^{36}$Cl con las quince transiciones más intensas de la captura de neutrones térmicos en $^{35}$Cl,
con los datos de la evaluación ENSDF (N.~Nica, J.~Cameron y B.~Singh, Nucl.\ Data Sheets 113, 1 (2012); intensidades de la base PGAA del OIEA, convertidas
a fotones por 100 capturas con $\sigma_{Z\gamma} = 33{,}22$\,b). Entre corchetes se dan las intensidades de MEIGA en las """ + f"{C['capturas_Cl35_MEIGA']:,}".replace(",", "\\,") + r""" capturas en $^{35}$Cl.
La Fig.~\ref{fig:O17} muestra lo mismo para $^{17}$O (Fig.~4.2 de la tesis; Firestone y Révay 2016), con las """ + str(O["capturas_O16_MEIGA"]) + r""" capturas en $^{16}$O de todas las corridas.
\paragraph{Lo que reproduce MEIGA.} En el $^{35}$Cl, 13 de las 15 transiciones coinciden con la evaluación dentro de pocos puntos porcentuales, incluidas las primarias
(6110,98\,keV: """ + f(TC["6110.98"]["MEIGA"], 1) + r"""\,\% frente a """ + f(TC["6110.98"]["referencia"], 1) + r"""\,\%; 7414,09\,keV: """ + f(TC["7414.09"]["MEIGA"], 1) + r"""\,\% frente a """ + f(TC["7414.09"]["referencia"], 1) + r"""\,\%)
y la transición directa al fundamental (8578,70\,keV: """ + f(TC["8578.70"]["MEIGA"], 1) + r"""\,\% frente a """ + f(TC["8578.70"]["referencia"], 1) + r"""\,\%). Las excepciones son la línea de 1170,94\,keV (""" + f(TC["1170.94"]["MEIGA"], 1) + r"""\,\% frente a """ + f(TC["1170.94"]["referencia"], 1) + r"""\,\%),
casi ausente en los datos de MEIGA, y la de 788,42\,keV, algo baja. En el $^{16}$O, las transiciones de la cascada coinciden dentro del error estadístico.
\paragraph{Lo que no reproduce: un gamma único con toda la energía de separación.} Además de las transiciones reales, Geant4 emite en el """ + f(C["gamma_unico_Sn_por_100"], 1) + r"""\,\% de las capturas en $^{35}$Cl
un único gamma de 8579,8\,keV, igual a $S_n$ sin la corrección por retroceso del núcleo (la transición real al fundamental tiene 8578,70\,keV). En el $^{16}$O ocurre lo mismo:
el """ + f(O["gamma_unico_Sn_por_100"], 1) + r""" $\pm$ """ + f(O["gamma_unico_Sn_error"], 1) + r"""\,\% de las capturas emite un único gamma de 4143,09\,keV ($S_n$ de $^{17}$O), mientras que la transición real de 4142,60\,keV no aparece
(""" + str(TO["4142.60"]["cuentas"]) + r""" casos, frente a 3,36\,\% esperado). La misma fracción en dos núcleos distintos ($\approx$\,24\,\%) indica que el origen está en el código de captura de Geant4 y no en los datos nucleares.
En el resto de las capturas los gammas de la cascada se sortean de forma independiente: su suma promedia """ + f(C["suma_media_keV"] / 1e3, 1) + r"""\,MeV en el Cl (el promedio incluye las capturas con el gamma único).
Por eso las intensidades por captura de las líneas coinciden con la evaluación mientras la energía depositada por captura no se conserva (Sec.~\ref{sec:nacl25}).
""")
            w(r"""\begin{landscape}\begin{figure}[p]\centering\includegraphics[width=\linewidth,height=0.86\textheight,keepaspectratio]{../figuras/fig19b_esquema_niveles_Cl36_MEIGA.pdf}\caption{Esquema de niveles de $^{36}$Cl y transiciones $\gamma$ más intensas de la captura $^{35}$Cl(n,$\gamma$) con neutrones térmicos (ENSDF, Nica et al.\ 2012; niveles sin escala). Intensidades por 100 capturas; entre corchetes, MEIGA. En magenta, el gamma único de energía $S_n$ que emite Geant4. La versión sin MEIGA está en \texttt{figuras/fig19\_esquema\_niveles\_Cl36}.}\label{fig:Cl36}\end{figure}\end{landscape}
""")
            w(r"""\begin{figure}[H]\centering\includegraphics[width=0.85\linewidth]{../figuras/fig18b_esquema_niveles_O17_MEIGA.pdf}\caption{Esquema de niveles y transiciones $\gamma$ de la captura $^{16}$O(n,$\gamma$)$^{17}$O con neutrones térmicos (Firestone y Révay, Phys.\ Rev.\ C 93, 044311, 2016; CapGam/NNDC) e intensidades por 100 capturas en MEIGA; en magenta, el gamma único de energía $S_n$. La réplica de la Fig.~4.2 está en \texttt{figuras/fig18\_esquema\_niveles\_O17}.}\label{fig:O17}\end{figure}
""")
    dj = os.path.join(R, "resultados", "deuterones_captura.json")
    ir("deut", 1)
    if os.path.exists(dj):
        DJ = json.load(open(dj)); d0 = DJ["pura"]; d1 = DJ.get("nacl25", d0)
        kev = lambda x, n=3: f(1e3 * x, n)
        w(r"""\section{Deuterones de la captura en H (Fig. 4.6 de la tesis)}\label{sec:deut}
En la captura $n + p \to d + \gamma$ el deuterón retrocede con $E_d \simeq E_\gamma^2/(2M_dc^2) = 2{,}2244^2/(2\times1875{,}6)$\,MeV $=""" + kev(d0["E_retroceso_teorico_MeV"], 3) + r"""$\,keV.
La distribución de MEIGA (Fig.~\ref{fig:deut}) tiene su máximo exactamente ahí (mediana """ + kev(d0["mediana_MeV"], 3) + r"""\,keV) y una anchura $\sigma = """ + f(1e6 * d0["sigma_ventana_MeV"], 1) + r"""$\,eV,
que viene del movimiento térmico del neutrón y del protón en el instante de la captura (la misma causa que da a la línea de 2,224\,MeV su anchura de 0,013\,keV).
Las alturas coinciden con la Fig.~4.6: con la sal el pico baja a $\approx$\,0,66 veces el de agua pura porque solo el """ + pct(a1["capturas_agua_por_nucleo"]["H"][1], 0) + r""" de las capturas ocurre en H.
La media y el RMS que se citan en la Fig.~4.6 no describen el pico: los dominan unos pocos deuterones (""" + pct(d0["frac_fuera_ventana"], 2) + r""") de capturas de neutrones aún rápidos, con energías de hasta """ + f(d0["max_MeV"], 1) + r"""\,MeV;
MEIGA da media """ + kev(d0["media_MeV"], 2) + r"""\,keV y RMS """ + kev(d0["RMS_MeV"], 1) + r"""\,keV en agua pura (tesis: 1,48 y 31,3\,keV). Para describir el pico conviene citar la mediana y la $\sigma$ en la ventana de 1,20--1,45\,keV
(""" + kev(d0["media_ventana_MeV"], 3) + r"""\,keV y """ + f(1e6 * d0["sigma_ventana_MeV"], 1) + r"""\,eV en agua pura; """ + kev(d1["media_ventana_MeV"], 3) + r"""\,keV y """ + f(1e6 * d1["sigma_ventana_MeV"], 1) + r"""\,eV con 2,5\,\% NaCl""" + "".join("; " + kev(DJ[m_]["media_ventana_MeV"], 3) + r"\,keV y " + f(1e6 * DJ[m_]["sigma_ventana_MeV"], 1) + r"\,eV con " + {"nacl5": "5", "nacl10": "10"}[m_] + r"\,\% NaCl" for m_ in ("nacl5", "nacl10") if m_ in DJ) + r"""): la mediana no depende del medio y la anchura crece ligeramente con la sal.
""")
        w(r"""\begin{figure}[H]\centering\includegraphics[width=0.85\linewidth]{../figuras/fig16_deuterones_captura.pdf}\caption{Energía de los deuterones producidos en la captura $^1$H(n,$\gamma$)$^2$H (formato de la Fig.~4.6 de la tesis); cuentas por 150\,000 neutrones primarios.}\label{fig:deut}\end{figure}
""")
    ir("carga", 3)
    w(r"""\section{Óptica: mismo transporte en todos los medios y decisión sobre el Tyvek}
El transporte óptico es prácticamente el mismo en los cuatro medios (Fig.~\ref{fig:destino}): llega al PMT el 6,30, 6,39, 6,41 y 6,50\,\% de los fotones transportados (agua pura, 2,5, 5 y 10\,\% NaCl), se absorbe en la pared el 76,7--76,2\,\% y en el agua el 16,4--16,8\,\%, con 7,1--7,3 rebotes medios; la dependencia con la energía del fotón es idéntica. En detalle, llega al PMT el """ + pct(D0["destino"]["PMT"]["frac"], 2) + " (agua pura) y el " + pct(D1["destino"]["PMT"]["frac"], 2) + r""" (2,5\,\% NaCl) de los fotones transportados,
y la probabilidad de absorción por choque con la pared es """ + pct(D0["prob_muerte_por_choque_pared"], 2) + " y " + pct(D1["prob_muerte_por_choque_pared"], 2) + r""". La razón carga/fotón creado no cambia
(""" + f(100 * a0["Q_sobre_fotones"], 3) + " y " + f(100 * a1["Q_sobre_fotones"], 3) + r"""\,\%). Por tanto el modelo del Tyvek fija una escala común de la carga, pero no altera las diferencias entre medios:
el aumento de carga con el NaCl (""" + rel(a0["Q_media"][0], a1["Q_media"][0]) + r""") se debe solo a la mayor producción de luz.
Con el esquema actual las comparaciones con Sidelnik (captura, espectros, Fig.~6 con su mismo observable) y la comparación relativa de la carga entre medios son válidas.
Mantener el Tyvek actual en las corridas de 2,5, 5 y 10\,\% NaCl asegura que los cuatro medios sean comparables con la corrida de agua pura; un Tyvek corregido obligaría a repetir también el agua pura.
""")
ir("fin")
w(r"""\section{Conclusiones preliminares}
\begin{enumerate}
\item La configuración de la corrida es la del artículo: los 150\,000 neutrones parten de $(-49{,}062;\,0;\,66{,}562)$\,cm con 500\,MeV, y la prueba de 10 neutrones verificó materiales, espesores, posición del PMT y física sin $S(\alpha,\beta)$.
\item La física de captura es coherente: """ + pct(p["capturas_agua_por_nucleo"]["H"][1], 2) + r""" de las capturas en H, $\tau = """ + f(p["tau_captura_us"], 0) + r"""$\,µs (teórico $\approx$\,200\,µs para agua pura con H libre) y espectros con las líneas y bordes Compton esperados.
\item La probabilidad de captura de la Tabla~2 de Sidelnik se reproduce si se interpreta como capturas en el agua divididas por todos los neutrones del evento (primario + cascada): """ + (pct(FC["pura"]["P_b_capturas_sobre_todos_los_neutrones"], 2) if "pura" in FC else "--") + r""" frente a 25,18\,\% en agua pura. La captura de la traza primaria (0,88\,\%) no es comparable. La distancia de máxima absorción
solo coincide en escala si se mide desde el vértice del neutrón capturado.
\item La carga en el PMT es baja por la óptica del detector: el """ + pct(json.load(open(os.path.join(R, "resultados", "diagnostico_pura.json")))["destino"]["pared"]["frac"], 0) + r""" de los fotones se absorbe en la pared de Tyvek y solo el 6\,\% llega al PMT. La Fig.~6 de Sidelnik coincide con los fotones aceptados por la eficiencia cuántica antes del transporte, no con la carga del PMT.
\item El espectro gamma reproduce la Fig.~3 de Sidelnik en las líneas de 2,223 y 6,13\,MeV (cociente 0,022 en ambos, sin el $^{16}$N) y en el continuo de 2,5--9\,MeV; la línea de 0,511\,MeV es unas 6 veces más intensa por los emisores $\beta^+$ de larga vida y la producción de piones (Sec.~\ref{sec:fig3}).
\item Con el observable de Sidelnik (Sec.~\ref{sec:fig6}), MEIGA reproduce su Fig.~6 entre 0 y 500 fotones en forma y en cuentas absolutas, sin reescalar. Por encima de 500 fotones MEIGA tiene 2--3 veces más eventos; esa cola se debe casi por completo a eventos con producción de piones, probablemente por diferencias en el modelo hadrónico a 500\,MeV.
\item Medios con NaCl (2,5, 5 y 10\,\%, 150\,000 neutrones cada uno; Secs.~\ref{sec:nacl25} y \ref{sec:razon}): las tendencias con la sal tienen el signo de Sidelnik y son monótonas (más capturas, menor distancia, $\tau$ de 192 a """ + ", ".join(f(S[m_]["tau_captura_us"], 0) for m_ in ("nacl25", "nacl5", "nacl10") if m_ in S) + r"""\,µs, como predicen las secciones eficaces térmicas; luz adicional entre 150 y 550 fotones en la Fig.~6), aunque el aumento de la fracción de captura es unas dos veces menor que en el artículo. Las curvas de razón NaCl/agua pura de la Fig.~6 coinciden con las del artículo ($r \geq 0{,}88$). Las líneas del Cl de 1,165--7,79\,MeV coinciden con el artículo; las cascadas del $^{35}$Cl de Geant4 no conservan la energía (exceso de la línea de 8,58\,MeV); el transporte óptico es idéntico en todos los medios, por lo que el Tyvek no afecta a la comparación entre medios.
\item El espectro de electrones producidos por gammas reproduce la Fig.~5 de Sidelnik en escala absoluta (bines de 20\,keV, cociente $\approx$\,1,06) y en forma, incluidos los bordes Compton y el aumento con NaCl entre 2 y 6\,MeV; solo el borde de 8,33\,MeV difiere, por las cascadas del $^{35}$Cl (Sec.~\ref{sec:fig5}).
\item Las diferencias con la Fig.~5 tienen una explicación física (Sec.~\ref{sec:interp_fig5}): por cada captura en H, MEIGA produce $\approx$\,1,6 veces más gammas de desexcitación nuclear tras la dispersión inelástica de neutrones, lo que reduce el salto en el borde de 1,994\,MeV y diluye el efecto del NaCl entre 2 y 6\,MeV; el exceso entre 7 y 8,3\,MeV se debe a las cascadas del $^{35}$Cl.
\item El aporte nuevo es el histograma de carga en el PMT, que incluye el transporte óptico. Su escala absoluta depende del modelo del Tyvek; las diferencias entre medios no.
\end{enumerate}
\appendix
@@APX@@\section{Reproducibilidad}
\texttt{Analisis-Sidelnik-500MeV/scripts/}: \texttt{procesar\_corrida.py} (lee la corrida del ADATA, 7,5\,min), \texttt{distancias\_alternativas.py},
\texttt{analizar.py}, \texttt{destino\_fotones.py} (78\,GB, 14\,min), \texttt{diagnostico\_carga.py}, \texttt{histograma\_tipo\_sidelnik.py}, \texttt{figura6\_sidelnik\_meiga.py}, \texttt{espectro\_gamma\_pasos.py} (lee \texttt{pasos-gamma.tsv}), \texttt{digitalizar\_fig3.py}, \texttt{cascadas\_cloro.py}, \texttt{digitalizar\_fig5.py}, \texttt{espectro\_electrones\_tipo\_sidelnik.py}, \texttt{origen\_electrones.py}, \texttt{interpretacion\_electrones.py}, \texttt{espectros\_captura\_nucleo.py}, \texttt{deuterones\_captura.py}, \texttt{esquema\_niveles\_O17.py}, \texttt{esquema\_niveles\_Cl36.py}, \texttt{tabla\_parametros\_nucleares.py}, \texttt{inelasticas\_primario.py}, \texttt{figura\_inelasticas\_primario.py}, \texttt{primario\_y\_captura.py}, \texttt{elasticas\_vertices.py} (lee \texttt{pasos-neutrones.tsv} y \texttt{pasos-particulas.tsv}), \texttt{figura\_elasticas.py}, \texttt{canales\_reaccion.py}, \texttt{gammas\_acumulados.py} (lee \texttt{pasos-gamma.tsv} hasta 600\,MeV), \texttt{fig4\_gammas\_acumulados.py}, \texttt{fraccion\_captura\_neutrones.py} (lee \texttt{pasos-neutrones.tsv}), \texttt{espectro\_gamma\_tipo\_sidelnik.py} (lee \texttt{secundarias-inelastica-neutron.tsv} del ADATA para el análisis de piones) y \texttt{escribir\_informe.py}. Curva digitalizada de la Fig.~2 en \texttt{datos/fig2\_agua\_pura\_digitalizada.csv}.
\end{document}
""")
import re
SECC = [("conf", "Configuración de la simulación", "Tabla 4.1"),
        ("captura", "Contribución de los principales núcleos a la captura de neutrones", "Figs. 4.1 y 4.2, Tabla 4.2"),
        ("gamma", "Comparación de los espectros de fotones gamma generados por captura de neutrones", "Figs. 4.3 y 4.4"),
        ("elec", "Comparación de los espectros de electrones y positrones secundarios", "Fig. 4.5"),
        ("deut", "Distribución de energía de los deuterones producidos en la captura de neutrones sobre hidrógeno", "Fig. 4.6"),
        ("luz", "Comparación de la distribución de fotones Cherenkov detectados para neutrones de 500 MeV", "Fig. 4.7"),
        ("carga", "Validación cuantitativa de los histogramas de carga", "Figs. 4.8--4.11, Tabla 4.3")]


def bajar(t):
    t = re.sub(r"\\subsection\{", r"\\subsubsection{", t)
    return re.sub(r"(?<!sub)\\section\{", r"\\subsection{", t)


def bajar_apx(t):
    return t       # en el apendice las tablas se mantienen como \section


def bloque(sec):
    return "".join(t for _, _, _, t in sorted(b for b in BLOQ if b[0] == sec))


salida = bloque("pre")
for k, (sec, tit, ref) in enumerate(SECC, 1):
    cuerpo = bloque(sec)
    if cuerpo.strip():
        salida += "\n\\section{" + tit + "}\n{\\small\\textit{Corresponde a la Sec.~4.1.1." + str(k) + " de la tesis (" + ref + ").}}\n\n" + bajar(cuerpo)
salida += bloque("fin").replace("@@APX@@", bajar_apx(bloque("apx")))
# tablas que exceden el ancho del texto: se reducen al ancho de la linea (las que caben no cambian)
salida = re.sub(r"(\\begin\{table\}\[H\].*?)\\begin\{tabular\}(.*?)\\end\{tabular\}",
                lambda m_: m_.group(1) + r"\begin{adjustbox}{max width=\linewidth}\begin{tabular}" + m_.group(2) + r"\end{tabular}\end{adjustbox}", salida, flags=re.S)
# nombres largos de carpetas de corridas: \url permite cortarlos en cualquier caracter (paquete xurl)
salida = re.sub(r"\\texttt\{([^{}]*-sinSab[^{}]*)\}", lambda m_: r"\url{" + m_.group(1).replace("\\_", "_") + "}", salida)
salida = salida.replace(r"\usepackage[colorlinks=true", r"\usepackage{adjustbox}\usepackage{xurl}\usepackage[colorlinks=true", 1)
open(os.path.join(R, "informe", "Informe-Sidelnik-500MeV-tecnico.tex"), "w").write(salida)   # notas tecnicas; el informe principal es la copia de la Sec. 4.1.1 de la tesis
print("ok")
