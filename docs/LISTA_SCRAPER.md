# Documentación del Scraper de Lista (corfo_scraper_lista_b01.py)

## Descripción General

Este script es el primer paso en el proceso de extracción de datos de CORFO. Su función principal es obtener un listado completo de todas las convocatorias disponibles en el sitio web de CORFO, tanto abiertas como cerradas.

## Características Principales

- Navegación automática por todas las páginas de convocatorias
- Extracción de información básica de cada convocatoria
- Guardado incremental de datos
- Manejo robusto de errores
- Sistema de logging detallado

## Datos Extraídos

Para cada convocatoria, el script extrae:
- Nombre de la convocatoria
- URL de la ficha detallada
- Estado (Abierta/Cerrada)
- Fecha de apertura
- Fecha de cierre
- Alcance territorial
- Descripción breve

## Funcionamiento Detallado

### 1. Inicialización
- Configura el webdriver de Chrome en modo headless
- Establece los parámetros de timeout y reintentos
- Inicializa el sistema de logging

### 2. Proceso de Scraping
1. Accede a la página principal de convocatorias
2. Aplica filtros para ver tanto convocatorias abiertas como cerradas
3. Detecta el número total de páginas
4. Para cada página:
   - Extrae información de cada convocatoria
   - Guarda los datos de forma incremental
   - Maneja posibles errores
   - Avanza a la siguiente página

### 3. Guardado de Datos
- Guarda los datos en formato CSV
- Evita duplicados mediante verificación de URLs
- Mantiene un registro de progreso

## Estructura del Código

```python
class CorfoScraper:
    def __init__(self):
        # Inicialización de variables y webdriver
        
    def iniciar_navegador(self):
        # Configuración del navegador Chrome
        
    def obtener_convocatorias(self):
        # Proceso principal de scraping
        
    def extraer_datos_convocatoria(self, elemento):
        # Extracción de datos de cada convocatoria
        
    def guardar_datos(self):
        # Guardado de datos en CSV
```

## Manejo de Errores

El script incluye manejo de errores para:
- Problemas de conexión
- Elementos no encontrados
- Timeouts
- Errores de formato de datos
- Problemas de guardado

## Configuración

Variables principales configurables:
```python
TIEMPO_ESPERA = 2  # Segundos entre requests
MAX_REINTENTOS = 3  # Número máximo de reintentos
ARCHIVO_SALIDA = 'corfo_convocatorias.csv'
```

## Requisitos

- Python 3.8+
- Selenium
- Chrome/Chromium Browser
- ChromeDriver
- pandas
- BeautifulSoup4

## Uso

```bash
python corfo_scraper_lista_b01.py
```

El script generará:
- Archivo CSV con los datos extraídos
- Archivo de log con el registro de la ejecución

## Salida

El archivo `corfo_convocatorias.csv` contendrá las siguientes columnas:
- NOMBRE
- URL
- ESTADO
- APERTURA
- CIERRE
- ALCANCE
- DESCRIPCION

## Mejores Prácticas

1. Ejecutar en horarios de bajo tráfico
2. Mantener un intervalo razonable entre ejecuciones
3. Verificar periódicamente cambios en la estructura del sitio
4. Revisar los logs después de cada ejecución
5. Hacer backup de los datos extraídos

## Troubleshooting

Problemas comunes y soluciones:
1. **Timeout al cargar página**
   - Aumentar TIEMPO_ESPERA
   - Verificar conexión a internet

2. **Elementos no encontrados**
   - Verificar selectores CSS
   - Comprobar cambios en el sitio web

3. **Errores de ChromeDriver**
   - Actualizar Chrome y ChromeDriver
   - Reiniciar el navegador
