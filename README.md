# Plataforma de Análisis de Violencias - Corredor Centro-Oriente (Puebla)

Este dashboard interactivo permite la visualización y análisis de datos sobre la incidencia delictiva en 18 municipios del Corredor Centro-Oriente del estado de Puebla, México, durante el periodo 2015-2024.

## Objetivo
Proporcionar una herramienta técnica para el análisis exploratorio de datos (EDA) que permita identificar patrones geográficos, tendencias temporales y comparativas municipales sobre diversas categorías de violencia.

## Estructura y Navegación

El dashboard está organizado en cuatro pestañas principales:

1.  **📍 Resumen y Mapa:** Vista panorámica geolocalizada. Incluye indicadores clave de desempeño (KPIs) sobre población, tasas globales, el municipio con mayor incidencia y el delito más frecuente.
2.  **📈 Tendencia Temporal:** Gráficos de líneas y áreas apiladas para observar la evolución histórica de los delitos por año, facilitando la identificación de cambios en la incidencia.
3.  **📊 Estructura y Comparativa:**
    *   **Distribución:** Treemap para entender el peso porcentual de cada delito dentro de una categoría.
    *   **Comparador Inteligente:** Herramienta para contrastar directamente la incidencia entre dos municipios seleccionados, incluyendo una sección de **Hallazgos Clave** que resume las diferencias estadísticas.
4.  **📋 Datos y Diccionario:** Sección de transparencia donde se puede consultar el diccionario de datos (metodología, fórmulas), explorar los registros filtrados y descargar los datos en formato CSV.

## Lógica de Desarrollo
*   **Lenguaje:** Python.
*   **Framework de Web:** Streamlit, para la creación rápida de la interfaz.
*   **Visualización:** Plotly, para gráficos interactivos.
*   **Procesamiento de Datos:** Pandas, para manipulación y limpieza de los datasets.
*   **Limpieza:** Se implementó una función `clean_text` para manejar caracteres especiales en los datos crudos, garantizando la correcta lectura de nombres geográficos y descripciones.

## Requisitos de Ejecución
El proyecto requiere Python 3.x y las librerías listadas en `requirements.txt`.

### Ejecución
Para iniciar el dashboard, ejecute el siguiente comando en la terminal:
```bash
streamlit run app.py
```
Acceda a la URL local proporcionada (usualmente `http://localhost:8501`).
