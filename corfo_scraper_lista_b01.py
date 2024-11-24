from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import logging
from datetime import datetime

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CorfoScraper:
    def __init__(self):
        self.base_url = "https://corfo.cl/sites/cpp/programasyconvocatorias"
        self.driver = None
        self.wait = None
        self.csv_filename = "corfo_convocatorias.csv"
        self.df_existing = None
        self.current_page_convocatorias = []
        self.total_nuevas = 0
        self.max_retries = 3
        self.page_load_timeout = 180
        self.script_timeout = 180

    def setup_driver(self):
        """Configura el driver de Selenium con Chrome"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-features=NetworkService')  # Ayuda con problemas de timeout
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.page_load_strategy = 'eager'  # Carga más rápida
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(self.page_load_timeout)
        self.driver.set_script_timeout(self.script_timeout)
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.implicitly_wait(10)

    def retry_on_timeout(self, func, *args, **kwargs):
        """Reintenta una función en caso de timeout"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:  # Si es el último intento
                    raise e
                logging.warning(f"Intento {attempt + 1} falló: {str(e)}. Reintentando...")
                time.sleep(5)  # Esperar antes de reintentar
                
                # Si es un error de timeout, reiniciar el driver
                if "timeout" in str(e).lower():
                    logging.info("Reiniciando el driver debido a timeout...")
                    self.restart_driver()

    def restart_driver(self):
        """Reinicia el driver en caso de problemas"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        finally:
            self.setup_driver()

    def wait_for_element(self, by, value, timeout=20):
        """Espera a que un elemento esté presente y visible"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            return element
        except TimeoutException:
            logging.error(f"Timeout esperando elemento {value}")
            return None

    def clean_resumen(self, html_content):
        """Limpia el contenido del resumen según las reglas especificadas"""
        if not html_content:
            return "No disponible"
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for span in soup.find_all('span', style="border: 2px solid #2fca70;padding: 20px;display: inline-block;"):
            if "Plataforma Matchmaking" in span.text:
                span.decompose()
        
        for a in soup.find_all('a'):
            a.decompose()
        
        text = soup.get_text()
        text = text.replace('<br> " -', '')
        text = text.replace('" -', '')
        
        return text.strip() or "No disponible"

    def get_existing_data(self):
        """Lee el archivo CSV existente si existe"""
        if os.path.exists(self.csv_filename):
            try:
                return pd.read_csv(self.csv_filename)
            except Exception as e:
                logging.error(f"Error leyendo CSV existente: {e}")
                return pd.DataFrame()
        return pd.DataFrame()

    def parse_convocatoria(self, caja):
        """Extrae la información de una convocatoria individual"""
        try:
            data = {
                'NOMBRE': '',
                'APERTURA': '',
                'CIERRE': '',
                'ALCANCE': 'No especificado',
                'ESTADO': 'No especificado',
                'RESUMEN': 'No disponible',
                'URL': 'No disponible'
            }
            
            data['NOMBRE'] = caja.find_element(By.CLASS_NAME, "titulo-cajas_fechas").text.strip()
            
            # Obtener fechas directamente del span
            try:
                apertura_span = caja.find_element(By.CSS_SELECTOR, ".apertura span")
                data['APERTURA'] = apertura_span.text.strip()
            except NoSuchElementException:
                logging.debug(f"No se encontró fecha de apertura para {data['NOMBRE']}")
                data['APERTURA'] = "No disponible"
            
            try:
                cierre_span = caja.find_element(By.CSS_SELECTOR, ".cierre span")
                data['CIERRE'] = cierre_span.text.strip()
            except NoSuchElementException:
                logging.debug(f"No se encontró fecha de cierre para {data['NOMBRE']}")
                data['CIERRE'] = "No disponible"
            
            try:
                alcance_elem = caja.find_element(By.XPATH, ".//*[contains(text(), 'Alcance:')]")
                data['ALCANCE'] = alcance_elem.text.replace("Alcance:", "").strip()
            except NoSuchElementException:
                logging.debug(f"No se encontró alcance para {data['NOMBRE']}")
            
            try:
                estado_elem = caja.find_element(By.XPATH, ".//*[contains(text(), 'Estado:')]")
                data['ESTADO'] = estado_elem.text.replace("Estado:", "").strip()
            except NoSuchElementException:
                logging.debug(f"No se encontró estado para {data['NOMBRE']}")
            
            try:
                resumen_elem = caja.find_element(By.TAG_NAME, "p")
                data['RESUMEN'] = self.clean_resumen(resumen_elem.get_attribute('innerHTML'))
            except NoSuchElementException:
                logging.debug(f"No se encontró resumen para {data['NOMBRE']}")
            
            try:
                url_elem = caja.find_element(By.CSS_SELECTOR, ".foot-caja_result a")
                url = url_elem.get_attribute("href")
                data['URL'] = f"https://corfo.cl{url}" if not url.startswith("https://corfo.cl") else url
            except NoSuchElementException:
                logging.debug(f"No se encontró URL para {data['NOMBRE']}")
            
            return data

        except Exception as e:
            logging.error(f"Error parseando convocatoria: {e}")
            return None

    def check_next_page(self):
        """Verifica si existe el botón 'Siguiente' y hace clic en él"""
        try:
            next_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//li[@class='page-item']/a[@class='page-link' and contains(text(), 'Siguiente')]"
                ))
            )
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1)
            next_button.click()
            time.sleep(2)
            return True
        except (NoSuchElementException, TimeoutException):
            return False

    def ensure_filter_visible(self):
        """Asegura que el filtro de Estado esté visible"""
        try:
            # Verificar si el acordeón está colapsado
            accordion = self.wait_for_element(By.ID, "collapse1")
            if not "show" in accordion.get_attribute("class"):
                # Click en el encabezado para expandir
                heading = self.driver.find_element(By.ID, "heading1")
                heading.click()
                time.sleep(1)
            return True
        except Exception as e:
            logging.error(f"Error asegurando visibilidad del filtro: {e}")
            return False

    def apply_filters(self):
        """Aplica los filtros de estado (Abiertas y Cerradas)"""
        try:
            # Asegurar que el filtro esté visible
            if not self.ensure_filter_visible():
                return False

            # Marcar checkbox de convocatorias cerradas (Abiertas ya está marcado por defecto)
            logging.info("Configurando filtros de estado...")
            
            # Asegurar que 'Abiertas' esté marcado
            checkbox_abierta = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "pullEstado-abierta-checkbox"))
            )
            if not checkbox_abierta.is_selected():
                self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_abierta)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", checkbox_abierta)
                logging.info("Checkbox 'Abiertas' marcado")
                time.sleep(1)

            # Marcar 'Cerradas'
            checkbox_cerrada = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "pullEstado-cerrada-checkbox"))
            )
            if not checkbox_cerrada.is_selected():
                self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_cerrada)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", checkbox_cerrada)
                logging.info("Checkbox 'Cerradas' marcado")
                time.sleep(1)

            # Hacer click en el botón "Aplicar filtros"
            logging.info("Aplicando filtros...")
            try:
                # Buscar y hacer click en el botón de aplicar filtros
                apply_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button.cpp-button-search"))
                )
                self.driver.execute_script("arguments[0].click();", apply_button)
                logging.info("Filtros aplicados exitosamente")
                time.sleep(3)  # Esperar a que se apliquen los filtros y se carguen los resultados
                return True
            except NoSuchElementException:
                logging.error("No se pudo encontrar el botón 'Aplicar filtros'")
                return False
            
        except Exception as e:
            logging.error(f"Error aplicando filtros: {e}")
            return False

    def update_csv_with_page_data(self, pagina):
        """Actualiza el CSV con los datos de la página actual"""
        if not self.current_page_convocatorias:
            logging.info("No se encontraron convocatorias en esta página")
            return 0
        
        # Crear DataFrame con convocatorias de la página actual
        df_page = pd.DataFrame(self.current_page_convocatorias)
        nuevas_convocatorias = len(df_page)
        
        if not self.df_existing.empty:
            # Verificar duplicados basados en URL
            existing_urls = set(self.df_existing['URL'].tolist())
            df_page = df_page[~df_page['URL'].isin(existing_urls)]
            nuevas_convocatorias = len(df_page)
        
        if nuevas_convocatorias > 0:
            # Agregar IDs a las nuevas convocatorias
            last_id = 0 if self.df_existing.empty else self.df_existing['ID'].max()
            df_page.insert(0, 'ID', range(last_id + 1, last_id + 1 + len(df_page)))
            
            # Concatenar con las convocatorias existentes (nuevas al final)
            if self.df_existing.empty:
                self.df_existing = df_page
            else:
                self.df_existing = pd.concat([self.df_existing, df_page], ignore_index=True)
            
            # Guardar el DataFrame actualizado
            self.df_existing.to_csv(self.csv_filename, index=False, encoding='utf-8-sig')
            
            # Reportar nuevas convocatorias
            logging.info(f"\nPágina {pagina}: Se agregaron {nuevas_convocatorias} nuevas convocatorias:")
            for _, conv in df_page.iterrows():
                logging.info(f"- {conv['NOMBRE']}")
                logging.info(f"  Apertura: {conv['APERTURA']}")
                logging.info(f"  Cierre: {conv['CIERRE']}")
                logging.info(f"  Estado: {conv['ESTADO']}")
                logging.info(f"  URL: {conv['URL']}\n")
        
        # Limpiar lista de convocatorias de la página
        self.current_page_convocatorias = []
        return nuevas_convocatorias

    def scrape_page(self, pagina):
        """Realiza el scraping de la página actual"""
        def _scrape():
            logging.info("Esperando que se cargue el listado...")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "listSearch"))
            )

            # Aplicar filtros solo en la primera página
            if pagina == 1:
                if not self.apply_filters():
                    return False

            logging.info("Esperando que se carguen las cajas de resultados...")
            cajas = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "caja-resultados_uno"))
            )
            
            logging.info(f"Procesando {len(cajas)} convocatorias encontradas...")
            self.current_page_convocatorias = []
            for caja in cajas:
                convocatoria = self.parse_convocatoria(caja)
                if convocatoria:
                    self.current_page_convocatorias.append(convocatoria)
            
            # Actualizar CSV con los datos de esta página
            nuevas = self.update_csv_with_page_data(pagina)
            self.total_nuevas += nuevas
            
            return True

        try:
            return self.retry_on_timeout(_scrape)
        except Exception as e:
            logging.error(f"Error en scrape_page: {e}")
            return False

    def check_duplicates(self):
        """Verifica si hay duplicados potenciales"""
        if not os.path.exists(self.csv_filename):
            return False
            
        try:
            # Obtener primera página sin procesar completamente
            self.driver.get(self.base_url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "caja-resultados_uno"))
            )
            
            primera_convocatoria = self.driver.find_element(
                By.CLASS_NAME, "titulo-cajas_fechas"
            ).text.strip()
            
            # Verificar si existe en el CSV
            df = pd.read_csv(self.csv_filename)
            return primera_convocatoria in df['NOMBRE'].values
            
        except Exception as e:
            logging.error(f"Error verificando duplicados: {e}")
            return False

    def run(self):
        """Ejecuta el proceso completo de scraping"""
        try:
            self.setup_driver()
            
            # Verificar duplicados solo si existe el archivo
            if self.check_duplicates():
                respuesta = input("Se encontraron convocatorias que ya existen en la base de datos. ¿Desea continuar? (s/n): ")
                if respuesta.lower() != 's':
                    logging.info("Operación cancelada por el usuario")
                    return
            
            # Cargar datos existentes
            self.df_existing = self.get_existing_data()
            
            # Iniciar scraping
            self.driver.get(self.base_url)
            pagina = 1
            
            while True:
                logging.info(f"\nProcesando página {pagina}...")
                try:
                    if not self.scrape_page(pagina):
                        break
                    
                    if not self.check_next_page():
                        logging.info("No hay más páginas para procesar")
                        break
                        
                    pagina += 1
                except Exception as e:
                    logging.error(f"Error procesando página {pagina}: {e}")
                    if "timeout" in str(e).lower():
                        logging.info("Intentando reiniciar el driver y continuar...")
                        self.restart_driver()
                        self.driver.get(self.base_url)
                        continue
                    break
            
            logging.info(f"\nProceso completado. Total de nuevas convocatorias agregadas: {self.total_nuevas}")
            
        except Exception as e:
            logging.error(f"Error durante la ejecución: {e}")
        finally:
            if self.driver:
                self.driver.quit()

def main():
    scraper = CorfoScraper()
    scraper.run()

if __name__ == "__main__":
    main()
