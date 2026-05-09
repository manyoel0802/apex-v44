import requests

# Kredensial Kapten
TELE_TOKEN = "8457858315:AAGPSHq0UsfPv8MZ733tHs40gAOxwvx7G0o"
TELE_CHAT_ID = "5916986433"

def send_test():
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELE_CHAT_ID,
        "text": "🚀 <b>KOMUNIKASI AKTIF!</b>\nLapor Kapten, jalur intelijen V45.0 OMNI-APEX telah terhubung sempurna. Siap menerima sinyal bursa besok pagi!",
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print("✅ BERHASIL: Pesan tes telah mendarat di Telegram Kapten!")
        else:
            print(f"❌ GAGAL: Error {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ KONEKSI ERROR: {e}")

if __name__ == "__main__":
    send_test()