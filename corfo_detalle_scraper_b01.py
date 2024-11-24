#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CORFO Web Scraper - Extractor de Detalles de Convocatorias
Versión B01 - Enriquecimiento de datos de convocatorias

Este script toma el archivo corfo_convocatorias_enriched.csv y agrega información
detallada de cada convocatoria, manteniendo todos los datos originales.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import sys
import logging
from typing import Dict, Optional
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('corfo_scraper_detalles.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuración
ARCHIVO_ENTRADA = 'corfo_convocatorias_enriched.csv'
ARCHIVO_SALIDA = 'corfo_convocatorias_full.csv'
TIEMPO_ESPERA = 2  # segundos entre requests

def extract_text(soup: BeautifulSoup, selector: str, default: str = "No disponible", get_all: bool = False) -> str:
    """Extrae texto de manera segura desde elementos HTML."""
    try:
        elements = soup.select(selector)
        if get_all:
            return ' '.join([el.get_text(strip=True) for el in elements]) if elements else default
        else:
            return elements[0].get_text(strip=True) if elements else default
    except Exception as e:
        logger.warning(f"Error al extraer texto con selector {selector}: {str(e)}")
        return default

def extract_old_page_info(soup: BeautifulSoup) -> Dict[str, str]:
    """Extrae información de páginas con formato antiguo."""
    try:
        detalle = soup.select_one('.col-sm-8')
        if not detalle:
            return {}

        info = {
            'DETALLE': extract_text(detalle, 'p', get_all=True),
            'BENEFICIO': extract_text(detalle, '.beneficios', get_all=True),
            'QUIENES': extract_text(detalle, '.requisitos', get_all=True),
            'RESULTADOS': extract_text(detalle, '.resultados_esperados', get_all=True)
        }
        
        return {k: v for k, v in info.items() if v != "No disponible"}
    except Exception as e:
        logger.error(f"Error al procesar página antigua: {str(e)}")
        return {}

def extract_new_page_info(soup: BeautifulSoup) -> Dict[str, str]:
    """Extrae información de páginas con formato nuevo."""
    try:
        info = {
            'DETALLE': extract_text(soup, '.marcoque_fase2', get_all=True),
            'BENEFICIO': extract_text(soup, '.postula_fase2-cuerpodos_fase2_bloque_q_entrega', get_all=True),
            'QUIENES': extract_text(soup, '.postula_fase2-der_fase2', get_all=True),
            'RESULTADOS': extract_text(soup, '.diviPuntoTexto_fase2')
        }
        
        return {k: v for k, v in info.items() if v != "No disponible"}
    except Exception as e:
        logger.error(f"Error al procesar página nueva: {str(e)}")
        return {}

def guardar_progreso(df_original: pd.DataFrame, datos_nuevos: Dict[str, Dict], archivo: str):
    """Guarda el progreso combinando datos originales con nuevos."""
    try:
        # Crear un DataFrame con los nuevos datos
        df_nuevos = pd.DataFrame.from_dict(datos_nuevos, orient='index')
        
        # Combinar con el DataFrame original
        df_combinado = df_original.copy()
        for columna in ['DETALLE', 'BENEFICIO', 'QUIENES', 'RESULTADOS']:
            if columna not in df_combinado.columns:
                df_combinado[columna] = 'No disponible'
        
        # Actualizar con los nuevos datos
        for url, datos in datos_nuevos.items():
            mask = df_combinado['URL'] == url
            for campo, valor in datos.items():
                # Limpiar "¿Qué es?" del inicio de DETALLE
                if campo == 'DETALLE' and isinstance(valor, str):
                    valor = re.sub(r'^¿Qué es\?[\s:]*', '', valor.strip())
                df_combinado.loc[mask, campo] = valor
        
        # Guardar
        df_combinado.to_csv(archivo, index=False, encoding='utf-8')
        logger.info(f"Progreso guardado en {archivo}")
        
    except Exception as e:
        logger.error(f"Error al guardar progreso: {str(e)}")

def main():
    """Función principal de ejecución."""
    try:
        # Leer archivo de entrada
        logger.info(f"Leyendo archivo {ARCHIVO_ENTRADA}")
        try:
            df = pd.read_csv(ARCHIVO_ENTRADA)
            logger.info(f"Archivo cargado exitosamente. Total de registros: {len(df)}")
            logger.info(f"Columnas disponibles: {df.columns.tolist()}")
        except FileNotFoundError:
            logger.error(f"No se encontró el archivo {ARCHIVO_ENTRADA}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error al leer el archivo: {str(e)}")
            sys.exit(1)

        # Verificar columna URL
        if 'URL' not in df.columns:
            logger.error("El archivo no contiene la columna 'URL' requerida")
            sys.exit(1)

        # Diccionario para almacenar los nuevos datos
        datos_nuevos = {}
        total = len(df)
        
        # Procesar cada URL
        for i, (index, row) in enumerate(df.iterrows(), 1):
            url = row['URL']
            logger.info(f"Procesando {i}/{total}: {url}")
            
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Intentar ambos formatos
                info_new = extract_new_page_info(soup)
                info_old = extract_old_page_info(soup)
                
                # Usar la información que tenga más campos
                info = info_new if len(info_new) >= len(info_old) else info_old
                
                if info:
                    datos_nuevos[url] = info
                    logger.info(f"Información extraída exitosamente de {url}")
                else:
                    logger.warning(f"No se pudo extraer información de {url}")
                
                # Guardar progreso cada 10 registros o al final
                if i % 10 == 0 or i == total:
                    guardar_progreso(df, datos_nuevos, ARCHIVO_SALIDA)
                    logger.info(f"Progreso: {i}/{total} URLs procesadas")
                
                time.sleep(TIEMPO_ESPERA)
                
            except Exception as e:
                logger.error(f"Error procesando {url}: {str(e)}")
                continue
        
        logger.info("Proceso completado")
        logger.info(f"Total de URLs procesadas: {total}")
        logger.info(f"Total de URLs con información extraída: {len(datos_nuevos)}")
        
    except Exception as e:
        logger.critical(f"Error crítico en la ejecución: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
