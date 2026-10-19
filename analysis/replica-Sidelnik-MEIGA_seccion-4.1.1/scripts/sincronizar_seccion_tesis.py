#!/usr/bin/env python3
"""Copia la fuente comun de la Sec. 4.1.1 (informe/seccion_4_1_1.tex y informe/apendice_procesos.tex) a:
  1) seccion_4.1.1_tesis/ (documento de revision en formato de tesis);
  2) la version de la tesis con la seccion nueva (TESIS_NUEVA): reemplaza el bloque marcado en
     capitulos/cap4_resultados.tex, ajusta las rutas de las figuras (Figuras-4.1.1/ y Figuras/) y copia las figuras.
Uso: sincronizar_seccion_tesis.py   (ruta de la tesis en TESIS_NUEVA)"""
import os, re, shutil

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
T = os.environ.get("TESIS_NUEVA", os.path.join(R, "..", "..", "Conclusiones-recomendaciones", "plantilla_tesis_definitiva_seccion_4.1.1_nueva"))
INI, FIN = "% ===== Sec. 4.1.1 nueva", "% ===== fin de la Sec. 4.1.1 nueva ====="
sec = open(os.path.join(R, "informe", "seccion_4_1_1.tex")).read()
ap = open(os.path.join(R, "informe", "apendice_procesos.tex")).read()
for f, txt in (("seccion_4_1_1.tex", sec), ("apendice_procesos.tex", ap)):
    open(os.path.join(R, "seccion_4.1.1_tesis", f), "w").write(txt)
print("seccion_4.1.1_tesis/ actualizado")
import subprocess, sys
subprocess.run([sys.executable, os.path.join(R, "scripts", "construir_informe.py")], check=True)
if os.path.isdir(T):
    figs = sorted(set(re.findall(r"\{(fig[0-9A-Za-z_]+\.pdf)\}", sec)))
    os.makedirs(os.path.join(T, "Figuras-4.1.1"), exist_ok=True)
    for f in figs:
        shutil.copy(os.path.join(R, "figuras", f), os.path.join(T, "Figuras-4.1.1", f))
    st = re.sub(r"\{(fig[0-9A-Za-z_]+\.pdf)\}", r"{Figuras-4.1.1/\1}", sec)
    st = re.sub(r"\{(espectro-[a-z]+-ivan\.png)\}", r"{Figuras/\1}", st)
    p = os.path.join(T, "capitulos", "cap4_resultados.tex"); c = open(p).read()
    a = c.index(INI); a = c.index("\n", a) + 1; b = c.index(FIN)
    open(p, "w").write(c[:a] + st.rstrip("\n") + "\n" + c[b:])
    open(os.path.join(T, "apendice_procesos.tex"), "w").write(ap)
    print("tesis actualizada:", T, "-", len(figs), "figuras")
