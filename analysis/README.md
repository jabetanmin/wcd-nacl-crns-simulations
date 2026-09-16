# Análisis en Python

Este directorio contendrá los programas y cuadernos utilizados para:

- leer y depurar las salidas de simulación;
- construir histogramas con intervalos lineales o logarítmicos;
- normalizar distribuciones por neutrón incidente y ancho de intervalo;
- calcular eficiencias e incertidumbres estadísticas;
- comparar agua pura con soluciones de NaCl;
- producir tablas y figuras de la tesis.

## Convención propuesta

```text
analysis/
├── notebooks/       Exploración y comprobaciones
├── scripts/         Programas reproducibles
├── wcd_analysis/    Funciones reutilizables
└── tests/           Pruebas de las funciones de análisis
```

Los programas definitivos deben aceptar rutas y parámetros por línea de comandos o archivos de configuración; no deben contener rutas personales fijas.
