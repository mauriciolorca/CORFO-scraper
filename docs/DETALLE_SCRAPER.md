# Documentación del Scraper de Detalles (corfo_detalle_scraper_b01.py)

## Descripción General

Este script representa el tercer y último paso en el proceso de extracción de datos de CORFO. Su función principal es acceder a la ficha detallada de cada convocatoria y extraer información específica sobre beneficios, requisitos y otros detalles importantes.

## Características Principales

- Extracción de información detallada de cada convocatoria
- Soporte para múltiples formatos de página
- Guardado incremental de datos
- Sistema de logging robusto
- Manejo de errores avanzado

## Datos Extraídos

El script extrae los siguientes campos para cada convocatoria:
- DETALLE: Descripción detallada del programa
- BENEFICIO: Beneficios ofrecidos
- QUIENES: Requisitos y público objetivo
- RESULTADOS: Resultados esperados

## Funcionamiento Detallado

### 1. Inicialización
- Carga del archivo de convocatorias enriquecido
- Configuración del sistema de logging
- Inicialización de variables y estructuras de datos

### 2. Proceso de Scraping
Para cada convocatoria:
1. Accede a la URL específica
2. Detecta el formato de la página
3. Extrae la información según el formato
4. Limpia y procesa los datos
5. Guarda incrementalmente

### 3. Formatos de Página Soportados

#### Formato Antiguo
```python
def extract_old_page_info(soup):
    """Extrae información de páginas con formato antiguo."""
    detalle = soup.select_one('.col-sm-8')
    beneficio = soup.select('.beneficios')
    quienes = soup.select('.requisitos')
    resultados = soup.select('.resultados_esperados')
```

#### Formato Nuevo
```python
def extract_new_page_info(soup):
    """Extrae información de páginas con formato nuevo."""
    detalle = soup.select('.marcoque_fase2')
    beneficio = soup.select('.postula_fase2-cuerpodos_fase2_bloque_q_entrega')
    quienes = soup.select('.postula_fase2-der_fase2')
    resultados = soup.select('.diviPuntoTexto_fase2')
```

## Estructura del Código

```python
class CorfoDetailScraper:
    def __init__(self):
        # Inicialización de variables y logging
        
    def procesar_convocatoria(self, url):
        # Procesamiento de cada convocatoria
        
    def extraer_detalles(self, soup):
        # Extracción de información detallada
        
    def guardar_progreso(self):
        # Guardado incremental de datos
```

## Manejo de Errores

El script incluye manejo de:
- Errores de conexión
- Páginas no encontradas
- Formatos de página desconocidos
- Timeouts
- Errores de parsing

## Configuración

```python
ARCHIVO_ENTRADA = 'corfo_convocatorias_enriched.csv'
ARCHIVO_SALIDA = 'corfo_convocatorias_full.csv'
TIEMPO_ESPERA = 2  # Segundos entre requests
```

## Requisitos

- Python 3.8+
- requests
- BeautifulSoup4
- pandas
- logging

## Uso

```bash
python corfo_detalle_scraper_b01.py
```

El script requiere:
- Archivo `corfo_convocatorias_enriched.csv`
- Conexión a internet estable

## Salida

El archivo `corfo_convocatorias_full.csv` contendrá:
- Todas las columnas originales
- Nuevas columnas de detalle
- Timestamp de actualización

## Procesamiento de Texto

El script incluye funciones para:
- Limpieza de HTML
- Normalización de texto
- Eliminación de caracteres especiales
- Formateo consistente

## Mejores Prácticas

1. Ejecutar después del scraper de filtros
2. Verificar integridad del archivo de entrada
3. Monitorear el log de errores
4. Mantener respaldos regulares
5. Validar datos extraídos

## Troubleshooting

### Problemas Comunes

1. **Errores de Conexión**
   - Verificar conectividad
   - Aumentar timeouts
   - Implementar reintentos

2. **Formato de Página No Reconocido**
   - Actualizar selectores
   - Verificar cambios en el sitio
   - Revisar logs detallados

3. **Memoria Insuficiente**
   - Procesar en lotes
   - Liberar recursos
   - Optimizar estructuras de datos

## Validación de Datos

El script valida:
- Completitud de campos
- Formato de texto
- URLs válidas
- Consistencia de datos
- Duplicados

## Mantenimiento

Tareas periódicas:
1. Actualizar expresiones regulares
2. Verificar selectores CSS
3. Optimizar tiempos de espera
4. Limpiar archivos temporales
5. Actualizar documentación

## Logs

El script genera logs detallados:
- Nivel INFO para progreso normal
- Nivel WARNING para problemas menores
- Nivel ERROR para fallos importantes
- Nivel DEBUG para diagnóstico

## Rendimiento

Optimizaciones implementadas:
- Procesamiento asíncrono
- Guardado incremental
- Manejo eficiente de memoria
- Timeouts configurables
- Reintentos inteligentes

## Seguridad

Consideraciones:
- Respeto a robots.txt
- Tiempos de espera apropiados
- No almacenamiento de datos sensibles
- Manejo seguro de archivos
- Validación de entrada/salida
