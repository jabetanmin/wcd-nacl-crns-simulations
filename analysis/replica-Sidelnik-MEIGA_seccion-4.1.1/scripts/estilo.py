"""Estilo comun de las figuras: se dibujan a 8 pulgadas de ancho y la tesis las reduce al ancho del texto
(~6,3 pulgadas, factor ~0,78). Los tamanos de letra estan elegidos para que, ya reducidos, los ejes se impriman
a ~9-10 puntos y las leyendas a no menos de ~9 puntos (legibles junto al texto de 12 puntos de la tesis)."""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

ANCHO = 8.0          # pulgadas
LEYENDA_MIN = 11.5   # puntos antes de la reduccion (~9 puntos impresos)
TITULO_MIN = 12.0
MARCAS_MIN = 11.0


def _con_minimo(orig):
    def leyenda(self, *a, **k):
        fs = k.get("fontsize")
        if isinstance(fs, (int, float)) and fs < LEYENDA_MIN:
            k["fontsize"] = LEYENDA_MIN
        return orig(self, *a, **k)
    leyenda._minimo = True
    return leyenda


def _min_kw(orig, minimo, marca):
    def f(self, *a, **k):
        fs = k.get("fontsize")
        if isinstance(fs, (int, float)) and fs < minimo:
            k["fontsize"] = minimo
        return orig(self, *a, **k)
    setattr(f, marca, True)
    return f


def leyenda_medios(fig, medios, colores, etiquetas, abajo=0.0, ncol=4, **kw):
    """Una sola leyenda de colores de los medios para toda la figura, debajo de los paneles."""
    from matplotlib.patches import Patch
    H = [Patch(color=colores[m], label=etiquetas[m]) for m in medios]
    return fig.legend(handles=H, loc="lower center", ncol=ncol, bbox_to_anchor=(0.5, abajo), frameon=False, **kw)


def aplicar(**extra):
    mpl.rcParams.update({"font.size": 12, "axes.labelsize": 12.5, "axes.titlesize": 12.5, "xtick.labelsize": 11.5,
                         "ytick.labelsize": 11.5, "legend.fontsize": LEYENDA_MIN, "legend.frameon": False, "axes.grid": True,
                         "grid.color": "#e4e3df", "axes.spines.top": False, "axes.spines.right": False,
                         "savefig.dpi": 200, "savefig.bbox": "tight"})
    mpl.rcParams.update(extra)
    # las leyendas con un tamano fijo menor que LEYENDA_MIN se agrandan hasta ese minimo
    if not getattr(Axes.legend, "_minimo", False):
        Axes.legend = _con_minimo(Axes.legend)
        Figure.legend = _con_minimo(Figure.legend)
        Axes.set_title = _min_kw(Axes.set_title, TITULO_MIN, "_minimo")
        Axes.set_xticklabels = _min_kw(Axes.set_xticklabels, MARCAS_MIN, "_minimo")
        Axes.set_yticklabels = _min_kw(Axes.set_yticklabels, MARCAS_MIN, "_minimo")


def tres_paneles(alto=7.2, ancho=ANCHO):
    """Dos paneles arriba y uno ancho abajo (sustituye a las filas de tres paneles)."""
    fig = plt.figure(figsize=(ancho, alto))
    gs = fig.add_gridspec(2, 2)
    return fig, [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])]
