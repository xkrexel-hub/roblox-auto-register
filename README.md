
# 🤖 Roblox Auto Register & Cookie Harvester

Script Python untuk otomatisasi pembuatan akun Roblox dengan fitur ekstraksi cookie `.ROBLOSECURITY`.

## ⚠️ DISCLAIMER

**HANYA UNTUK TUJUAN EDUKASI!**

- Script ini melanggar [Roblox Terms of Service](https://en.help.roblox.com/hc/en-us/articles/115004647846-Roblox-Terms-of-Use)
- Penggunaan dapat mengakibatkan **IP ban permanen**
- Saya **TIDAK BERTANGGUNG JAWAB** atas penyalahgunaan
- Gunakan dengan resiko sendiri!

## ✨ Fitur

- ✅ Auto generate username random (Roblox-style)
- ✅ Auto generate password aman
- ✅ Auto register akun Roblox
- ✅ Ekstraksi cookie `.ROBLOSECURITY`
- ✅ Anti-detection (random delay, user-agent)
- ✅ Rate limit handling (exponential backoff)
- ✅ Opsional: Notifikasi ke Discord Webhook
- ✅ Simpan cookies dalam format JSON

## 📋 Requirements

- Python 3.8+
- Playwright
- aiohttp

## 🚀 Instalasi

### Windows/Linux/Mac
```bash
git clone https://github.com/YOUR_USERNAME/roblox-auto-register.git
cd roblox-auto-register
pip install -r requirements.txt
playwright install chromium
