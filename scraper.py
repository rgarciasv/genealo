"""
FamilySearch Parish Book Image Scraper
======================================
Descarga imágenes de libros parroquiales desde FamilySearch
usando Selenium con el perfil de Chrome existente (sesión activa).

Uso:
  1. CIERRA todas las ventanas de Chrome
  2. python scraper.py
  3. python scraper.py --start 50 --end 100   (rango específico)
  4. python scraper.py --resume                 (continuar donde se quedó)
"""

import argparse
import atexit
import os
import re
import shutil
import sys
import tempfile
import time
import random
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException,
)
from webdriver_manager.chrome import ChromeDriverManager

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

# URL base del grupo de imágenes (sin parámetro i=)
BASE_URL = (
    "https://www.familysearch.org/ark:/61903/3:1:S3HT-DZHQ-2JY"
    "?view=explore&groupId=M9F5-JRY&lang=es"
)

# Ruta del perfil de Chrome del usuario
CHROME_USER_DATA = Path(r"C:\Users\rgarc\AppData\Local\Google\Chrome\User Data")
CHROME_PROFILE = "Default"

# Directorio de salida para las imágenes descargadas
OUTPUT_DIR = Path(r"c:\TRABAJOS\personal\genealo\imagenes")

# Número total de imágenes en el grupo
TOTAL_IMAGES = 276

# Delays para simular comportamiento humano (segundos)
MIN_DELAY = 3
MAX_DELAY = 8

# Timeout máximo de espera para carga de elementos (segundos)
PAGE_LOAD_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 60

# ─── LOGGING ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            Path(r"c:\TRABAJOS\personal\genealo\scraper.log"),
            encoding="utf-8",
        ),
    ],
)
log = logging.getLogger(__name__)

# ─── FUNCIONES ────────────────────────────────────────────────────────────────


def get_downloaded_count() -> int:
    """Cuenta cuántas imágenes ya se descargaron (para reanudar)."""
    if not OUTPUT_DIR.exists():
        return 0
    image_extensions = (".jpg", ".jpeg", ".png", ".tiff", ".tif")
    count = sum(
        1 for f in OUTPUT_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
        and not f.name.endswith(".crdownload")
    )
    return count


def get_existing_files() -> set[str]:
    """Devuelve los nombres de archivos ya existentes en la carpeta de salida."""
    if not OUTPUT_DIR.exists():
        return set()
    return {f.name for f in OUTPUT_DIR.iterdir() if f.is_file()}


def _copy_chrome_profile() -> Path:
    """
    Copia los archivos esenciales del perfil de Chrome a un directorio temporal.
    Esto permite que el scraper funcione SIN cerrar Chrome.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="fs_scraper_"))
    log.info(f"Copiando perfil de Chrome a {temp_dir}...")

    profile_src = CHROME_USER_DATA / CHROME_PROFILE
    profile_dst = temp_dir / CHROME_PROFILE
    profile_dst.mkdir(parents=True, exist_ok=True)

    # Copiar archivos de nivel superior necesarios (Local State contiene claves de encriptación)
    local_state = CHROME_USER_DATA / "Local State"
    if local_state.exists():
        shutil.copy2(local_state, temp_dir / "Local State")

    # Archivos esenciales del perfil para mantener la sesión
    essential_files = [
        "Cookies",
        "Cookies-journal",
        "Login Data",
        "Login Data-journal",
        "Web Data",
        "Web Data-journal",
        "Preferences",
        "Secure Preferences",
        "Network",  # es un directorio
    ]

    for name in essential_files:
        src = profile_src / name
        dst = profile_dst / name
        try:
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            elif src.exists():
                shutil.copy2(src, dst)
        except (PermissionError, OSError) as e:
            log.debug(f"No se pudo copiar {name}: {e}")

    # Registrar limpieza al salir
    def cleanup():
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            log.debug(f"Perfil temporal eliminado: {temp_dir}")
        except Exception:
            pass

    atexit.register(cleanup)

    log.info("Perfil de Chrome copiado correctamente.")
    return temp_dir


def setup_driver() -> webdriver.Chrome:
    """
    Configura ChromeDriver copiando el perfil de Chrome del usuario.
    NO requiere cerrar Chrome — copia la sesión a un directorio temporal.
    """
    log.info("Configurando ChromeDriver...")

    # Copiar perfil para evitar conflicto con Chrome abierto
    temp_profile_dir = _copy_chrome_profile()

    options = Options()
    options.add_argument(f"--user-data-dir={temp_profile_dir}")
    options.add_argument(f"--profile-directory={CHROME_PROFILE}")

    # Directorio de descarga
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prefs = {
        "download.default_directory": str(OUTPUT_DIR),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    # Evitar detección como bot
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Ventana grande para que el visor cargue bien
    options.add_argument("--window-size=1920,1080")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except WebDriverException as e:
        log.error(f"Error al iniciar ChromeDriver: {e}")
        sys.exit(1)

    # Ocultar webdriver flag
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )

    log.info("ChromeDriver listo.")
    return driver


def build_image_url(image_index: int) -> str:
    """
    Construye la URL para una imagen específica (0-based index).
    FamilySearch usa el parámetro i= para navegar entre imágenes.
    """
    return (
        f"https://www.familysearch.org/ark:/61903/3:1:S3HT-DZHQ-2JY"
        f"?i={image_index}&groupId=M9F5-JRY&view=explore&lang=es"
    )


def wait_for_viewer_ready(driver: webdriver.Chrome):
    """Espera a que el visor de imágenes esté completamente cargado."""
    try:
        # Esperar a que el contenedor del visor exista
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='image-viewer'], [class*='ImageViewer'], canvas, .viewer-container, [data-testid*='viewer']"))
        )
        # Dar tiempo extra para que la imagen se renderice
        time.sleep(2)
        log.debug("Visor de imágenes listo.")
    except TimeoutException:
        log.warning("Timeout esperando al visor. Intentando continuar...")


def try_download_via_button(driver: webdriver.Chrome) -> bool:
    """
    Intenta descargar la imagen usando el botón de descarga nativo de FamilySearch.
    Busca varios selectores posibles para el botón de descarga.
    """
    download_selectors = [
        # Botón de descarga por aria-label
        "[aria-label*='ownload'], [aria-label*='escargar']",
        # Botón de descarga por title
        "[title*='ownload'], [title*='escargar']",
        # Icono de descarga SVG dentro de botón
        "button svg[data-icon='download'], button svg[data-icon='arrow-down']",
        # Botón con icono de descarga por clase
        "button[class*='download'], a[class*='download']",
        # Data-testid
        "[data-testid*='download']",
        # El botón ↓ en la barra de herramientas (ícono flecha abajo)
        ".toolbar button:has(svg), .controls button:has(svg)",
    ]

    for selector in download_selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            for btn in buttons:
                btn_text = btn.get_attribute("aria-label") or btn.get_attribute("title") or ""
                if any(kw in btn_text.lower() for kw in ["download", "descargar", "save", "guardar"]):
                    btn.click()
                    log.debug(f"Click en botón de descarga: {btn_text}")
                    return True
            # Si encontramos botones pero ninguno tiene label de descarga,
            # intentamos el primero
            if buttons:
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        log.debug("Click en botón candidato a descarga.")
                        return True
        except (NoSuchElementException, StaleElementReferenceException):
            continue

    return False


def try_download_via_context_menu(driver: webdriver.Chrome) -> bool:
    """
    Alternativa: descarga la imagen interceptando la URL del tile/imagen 
    desde el canvas o img del visor usando JavaScript.
    """
    # Intentar obtener la URL de la imagen desde el DOM
    scripts = [
        # Buscar img dentro del visor
        """
        const imgs = document.querySelectorAll('img[src*="familysearch"], img[src*="records"], img[src*="storage"]');
        for (const img of imgs) {
            if (img.naturalWidth > 100) return img.src;
        }
        return null;
        """,
        # Buscar en canvas (obtener data URL)
        """
        const canvas = document.querySelector('canvas');
        if (canvas && canvas.width > 100) {
            return canvas.toDataURL('image/jpeg', 0.95);
        }
        return null;
        """,
    ]

    for script in scripts:
        try:
            result = driver.execute_script(script)
            if result:
                log.debug(f"URL de imagen obtenida: {result[:80]}...")
                return result
        except Exception:
            continue

    return None


def download_via_url(driver: webdriver.Chrome, url: str, filepath: Path) -> bool:
    """Descarga una imagen desde una URL usando JavaScript fetch con las cookies de la sesión."""
    if url.startswith("data:"):
        # Es un data URL del canvas, guardarlo directamente
        import base64
        try:
            # Formato: data:image/jpeg;base64,/9j/4AAQ...
            header, data = url.split(",", 1)
            img_data = base64.b64decode(data)
            filepath.write_bytes(img_data)
            return True
        except Exception as e:
            log.error(f"Error decodificando data URL: {e}")
            return False

    # URL normal: usar fetch con credenciales
    script = f"""
    const response = await fetch("{url}", {{ credentials: 'include' }});
    const blob = await response.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = "{filepath.name}";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
    return true;
    """
    try:
        driver.execute_script(f"return (async () => {{ {script} }})()")
        time.sleep(3)
        return True
    except Exception as e:
        log.error(f"Error en fetch de imagen: {e}")
        return False



def get_new_downloaded_file(existing_before: set[str], timeout: int = DOWNLOAD_TIMEOUT) -> Path | None:
    """Espera a que aparezca un nuevo archivo descargado (no temporal)."""
    start = time.time()
    while time.time() - start < timeout:
        if OUTPUT_DIR.exists():
            for f in OUTPUT_DIR.iterdir():
                if (
                    f.is_file()
                    and f.name not in existing_before
                    and not f.suffix == ".crdownload"
                    and not f.suffix == ".tmp"
                    and f.stat().st_size > 0
                ):
                    return f
        time.sleep(0.5)
    return None


def navigate_to_image_via_input(driver: webdriver.Chrome, image_num: int) -> bool:
    """
    Navega a una imagen específica usando el campo de input de número de imagen.
    En FamilySearch, hay un input que dice "Imagen X de 276".
    """
    try:
        # Buscar el input de número de imagen
        input_selectors = [
            "input[type='number']",
            "input[aria-label*='magen'], input[aria-label*='mage']",
            "input[class*='page'], input[class*='image']",
            "input[data-testid*='page'], input[data-testid*='image']",
        ]

        img_input = None
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed():
                        img_input = elem
                        break
                if img_input:
                    break
            except NoSuchElementException:
                continue

        if img_input:
            img_input.clear()
            img_input.send_keys(str(image_num))
            img_input.send_keys(Keys.ENTER)
            time.sleep(2)
            log.debug(f"Navegado a imagen {image_num} via input.")
            return True

    except Exception as e:
        log.debug(f"No se pudo usar input de navegación: {e}")

    return False


def navigate_via_url(driver: webdriver.Chrome, image_num: int):
    """Navega directamente a una imagen cambiando la URL (i= parameter, 0-based)."""
    url = build_image_url(image_num - 1)  # FamilySearch usa 0-based index
    driver.get(url)
    wait_for_viewer_ready(driver)


def download_image(driver: webdriver.Chrome, image_num: int) -> bool:
    """
    Descarga una imagen individual preservando el nombre original.
    Intenta múltiples estrategias:
    1. Botón de descarga nativo
    2. Extracción de URL + fetch
    3. Screenshot del canvas como último recurso
    """
    # Snapshot de archivos existentes antes de descargar
    existing_before = get_existing_files()

    # Estrategia 1: Botón de descarga nativo
    log.info(f"Imagen {image_num}/{TOTAL_IMAGES}: intentando botón de descarga...")

    if try_download_via_button(driver):
        time.sleep(2)  # esperar a que empiece la descarga

        downloaded = get_new_downloaded_file(existing_before, timeout=DOWNLOAD_TIMEOUT)
        if downloaded:
            log.info(f"  ✓ Descargada: {downloaded.name} ({downloaded.stat().st_size / 1024:.0f} KB)")
            return True
        else:
            log.warning("  Botón clickeado pero no se detectó descarga.")

    # Estrategia 2: Extraer URL de imagen y descargar
    log.info(f"Imagen {image_num}/{TOTAL_IMAGES}: intentando extracción de URL...")
    img_url = try_download_via_context_menu(driver)
    if img_url:
        fallback_filepath = OUTPUT_DIR / f"img_{image_num:03d}.jpg"
        if download_via_url(driver, img_url, fallback_filepath):
            downloaded = get_new_downloaded_file(existing_before, timeout=15)
            if downloaded:
                log.info(f"  ✓ Descargada via URL: {downloaded.name} ({downloaded.stat().st_size / 1024:.0f} KB)")
                return True
            if fallback_filepath.exists() and fallback_filepath.stat().st_size > 0:
                log.info(f"  ✓ Descargada via URL: {fallback_filepath.name} ({fallback_filepath.stat().st_size / 1024:.0f} KB)")
                return True

    # Estrategia 3: Screenshot del canvas/viewer como último recurso
    log.info(f"Imagen {image_num}/{TOTAL_IMAGES}: usando screenshot como fallback...")
    fallback_filepath = OUTPUT_DIR / f"screenshot_{image_num:03d}.png"
    try:
        # Buscar el canvas o contenedor de imagen principal
        viewer_selectors = [
            "canvas",
            "[class*='image-viewer'] img",
            "[class*='ImageViewer']",
            ".viewer-container",
            "[class*='viewer'] canvas",
        ]

        for selector in viewer_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed() and element.size["width"] > 100:
                    element.screenshot(str(fallback_filepath))
                    if fallback_filepath.exists() and fallback_filepath.stat().st_size > 1000:
                        log.info(f"  ✓ Screenshot guardado: {fallback_filepath.name} ({fallback_filepath.stat().st_size / 1024:.0f} KB)")
                        return True
            except (NoSuchElementException, StaleElementReferenceException):
                continue

        # Último recurso: screenshot de toda la ventana
        driver.save_screenshot(str(fallback_filepath))
        log.warning(f"  ⚠ Screenshot de página completa: {fallback_filepath.name}")
        return True

    except Exception as e:
        log.error(f"  ✗ Todas las estrategias fallaron: {e}")
        return False


def human_delay():
    """Delay aleatorio para simular comportamiento humano."""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    log.debug(f"Esperando {delay:.1f}s...")
    time.sleep(delay)


def run(start: int, end: int, resume: bool = False):
    """Loop principal de descarga."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Determinar qué imágenes descargar
    already_count = get_downloaded_count()
    total_requested = end - start + 1

    if resume and already_count > 0:
        # Saltar las primeras N imágenes que ya se descargaron
        adjusted_start = start + already_count
        if adjusted_start > end:
            log.info(f"¡Todas las imágenes ya están descargadas! ({already_count} archivos)")
            return
        images_to_download = list(range(adjusted_start, end + 1))
        log.info(f"Reanudando: {already_count} ya descargadas, {len(images_to_download)} pendientes.")
    else:
        images_to_download = list(range(start, end + 1))

    if not images_to_download:
        log.info("¡No hay imágenes pendientes!")
        return

    log.info(f"Descargando {len(images_to_download)} imágenes ({images_to_download[0]}-{images_to_download[-1]})...")

    # Iniciar navegador
    driver = setup_driver()

    failed = []
    try:
        for idx, image_num in enumerate(images_to_download):
            log.info(f"── Progreso: {idx + 1}/{len(images_to_download)} ── Imagen {image_num} ──")

            # Navegar a la imagen
            navigate_via_url(driver, image_num)

            # Intentar descargar
            success = download_image(driver, image_num)

            if not success:
                failed.append(image_num)
                log.error(f"  ✗ FALLÓ imagen {image_num}")

            # Delay humano (excepto en la última)
            if idx < len(images_to_download) - 1:
                human_delay()

    except KeyboardInterrupt:
        log.info("\n⏸  Interrumpido por el usuario. Usa --resume para continuar.")
    except Exception as e:
        log.error(f"Error inesperado: {e}", exc_info=True)
    finally:
        driver.quit()
        log.info("Navegador cerrado.")

    # Resumen
    final_count = get_downloaded_count()
    log.info(f"\n{'='*50}")
    log.info(f"RESUMEN:")
    log.info(f"  Total archivos en carpeta: {final_count}")
    log.info(f"  Fallidas:    {len(failed)}")
    if failed:
        log.info(f"  IDs fallidos: {failed}")
        log.info(f"  Re-intenta con: python scraper.py --resume")
    log.info(f"  Directorio:  {OUTPUT_DIR}")
    log.info(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(
        description="Descarga imágenes de libros parroquiales de FamilySearch"
    )
    parser.add_argument(
        "--start", type=int, default=1,
        help="Número de imagen inicial (1-based, default: 1)"
    )
    parser.add_argument(
        "--end", type=int, default=TOTAL_IMAGES,
        help=f"Número de imagen final (default: {TOTAL_IMAGES})"
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Reanudar descarga saltando imágenes ya existentes"
    )
    args = parser.parse_args()

    if args.start < 1 or args.end > TOTAL_IMAGES or args.start > args.end:
        log.error(f"Rango inválido: {args.start}-{args.end} (válido: 1-{TOTAL_IMAGES})")
        sys.exit(1)

    log.info("╔══════════════════════════════════════════════════════════╗")
    log.info("║  FamilySearch - Scraper de Libros Parroquiales          ║")
    log.info("║  San Juan Bautista · Bautismos 1752-1800               ║")
    log.info("╚══════════════════════════════════════════════════════════╝")
    log.info(f"Rango: imágenes {args.start} a {args.end}")
    log.info(f"Salida: {OUTPUT_DIR}")

    run(args.start, args.end, args.resume)


if __name__ == "__main__":
    main()
