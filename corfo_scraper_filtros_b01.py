import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Constantes
URL_BASE = "https://corfo.cl"
URL_CONVOCATORIAS = "https://corfo.cl/sites/cpp/programasyconvocatorias"
TIEMPO_ESPERA = 20

# Mapeo de filtros
FILTROS = {
    'perfil': {
        'menu_id': 'collapse5',
        'menu_button': '//a[@data-target="#collapse5"]',
        'filtros': {
            'PERSONA': 'asPerfilQuienSoy-persona-checkbox',
            'EMPRESA': 'asPerfilQuienSoy-empresa-checkbox',
            'ORGANIZACIÓN': 'asPerfilQuienSoy-organizacion-checkbox',
            'INTERMEDIARIO': 'asPerfilQuienSoy-intermediario-checkbox',
            'INSTITUCION': 'asPerfilQuienSoy-institucion-checkbox',
            'EXTRANJERO': 'asPerfilQuienSoy-extranjero-checkbox'
        }
    },
    'etapa': {
        'menu_id': 'collapse4',
        'menu_button': '//a[@data-target="#collapse4"]',
        'filtros': {
            'EMPRENDER': 'asEtapaQueBusco-emprender-checkbox',
            'IDEA': 'asEtapaQueBusco-ideaNegocio-checkbox',
            'VENTAS': 'asEtapaQueBusco-aumentarVentas-checkbox',
            'ESCALAR': 'asEtapaQueBusco-escalar-checkbox',
            'INNOVAR': 'asEtapaQueBusco-innovar-checkbox',
            'I+D': 'asEtapaQueBusco-desarrollandoID-checkbox',
            'SERVICIOS': 'asEtapaQueBusco-entregarServicios-checkbox',
            'ECOSISTEMA': 'asEtapaQueBusco-fortalecerEcosistema-checkbox'
        }
    },
    'genero': {
        'menu_id': 'collapse3',
        'menu_button': '//a[@data-target="#collapse3"]',
        'filtros': {
            'GENERO': 'asQueNecesito-incentivoMujeres-checkbox'
        }
    }
}

class CorfoScraper:
    def __init__(self):
        self.driver = None
        self.df = None
        
    def inicializar_driver(self):
        """Inicializa el driver de Chrome en modo headless"""
        try:
            # Configurar opciones de Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Modo headless
            chrome_options.add_argument("--disable-gpu")  # Deshabilitar GPU
            chrome_options.add_argument("--no-sandbox")  # Necesario para algunos sistemas
            chrome_options.add_argument("--disable-dev-shm-usage")  # Necesario para algunos sistemas
            chrome_options.add_argument("--window-size=1920,1080")  # Tamaño de ventana fijo
            
            # Inicializar el driver con las opciones
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            return True
        except Exception as e:
            print(f"Error al inicializar driver: {e}")
            return False

    def preparar_dataframe(self):
        """Prepara el DataFrame inicial copiando el CSV de entrada y agregando columnas nuevas"""
        try:
            # Leer CSV original
            self.df = pd.read_csv('corfo_convocatorias.csv')
            
            # Crear nuevas columnas con valor 0
            nuevas_columnas = [
                'PERSONA', 'EMPRESA', 'ORGANIZACIÓN', 'INTERMEDIARIO', 'INSTITUCION', 
                'EXTRANJERO', 'EMPRENDER', 'IDEA', 'VENTAS', 'ESCALAR', 'INNOVAR', 
                'I+D', 'SERVICIOS', 'ECOSISTEMA', 'GENERO'
            ]
            
            for columna in nuevas_columnas:
                self.df[columna] = 0
                
            # Guardar DataFrame inicial
            self.df.to_csv('corfo_convocatorias_enriched.csv', index=False)
            return True
        except Exception as e:
            print(f"Error al preparar DataFrame: {e}")
            return False

    def navegar_a_convocatorias(self):
        """Navega a la página de convocatorias"""
        try:
            self.driver.get(URL_CONVOCATORIAS)
            return True
        except Exception as e:
            print(f"Error al navegar: {e}")
            return False

    def limpiar_filtros(self):
        """Limpia todos los filtros activos"""
        try:
            boton_limpiar = WebDriverWait(self.driver, TIEMPO_ESPERA).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.primary2.cpp-button-search[onclick*='removeAllFiltros']"))
            )
            self.driver.execute_script("arguments[0].click();", boton_limpiar)
            return True
        except Exception as e:
            print(f"Error al limpiar filtros: {e}")
            return False

    def abrir_menu(self, menu_xpath):
        """Abre un menú colapsable"""
        try:
            menu = WebDriverWait(self.driver, TIEMPO_ESPERA).until(
                EC.presence_of_element_located((By.XPATH, menu_xpath))
            )
            self.driver.execute_script("arguments[0].click();", menu)
            return True
        except Exception as e:
            print(f"Error al abrir menú: {e}")
            return False

    def aplicar_filtro(self, filtro_id):
        """Aplica un filtro específico y hace clic en 'Aplicar filtros'"""
        try:
            # Seleccionar el checkbox
            checkbox = WebDriverWait(self.driver, TIEMPO_ESPERA).until(
                EC.presence_of_element_located((By.ID, filtro_id))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
            self.driver.execute_script("arguments[0].click();", checkbox)

            # Hacer clic en "Aplicar filtros"
            boton_aplicar = WebDriverWait(self.driver, TIEMPO_ESPERA).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.primary2.cpp-button-search[onclick*='funcSearch']"))
            )
            self.driver.execute_script("arguments[0].click();", boton_aplicar)
            
            # Esperar a que se actualice el listado
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Error al aplicar filtro: {e}")
            return False

    def procesar_pagina(self, columna_filtro):
        """Procesa una página de resultados y actualiza el DataFrame"""
        try:
            # Esperar a que se cargue el listado
            WebDriverWait(self.driver, TIEMPO_ESPERA).until(
                EC.presence_of_element_located((By.ID, "listSearch"))
            )
            time.sleep(2)  # Espera adicional para asegurar carga completa del listado

            # Obtener todos los enlaces "Más Información"
            enlaces = self.driver.find_elements(By.CSS_SELECTOR, "div.foot-caja_result a")
            
            for enlace in enlaces:
                url_relativa = enlace.get_attribute('href')
                if url_relativa:
                    url_completa = URL_BASE + url_relativa if not url_relativa.startswith('http') else url_relativa
                    
                    # Buscar coincidencia en el DataFrame
                    mascara = self.df['URL'] == url_completa
                    if mascara.any():
                        self.df.loc[mascara, columna_filtro] = 1
                        
            # Guardar cambios
            self.df.to_csv('corfo_convocatorias_enriched.csv', index=False)
            return True
        except Exception as e:
            print(f"Error al procesar página: {e}")
            return False

    def hay_siguiente_pagina(self):
        """Verifica si hay una página siguiente y navega a ella"""
        try:
            siguiente = self.driver.find_element(By.CSS_SELECTOR, "a.page-link[href*='getRedirectNext']")
            self.driver.execute_script("arguments[0].click();", siguiente)
            time.sleep(3)  # Espera necesaria para la carga del nuevo listado
            return True
        except NoSuchElementException:
            return False
        except Exception as e:
            print(f"Error al verificar página siguiente: {e}")
            return False

    def procesar_grupo_filtros(self, grupo_config):
        """Procesa un grupo completo de filtros"""
        # Abrir menú del grupo
        if not self.abrir_menu(grupo_config['menu_button']):
            return False

        # Procesar cada filtro del grupo
        for columna, filtro_id in grupo_config['filtros'].items():
            print(f"\nProcesando filtro: {columna}")
            
            # Limpiar filtros anteriores
            if not self.limpiar_filtros():
                continue

            # Aplicar el filtro actual
            if not self.aplicar_filtro(filtro_id):
                continue

            # Procesar todas las páginas para este filtro
            while True:
                if not self.procesar_pagina(columna):
                    break
                    
                if not self.hay_siguiente_pagina():
                    break

            time.sleep(2)

        return True

    def ejecutar_scraping(self):
        """Ejecuta el proceso completo de scraping"""
        try:
            # Inicializar
            if not self.inicializar_driver():
                return False

            # Preparar DataFrame
            if not self.preparar_dataframe():
                return False

            # Navegar a la página
            if not self.navegar_a_convocatorias():
                return False

            # Procesar cada grupo de filtros
            for grupo_nombre, grupo_config in FILTROS.items():
                print(f"\nProcesando grupo de filtros: {grupo_nombre}")
                if not self.procesar_grupo_filtros(grupo_config):
                    print(f"Error al procesar grupo {grupo_nombre}")

            print("\nProceso de scraping completado")
            return True

        except Exception as e:
            print(f"Error en el proceso de scraping: {e}")
            return False

        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    scraper = CorfoScraper()
    scraper.ejecutar_scraping()
