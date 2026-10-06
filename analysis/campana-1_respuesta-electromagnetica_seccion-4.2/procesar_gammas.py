#!/usr/bin/env python3
"""Procesa los fotones gamma de las 64 corridas de la Campaña 1 (Sección 4.2 de la tesis).

Lee, para cada energía y medio, el archivo crudo gamma-completo-*.txt escrito por
G4WCDSteppingAction (etiqueta campana-1-QGSP_BERT_HP): una fila por paso de cada fotón,

    gamma  trackID  parentID  paso  proceso  x  y  z  E

con (x, y, z) [mm] la posición posterior del paso y E [MeV] la energía cinética posterior
(track->GetKineticEnergy()). El archivo no tiene identificador de evento: cada traza empieza
cuando el número de paso vuelve a 1 y sus pasos son consecutivos. Como la energía es la
posterior, en los pasos `phot` y `conv` vale 0; la energía con la que el fotón llega a esas
interacciones es la del paso anterior de la misma traza.

Definiciones:
  - tanque: |x|,|y| <= 480 mm y 0 <= z <= 1330.05 mm (criterio de la tesis; incluye los cruces de
    la cara interior de la tapa); tanque estricto: lo mismo con z <= 1330 mm.
  - fotón del neutrón: traza con parentID == 1 (fotones de captura y, en mucha menor medida, de
    interacciones inelásticas); el resto son fotones secundarios (aniquilación, bremsstrahlung,
    fluorescencia, desintegración del 24Na).
  - destino de cada traza: último paso `phot` o `conv` (absorbido, dentro o fuera del tanque),
    último paso fuera del tanque (escapa) u otro.

Uso:
  python3 procesar_gammas.py <carpeta Gammas-contenido-completo> <carpeta de salida> [procesos]
Salida: <salida>/<energía>/<medio>/resumen_gammas.json y <salida>/resumen_gammas_campana.tsv.
"""
import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

ENERGIAS = ["1meV", "2.5meV", "5meV", "7meV", "10meV", "25meV", "50meV", "80meV", "100meV",
            "300meV", "500meV", "700meV", "1000meV", "10000meV", "100000meV", "1000000meV"]
CARPETA_ENERGIA = {"2.5meV": "2-5meV"}          # nombre de la carpeta en los datos crudos
MEDIOS = ["Agua-pura", "Agua+2.5NaCl", "Agua+5NaCl", "Agua+10NaCl"]
PROCESOS = ["compt", "phot", "Rayl", "conv", "Transportation"]

XY_MAX, Z_MIN, Z_MAX, Z_MAX_ESTRICTO = 480.0, 0.0, 1330.05, 1330.0

# Fotones de emisión que identifican el núcleo (energías tal como las emite G4NeutronHP, MeV).
# H: único fotón de 2.2244; 14N (aire): 10.83; 10B (vidrio Pyrex del PMT): 0.4776.
# Líneas características del 35Cl, usadas para reconocer sus cascadas en gamma-primario.
E_H, E_N, E_B = 2.2244, 10.831, 0.4776
LINEAS_CL = [0.5171, 0.7864, 0.7883, 1.1647, 1.9511, 1.9592, 5.7154, 6.1109, 6.6198, 6.6283, 7.4140,
             7.7901, 8.5784]
Q = {"H": 2.2246, "Cl": 8.5794}            # energía de separación del neutrón en 2H y 36Cl (MeV)
TOL_LINEA = 0.003       # MeV

# Histogramas: espectro completo y zona de baja energía
H_ANCHO, H_MAX = 0.005, 11.0                 # 2200 intervalos de 5 keV
B_ANCHO, B_MAX = 0.0005, 0.3                 # 600 intervalos de 0.5 keV
Z_ANCHO, R_ANCHO, R_MAX = 10.0, 10.0, 700.0  # mm


class Hist:
    def __init__(self, ancho, maximo):
        self.ancho, self.maximo = ancho, maximo
        self.c = [0] * int(round(maximo / ancho))
        self.encima = 0
        self.n = self.s = self.s2 = 0

    def add(self, v):
        self.n += 1
        self.s += v
        self.s2 += v * v
        i = int(v / self.ancho)
        if 0 <= i < len(self.c):
            self.c[i] += 1
        else:
            self.encima += 1

    def dic(self):
        media = self.s / self.n if self.n else None
        sd = math.sqrt(max(self.s2 / self.n - media * media, 0)) if self.n else None
        return {"ancho": self.ancho, "rango": [0.0, self.maximo], "conteos": self.c, "encima": self.encima,
                "n": self.n, "media": media, "std": sd}


def dentro(x, y, z, zmax=Z_MAX):
    return -XY_MAX <= x <= XY_MAX and -XY_MAX <= y <= XY_MAX and Z_MIN <= z <= zmax


def clase_emision(e):
    """Origen del fotón de emisión según su energía (solo las líneas inequívocas)."""
    if abs(e - E_H) <= TOL_LINEA:
        return "H_2.224"
    if abs(e - E_N) <= 0.005:
        return "N_10.83"
    if abs(e - E_B) <= TOL_LINEA:
        return "B_0.478"
    return "otras"


def clase_cascada(c):
    if len(c) == 1 and abs(c[0] - E_H) <= TOL_LINEA:
        return "H"
    if any(abs(e - E_N) <= 0.005 for e in c):
        return "N"
    if any(abs(e - l) <= TOL_LINEA for e in c for l in LINEAS_CL):
        return "Cl"
    if len(c) == 1 and abs(c[0] - E_B) <= TOL_LINEA:
        return "B"
    return "otros"


def cascadas_primarias(carpeta):
    """Cascadas de captura desde gamma-primario-*.txt (energías exactas de emisión, solo 1-10 meV).

    Los fotones de una misma captura comparten la posición del punto de captura y aparecen en filas
    consecutivas; cada grupo es una cascada (una captura)."""
    fs = sorted(carpeta.glob("gamma-primario-*.txt"))
    if not fs:
        return None
    cas, prev = [], None
    pos = []
    with open(fs[0]) as f:
        for linea in f:
            c = linea.split()
            if len(c) < 9 or c[4] != "nCapture":
                continue
            k = (c[5], c[6], c[7])
            if k != prev:
                cas.append([])
                pos.append(tuple(float(v) for v in k))
                prev = k
            cas[-1].append(float(c[8]))
    hemi = Hist(H_ANCHO, H_MAX)
    for c in cas:
        for e in c:
            hemi.add(e)
    tipos = {}
    for c, p in zip(cas, pos):
        t = clase_cascada(c)
        d = tipos.setdefault(t, {"capturas": 0, "fotones": 0, "suma": 0.0, "conserva": 0,
                                 "dentro_tanque": 0, "hist_suma": Hist(0.05, 20.0)})
        s = sum(c)
        d["capturas"] += 1
        d["fotones"] += len(c)
        d["suma"] += s
        d["hist_suma"].add(s)
        if t in Q and abs(s - Q[t]) <= 0.05:
            d["conserva"] += 1
        if dentro(*p):
            d["dentro_tanque"] += 1
    out = {"archivo": fs[0].name, "capturas": len(cas), "fotones": sum(len(c) for c in cas),
           "espectro_emision": hemi.dic(), "por_tipo": {}}
    for t, d in tipos.items():
        out["por_tipo"][t] = {"capturas": d["capturas"], "fotones_por_captura": d["fotones"] / d["capturas"],
                              "energia_media_cascada_MeV": d["suma"] / d["capturas"],
                              "fraccion_conserva_Q": (d["conserva"] / d["capturas"]) if t in Q else None,
                              "capturas_dentro_tanque": d["dentro_tanque"],
                              "hist_energia_cascada": d["hist_suma"].dic()}
    return out


def archivo_crudo(carpeta):
    fs = sorted(carpeta.glob("gamma-completo-*.txt"))
    if len(fs) != 1:
        raise SystemExit(f"{carpeta}: se esperaba un archivo gamma-completo-*.txt y hay {len(fs)}")
    return fs[0]


def procesar(carpeta, salida, nombre):
    arch = archivo_crudo(carpeta)
    filas = {"total": 0, "tanque": 0, "exterior": 0, "tanque_estricto": 0}
    proc = {p: {"total": 0, "tanque": 0, "exterior": 0, "tanque_estricto": 0} for p in PROCESOS}
    otros_procesos = {}
    compt_menor_3MeV = 0
    trazas = {"total": 0, "neutron": 0, "secundarias": 0}
    primer_paso = {}                       # proceso del primer paso de las trazas del neutrón
    destino = {"neutron": {}, "secundarias": {}}
    lineas = {"H_2.224": 0, "N_10.83": 0, "B_0.478": 0, "otras": 0}
    interacciones_por_traza = []           # (compt, Rayl) en el tanque por fotón del neutrón
    h = {k: Hist(H_ANCHO, H_MAX) for k in ["filas_tanque", "emision_neutron", "compt", "Rayl", "phot_entrada",
                                           "conv_entrada", "escapa"]}
    hb = {k: Hist(B_ANCHO, B_MAX) for k in ["compt", "Rayl", "phot_entrada"]}
    hz, hr = Hist(Z_ANCHO, 1340.0), Hist(R_ANCHO, R_MAX)       # posición de la fotoabsorción en el tanque
    sin_entrada = {"phot": 0, "conv": 0}
    # Reproducción de la Tabla de fotoabsorción de la tesis: paso phot del archivo filtrado (tanque
    # estricto) cuya fila anterior en ese mismo archivo es compt; energía = la de esa fila anterior.
    tesis_phot = []
    prev_estricto = None
    # Histogramas con la binning de las figuras de la tesis
    ht = {"compt_estricto_2.7MeV_1000": Hist(2.7 / 1000, 2.7),     # Fig. 4.36 y tabla de FWHM
          "Rayl_tanque_3keV": Hist(0.003, 3.0),                    # Fig. 4.39 (máximo en intervalos de 3 keV)
          "phot_previa_compt_0.15MeV_500": Hist(0.15 / 500, 0.15)}   # Fig. 4.41

    traza = []

    def cerrar(traza):
        if not traza:
            return
        es_n = traza[0][1] == 1
        clave = "neutron" if es_n else "secundarias"
        trazas["total"] += 1
        trazas[clave] += 1
        p0, e0 = traza[0][2], traza[0][6]
        if es_n:
            primer_paso[p0] = primer_paso.get(p0, 0) + 1
            if p0 in ("Transportation", "Rayl"):      # energía posterior = energía de emisión
                h["emision_neutron"].add(e0)
                lineas[clase_emision(e0)] += 1
            nc = sum(1 for r in traza if r[2] == "compt" and r[7])
            nr = sum(1 for r in traza if r[2] == "Rayl" and r[7])
            interacciones_por_traza.append((nc, nr))
        ult = traza[-1]
        if ult[2] in ("phot", "conv"):
            d = ult[2] + ("_tanque" if ult[7] else "_fuera")
        elif not ult[7]:
            d = "escapa"
            if es_n:
                pass
        else:
            d = "otro_" + ult[2]
        destino[clave][d] = destino[clave].get(d, 0) + 1
        if d == "escapa":
            h["escapa"].add(ult[6])

    with open(arch) as f:
        for linea in f:
            c = linea.split()
            if len(c) < 9:
                continue
            parent, paso, p = int(c[2]), int(c[3]), c[4]
            x, y, z, e = float(c[5]), float(c[6]), float(c[7]), float(c[8])
            ins = dentro(x, y, z)
            est = dentro(x, y, z, Z_MAX_ESTRICTO)
            if paso == 1:
                cerrar(traza)
                traza = []
            filas["total"] += 1
            filas["tanque" if ins else "exterior"] += 1
            if est:
                filas["tanque_estricto"] += 1
            if p in proc:
                d = proc[p]
            else:
                d = otros_procesos.setdefault(p, {"total": 0, "tanque": 0, "exterior": 0, "tanque_estricto": 0})
            d["total"] += 1
            d["tanque" if ins else "exterior"] += 1
            if est:
                d["tanque_estricto"] += 1
            if p == "compt" and e < 3.0:
                compt_menor_3MeV += 1
            if ins:
                h["filas_tanque"].add(e)
                if p == "compt":
                    h["compt"].add(e)
                    hb["compt"].add(e)
                elif p == "Rayl":
                    h["Rayl"].add(e)
                    hb["Rayl"].add(e)
                elif p in ("phot", "conv"):
                    if traza:
                        ein = traza[-1][6]
                        h[p + "_entrada"].add(ein)
                        if p == "phot":
                            hb["phot_entrada"].add(ein)
                    else:
                        sin_entrada[p] += 1
                    if p == "phot":
                        hz.add(z)
                        hr.add(math.hypot(x, y))
            if ins and p == "Rayl":
                ht["Rayl_tanque_3keV"].add(e)
            if est:
                if p == "compt":
                    ht["compt_estricto_2.7MeV_1000"].add(e)
                if p == "phot" and prev_estricto is not None and prev_estricto[0] == "compt":
                    tesis_phot.append(prev_estricto[1])
                    ht["phot_previa_compt_0.15MeV_500"].add(prev_estricto[1])
                prev_estricto = (p, e)
            traza.append((paso, parent, p, x, y, z, e, ins))
    cerrar(traza)

    def momentos(v, lo=None, hi=None):
        w = [a for a in v if (lo is None or a >= lo) and (hi is None or a <= hi)]
        if not w:
            return {"n": 0, "media": None, "std": None}
        m = sum(w) / len(w)
        return {"n": len(w), "media": m, "std": math.sqrt(sum((a - m) ** 2 for a in w) / len(w))}

    nc = [a for a, _ in interacciones_por_traza]
    res = {
        "corrida": nombre,
        "archivo": arch.name,
        "filas": filas,
        "procesos": proc,
        "otros_procesos": otros_procesos,
        "compt_E_menor_3MeV_total": compt_menor_3MeV,
        "trazas": trazas,
        "primer_paso_trazas_neutron": primer_paso,
        "destino": destino,
        "lineas_emision_neutron": lineas,
        "cascadas_captura": cascadas_primarias(carpeta),
        "compt_por_foton_neutron_media": sum(nc) / len(nc) if nc else None,
        "sin_energia_entrada": sin_entrada,
        "histogramas": {k: v.dic() for k, v in h.items()},
        "histogramas_baja_energia": {k: v.dic() for k, v in hb.items()},
        "fotoabsorcion_tanque": {"z_mm": hz.dic(), "r_mm": hr.dic()},
        "histogramas_tesis": {k: v.dic() for k, v in ht.items()},
        "tesis_fotoabsorcion_previa_compt": {
            "n": len(tesis_phot),
            "todas": momentos(tesis_phot),
            "0-0.15MeV": momentos(tesis_phot, 0.0, 0.15),
            "0.01-0.1MeV": momentos(tesis_phot, 0.01, 0.1),
            "0.01-0.15MeV": momentos(tesis_phot, 0.01, 0.15),
            "0-0.1MeV": momentos(tesis_phot, 0.0, 0.1),
        },
    }
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "resumen_gammas.json").write_text(json.dumps(res))
    return res


def tarea(args):
    base, salida, e, m = args
    return procesar(Path(base) / CARPETA_ENERGIA.get(e, e) / m, Path(salida) / e / m, f"{e}/{m}")


def main():
    base, salida = sys.argv[1], sys.argv[2]
    procesos = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    trabajos = [(base, salida, e, m) for e in ENERGIAS for m in MEDIOS]
    with Pool(procesos) as pool:
        resumenes = pool.map(tarea, trabajos)
    cols = ["energia", "medio", "filas_total", "filas_tanque", "filas_exterior", "filas_tanque_estricto",
            "trazas_total", "trazas_neutron", "trazas_secundarias"]
    cols += [f"{p}_{z}" for p in PROCESOS for z in ("total", "tanque", "exterior")]
    cols += ["compt_E_menor_3MeV_total", "compt_por_foton_neutron_media",
             "absorbidos_phot_tanque", "absorbidos_conv_tanque", "escapan", "emision_H_2.224",
             "emision_N_10.83", "emision_B_0.478", "emision_otras", "z_fotoabs_media_mm",
             "r_fotoabs_media_mm", "E_phot_entrada_media", "cascadas", "cascadas_H", "cascadas_Cl",
             "E_cascada_Cl_media_MeV", "fraccion_Cl_conserva_Q", "tesis_phot_n", "tesis_phot_media_0.01-0.1",
             "tesis_phot_std_0.01-0.1"]
    with open(Path(salida) / "resumen_gammas_campana.tsv", "w") as f:
        f.write("\t".join(cols) + "\n")
        for (b, s, e, m), r in zip(trabajos, resumenes):
            dn, ds = r["destino"]["neutron"], r["destino"]["secundarias"]
            fila = [e, m] + [r["filas"][k] for k in ("total", "tanque", "exterior", "tanque_estricto")]
            fila += [r["trazas"][k] for k in ("total", "neutron", "secundarias")]
            fila += [r["procesos"][p][z] for p in PROCESOS for z in ("total", "tanque", "exterior")]
            fila += [r["compt_E_menor_3MeV_total"], f"{r['compt_por_foton_neutron_media']:.4f}",
                     dn.get("phot_tanque", 0) + ds.get("phot_tanque", 0),
                     dn.get("conv_tanque", 0) + ds.get("conv_tanque", 0),
                     dn.get("escapa", 0) + ds.get("escapa", 0)]
            fila += [r["lineas_emision_neutron"][k] for k in ("H_2.224", "N_10.83", "B_0.478", "otras")]
            fila += [f"{r['fotoabsorcion_tanque']['z_mm']['media']:.2f}",
                     f"{r['fotoabsorcion_tanque']['r_mm']['media']:.2f}",
                     f"{r['histogramas']['phot_entrada']['media']:.5f}"]
            cc = r["cascadas_captura"]
            if cc:
                cl = cc["por_tipo"].get("Cl")
                fila += [cc["capturas"], cc["por_tipo"].get("H", {}).get("capturas", 0),
                         cl["capturas"] if cl else 0,
                         f"{cl['energia_media_cascada_MeV']:.3f}" if cl else "",
                         f"{cl['fraccion_conserva_Q']:.3f}" if cl else ""]
            else:
                fila += ["", "", "", "", ""]
            tp = r["tesis_fotoabsorcion_previa_compt"]
            fila += [tp["n"], f"{tp['0.01-0.1MeV']['media']:.4f}", f"{tp['0.01-0.1MeV']['std']:.4f}"]
            f.write("\t".join(str(v) for v in fila) + "\n")


if __name__ == "__main__":
    main()
