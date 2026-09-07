# Gestión de datos

## Datos que pueden incorporarse

- configuraciones y espectros de entrada pequeños;
- muestras reducidas de salidas;
- tablas procesadas necesarias para reproducir figuras;
- metadatos de campañas de simulación;
- figuras y tablas finales seleccionadas.

## Datos que no deben incorporarse directamente

- árboles ROOT u otras salidas masivas de producción;
- directorios de compilación;
- duplicados de datos descargables desde fuentes externas;
- credenciales, rutas personales o información sensible;
- archivos de terceros sin permiso de redistribución.

## Convención recomendada

```text
data/
├── README.md
├── sample-input/
├── processed/
└── external-sources.yml
```

Cada conjunto de datos debe registrar su procedencia, fecha, unidad, transformación aplicada y programa que lo generó.
