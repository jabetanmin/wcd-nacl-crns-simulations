# Diferenciación de contribuciones

## Capacidades preexistentes de MEIGA

Las siguientes capacidades deben atribuirse al proyecto MEIGA original:

- arquitectura general del framework;
- clases base y organización de objetos;
- mecanismos fundamentales de inicialización y ejecución;
- integración general con Geant4;
- mecanismos preexistentes de escritura de datos.

Esta lista se completará mediante una comparación verificable con la revisión exacta del repositorio original utilizada como punto de partida.

## Contribuciones de la tesis

La investigación extendió y adaptó MEIGA para estudiar un detector Cherenkov de agua dopado con NaCl. Entre las contribuciones que deben documentarse archivo por archivo se encuentran:

- geometría detallada del tanque, volumen activo, revestimiento, ventana y fotocátodo;
- definición de agua pura y soluciones con 2.5 %, 5.0 % y 10.0 % de NaCl;
- implementación de densidades y propiedades ópticas de los medios;
- configuración de procesos electromagnéticos, ópticos y neutrónicos;
- tratamiento de capturas neutrónicas y producción de fotones secundarios;
- selección de fotones mediante la eficiencia cuántica del PMT;
- nuevas variables y mecanismos para seleccionar, registrar y organizar las salidas;
- configuraciones para fuentes monocromáticas, espectros atmosféricos, albedo del suelo y validación Am-Be;
- programas Python para normalización, eficiencia, incertidumbres, tablas y figuras.

## Registro preliminar de archivos modificados

La comparación de la carpeta recibida con el commit base `39b950e` detectó 18 archivos versionados con cambios locales:

| Archivo | Estado | Descripción científica pendiente |
|---|---|---|
| `src/Applications/G4WCDSimulator/G4WCDRunAction.cc` | Modificado | Sí |
| `src/Applications/G4WCDSimulator/G4WCDStackingAction.h` | Modificado | Sí |
| `src/Applications/G4WCDSimulator/G4WCDSteppingAction.cc` | Modificado | Sí |
| `src/Applications/G4WCDSimulator/G4WCDSteppingAction.h` | Modificado | Sí |
| `src/Applications/G4WCDSimulator/G4WCDTrackingAction.cc` | Modificado | Sí |
| `src/Framework/ConfigManager/DefaultProperties.h` | Modificado | Sí |
| `src/Framework/ConfigManager/DetectorProperties.xml` | Modificado | Sí |
| `src/Framework/Detector/OptDevice.cc` | Modificado | Sí |
| `src/Framework/Detector/OptDevice.h` | Modificado | Sí |
| `src/G4Models/G4MOptDeviceAction.cc` | Modificado | Sí |
| `src/G4Models/G4MPMTAction.cc` | Modificado | Sí |
| `src/G4Models/G4MPhysicsList.cc` | Modificado | Sí |
| `src/G4Models/G4MPhysicsList.h` | Modificado | Sí |
| `src/G4Models/Materials.cc` | Modificado | Sí |
| `src/G4Models/Materials.h` | Modificado | Sí |
| `src/G4Models/SaltyWCD.cc` | Modificado | Sí |
| `src/G4Models/WCD.cc` | Modificado | Sí |
| `src/Utilities/FluxGenerators/generate.sh` | Modificado | Sí |

Los archivos `ExtraPhysics.cc` y `OpticalPhysics.cc` mencionados inicialmente coinciden byte a byte con las versiones del commit base y Git no los identifica actualmente como modificados. Pueden haber sido revisados, modificados y luego restaurados; se conservarán en el inventario de revisión, pero no se atribuirán como contribuciones sin evidencia adicional.

La repetición de `G4WCDSteppingAction.cc` en la lista inicial probablemente corresponde al par `G4WCDSteppingAction.cc` y `G4WCDSteppingAction.h`, ambos modificados en la copia recibida.

## Criterio de incorporación

Un archivo solo debe marcarse como contribución original después de comparar sus cambios con la revisión base de MEIGA y describir su finalidad. Las adaptaciones menores, configuraciones y código completamente nuevo deben distinguirse explícitamente.
