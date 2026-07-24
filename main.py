import asyncio
from playwright.async_api import async_playwright
import aiohttp
import os
import json
from datetime import datetime
import random
import string

# WEBHOOK AKAN DIMINTA SAAT RUNTIME - AMAN UNTUK GITHUB!
DISCORD_WEBHOOK_URL = None  # Akan diisi nanti

RATE_LIMIT_WAIT_TIMES = [3 * 60, 8 * 60, 20 * 60]

def generate_random_username():
    """Generate random username Roblox style"""
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
        f"{adj}{noun}{number}",
        f"{adj}_{noun}{number}",
        f"{noun}{adj}{number}",
        f"{adj}{number}{noun}",
        f"x{adj}_{noun}x",
        f"its_{adj}{number}",
        f"real_{noun}{number}",
        f"{adj}o{number}",
        f"i{adj}{noun}",
        f"{noun}_{number}",
        f"{adj}.{noun}{number}",
        f"the{adj}{noun}",
        f"x{adj}{number}x",
        f"{adj}v{noun}"
    ]
    
    username = random.choice(patterns)
    
    if random.random() < 0.3:
        username += str(random.randint(0, 99))
    
    if random.random() < 0.2:
        replacements = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5'}
        username = ''.join(replacements.get(c.lower(), c) if random.random() < 0.3 else c for c in username)
    
    if len(username) > 20:
        username = username[:20]
    elif len(username) < 3:
        username += str(random.randint(100, 999))
    
    return username

def generate_random_password():
    """Generate random password yang aman"""
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
    """Fungsi untuk mengirim notifikasi ke Discord Webhook (Hanya untuk akun berhasil)."""
    if not DISCORD_WEBHOOK_URL:
        return

    payload = {
        "embeds": [
            {
                "title": "🤖 Roblox Auto Register & Cookie Harvester",
                "description": message,
                "color": 3066993,
                "timestamp": datetime.now().isoformat()
            }
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, json=payload) as response:
                if response.status not in (200, 204):
                    print(f"[!] Gagal mengirim webhook (Status: {response.status})")
    except Exception as e:
        print(f"[!] Error saat mengirim webhook: {e}")

async def send_discord_limit_notification(retry_count, wait_minutes, username):
    """Mengirim notifikasi ketika terkena rate limit."""
    if not DISCORD_WEBHOOK_URL:
        return

    retry_emoji = ["1️⃣", "2️⃣", "3️⃣"]
    retry_label = retry_emoji[retry_count] if retry_count < len(retry_emoji) else "🔄"
    
    payload = {
        "embeds": [
            {
                "title": "⚠️ Roblox Rate Limit Terdeteksi",
                "description": (
                    f"{retry_label} **Percobaan ke-{retry_count + 1}**\n\n"
                    f"👤 Username: `{username}`\n"
                    f"⏰ Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"⏳ Menunggu: **{wait_minutes} menit**\n"
                    f"📊 Sistem: Exponential Backoff (3m → 8m → 20m)"
                ),
                "color": 16705372,
                "timestamp": datetime.now().isoformat()
            }
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, json=payload) as response:
                if response.status not in (200, 204):
                    print(f"[!] Gagal mengirim webhook limit (Status: {response.status})")
    except Exception as e:
        print(f"[!] Error saat mengirim webhook limit: {e}")

async def daftar_roblox(username, password, output_file, retry_count=0):
    max_retries = len(RATE_LIMIT_WAIT_TIMES)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = await context.new_page()
        
        print(f"\n[+] Memproses: {username}")
        
        random_delay = random.uniform(1, 3)
        await asyncio.sleep(random_delay)
        
        await page.goto("https://www.roblox.com/")
        
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        await page.select_option("#MonthDropdown", label="January")
        await asyncio.sleep(random.uniform(0.3, 0.7))
        await page.select_option("#DayDropdown", label="01")
        await asyncio.sleep(random.uniform(0.3, 0.7))
        await page.select_option("#YearDropdown", label="2011")
        
        await asyncio.sleep(random.uniform(0.5, 1.0))
        
        await page.fill("#signup-username", username)
        
        await asyncio.sleep(1.5)
        
        error_element = page.locator("#signup-usernameInputValidation")
        if await error_element.is_visible():
            error_text = await error_element.inner_text()
            if error_text.strip():
                print(f"[!] Username '{username}' tidak dapat digunakan: {error_text.strip()}")
                print("[→] Generate username baru dan coba lagi...")
                await browser.close()
                return "invalid_username"
        
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        await page.fill("#signup-password", password)
        
        await asyncio.sleep(random.uniform(0.5, 1.0))
        
        await page.click("#signup-button")
        
        print(f"[!] Kalo ada Captcha, silakan diselesaikan manual dulu ya...")
        print(f"[*] Menunggu pendaftaran selesai (max 5 menit)...")
        
        try:
            await asyncio.sleep(3)
            
            try:
                error_message = await page.locator('text="Sorry! An unknown error occurred. Please try again later."').is_visible(timeout=5000)
                
                if error_message:
                    print(f"[⚠️] Rate limit terdeteksi untuk {username}!")
                    
                    if retry_count < max_retries:
                        wait_seconds = RATE_LIMIT_WAIT_TIMES[retry_count]
                        wait_minutes = wait_seconds // 60
                        
                        print(f"[🔄] Percobaan ke-{retry_count + 1} dari {max_retries}")
                        print(f"[⏳] Exponential Backoff: Menunggu {wait_minutes} menit...")
                        
                        await send_discord_limit_notification(retry_count, wait_minutes, username)
                        
                        await browser.close()
                        
                        for remaining in range(wait_seconds, 0, -30):
                            minutes_left = remaining // 60
                            seconds_left = remaining % 60
                            if seconds_left == 0:
                                print(f"[⏰] Sisa waktu menunggu: {minutes_left} menit...")
                            await asyncio.sleep(30)
                        
                        print(f"[🔄] Melanjutkan pendaftaran untuk {username} setelah menunggu {wait_minutes} menit...")
                        return await daftar_roblox(username, password, output_file, retry_count + 1)
                    else:
                        print(f"[X] Sudah mencoba {max_retries} kali. Melewati {username}.")
                        await browser.close()
                        return False
                        
            except:
                pass
            
            await page.wait_for_url("**/home**", timeout=300000)
            print(f"[✓] Berhasil mendaftar: {username}")
            
            await asyncio.sleep(1)
            
            cookies = await context.cookies()
            
            raw_cookie_value = None
            for cookie in cookies:
                if cookie.get("name") == ".ROBLOSECURITY":
                    raw_cookie_value = cookie.get("value")
                    break

            # ============================================
            # 🔥 SIMPAN COOKIES (DEFAULT + STORAGE/KREXEL)
            # ============================================
            
            # Simpan di folder cookies utama (Termux/PC)
            os.makedirs("cookies", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cookies_file = f"cookies/{username}_{timestamp}.json"
            with open(cookies_file, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=4)
            print(f"[📁] Cookie disimpan: {cookies_file}")
            
            # 🔥 AUTO COPY KE STORAGE/KREXEL/COOKIES (BUAT TERMUX)
            try:
                storage_cookies = os.path.expanduser("~/storage/shared/krexel/cookies")
                os.makedirs(storage_cookies, exist_ok=True)
                with open(f"{storage_cookies}/{username}_{timestamp}.json", "w", encoding="utf-8") as f:
                    json.dump(cookies, f, indent=4)
                print(f"[📁] Cookie juga disimpan ke: storage/krexel/cookies/")
            except Exception as e:
                pass  # Gagal copy? Gapapa, udah ada di folder cookies/

            if raw_cookie_value:
                full_cookie_string = f".ROBLOSECURITY={raw_cookie_value}"
                
                print(f"[+] .ROBLOSECURITY Berhasil Didapatkan!")
                
                # Simpan ke file utama
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(f"{username}:{password}:{full_cookie_string}\n")
                
                # 🔥 AUTO COPY HASIL KE STORAGE/KREXEL/ (BUAT TERMUX)
                try:
                    storage_path = os.path.expanduser("~/storage/shared/krexel")
                    os.makedirs(storage_path, exist_ok=True)
                    with open(f"{storage_path}/{output_file}", "a", encoding="utf-8") as f:
                        f.write(f"{username}:{password}:{full_cookie_string}\n")
                    print(f"[📁] Hasil juga disimpan ke: storage/krexel/{output_file}")
                except Exception as e:
                    pass  # Gagal copy? Gapapa, udah ada di folder utama
                
                cookie_msg = f"```\n{full_cookie_string}\n```"
            else:
                print(f"[!] Warning: Cookie .ROBLOSECURITY tidak ditemukan.")
                cookie_msg = "*Tidak Ditemukan*"
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(f"{username}:{password}:NO_COOKIE\n")

            msg = (
                f"✅ **Akun Berhasil Dibuat!**\n\n"
                f"👤 **Username:** `{username}`\n"
                f"🔑 **Password:** `{password}`\n\n"
                f"🍪 **Cookie (.ROBLOSECURITY):**\n{cookie_msg}\n"
                f"📅 **Waktu:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await send_discord_webhook(msg)
            
            await browser.close()
            return True

        except Exception as e:
            print(f"[X] Gagal/Timeout pendaftaran {username}: {e}")
            
            try:
                error_text = await page.locator('body').inner_text()
                if "unknown error occurred" in error_text.lower():
                    print(f"[⚠️] Rate limit terkonfirmasi dari error text!")
                    
                    if retry_count < max_retries:
                        wait_seconds = RATE_LIMIT_WAIT_TIMES[retry_count]
                        wait_minutes = wait_seconds // 60
                        
                        await browser.close()
                        print(f"[⏳] Exponential Backoff: Menunggu {wait_minutes} menit...")
                        await send_discord_limit_notification(retry_count, wait_minutes, username)
                        
                        for remaining in range(wait_seconds, 0, -30):
                            minutes_left = remaining // 60
                            if remaining % 60 == 0:
                                print(f"[⏰] Sisa waktu menunggu: {minutes_left} menit...")
                            await asyncio.sleep(30)
                        
                        return await daftar_roblox(username, password, output_file, retry_count + 1)
            except:
                pass
            
            await browser.close()
            return False

async def main():
    global DISCORD_WEBHOOK_URL
    
    print("\n" + "="*50)
    print("🤖 ROBLOX AUTO REGISTER + COOKIE HARVESTER")
    print("="*50)
    
    # 🔒 MINTA WEBHOOK DARI USER (GA DISIMPEN DI KODE)
    print("\n[🔒] Masukkan Discord Webhook URL")
    print("[💡] Biarin kosong kalo ga mau pake notifikasi Discord")
    DISCORD_WEBHOOK_URL = input("[?] Webhook URL: ").strip()
    
    if DISCORD_WEBHOOK_URL:
        print("[✓] Webhook Discord berhasil diset!")
        print("[ℹ️] Notifikasi akan dikirim ke Discord")
    else:
        print("[ℹ️] Mode tanpa notifikasi Discord")
        DISCORD_WEBHOOK_URL = None
    
    # Input jumlah akun
    while True:
        try:
            jumlah_akun = int(input("\n[?] Mau bikin berapa akun? (contoh: 5): "))
            if jumlah_akun <= 0:
                print("[!] Jumlah akun harus lebih dari 0!")
                continue
            if jumlah_akun > 50:
                konfirmasi = input("[!] Banyak banget nih, yakin mau lanjut? (y/n): ")
                if konfirmasi.lower() != 'y':
                    continue
            break
        except ValueError:
            print("[!] Masukkan angka yang valid!")
    
    # Input nama file output
    while True:
        nama_file = input("[?] Nama file buat nyimpen cookies? (contoh: hasil.txt): ").strip()
        if not nama_file:
            print("[!] Nama file tidak boleh kosong!")
            continue
        if not nama_file.endswith('.txt'):
            nama_file += '.txt'
            print(f"[*] Ditambahkan ekstensi .txt -> {nama_file}")
        break
    
    print(f"\n[+] Membuat {jumlah_akun} akun dengan username & password random...")
    print(f"[⚙️] Rate Limit Settings: {', '.join([str(t//60)+' menit' for t in RATE_LIMIT_WAIT_TIMES])}")
    print(f"[🛡️] Anti-detection: Random delays + Natural behavior enabled")
    print(f"[⏰] Timeout Captcha: 5 menit per akun")
    print(f"[💾] Hasil akan disimpan ke: {nama_file}")
    print(f"[📱] Storage backup: storage/krexel/ (Termux)")
    if DISCORD_WEBHOOK_URL:
        print(f"[📨] Notifikasi Discord: AKTIF")
    else:
        print(f"[📨] Notifikasi Discord: NONAKTIF")
    print()
    
    # Generate akun random
    akun_list = []
    used_usernames = set()
    
    for i in range(jumlah_akun):
        attempts = 0
        while attempts < 10:
            username = generate_random_username()
            if username not in used_usernames:
                used_usernames.add(username)
                break
            attempts += 1
        
        password = generate_random_password()
        akun_list.append((username, password))
        
        print(f"[{i+1}/{jumlah_akun}] Generated: {username}:{password}")
    
    print(f"\n[✓] {jumlah_akun} akun berhasil digenerate!")
    
    input("\n[!] Tekan ENTER untuk mulai mendaftarkan akun...")
    
    total = len(akun_list)
    berhasil_count = 0
    gagal_count = 0
    retry_username = 0
    
    for current, (username, password) in enumerate(akun_list, 1):
        print(f"\n{'='*50}")
        print(f"[📊] Progress: {current}/{total} | ✅ Berhasil: {berhasil_count} | ❌ Gagal: {gagal_count}")
        print(f"{'='*50}")
        
        result = await daftar_roblox(username, password, nama_file)
        
        if result == True:
            berhasil_count += 1
            print(f"[✓] Akun {current}/{total} berhasil. Melanjutkan...")
        elif result == "invalid_username":
            retry_username += 1
            new_username = generate_random_username()
            while new_username in used_usernames:
                new_username = generate_random_username()
            used_usernames.add(new_username)
            
            print(f"[🔄] Mencoba dengan username baru: {new_username}")
            result2 = await daftar_roblox(new_username, password, nama_file)
            if result2 == True:
                berhasil_count += 1
            else:
                gagal_count += 1
        else:
            gagal_count += 1
            print(f"[→] Akun {current}/{total} gagal/dilewati. Melanjutkan...")
    
    print(f"\n{'='*50}")
    print(f"[🏁] SELESAI!")
    print(f"[📊] Total akun: {total}")
    print(f"[✅] Berhasil: {berhasil_count} akun")
    print(f"[❌] Gagal: {gagal_count} akun")
    if retry_username > 0:
        print(f"[🔄] Username diganti: {retry_username}x")
    print(f"[💾] Hasil disimpan di: {nama_file}")
    print(f"[📁] Cookies detail di folder: cookies/")
    print(f"[📱] Backup di: storage/krexel/")
    print(f"{'='*50}")
    
    # Tampilkan isi file hasil
    if os.path.exists(nama_file) and os.path.getsize(nama_file) > 0:
        print(f"\n[📄] Preview hasil di {nama_file}:")
        with open(nama_file, "r") as f:
            lines = f.readlines()
            for line in lines[:5]:
                print(f"  {line.strip()}")
            if len(lines) > 5:
                print(f"  ... dan {len(lines)-5} akun lainnya")

if __name__ == "__main__":
    asyncio.run(main())
