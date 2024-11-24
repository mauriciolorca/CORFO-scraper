# CORFO Web Scraper

Este proyecto proporciona un conjunto de herramientas para extraer y analizar información de los programas y convocatorias de CORFO (Corporación de Fomento de la Producción de Chile).

## Descripción

El proyecto consta de tres scripts principales que trabajan en secuencia para recopilar información detallada de las convocatorias de CORFO:

1. `corfo_scraper_lista_b01.py`: Extrae el listado completo de convocatorias
2. `corfo_scraper_filtros_b01.py`: Enriquece los datos con información de filtros
3. `corfo_detalle_scraper_b01.py`: Obtiene información detallada de cada convocatoria

## Requisitos

- Python 3.8+
- Chrome/Chromium Browser
- Dependencias de Python (ver `requirements.txt`)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/mauriciolorca/CORFO-scraper.git
cd CORFO-scraper
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### 1. Extracción de Lista Base (`corfo_scraper_lista_b01.py`)

Este script extrae el listado completo de convocatorias abiertas y cerradas.

```bash
python corfo_scraper_lista_b01.py
```

- **Entrada**: Ninguna
- **Salida**: `corfo_convocatorias.csv`
- **Funcionalidad**:
  - Navega por todas las páginas de convocatorias
  - Extrae información básica de cada convocatoria
  - Guarda datos incrementalmente

### 2. Enriquecimiento con Filtros (`corfo_scraper_filtros_b01.py`)

Analiza las convocatorias a través de 15 filtros diferentes y enriquece la información.

```bash
python corfo_scraper_filtros_b01.py
```

- **Entrada**: `corfo_convocatorias.csv`
- **Salida**: `corfo_convocatorias_enriched.csv`
- **Filtros procesados**:
  - Perfiles: Persona, Empresa, Organización, Intermediario, Institución, Extranjero
  - Etapas: Emprender, Idea de Negocio, Aumentar Ventas, Escalar, Innovar, I+D, Servicios, Ecosistema Emprendimiento

### 3. Extracción de Detalles (`corfo_detalle_scraper_b01.py`)

Obtiene información detallada de cada convocatoria accediendo a sus fichas individuales.

```bash
python corfo_detalle_scraper_b01.py
```

- **Entrada**: `corfo_convocatorias_enriched.csv`
- **Salida**: `corfo_convocatorias_full.csv`
- **Información extraída**:
  - Detalles del programa
  - Beneficios
  - Requisitos
  - Resultados esperados

## Estructura de Archivos

```
CORFO-scraper/
├── README.md
├── requirements.txt
├── corfo_scraper_lista_b01.py
├── corfo_scraper_filtros_b01.py
├── corfo_detalle_scraper_b01.py
└── docs/
    ├── LISTA_SCRAPER.md
    ├── FILTROS_SCRAPER.md
    └── DETALLE_SCRAPER.md
```

## Documentación Detallada

Para información más detallada sobre cada script, consulte los archivos en la carpeta `docs/`:

- [Documentación del Scraper de Lista](docs/LISTA_SCRAPER.md)
- [Documentación del Scraper de Filtros](docs/FILTROS_SCRAPER.md)
- [Documentación del Scraper de Detalles](docs/DETALLE_SCRAPER.md)

## Manejo de Errores

Cada script incluye:
- Logging detallado
- Guardado incremental de datos
- Recuperación de errores
- Timeouts configurables

## Contribuir

1. Fork el repositorio
2. Cree una rama para su característica (`git checkout -b feature/AmazingFeature`)
3. Commit sus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abra un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - vea el archivo [LICENSE](LICENSE) para detalles.

## Contacto

Mauricio Lorca - [@mauriciolorca](https://github.com/mauriciolorca)

Link del proyecto: [https://github.com/mauriciolorca/CORFO-scraper](https://github.com/mauriciolorca/CORFO-scraper)
