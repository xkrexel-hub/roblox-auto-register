import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import aiohttp
import os
import json
from datetime import datetime
import random
import string
import time

DISCORD_WEBHOOK_URL = None
RATE_LIMIT_WAIT_TIMES = [3 * 60, 8 * 60, 20 * 60]

def generate_random_username():
    adjectives = ["cool", "super", "mega", "ultra", "pro", "epic", "dark", "fire", "ice", "storm", 
                  "shadow", "ninja", "dragon", "phoenix", "thunder", "blade", "ghost", "cyber",
                  "neo", "atomic", "cosmic", "solar", "lunar", "turbo", "hyper", "zen"]
    nouns = ["gamer", "player", "master", "king", "lord", "warrior", "hunter", "killer", "sniper", 
             "boss", "demon", "angel", "tiger", "wolf", "eagle", "samurai", "knight", "rider",
             "legend", "hero", "phantom", "reaper", "titan", "gladiator", "viking", "ronin"]
    
    adj = random.choice(adjectives)
    noun = random.choice(nouns)
    number = random.randint(1, 9999)
    
    patterns = [
        f"{adj}{noun}{number}", f"{adj}_{noun}{number}", f"{noun}{adj}{number}",
        f"{adj}{number}{noun}", f"x{adj}_{noun}x", f"its_{adj}{number}",
        f"real_{noun}{number}", f"{adj}o{number}", f"i{adj}{noun}",
        f"{noun}_{number}", f"{adj}.{noun}{number}", f"the{adj}{noun}",
        f"x{adj}{number}x", f"{adj}v{noun}"
    ]
    
    username = random.choice(patterns)
    
    if random.random() < 0.3:
        username += str(random.randint(0, 99))
    
    if len(username) > 20:
        username = username[:20]
    elif len(username) < 3:
        username += str(random.randint(100, 999))
    
    return username

def generate_random_password():
    length = random.randint(10, 16)
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*_+-="
    
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special)
    ]
    
    all_chars = lowercase + uppercase + digits + special
    password += random.choices(all_chars, k=length - 4)
    random.shuffle(password)
    
    return ''.join(password)

async def send_discord_webhook(message: str):
    if not DISCORD_WEBHOOK_URL:
        return
    payload = {
        "embeds": [{
            "title": "🤖 Roblox Auto Register & Cookie Harvester",
            "description": message,
            "color": 3066993,
            "timestamp": datetime.now().isoformat()
        }]
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, json=payload) as response:
                if response.status not in (200, 204):
                    print(f"[!] Gagal mengirim webhook (Status: {response.status})")
    except Exception as e:
        print(f"[!] Error saat mengirim webhook: {e}")

async def send_discord_limit_notification(retry_count, wait_minutes, username):
    if not DISCORD_WEBHOOK_URL:
        return
    retry_emoji = ["1️⃣", "2️⃣", "3️⃣"]
    retry_label = retry_emoji[retry_count] if retry_count < len(retry_emoji) else "🔄"
    
    payload = {
        "embeds": [{
            "title": "⚠️ Roblox Rate Limit Terdeteksi",
            "description": (
                f"{retry_label} **Percobaan ke-{retry_count + 1}**\n\n"
                f"👤 Username: `{username}`\n"
                f"⏰ Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"⏳ Menunggu: **{wait_minutes} menit**\n"
                f"📊 Sistem: Exponential Backoff"
            ),
            "color": 16705372,
            "timestamp": datetime.now().isoformat()
        }]
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, json=payload) as response:
                if response.status not in (200, 204):
                    print(f"[!] Gagal mengirim webhook limit")
    except Exception as e:
        print(f"[!] Error webhook: {e}")

def daftar_roblox(username, password, output_file, retry_count=0):
    max_retries = len(RATE_LIMIT_WAIT_TIMES)
    
    options = Options()
    options.set_preference("general.useragent.override", 
                          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Firefox(options=options)
    
    try:
        print(f"\n[+] Memproses: {username}")
        time.sleep(random.uniform(1, 3))
        
        driver.get("https://www.roblox.com/")
        time.sleep(random.uniform(0.5, 1.5))
        
        # Isi tanggal lahir
        driver.find_element(By.ID, "MonthDropdown").send_keys("January")
        time.sleep(random.uniform(0.3, 0.7))
        driver.find_element(By.ID, "DayDropdown").send_keys("01")
        time.sleep(random.uniform(0.3, 0.7))
        driver.find_element(By.ID, "YearDropdown").send_keys("2011")
        time.sleep(random.uniform(0.5, 1.0))
        
        # Isi username
        driver.find_element(By.ID, "signup-username").send_keys(username)
        time.sleep(1.5)
        
        # Cek error username
        try:
            error_element = driver.find_element(By.ID, "signup-usernameInputValidation")
            if error_element.text.strip():
                print(f"[!] Username '{username}' tidak dapat digunakan")
                driver.quit()
                return "invalid_username"
        except:
            pass
        
        # Isi password
        driver.find_element(By.ID, "signup-password").send_keys(password)
        time.sleep(random.uniform(0.5, 1.0))
        
        # Klik daftar
        driver.find_element(By.ID, "signup-button").click()
        
        print(f"[!] Kalo ada Captcha, mode headless gabisa solve")
        print(f"[*] Menunggu pendaftaran (max 2 menit)...")
        
        try:
            WebDriverWait(driver, 120).until(
                lambda d: "home" in d.current_url
            )
            print(f"[✓] Berhasil mendaftar: {username}")
            
            time.sleep(2)
            cookies = driver.get_cookies()
            
            # Cari .ROBLOSECURITY
            raw_cookie_value = None
            for cookie in cookies:
                if cookie.get("name") == ".ROBLOSECURITY":
                    raw_cookie_value = cookie.get("value")
                    break
            
            # Simpan cookies
            os.makedirs("cookies", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            cookies_file = f"cookies/{username}_{timestamp}.json"
            with open(cookies_file, "w") as f:
                json.dump(cookies, f, indent=4)
            print(f"[📁] Cookie disimpan: {cookies_file}")
            
            # Copy ke storage
            try:
                storage_cookies = os.path.expanduser("~/storage/shared/krexel/cookies")
                os.makedirs(storage_cookies, exist_ok=True)
                with open(f"{storage_cookies}/{username}_{timestamp}.json", "w") as f:
                    json.dump(cookies, f, indent=4)
                print(f"[📁] Cookie juga ke: storage/krexel/cookies/")
            except:
                pass
            
            # Simpan hasil
            if raw_cookie_value:
                full_cookie = f".ROBLOSECURITY={raw_cookie_value}"
                print(f"[+] .ROBLOSECURITY Didapatkan!")
                
                with open(output_file, "a") as f:
                    f.write(f"{username}:{password}:{full_cookie}\n")
                
                # Copy ke storage
                try:
                    storage_path = os.path.expanduser("~/storage/shared/krexel")
                    os.makedirs(storage_path, exist_ok=True)
                    with open(f"{storage_path}/{output_file}", "a") as f:
                        f.write(f"{username}:{password}:{full_cookie}\n")
                    print(f"[📁] Hasil ke: storage/krexel/{output_file}")
                except:
                    pass
            else:
                print(f"[!] Cookie .ROBLOSECURITY tidak ditemukan")
                with open(output_file, "a") as f:
                    f.write(f"{username}:{password}:NO_COOKIE\n")
            
            driver.quit()
            return True
            
        except Exception as e:
            print(f"[X] Gagal: {e}")
            
            # Cek rate limit
            try:
                if "unknown error" in driver.page_source.lower():
                    print(f"[⚠️] Rate limit terdeteksi!")
                    if retry_count < max_retries:
                        wait_seconds = RATE_LIMIT_WAIT_TIMES[retry_count]
                        wait_minutes = wait_seconds // 60
                        driver.quit()
                        print(f"[⏳] Menunggu {wait_minutes} menit...")
                        time.sleep(wait_seconds)
                        return daftar_roblox(username, password, output_file, retry_count + 1)
            except:
                pass
            
            driver.quit()
            return False
            
    except Exception as e:
        print(f"[X] Error: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

async def main():
    global DISCORD_WEBHOOK_URL
    
    print("\n" + "="*50)
    print("🤖 ROBLOX AUTO REGISTER + COOKIE HARVESTER")
    print("🦊 Selenium + Firefox Version")
    print("="*50)
    
    print("\n[🔒] Masukkan Discord Webhook URL")
    print("[💡] Biarin kosong kalo ga mau pake notifikasi Discord")
    DISCORD_WEBHOOK_URL = input("[?] Webhook URL: ").strip()
    
    if DISCORD_WEBHOOK_URL:
        print("[✓] Webhook Discord berhasil diset!")
    else:
        print("[ℹ️] Mode tanpa notifikasi Discord")
        DISCORD_WEBHOOK_URL = None
    
    while True:
        try:
            jumlah_akun = int(input("\n[?] Mau bikin berapa akun? (contoh: 5): "))
            if jumlah_akun <= 0:
                print("[!] Jumlah akun harus lebih dari 0!")
                continue
            break
        except ValueError:
            print("[!] Masukkan angka yang valid!")
    
    while True:
        nama_file = input("[?] Nama file output? (contoh: hasil.txt): ").strip()
        if not nama_file:
            print("[!] Nama file tidak boleh kosong!")
            continue
        if not nama_file.endswith('.txt'):
            nama_file += '.txt'
        break
    
    print(f"\n[+] Membuat {jumlah_akun} akun...")
    
    akun_list = []
    for i in range(jumlah_akun):
        username = generate_random_username()
        password = generate_random_password()
        akun_list.append((username, password))
        print(f"[{i+1}/{jumlah_akun}] {username}:{password}")
    
    input("\n[!] Tekan ENTER untuk mulai...")
    
    berhasil = 0
    gagal = 0
    
    for current, (username, password) in enumerate(akun_list, 1):
        print(f"\n{'='*50}")
        print(f"[📊] Progress: {current}/{jumlah_akun} | ✅ {berhasil} | ❌ {gagal}")
        print(f"{'='*50}")
        
        result = daftar_roblox(username, password, nama_file)
        
        if result == True:
            berhasil += 1
        elif result == "invalid_username":
            new_username = generate_random_username()
            print(f"[🔄] Coba username baru: {new_username}")
            result2 = daftar_roblox(new_username, password, nama_file)
            if result2 == True:
                berhasil += 1
            else:
                gagal += 1
        else:
            gagal += 1
    
    print(f"\n{'='*50}")
    print(f"[🏁] SELESAI!")
    print(f"[✅] Berhasil: {berhasil} | [❌] Gagal: {gagal}")
    print(f"[💾] Hasil: {nama_file}")
    print(f"[📁] Cookies: cookies/ & storage/krexel/")
    print(f"{'='*50}")

if __name__ == "__main__":
    asyncio.run(main())
