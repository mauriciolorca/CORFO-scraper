# CORFO Web Scraper

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Un scraper robusto y eficiente para extraer información de convocatorias desde el sitio web de CORFO (Corporación de Fomento de la Producción).

## Características

- Extracción automática de convocatorias abiertas y cerradas
- Manejo robusto de errores y reintentos
- Sistema de logging detallado
- Prevención de duplicados
- Almacenamiento en CSV con IDs únicos
- Manejo eficiente de recursos del navegador
- Documentación completa

## Datos Extraídos

Para cada convocatoria, el scraper extrae:
- ID único
- Nombre de la convocatoria
- Fecha de apertura
- Fecha de cierre
- Alcance
- Estado
- Resumen
- URL

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/[tu-usuario]/corfo-scraper.git
cd corfo-scraper
```

2. Crea un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Para ejecutar el scraper:

```bash
python corfo_scraper.py
```

Los resultados se guardarán en `corfo_convocatorias.csv` en el directorio actual.

## Estructura del Proyecto

```
corfo-scraper/
│
├── corfo_scraper.py     # Script principal
├── requirements.txt     # Dependencias del proyecto
├── LICENSE             # Licencia MIT
├── README.md          # Este archivo
└── .gitignore        # Archivos ignorados por git
```

## Detalles Técnicos

### Componentes Principales

1. **WebDriverManager**: Gestiona el ciclo de vida del navegador Chrome
   - Configuración automática
   - Manejo de recursos
   - Reinicio automático en caso de problemas

2. **CorfoScraper**: Clase principal del scraper
   - Extracción de datos
   - Manejo de paginación
   - Gestión de CSV
   - Sistema de logging

### Manejo de Errores

- Reintentos automáticos en caso de timeout
- Logging detallado de errores
- Recuperación automática de fallos
- Preservación de datos en caso de error

## Logs

El scraper genera logs detallados con:
- Progreso del scraping
- Nuevas convocatorias encontradas
- Errores y advertencias
- Estadísticas de ejecución

## Contribuir

1. Fork el proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: nueva característica'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## Notas Importantes

- Respetar los términos de uso del sitio web de CORFO
- Mantener un intervalo razonable entre ejecuciones
- Verificar cambios en la estructura del sitio web

## Mantenimiento

Para mantener el scraper funcionando correctamente:
1. Revisar periódicamente cambios en el sitio web
2. Actualizar las dependencias
3. Verificar los selectores CSS/XPath
4. Monitorear los logs en busca de errores

## Contacto

[Tu Nombre] - [tu@email.com]

Link del proyecto: [https://github.com/[tu-usuario]/corfo-scraper](https://github.com/[tu-usuario]/corfo-scraper)
