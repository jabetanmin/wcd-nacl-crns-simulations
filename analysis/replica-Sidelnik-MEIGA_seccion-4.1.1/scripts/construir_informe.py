#!/usr/bin/env python3
"""Genera el cuerpo del informe del repositorio a partir de la fuente comun con la tesis
(informe/seccion_4_1_1.tex y informe/apendice_procesos.tex), cambiando solo la jerarquia de titulos:
la Sec. 4.1.1 de la tesis pasa a ser la Introduccion (seccion 1), cada subsubseccion 4.1.1.k pasa a ser la
seccion k+1 y el capitulo de apendice pasa a ser el Apendice A. El texto, las figuras, las tablas y las
ecuaciones son los mismos. Escribe informe/cuerpo_informe.tex y informe/apendice_informe.tex, que incluye
informe/Informe-Sidelnik-500MeV.tex (formato de informe)."""
import os, re

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INF = os.path.join(R, "informe")
sec = open(os.path.join(INF, "seccion_4_1_1.tex")).read()
ap = open(os.path.join(INF, "apendice_procesos.tex")).read()
aviso = "% ARCHIVO GENERADO por scripts/construir_informe.py a partir de seccion_4_1_1.tex: no editar aqui.\n"
c = re.sub(r"\\subsection\{Validación numérica mediante reproducción de resultados de referencia\}",
           r"\\section{Introducción y configuración de la simulación}", sec, count=1)
c = c.replace("\\subsubsection{", "\\section{")
c = c.replace("Los resultados de esta sección se obtuvieron", "Los resultados de este informe se obtuvieron")
c = c.replace("definidos al inicio de esta sección", "definidos en la introducción (Sec.~\\ref{sec:Res-WCD-500MeV})")
# la pagina del informe es algo mas alta que la de la tesis: dos figuras se limitan en altura para que quepan con su leyenda
c = c.replace("height=0.83\\textwidth,keepaspectratio]{fig19b", "height=0.70\\textwidth,keepaspectratio]{fig19b")
c = c.replace("[width=\\linewidth]{fig14_origen_electrones.pdf}", "[width=\\linewidth,height=0.78\\textheight,keepaspectratio]{fig14_origen_electrones.pdf}")
open(os.path.join(INF, "cuerpo_informe.tex"), "w").write(aviso + c)
a = ap.replace("\\chapter{", "\\section{", 1)
open(os.path.join(INF, "apendice_informe.tex"), "w").write(aviso.replace("seccion_4_1_1", "apendice_procesos") + a)
print("cuerpo_informe.tex y apendice_informe.tex generados")
