"""
CORFO Web Scraper
----------------
Scraper para extraer información de convocatorias desde el sitio web de CORFO.
Maneja tanto convocatorias abiertas como cerradas y guarda los resultados en CSV.

Autor: [Tu Nombre]
Versión: 8.0
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Configuración de logging
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

            # Extraer campos opcionales
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
                url = caja.find_element(By.CSS_SELECTOR, ".foot-caja_result a").get_attribute("href")
                data['URL'] = f"https://corfo.cl{url}" if not url.startswith("https://corfo.cl") else url
            except NoSuchElementException:
                pass

            return data
        except Exception as e:
            logging.error(f"Error extrayendo datos: {e}")
            return None

    def _apply_filters(self) -> bool:
        """Aplica los filtros de estado para mostrar convocatorias abiertas y cerradas."""
        try:
            # Expandir filtros si es necesario
            accordion = self._wait_and_find_element(By.ID, "collapse1")
            if accordion and "show" not in accordion.get_attribute("class"):
                self.driver_manager.driver.find_element(By.ID, "heading1").click()
                time.sleep(1)

            # Marcar checkboxes
            for estado in ['abierta', 'cerrada']:
                checkbox = self._wait_and_find_element(By.ID, f"pullEstado-{estado}-checkbox")
                if checkbox and not checkbox.is_selected():
                    self.driver_manager.driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(1)

            # Aplicar filtros
            apply_button = self._wait_and_find_element(By.CSS_SELECTOR, "button.cpp-button-search")
            if apply_button:
                self.driver_manager.driver.execute_script("arguments[0].click();", apply_button)
                time.sleep(3)
                return True
            return False
        except Exception as e:
            logging.error(f"Error aplicando filtros: {e}")
            return False

    def _update_csv(self, nuevas_convocatorias: List[Dict[str, str]], pagina: int) -> int:
        """Actualiza el CSV con nuevas convocatorias."""
        if not nuevas_convocatorias:
            return 0

        df_new = pd.DataFrame(nuevas_convocatorias)
        if not self.df_existing.empty:
            existing_urls = set(self.df_existing['URL'].tolist())
            df_new = df_new[~df_new['URL'].isin(existing_urls)]

        if len(df_new) > 0:
            last_id = 0 if self.df_existing.empty else self.df_existing['ID'].max()
            df_new.insert(0, 'ID', range(last_id + 1, last_id + 1 + len(df_new)))
            
            self.df_existing = pd.concat([self.df_existing, df_new], ignore_index=True)
            self.df_existing.to_csv(self.csv_filename, index=False, encoding='utf-8-sig')

            # Logging de nuevas convocatorias
            logging.info(f"\nPágina {pagina}: Se agregaron {len(df_new)} nuevas convocatorias:")
            for _, conv in df_new.iterrows():
                logging.info(f"- {conv['NOMBRE']}")
                logging.info(f"  Apertura: {conv['APERTURA']}")
                logging.info(f"  Cierre: {conv['CIERRE']}")
                logging.info(f"  Estado: {conv['ESTADO']}")
                logging.info(f"  URL: {conv['URL']}\n")

        return len(df_new)

    def _scrape_page(self, pagina: int) -> bool:
        """Realiza el scraping de una página."""
        try:
            # Esperar carga de página
            self._wait_and_find_element(By.ID, "listSearch")
            
            # Aplicar filtros en primera página
            if pagina == 1 and not self._apply_filters():
                return False

            # Extraer convocatorias
            cajas = self.driver_manager.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "caja-resultados_uno"))
            )
            
            convocatorias = []
            for caja in cajas:
                if data := self._extract_convocatoria_data(caja):
                    convocatorias.append(data)

            # Actualizar CSV
            nuevas = self._update_csv(convocatorias, pagina)
            self.total_nuevas += nuevas
            
            return True
        except Exception as e:
            logging.error(f"Error en página {pagina}: {e}")
            return False

    def _check_next_page(self) -> bool:
        """Verifica y navega a la siguiente página si existe."""
        try:
            next_button = self._wait_and_find_element(
                By.XPATH,
                "//li[@class='page-item']/a[@class='page-link' and contains(text(), 'Siguiente')]",
                timeout=5
            )
            if next_button:
                self.driver_manager.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
                return True
            return False
        except Exception:
            return False

    def run(self) -> None:
        """Ejecuta el proceso completo de scraping."""
        try:
            self.driver_manager.setup()
            
            # Cargar datos existentes
            if os.path.exists(self.csv_filename):
                self.df_existing = pd.read_csv(self.csv_filename)
            
            # Iniciar scraping
            self.driver_manager.driver.get(self.base_url)
            pagina = 1
            
            while True:
                logging.info(f"\nProcesando página {pagina}...")
                for _ in range(self.max_retries):
                    try:
                        if not self._scrape_page(pagina):
                            raise Exception("Error procesando página")
                        break
                    except Exception as e:
                        if "timeout" in str(e).lower():
                            logging.warning("Timeout detectado, reiniciando driver...")
                            self.driver_manager.restart()
                            self.driver_manager.driver.get(self.base_url)
                            continue
                        raise e

                if not self._check_next_page():
                    break
                pagina += 1

            logging.info(f"\nProceso completado. Total de nuevas convocatorias agregadas: {self.total_nuevas}")
            
        except Exception as e:
            logging.error(f"Error durante la ejecución: {e}")
        finally:
            self.driver_manager.quit()

if __name__ == "__main__":
    scraper = CorfoScraper()
    scraper.run()
