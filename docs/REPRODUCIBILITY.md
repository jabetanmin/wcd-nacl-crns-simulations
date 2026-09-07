# Reproducibilidad

## Entorno principal de simulación

- Geant4: 10.07.p04.
- Lista de física de referencia: QGSP_BERT_HP, con las configuraciones específicas que se documenten para cada campaña.
- Procesos ópticos: Cherenkov, absorción, Rayleigh, Mie y procesos de frontera, según la configuración empleada.
- Semillas aleatorias: deben almacenarse junto con los metadatos de cada corrida cuando sea posible.

## Información mínima por campaña

Cada directorio de simulación debe registrar:

1. propósito de la campaña;
2. geometría y versión del código;
3. medio detector;
4. fuente y distribución de partículas;
5. número de eventos incidentes;
6. lista de física y bibliotecas de datos;
7. semillas aleatorias;
8. comandos de compilación y ejecución;
9. archivos de salida esperados;
10. programa utilizado para analizar los resultados.

## Verificación prevista

La primera versión estable deberá incluir al menos un ejemplo pequeño que pueda ejecutarse de principio a fin y reproduzca una tabla o figura seleccionada de la tesis.
