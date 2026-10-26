"""
Normalización absoluta del flujo de Bucaramanga (all_bga_neutron_35.shw): 1 m² y 12 h (43 200 s), como en la tesis.
Verificación (26 de octubre de 2026): la corrida de ARTI Salida_BGA_300 (repositorio csarmiento03/ReunionLAGO2025_ARTI;
956 m s. n. m., 1 m², -t 300 s; 165 232 secundarios = 551 m^-2 s^-1, como los 540 m^-2 s^-1 de Sarmiento-Cano et al. 2022)
tiene 3923 neutrones (corte de CORSIKA en 50 MeV) = 13.1 m^-2 s^-1. Los 569 038 neutrones que bajan con más de 50 MeV en
all_bga equivalen a 12.09 h, y los de más de 1 GeV a 12.10 h.
"""
T_EXPOSICION_S = 12 * 3600.0
J_BAJA_ANTES_N_M2_S = 308.6          # normalización anterior (3600 s), usada en flujos/entrada_tanque.json del paquete del tanque
