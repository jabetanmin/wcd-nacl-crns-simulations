# Resumen por evento de rastreo-neutron-completo.txt (incluye neutrones secundarios: track > 1).
# Columnas: nombre track padre paso proceso x y z(post, mm) KEpre KEpost KE (MeV)
# Un evento empieza en la línea con track 1 y paso 1.
# Salida: evento E0 n_hadElastic_primario proceso_final_primario x y z (fin del primario) n_capturas(todas) n_lineas
function volcar() { if (ev > 0) printf "%d\t%.6g\t%d\t%s\t%.3f\t%.3f\t%.3f\t%d\t%d\n", ev, e0, nel, ult, x, y, z, ncap, nl }
$2 == 1 && $4 == 1 { volcar(); ev++; e0 = $9; nel = 0; nl = 0; ncap = 0 }
{ nl++; if ($5 == "nCapture") ncap++ }
$2 == 1 { if ($5 == "hadElastic") nel++; ult = $5; x = $6; y = $7; z = $8 }
END { volcar() }
