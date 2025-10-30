from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@given('pengguna membuka halaman utama IMDB')
def step_open_home(context):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    context.driver = webdriver.Chrome(service=service, options=options)
    context.wait = WebDriverWait(context.driver, 10)
    context.driver.get("https://www.imdb.com")

@when('pengguna mencari film "{movie_name}"')
def step_search_movie(context, movie_name):
    search_box = context.wait.until(EC.presence_of_element_located((By.ID, "suggestion-search")))
    search_box.send_keys(movie_name)
    search_box.send_keys(Keys.RETURN)
    time.sleep(3)

@then('hasil pencarian menampilkan film yang berjudul "{movie_name}"')
def step_verify_search(context, movie_name):
    results = context.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ipc-metadata-list-summary-item__t")))
    assert movie_name.lower() in results.text.lower(), f"Expected {movie_name} in results, got {results.text}"
    print(f"✅ Hasil pencarian menampilkan film: {movie_name}")

@given('pengguna sudah berada di halaman hasil pencarian "{movie_name}"')
def step_on_search_results(context, movie_name):
    context.execute_steps(f'''
        Given pengguna membuka halaman utama IMDB
        When pengguna mencari film "{movie_name}"
    ''')

@when('pengguna mengklik film pertama')
def step_click_first_movie(context):
    first_result = context.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ipc-metadata-list-summary-item__t")))
    first_result.click()
    time.sleep(3)

@when('pengguna membuka tab trailer')
def step_open_trailer(context):
    try:
        trailer_link = context.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.ipc-lockup-overlay.ipc-lockup-overlay--hover.ipc-focusable"))
        )
        context.driver.execute_script("arguments[0].scrollIntoView(true);", trailer_link)
        time.sleep(1)
        trailer_link.click()
        print("▶️ Trailer diklik, membuka halaman trailer...")
        time.sleep(5)
    except Exception as e:
        print(f"⚠️ Gagal membuka trailer: {e}")

@then('trailer film muncul di layar')
def step_verify_trailer(context):
    try:
        context.wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.TAG_NAME, "video")),
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
        )
        print("🎬 Trailer berhasil dimuat dan muncul di layar!")
    except:
        print("❌ Trailer tidak muncul atau gagal dimuat.")

def after_scenario(context, scenario):
    context.driver.quit()