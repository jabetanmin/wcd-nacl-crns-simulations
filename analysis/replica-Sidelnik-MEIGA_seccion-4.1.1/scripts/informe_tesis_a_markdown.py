#!/usr/bin/env python3
"""Convierte el informe del repositorio (informe/Informe-Sidelnik-500MeV.tex, copia fiel de la Sec. 4.1.1 de la tesis:
incluye seccion_4_1_1.tex y apendice_procesos.tex) en celdas Markdown para el notebook. Una celda por subseccion,
con texto, ecuaciones (MathJax), tablas (Markdown) y figuras (PNG de figuras/ o de informe/Figuras/). La numeracion
de secciones, figuras, tablas y ecuaciones sigue la de la tesis (capitulo 4; apendice A), de modo que las referencias
cruzadas coinciden con el PDF.
Uso como modulo: from informe_tesis_a_markdown import celdas; celdas() -> lista de textos Markdown."""
import os, re

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INF = os.path.join(R, "informe")
TEX = os.path.join(INF, "Informe-Sidelnik-500MeV.tex")
CIT = {"Sidelnik2020": ("Sidelnik et al.", "2020"), "Firestone2016": ("Firestone y Révay", "2016"),
       "NNDC16OCapGam": ("National Nuclear Data Center", "2025"), "Nica2012": ("Nica et al.", "2012"),
       "Betancourt2026WCDNaCl": ("Betancourt", "2026")}


def arg(s, i, a="{", c="}"):
    """(contenido, indice tras el cierre) del argumento que empieza en s[i] == a"""
    assert s[i] == a, s[i:i + 40]
    n, j = 0, i
    while j < len(s):
        if s[j] == "\\":
            j += 2; continue
        if s[j] == a:
            n += 1
        elif s[j] == c:
            n -= 1
            if n == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def cmd(s, nombre, fn, nargs=1, opcional=False):
    """reemplaza \\nombre[opt]{a}{b}... por fn(opt, a, b, ...) (opt solo si opcional=True), respetando llaves"""
    out, i = [], 0
    pat = re.compile(r"\\" + re.escape(nombre) + r"(?![A-Za-z])")
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:]); return "".join(out)
        out.append(s[i:m.start()]); j = m.end(); opt = None
        while j < len(s) and s[j] in " \n\t":
            j += 1
        if j < len(s) and s[j] == "[":
            opt, j = arg(s, j, "[", "]")
        args = []
        for _ in range(nargs):
            while j < len(s) and s[j] in " \n\t":
                j += 1
            if j >= len(s) or s[j] != "{":
                break
            a, j = arg(s, j); args.append(a)
        if len(args) < nargs:
            out.append(s[m.start():j]); i = j; continue
        out.append(fn(opt, *args) if opcional else fn(*args)); i = j


def cita(opt, clave, entre_par):
    partes = []
    for k in clave.split(","):
        a, y = CIT.get(k.strip(), (k.strip(), ""))
        partes.append((a, y))
    if entre_par:
        t = "; ".join(f"{a}, {y}" for a, y in partes)
        return f"({t}{', ' + opt if opt else ''})"
    return "; ".join(f"{a} ({y}{', ' + opt if opt else ''})" for a, y in partes)


def math_fuera(s, fn):
    partes = re.split(r"(\$\$.*?\$\$|\$[^$]*\$)", s, flags=re.S)
    return "".join(p if (p.startswith("$") and len(p) > 1) else fn(p) for p in partes)


def texto(s, refs):
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    s = re.sub(r"\\(?:eq)?ref\{([^}]*)\}", lambda m: refs.get(m.group(1), "?"), s)
    s = cmd(s, "citet", lambda o, k: cita(o, k, False), 1, True)
    s = cmd(s, "citep", lambda o, k: cita(o, k, True), 1, True)
    s = s.replace("\\protect", "")
    for c, f in [("texttt", lambda a: "`" + a.replace("\\_", "_") + "`"), ("textbf", lambda a: "**" + a + "**"), ("textit", lambda a: "*" + a + "*"),
                 ("emph", lambda a: "*" + a + "*"), ("textsc", lambda a: a), ("url", lambda a: "`" + a + "`"),
                 ("makecell", lambda a: a.replace("\\\\", " ")), ("shortstack", lambda a: a.replace("\\\\", " ")),
                 ("footnote", lambda a: " *(Nota: " + a + ")*")]:
        s = cmd(s, c, f)
    s = cmd(s, "textcolor", lambda c, a: a, 2)
    s = cmd(s, "multicolumn", lambda n, al, a: a, 3)
    s = cmd(s, "paragraph", lambda a: "\n\n**" + a.strip().rstrip(".:") + ".** ")
    s = re.sub(r"\\(footnotesize|small|normalsize|centering|noindent|par\b|clearpage|bfseries|raggedright|arraybackslash)", " ", s)
    s = re.sub(r"\\vspace\{[^}]*\}", "", s)
    s = s.replace("\\allowbreak", "")
    s = math_fuera(s, lambda t: t.replace("\\quad", "\u2003"))

    def plano(t):
        t = t.replace("\\,", " ").replace("\\;", " ").replace("~", " ").replace("\\%", "%").replace("\\&", "&").replace("\\_", "_").replace("\\ ", " ")
        t = t.replace("---", "—").replace("--", "–").replace("``", "“").replace("''", "”").replace("{,}", ",").replace("\\$", "$")
        t = t.replace("{", "").replace("}", "")
        return t
    return math_fuera(s, plano)


def tabla_md(cuerpo, refs):
    cuerpo = cmd(cuerpo, "grupo", lambda a: "\\multicolumn{1}{c}{**" + a + "**}\\\\")
    cuerpo = re.sub(r"\\cmidrule(\([^)]*\))?\{[^}]*\}", "", cuerpo)
    filas = []
    for r in re.split(r"\\\\(?:\[[^\]]*\])?", cuerpo):
        r = re.sub(r"\\(toprule|midrule|bottomrule|hline|endfirsthead|endhead|endfoot|endlastfoot)", "", r)
        r = re.sub(r"\\rowcolor\{[^}]*\}", "", r).strip()
        if not r:
            continue
        filas.append([texto(c, refs).strip().replace("\n", " ").replace("|", "\\|") for c in re.split(r"(?<!\\)&", r)])
    if not filas:
        return ""
    n = max(len(f) for f in filas)
    filas = [f + [""] * (n - len(f)) for f in filas]
    md = ["| " + " | ".join(filas[0]) + " |", "|" + "@@SEP@@|" * n] + ["| " + " | ".join(f) + " |" for f in filas[1:]]
    return "\n".join(md)


def cuerpo_tabular(b):
    """devuelve el cuerpo del primer tabular/tabularx/longtable de b (sin la especificacion de columnas)"""
    m = re.search(r"\\begin\{(tabularx|tabular|longtable)\}", b)
    if not m:
        return ""
    j = m.end()
    if m.group(1) == "tabularx":
        _, j = arg(b, j)
    _, j = arg(b, j)
    fin = b.index("\\end{" + m.group(1) + "}", j)
    t = b[j:fin]
    if m.group(1) == "longtable":
        cap = re.search(r"\\caption", t)
        if cap:                                   # quita la leyenda y la cabecera repetida
            k = t.index("\\endhead") + len("\\endhead") if "\\endhead" in t else 0
            enc = re.search(r"\\toprule(.*?)\\midrule\\endfirsthead", t, re.S)
            t = (enc.group(1) if enc else "") + t[k:]
    return t


def leyenda(b):
    m = re.search(r"\\caption(?![a-z])", b)
    if not m:
        return ""
    j = m.end()
    if b[j] == "[":
        _, j = arg(b, j, "[", "]")
    return arg(b, j)[0] if b[j] == "{" else ""


def celdas():
    if not os.path.exists(TEX):
        return []
    s = open(TEX).read()
    c = s[s.index("\\begin{document}") + len("\\begin{document}"):s.index("\\end{document}")]
    c = re.sub(r"\\input\{([^}]*)\}", lambda m: open(os.path.join(INF, m.group(1) + (".tex" if not m.group(1).endswith(".tex") else ""))).read(), c)
    c = re.sub(r"(?<!\\)%.*", "", c)
    c = re.sub(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", r"\\section*{Resumen}\1", c, flags=re.S)
    c = re.sub(r"\\begin\{center\}.*?\\end\{center\}", "", c, count=1, flags=re.S)       # portada
    c = re.sub(r"\\(tableofcontents|listoffigures|listoftables|clearpage|thispagestyle\{[^}]*\}|vspace\{[^}]*\})", "", c)
    c = re.sub(r"\\printbibliography(\[[^\]]*\])?", "", c)
    c = re.sub(r"\\begin\{landscape\}|\\end\{landscape\}", "", c)
    # ---- numeracion del informe (article): secciones 1..N y apendice A; figuras, tablas y ecuaciones por seccion
    refs, num, k, apendice = {}, "", 0, False
    cnt = {"fig": 0, "tab": 0, "eq": 0}
    for m in re.finditer(r"\\appendix|\\section(\*?)\{|\\begin\{(figure|table|equation|gather)\}|\{\\footnotesize(?:(?!\\end\{longtable\}).)*?\\begin\{longtable\}|\\ContinuedFloat|\\label\{([^}]*)\}", c, re.S):
        g = m.group(0)
        if g == "\\appendix":
            apendice, k = True, 0
        elif g.startswith("\\section"):
            if m.group(1):
                continue
            k += 1; num = chr(64 + k) if apendice else str(k); cnt = {"fig": 0, "tab": 0, "eq": 0}; ult = num
        elif m.group(2) == "figure":
            cnt["fig"] += 1; ult = f"{num}.{cnt['fig']}"
        elif g == "\\ContinuedFloat":
            cnt["fig"] -= 1; ult = f"{num}.{cnt['fig']}"
        elif m.group(2) == "table" or "longtable" in g:
            cnt["tab"] += 1; ult = f"{num}.{cnt['tab']}"
        elif m.group(2) == "equation":
            cnt["eq"] += 1; ult = f"{num}.{cnt['eq']}"
        elif m.group(2) == "gather":
            fin = c.index("\\end{gather}", m.end()); cnt["eq"] += c[m.end():fin].count("\\\\") + 1
            ult = f"{num}.{cnt['eq']}"
        elif m.group(3):
            refs[m.group(3)] = ult
    # ---- celdas: una por seccion
    trozos = re.split(r"(\\appendix|\\section\*?\{)", c)
    res, k, apendice, i = [], 0, False, 0
    actual = None
    while i < len(trozos):
        t = trozos[i]
        if t == "\\appendix":
            apendice, k = True, 0; i += 1; continue
        if t in ("\\section{", "\\section*{"):
            tit, j = arg("{" + trozos[i + 1], 0); cuerpo = trozos[i + 1][j - 1:]
            if t == "\\section{":
                k += 1; num = chr(64 + k) if apendice else str(k)
                cab = f"## {'Apéndice ' if apendice else ''}{num}. {texto(tit, refs).strip()}"
            else:
                num = ""; cab = f"## {texto(tit, refs).strip()}"
            res.append(cab + "\n\n" + render(cuerpo, refs, num)); i += 2; continue
        i += 1
    return [x.strip() for x in res if x.strip()]


def render(c, refs, num):
    cont = {"fig": 0, "tab": 0, "eq": 0}

    def figura(b):
        if "\\ContinuedFloat" not in b:
            cont["fig"] += 1
        n = f"{num}.{cont['fig']}"
        md = ""
        for im in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", b):
            base = os.path.basename(im)
            ruta = f"figuras/{base.replace('.pdf', '.png')}" if base.startswith("fig") else f"informe/Figuras/{base}"
            md += f"\n\n![Figura {n}]({ruta})"
        for et in re.findall(r"\{\\normalsize\\bfseries ([^}]*)\}", b):
            md += f"\n\n*{et}*"
        return md + f"\n\n**Figura {n}:** {texto(leyenda(b), refs).strip()}\n\n"

    def tabla(b):
        cont["tab"] += 1
        n = f"{num}.{cont['tab']}"
        notas = "".join("\n\n" + texto(x, refs).strip() for x in re.findall(r"\\begin\{minipage\}\{[^}]*\}(.*?)\\end\{minipage\}", b, re.S)
                        if "tabular" not in x)
        return f"\n\n**Tabla {n}:** {texto(leyenda(b), refs).strip()}\n\n{tabla_md(cuerpo_tabular(b), refs)}{notas}\n\n"

    def ecuacion(m):
        e = re.sub(r"\\label\{([^}]*)\}", "", m.group(2)).strip()
        nl = e.count("\\\\") + 1 if m.group(1) == "gather" else 1
        a = cont["eq"] + 1; cont["eq"] += nl
        n = f"{num}.{a}" + (f"–{num}.{cont['eq']}" if nl > 1 else "")
        if m.group(1) == "gather":
            e = "\\begin{gathered}" + e + "\\end{gathered}"
        return f"\n\n$$ {e} \\qquad ({n}) $$\n\n"

    out, i = [], 0
    pat = re.compile(r"\\begin\{(figure|table)\}.*?\\end\{\1\}|\{\\footnotesize(?:(?!\\end\{longtable\}).)*?\\begin\{longtable\}.*?\\end\{longtable\}\}|\\begin\{(equation|gather)\}.*?\\end\{\2\}", re.S)
    for m in pat.finditer(c):
        out.append(c[i:m.start()]); b = m.group(0)
        if m.group(1) == "figure":
            out.append(figura(b))
        elif m.group(2):
            out.append(ecuacion(re.match(r"\\begin\{(equation|gather)\}(.*)\\end\{\1\}", b, re.S)))
        else:
            out.append(tabla(b))
        i = m.end()
    out.append(c[i:]); c = "".join(out)
    c = re.sub(r"\\begin\{(itemize|enumerate)\}(\[[^\]]*\])?|\\end\{(itemize|enumerate)\}", "\n", c)
    c = re.sub(r"\\item\s*", "\n- ", c)
    t = texto(c, refs).replace("@@SEP@@", ":--")
    t = re.sub(r"\n{3,}", "\n\n", t)
    return re.sub(r"(?m)^[ \t]+", "", t).strip()


if __name__ == "__main__":
    cs = celdas(); print(len(cs), "celdas")
    for x in cs[:3] + cs[-2:]:
        print("-----\n" + x[:900])
