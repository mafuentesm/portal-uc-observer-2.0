import os
import time
import platform
import subprocess
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

SO = platform.system().lower()

# Si es Windows, intentar cargar win10toast
toast = None
if SO == "windows":
    try:
        from win10toast import ToastNotifier
        toast = ToastNotifier()
    except:
        print("win10toast no está instalado. Usa: pip install -r requirements.txt")

# ---------------------------------------------------
# Cargar variables desde .env
# ---------------------------------------------------
load_dotenv()

LOGIN_URL = os.getenv("LOGIN_URL")
TARGET_URL = os.getenv("TARGET_URL")  # Aunque ya no se usa para obtener el contenido portlet
PORTLET_URL = os.getenv("PORTLET_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

if not all([LOGIN_URL, PORTLET_URL, USERNAME, PASSWORD]):
    raise ValueError("Faltan variables en el archivo .env")

CACHE_FILE = "ultima_version_portlet.txt"


# ---------------------------------------------------
# Manejo de la versión anterior guardada
# ---------------------------------------------------
def load_cached_version():
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_cached_version(text):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(text)


# ---------------------------------------------------
# Popup nativo de MacOS
# ---------------------------------------------------
def show_popup(mensaje):
    os.system(f'''
        osascript -e 'display dialog "{mensaje}" buttons {{"OK"}} with icon caution'
    ''')


# ---------------------------------------------------
# Login CAS mejorado
# ---------------------------------------------------
def login_and_get_session():
    s = requests.Session()
    # Headers realistas
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9',
    }
    s.headers.update(headers)

    # Paso 1: acceder a la página para obtener el formulario CAS
    resp = s.get(LOGIN_URL, allow_redirects=True)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    execution_input = soup.find("input", {"name": "execution"})
    if execution_input is None:
        print("[WARN] No se encontró input 'execution', podría no ser un CAS estándar.")
        execution = None
    else:
        execution = execution_input.get("value")[:20] + "..."
        print(f"[INFO] Execution token: {execution}")

    # Preparar payload para login
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "_eventId": "submit",
    }
    if execution is not None:
        payload["execution"] = execution
    payload["geolocation"] = ""

    # Hacer login
    resp2 = s.post(LOGIN_URL, data=payload, allow_redirects=True)
    resp2.raise_for_status()

    # Opcional: verificar que ya estés fuera del CAS
    # puedes mirar resp2.url o resp2.text

    return s


# ---------------------------------------------------
# Obtener el HTML del portlet usando la URL AJAX
# ---------------------------------------------------
def get_portlet_html(session):
    resp = session.get(PORTLET_URL, allow_redirects=True)
    resp.raise_for_status()
    return resp.text


# ---------------------------------------------------
# Extraer div.portlet-body desde el HTML del portlet
# ---------------------------------------------------
def extract_div_portlet_body(html):
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find("div", class_="portlet-body")
    if not div:
        print("[WARN] No se encontró <div class='portlet-body'> en el portlet.")
        return None
    return div.get_text(strip=True)


# ---------------------------------------------------
# Comparación con el contenido previo
# ---------------------------------------------------
def check_for_changes():
    session = login_and_get_session()
    portlet_html = get_portlet_html(session)
    contenido = extract_div_portlet_body(portlet_html)

    if contenido is None:
        print("[ERROR] No pude extraer el contenido que quieres monitorear.")
        return

    anterior = load_cached_version()

    if anterior is None:
        print("[INFO] Primera ejecución: guardando contenido inicial.")
        save_cached_version(contenido)
        return

    if contenido != anterior:
        print("⚠️ CAMBIO DETECTADO ⚠️")
        print("Antes:", anterior[:200], "…")
        print("Ahora:", contenido[:200], "…")
        save_cached_version(contenido)
        show_popup("¡Cambio detectado en el contenido del portlet!")
    else:
        print("[OK] Sin cambios.")


# ---------------------------------------------------
# Loop infinito cada 10 segundos
# ---------------------------------------------------
def main():
    print("Monitoreo del portlet cada 10 segundos...")
    while True:
        try:
            check_for_changes()
        except Exception as e:
            print("[ERROR] Ocurrió un error:", e)
        time.sleep(10)


if __name__ == "__main__":
    main()
