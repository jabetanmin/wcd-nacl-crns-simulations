#!/usr/bin/env python3
"""
Decide si la calibración p.e./ADC con muones del PMT bajado entra al informe. Solo se usa si mejora el acuerdo de la
forma de los histogramas con los datos frente al ajuste libre por factores comunes (k horizontal, N vertical, comunes
a los tres medios). Criterio (las tres condiciones, con la ventana del disparo y con la carga robusta):
  1. 0.67 <= k_libre / k_muones <= 1.5
  2. rms_ln(k_muones) <= 1.25 * rms_ln(k_libre)
  3. con k_muones, al menos el 80 % de los bins del intervalo 4500-30 000 ADC tienen simulación, en los tres medios
Además resume la comparación con el PMT en la tapa (A3b).
Entrada: resultados/ajuste_factor_comun_horizontal-PMTbajo.json, respuesta_prototipo_horizontal-PMTbajo.json y los
del montaje con el PMT en la tapa (Analisis-montaje-MEIGA/resultados).
-> resultados/decision_calibracion_muones.json
"""
import json, os

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RES = os.path.join(BASE, "resultados")
TAPA = os.path.join(BASE, "..", "Analisis-montaje-MEIGA", "resultados")
F = json.load(open(os.path.join(RES, "ajuste_factor_comun_horizontal-PMTbajo.json")))
P = json.load(open(os.path.join(RES, "respuesta_prototipo_horizontal-PMTbajo.json")))
FT = json.load(open(os.path.join(TAPA, "ajuste_factor_comun.json")))
PT = json.load(open(os.path.join(TAPA, "respuesta_prototipo_montaje-tapa.json")))

out = {"criterio": {"cociente_k": [0.67, 1.5], "rms_max_relativo": 1.25, "fraccion_bins_min": 0.8}, "metodos": {}}
pasa_todo = True
for met in ("ventana_trigger", "robusto"):
    lib, mu = F[met], F[met + "_muones"]
    c1 = lib["k_ADC_por_pe"] / mu["k_ADC_por_pe"]
    c2 = mu["rms_ln"] / lib["rms_ln"]
    c3 = min(mu["fraccion_bins_con_simulacion"].values())
    el = P["metodos"][met]                                   # con la electrónica completa
    ok = (0.67 <= c1 <= 1.5) and c2 <= 1.25 and c3 >= 0.8
    pasa_todo &= ok
    out["metodos"][met] = {
        "k_libre_ADC_por_pe": lib["k_ADC_por_pe"], "k_muones_ADC_por_pe": mu["k_ADC_por_pe"],
        "cociente_k_libre_sobre_muones": c1, "rms_muones_sobre_libre": c2, "fraccion_bins_min_con_muones": c3,
        "rms_ln": {"libre": lib["rms_ln"], "muones": mu["rms_ln"]},
        "N_inc_300s": {"libre": lib["N_inc_300s"], "muones": mu["N_inc_300s"]},
        "ks_forma": {"libre": lib["ks_forma"], "muones": mu["ks_forma"]},
        "electronica_completa": {"k_muones": el["k_ADC_por_pe"], "rms_muones": el["rms_ln"],
                                 "k_libre": el["k_libre"]["k_ADC_por_pe"], "rms_libre": el["k_libre"]["rms_ln"],
                                 "N_libre": el["k_libre"]["N_inc_300s"], "fraccion_disparo_muones": el["fraccion_disparo"]},
        "pasa": ok}
out["implementar_calibracion_muones"] = bool(pasa_todo)
out["comparacion_PMT_tapa"] = {met: {
    "tapa": {"k_libre": FT[met]["k_ADC_por_pe"], "N_inc_300s": FT[met]["N_inc_300s"], "rms_ln": FT[met]["rms_ln"],
             "k_muones": FT["k_muones_ADC_por_pe"],
             "k_libre_electronica": PT["metodos"][met]["k_libre"]["k_ADC_por_pe"],
             "rms_libre_electronica": PT["metodos"][met]["k_libre"]["rms_ln"]},
    "bajado": {"k_libre": F[met]["k_ADC_por_pe"], "N_inc_300s": F[met]["N_inc_300s"], "rms_ln": F[met]["rms_ln"],
               "k_muones": F["k_muones_ADC_por_pe"],
               "k_libre_electronica": P["metodos"][met]["k_libre"]["k_ADC_por_pe"],
               "rms_libre_electronica": P["metodos"][met]["k_libre"]["rms_ln"]}} for met in ("ventana_trigger", "robusto")}
json.dump(out, open(os.path.join(RES, "decision_calibracion_muones.json"), "w"), indent=2, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
