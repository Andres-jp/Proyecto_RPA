# ==========================================================================
#  SCRIPT RPA: Consulta de Climatología para la Pesca
# ==========================================================================
#  Extrae datos de mareas, oleaje y condiciones meteorológicas
#  desde tablademareas.com usando web scraping con BeautifulSoup.


import requests
from bs4 import BeautifulSoup
import re
import sys
import io

# Forzar UTF-8 en consola Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ==========================================================================
#  PEDIR UBICACIÓN AL USUARIO
# ==========================================================================

UBICACIONES = {
    'P': 'punta-de-teno',
    'I': 'icod-de-los-vinos',
    'C': 'puerto-de-la-cruz',
    'E': 'el-sauzal',
}

print("=========================================")
print("       UBICACION DE LA PESCA")
print("=========================================")
print("  [P] Punta de Teno")
print("  [I] Icod de los Vinos")
print("  [C] Puerto de la Cruz")
print("  [E] El Sauzal")
print("-----------------------------------------")

opcion = input(" => Selecciona una opcion: ").strip().upper()

if opcion not in UBICACIONES:
    print("Opcion no valida.")
    exit()

ubicacion = UBICACIONES[opcion]

# ==========================================================================
#  DESCARGAR LA PÁGINA WEB
# ==========================================================================
# Construimos la URL completa 
url = 'https://tablademareas.com/es/islas-canarias/' + ubicacion

# Simulamos con  'User-Agent' que somos Chrome para evitar que el servidor nos rechace la petición.
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
}

print(f"\nDescargando datos de: {url} ...")

# Descargar el HTML de la página web.
respuesta = requests.get(url, headers=headers)

# Comprobamos que la descarga fue exitosa.
if respuesta.status_code != 200:
    print(f"Error al descargar la pagina: {respuesta.status_code}")
    exit()

# onvertimos el HTML en un objeto para poder extraer los datos.
soup = BeautifulSoup(respuesta.text, 'html.parser')

# ==========================================================================
# EXTRAER DATOS DE MAREAS 
# ==========================================================================

# Buscamos las mareas, que están dentro de elementos <div> con la clase CSS 'fondo_grafico_pleamares_bajamares'. (índice 2) contiene el día actual.

# Buscamos TODOS los divs con esa clase CSS
divs_grafico = soup.find_all('div', class_='fondo_grafico_pleamares_bajamares')

# Lista guardar datos de mareas
mareas = []

# Verificamos que existan al menos 3 divs 
if len(divs_grafico) >= 3:
    # Obtenemos el texto del tercer div
    texto_alturas = divs_grafico[2].get_text(strip=True)
    pares = re.findall(r'(\d{1,2}:\d{2})h\s*(-?\d+,\d)', texto_alturas)

    # Procesamos cada par (hora, altura) encontrado
    for hora, altura in pares:
        alt = float(altura.replace(',', '.'))

        # Si la altura es positiva es PLEAMAR
        # si es negativa es BAJAMAR 
        tipo = 'PLEAMAR' if alt > 0 else 'BAJAMAR'

        # Guardamos los datos como un diccionario en la lista
        mareas.append({'tipo': tipo, 'hora': hora, 'altura': alt})


# EXTRAER COEFICIENTES DE MAREAS
# Estos datos están dentro de código JavaScript
# Inicializamos los valores con '-'
coef_inicio = coef_medio = coef_fin = '-'

# Recorremos todos los bloques <script> de la página
for script in soup.find_all('script'):
    texto = script.string or ''  # Obtenemos el contenido del script

    # Solo procesamos el script que contiene 'gm.coef_inicio'
    if 'gm.coef_inicio' in texto:
        # Buscamos cada coeficiente con expresiones regulares guardamos datos
        m = re.search(r'gm\.coef_inicio=(\d+)', texto)
        if m: coef_inicio = m.group(1)  

        m = re.search(r'gm\.coef_medio=(\d+)', texto)
        if m: coef_medio = m.group(1)

        m = re.search(r'gm\.coef_fin=(\d+)', texto)
        if m: coef_fin = m.group(1)


# EXTRAER AMANECER Y PUESTA DE SOL
# La hora del amanecer y puesta de sol están en un párrafo descriptivo del HTML con la clase 'txt_descripcion'

 # Inicializamos los valores con '-'
amanecer = puesta_sol = '-'  

# Buscamos todos los párrafos <p> con clase 'txt_descripcion'
for p in soup.find_all('p', class_='txt_descripcion'):
    texto = p.get_text(strip=True)

    # Patrón para amanecer:
    m = re.search(r'a\s*las\s*(\d{1,2}:\d{2}:\d{2})\s*h\s*y\s*la\s*puesta', texto)
    if m: amanecer = m.group(1)

    # Patrón para puesta de sol:
    m = re.search(r'puesta de sol.*?(\d{1,2}:\d{2}:\d{2})\s*h', texto)
    if m: puesta_sol = m.group(1)

# ==========================================================================
# MOSTRAR RESULTADOS EN TERMINAL
# ==========================================================================
from datetime import datetime

# Eliminamos los guiones de la ubicacion y lo convertimos a mayusculas
nombre = ubicacion.replace('-', ' ').upper()

# Imprimimos el informe formateado con todos los datos extraídos
print("\n" + "=" * 55)
print(f"  INFORME DE PESCA - {nombre}")
print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}") #Fecha y hora actual usando libreria datetime
print("=" * 55)

print("\n--- PLEAMARES Y BAJAMARES ---")
for m in mareas:

    print(f"  {m['tipo']:>8}:  {m['hora']} h  ->  {m['altura']:+.1f} m")

print(f"\n  Coeficiente:    {coef_medio} (inicio: {coef_inicio}, fin: {coef_fin})")
print(f"  Amanecer:       {amanecer} h")
print(f"  Puesta sol:     {puesta_sol} h")

print("\n" + "=" * 55)

# ==========================================================================
# ABRIR WINDY.APP EN EL NAVEGADOR CON SELENIUM
# ==========================================================================
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By 
import pyautogui 
import cv2 
import time 

# Inicializar el controlador de Selenium para Chrome 
driver = webdriver.Chrome() 

#Navegar a la página de Windy app para ver infromacion de viento y precipitaciones de forma visual  
driver.get("https://windy.app/")

#Ahustamos ancho y alto de navegador par poder buscar por imagen en la captura de pantalla 
driver.set_window_size(1920, 1080)

# Esperar unos segundos para que la página se cargue completamente 
time.sleep(2)

pyautogui.typewrite(nombre, interval=0.2) 
pyautogui.press('enter')
time.sleep(0.1)
pyautogui.press('enter')

# Esperar unos segundos para que la página se cargue completamente 
time.sleep(2)

# Cargar la imagen a buscar usando OpenCV para cambiar formato a 1h de la pagina web 
imagen_a_buscar = cv2.imread("1h.png") 

# Guardar la captura de pantalla donde buscaremos como un archivo de imagen temporal 
captura = pyautogui.screenshot() 
captura_path = "captura_temporal.png" 
captura.save(captura_path) 

# Buscar la imagen en la captura de pantalla 
resultado = cv2.matchTemplate(cv2.cvtColor(cv2.imread(captura_path), cv2.COLOR_BGR2GRAY), cv2.cvtColor(imagen_a_buscar, cv2.COLOR_BGR2GRAY), cv2.TM_CCOEFF_NORMED) 
 
# Obtener las coordenadas de la imagen si se encuentra 
_, _, _, max_loc = cv2.minMaxLoc(resultado) 
x, y = max_loc 

# Hacer clic en el centro de la imagen si se encuentra 
if resultado.max() > 0.9: 
    centro_x = x + imagen_a_buscar.shape[1] // 2 
    centro_y = y + imagen_a_buscar.shape[0] // 2 
    pyautogui.moveTo(centro_x, centro_y, 2, pyautogui.easeOutQuad) 
    pyautogui.click(centro_x, centro_y,clicks=2,interval=0.2) 
    time.sleep(2) 
    # Tomar la captura de pantalla 
    screenshot = pyautogui.screenshot()
    pyautogui.alert("Imagen encontrada y clic realizando en el centro.") 
else: 
    time.sleep(2) 
    pyautogui.alert("Imagen no encontrada.") 

    # Guardar la captura de pantalla
if pyautogui.confirm('¿Guardar la captura de pantalla windy?') == 'OK':
    captura_path_save = "1h_windy.png" 
    screenshot.save(captura_path_save) 
else:
    print("Captura no guardada")

# Eliminar el archivo de imagen temporal 
import os 
os.remove(captura_path) 

# Cerrar el navegador 
driver.quit() 

