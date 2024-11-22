"""
CORFO Web Scraper
----------------
Scraper para extraer información de convocatorias desde el sitio web de CORFO.
Extrae datos de convocatorias abiertas y cerradas, guardando los resultados en CSV.

Author: mlorca
License: MIT
Version: 1.0.0
"""

import logging
from datetime import datetime
import os
import time
from typing import Dict, List, Optional, Any

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WebDriverManager:
    """Gestiona la configuración y ciclo de vida del WebDriver."""
    
    def __init__(self, page_load_timeout: int = 180, script_timeout: int = 180):
        self.page_load_timeout = page_load_timeout
        self.script_timeout = script_timeout
        self.driver = None
        self.wait = None

    def setup(self) -> None:
        """Configura una nueva instancia del WebDriver."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-features=NetworkService')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.page_load_strategy = 'eager'
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(self.page_load_timeout)
        self.driver.set_script_timeout(self.script_timeout)
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.implicitly_wait(10)

    def quit(self) -> None:
        """Cierra el WebDriver de manera segura."""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logging.error(f"Error cerrando WebDriver: {e}")
        finally:
            self.driver = None
            self.wait = None

    def restart(self) -> None:
        """Reinicia el WebDriver."""
        self.quit()
        self.setup()

class CorfoScraper:
    """Scraper principal para el sitio web de CORFO."""

    def __init__(self, csv_filename: str = "corfo_convocatorias.csv"):
        self.base_url = "https://corfo.cl/sites/cpp/programasyconvocatorias"
        self.csv_filename = csv_filename
        self.driver_manager = WebDriverManager()
        self.df_existing = pd.DataFrame()
        self.total_nuevas = 0
        self.max_retries = 3

    def _wait_and_find_element(self, by: By, value: str, timeout: int = 20) -> Optional[Any]:
        """Espera y encuentra un elemento en la página."""
        try:
            element = WebDriverWait(self.driver_manager.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            self.driver_manager.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            return element
        except TimeoutException:
            logging.error(f"Timeout esperando elemento {value}")
            return None

    def _clean_html(self, html_content: str) -> str:
        """Limpia el contenido HTML de elementos no deseados."""
        if not html_content:
            return "No disponible"
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Eliminar elementos específicos
        for span in soup.find_all('span', style="border: 2px solid #2fca70;padding: 20px;display: inline-block;"):
            if "Plataforma Matchmaking" in span.text:
                span.decompose()
        
        for a in soup.find_all('a'):
            a.decompose()
        
        text = soup.get_text().replace('<br> " -', '').replace('" -', '')
        return text.strip() or "No disponible"

    def _extract_convocatoria_data(self, caja: Any) -> Optional[Dict[str, str]]:
        """Extrae datos de una convocatoria individual."""
        try:
            data = {
                'NOMBRE': caja.find_element(By.CLASS_NAME, "titulo-cajas_fechas").text.strip(),
                'APERTURA': caja.find_element(By.CSS_SELECTOR, ".apertura span").text.strip(),
                'CIERRE': caja.find_element(By.CSS_SELECTOR, ".cierre span").text.strip(),
                'ALCANCE': 'No especificado',
                'ESTADO': 'No especificado',
                'RESUMEN': 'No disponible',
                'URL': 'No disponible'
            }

            try:
                data['ALCANCE'] = caja.find_element(
                    By.XPATH, ".//*[contains(text(), 'Alcance:')]"
                ).text.replace("Alcance:", "").strip()
            except NoSuchElementException:
                pass

            try:
                data['ESTADO'] = caja.find_element(
                    By.XPATH, ".//*[contains(text(), 'Estado:')]"
                ).text.replace("Estado:", "").strip()
            except NoSuchElementException:
                pass

            try:
                data['RESUMEN'] = self._clean_html(
                    caja.find_element(By.TAG_NAME, "p").get_attribute('innerHTML')
                )
            except NoSuchElementException:
                pass

            try:
                url_elem = caja.find_element(By.CSS_SELECTOR, ".foot-caja_result a")
                url = url_elem.get_attribute("href")
                data['URL'] = f"https://corfo.cl{url}" if not url.startswith("https://corfo.cl") else url
            except NoSuchElementException:
                pass

            return data
        except Exception as e:
            logging.error(f"Error extrayendo datos de convocatoria: {e}")
            return None

    def _check_next_page(self) -> bool:
        """Verifica si existe y hace clic en el botón 'Siguiente'."""
        try:
            next_button = self._wait_and_find_element(
                By.XPATH,
                "//li[@class='page-item']/a[@class='page-link' and contains(text(), 'Siguiente')]"
            )
            if next_button:
                next_button.click()
                time.sleep(2)
                return True
            return False
        except Exception:
            return False

    def _ensure_filter_visible(self) -> None:
        """Asegura que el filtro de Estado esté visible."""
        try:
            accordion = self._wait_and_find_element(
                By.CSS_SELECTOR, 
                "button.accordion-button.collapsed"
            )
            if accordion:
                accordion.click()
                time.sleep(1)
        except Exception as e:
            logging.error(f"Error al expandir filtros: {e}")

    def _load_existing_data(self) -> None:
        """Carga datos existentes del CSV si existe."""
        if os.path.exists(self.csv_filename):
            try:
                self.df_existing = pd.read_csv(self.csv_filename)
                logging.info(f"Datos existentes cargados: {len(self.df_existing)} registros")
            except Exception as e:
                logging.error(f"Error al cargar CSV existente: {e}")
                self.df_existing = pd.DataFrame()

    def _save_data(self, convocatorias: List[Dict[str, str]]) -> None:
        """Guarda los datos en CSV."""
        try:
            df_new = pd.DataFrame(convocatorias)
            
            if not self.df_existing.empty:
                # Combinar datos nuevos con existentes
                df_combined = pd.concat([self.df_existing, df_new], ignore_index=True)
                # Eliminar duplicados basados en NOMBRE y URL
                df_combined = df_combined.drop_duplicates(subset=['NOMBRE', 'URL'], keep='last')
                df_combined.to_csv(self.csv_filename, index=False)
                self.total_nuevas = len(df_combined) - len(self.df_existing)
            else:
                df_new.to_csv(self.csv_filename, index=False)
                self.total_nuevas = len(df_new)
                
            logging.info(f"Se agregaron {self.total_nuevas} nuevas convocatorias")
            
        except Exception as e:
            logging.error(f"Error al guardar datos: {e}")
            raise

    def scrape(self) -> None:
        """Ejecuta el proceso de scraping."""
        convocatorias = []
        
        try:
            self.driver_manager.setup()
            self.driver_manager.driver.get(self.base_url)
            
            # Expandir filtros si es necesario
            self._ensure_filter_visible()
            
            while True:
                # Esperar a que las cajas de convocatorias estén presentes
                cajas = self._wait_and_find_element(
                    By.CLASS_NAME, "caja-resultado"
                )
                if not cajas:
                    break
                
                # Extraer datos de cada caja
                cajas = self.driver_manager.driver.find_elements(By.CLASS_NAME, "caja-resultado")
                for caja in cajas:
                    data = self._extract_convocatoria_data(caja)
                    if data:
                        convocatorias.append(data)
                
                # Verificar siguiente página
                if not self._check_next_page():
                    break
            
            return convocatorias
            
        except Exception as e:
            logging.error(f"Error durante el scraping: {e}")
            raise
        finally:
            self.driver_manager.quit()

    def run(self) -> None:
        """Ejecuta el proceso completo de scraping."""
        try:
            logging.info("Iniciando scraping de convocatorias CORFO...")
            self._load_existing_data()
            
            convocatorias = self.scrape()
            if convocatorias:
                self._save_data(convocatorias)
                logging.info("Proceso completado exitosamente")
            else:
                logging.warning("No se encontraron convocatorias")
                
        except Exception as e:
            logging.error(f"Error durante la ejecución: {e}")
            raise

def main():
    """Función principal."""
    scraper = CorfoScraper()
    scraper.run()

if __name__ == "__main__":
    main()
