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
        print("🔍 Mencari trailer...")
        
        # Scroll ke bagian videos
        context.driver.execute_script("window.scrollTo(0, 600);")
        time.sleep(2)
        
        # Method 1: Cari link "See all videos" terlebih dahulu
        try:
            see_all_videos = context.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'See all') and contains(., 'video')]"))
            )
            context.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", see_all_videos)
            time.sleep(1)
            see_all_videos.click()
            print("✅ Berhasil membuka halaman semua video")
            time.sleep(3)
            
            # Di halaman videos, cari dan klik trailer pertama
            _click_trailer_in_videos_page(context)
            
        except:
            # Method 2: Jika tidak ada "See all", coba klik video langsung dari halaman utama
            print("⏩ Coba method langsung dari halaman utama...")
            _click_video_from_main_page(context)
            
    except Exception as e:
        print(f"❌ Gagal membuka trailer: {e}")
        # Screenshot untuk debug
        context.driver.save_screenshot("error_trailer.png")
        raise

def _click_trailer_in_videos_page(context):
    """Klik trailer di halaman videos"""
    try:
        # Cari trailer berdasarkan text
        trailer_elements = context.driver.find_elements(By.XPATH, "//*[contains(text(), 'Trailer')]")
        
        if trailer_elements:
            # Scroll ke trailer dan klik
            context.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trailer_elements[0])
            time.sleep(1)
            trailer_elements[0].click()
            print("🎬 Trailer diklik di halaman videos")
        else:
            # Klik video pertama jika tidak ada trailer spesifik
            first_video = context.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/video'], [data-testid*='video']"))
            )
            first_video.click()
            print("🎬 Video pertama diklik")
            
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ Gagal klik trailer di videos page: {e}")
        raise

def _click_video_from_main_page(context):
    """Klik video langsung dari halaman film utama"""
    try:
        # Cari section videos
        videos_section = context.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'VIDEOS') or contains(text(), 'Videos')]"))
        )
        context.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", videos_section)
        time.sleep(2)
        
        # Cari elemen video di dalam section
        video_elements = videos_section.find_elements(By.XPATH, "./following-sibling::div//a[contains(@class, 'ipc-lockup-overlay')] | //section[.//*[contains(text(), 'VIDEOS')]]//a")
        
        if video_elements:
            video_elements[0].click()
            print("🎬 Video diklik dari halaman utama")
            time.sleep(5)
        else:
            raise Exception("Tidak ada elemen video yang ditemukan")
            
    except Exception as e:
        print(f"❌ Gagal klik video dari main page: {e}")
        raise

@then('trailer film muncul di layar')
def step_verify_trailer(context):
    try:
        # Tunggu video player muncul dengan berbagai kemungkinan selector
        video_player = context.wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.TAG_NAME, "video")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='video-player']")),
                EC.presence_of_element_located((By.CLASS_NAME, "video-player")),
                EC.presence_of_element_located((By.ID, "video-player")),
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
        )
        
        print("✅ Trailer berhasil dimuat dan muncul di layar!")
        
        # Coba check jika video bisa diputar
        try:
            if video_player.tag_name == "video":
                is_playing = context.driver.execute_script("return !arguments[0].paused;", video_player)
                if is_playing:
                    print("▶️ Video sedang diputar")
                else:
                    print("⏸️ Video dimuat tapi belum diputar")
        except:
            print("📺 Video player terdeteksi")
            
    except Exception as e:
        print(f"❌ Trailer tidak muncul: {e}")
        # Screenshot untuk debug
        context.driver.save_screenshot("trailer_error.png")
        raise

def after_scenario(context, scenario):
    if hasattr(context, 'driver'):
        context.driver.quit()