# Documentación del Scraper de Filtros (corfo_scraper_filtros_b01.py)

## Descripción General

Este script representa el segundo paso en el proceso de extracción de datos. Su función es enriquecer la información base de las convocatorias aplicando diferentes filtros disponibles en el sitio web de CORFO y analizando qué convocatorias aparecen bajo cada filtro.

## Características Principales

- Procesamiento de 15 filtros diferentes
- Enriquecimiento de datos existentes
- Análisis de perfiles y etapas
- Guardado incremental
- Sistema de logging detallado

## Filtros Procesados

### Filtros de Perfil
1. Persona
2. Empresa
3. Organización
4. Intermediario
5. Institución
6. Extranjero

### Filtros de Etapa
1. Emprender
2. Idea de Negocio
3. Aumentar Ventas
4. Escalar
5. Innovar
6. I+D
7. Servicios
8. Ecosistema Emprendimiento
9. Otros

## Funcionamiento Detallado

### 1. Inicialización
- Carga del archivo de convocatorias base
- Configuración del webdriver
- Inicialización del sistema de logging

### 2. Proceso de Filtrado
Para cada filtro:
1. Selecciona el filtro en la interfaz web
2. Extrae todas las convocatorias visibles
3. Compara con la base de datos existente
4. Marca las coincidencias en nuevas columnas

### 3. Guardado de Datos
- Actualización del CSV con nuevas columnas
- Preservación de datos existentes
- Backup automático

## Estructura del Código

```python
class CorfoFilterScraper:
    def __init__(self):
        # Inicialización y carga de datos
        
    def aplicar_filtro(self, tipo_filtro, valor):
        # Aplicación de cada filtro
        
    def obtener_convocatorias_filtradas(self):
        # Extracción de convocatorias por filtro
        
    def actualizar_datos(self):
        # Actualización de la base de datos
```

## Datos Enriquecidos

El script agrega las siguientes columnas al dataset:
- PERFIL_PERSONA
- PERFIL_EMPRESA
- PERFIL_ORGANIZACION
- PERFIL_INTERMEDIARIO
- PERFIL_INSTITUCION
- PERFIL_EXTRANJERO
- ETAPA_EMPRENDER
- ETAPA_IDEA
- ETAPA_VENTAS
- ETAPA_ESCALAR
- ETAPA_INNOVAR
- ETAPA_ID
- ETAPA_SERVICIOS
- ETAPA_ECOSISTEMA
- ETAPA_OTROS

## Manejo de Errores

El script maneja:
- Errores de carga de filtros
- Problemas de conexión
- Inconsistencias en los datos
- Errores de guardado
- Timeouts

## Configuración

```python
ARCHIVO_ENTRADA = 'corfo_convocatorias.csv'
ARCHIVO_SALIDA = 'corfo_convocatorias_enriched.csv'
TIEMPO_ESPERA = 2  # Segundos entre acciones
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
python corfo_scraper_filtros_b01.py
```

El script requiere:
- Archivo `corfo_convocatorias.csv` en el directorio
- Conexión a internet
- Chrome instalado

## Salida

El archivo `corfo_convocatorias_enriched.csv` contendrá:
- Todas las columnas originales
- Nuevas columnas de filtros (valores True/False)
- Metadata adicional del proceso

## Mejores Prácticas

1. Verificar integridad del archivo de entrada
2. Ejecutar después del scraper de lista
3. Mantener respaldos de los datos
4. Monitorear los logs
5. Validar resultados periódicamente

## Troubleshooting

### Problemas Comunes

1. **Filtros no funcionan**
   - Verificar cambios en la interfaz web
   - Comprobar selectores CSS
   - Aumentar tiempos de espera

2. **Datos inconsistentes**
   - Verificar archivo de entrada
   - Validar formato de datos
   - Comprobar codificación UTF-8

3. **Errores de memoria**
   - Reducir tamaño de batch
   - Limpiar datos temporales
   - Reiniciar el navegador periódicamente

## Validación de Datos

El script incluye validaciones para:
- Consistencia de URLs
- Formato de datos
- Completitud de información
- Duplicados
- Valores nulos

## Mantenimiento

Tareas recomendadas:
1. Actualización periódica de dependencias
2. Verificación de selectores CSS
3. Monitoreo de cambios en el sitio
4. Backup de datos procesados
5. Revisión de logs
