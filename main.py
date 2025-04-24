import time
import requests
from urllib.parse import quote

# === TELEGRAM BİLGİLERİ ===
TELEGRAM_TOKEN = "7279104095:AAFnm5SHJs9ntWDmNF1IGUyapU8HurwCRs4"
TELEGRAM_CHAT_ID = "-1002293601074"  # GokDeprem kanal ID

# === WHATSAPP BİLGİLERİ (CallMeBot) ===
WHATSAPP_PHONE = "905311021590"
WHATSAPP_APIKEY = "3115945"

# === HARİTA BAĞLANTISI OLUŞTUR ===
def generate_map_link(location):
    return f"https://www.google.com/maps/search/?api=1&query={quote(location)}"

# === TELEGRAM MESAJI GÖNDER ===
def send_telegram(text):
    print("Telegram mesajı gönderiliyor...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.get(url, params=params)
        print("Telegram cevap kodu:", response.status_code)
        print("Telegram response:", response.text)
    except Exception as e:
        print("Telegram HATASI:", e)

# === WHATSAPP MESAJI GÖNDER ===
def send_whatsapp(text):
    print("WhatsApp mesajı gönderiliyor...")
    text = quote(text)
    url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={text}&apikey={WHATSAPP_APIKEY}"
    try:
        response = requests.get(url)
        print("WhatsApp cevap kodu:", response.status_code)
        print("WhatsApp response:", response.text)
    except Exception as e:
        print("WhatsApp HATASI:", e)

# === BAŞLANGIÇ MESAJI ===
def send_start_message():
    message = "\ud83d\udce1 Bot aktif hale getirildi (PY Test)"
    send_telegram(message)
    send_whatsapp(message)

# === DEPREM VERİSİ ===
def get_latest_earthquake():
    print("Yeni API'den veri çekiliyor...")
    urls = [
        "https://depremapi.gokkripto.com/latest",
        "https://api.orhanaydogdu.com.tr/deprem/kandilli/live",
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_hour.geojson"
    ]

    for url in urls:
        try:
            response = requests.get(url)
            data = response.json()

            if "tarih" in data:
                return {
                    "tarih": data["tarih"],
                    "saat": data["saat"],
                    "yer": data["yer"],
                    "buyukluk": float(data["buyukluk"])
                }
            elif "result" in data and len(data["result"]) > 0:
                afad = data["result"][0]
                return {
                    "tarih": afad["date"].split(" ")[0],
                    "saat": afad["date"].split(" ")[1],
                    "yer": afad["title"],
                    "buyukluk": float(afad["mag"])
                }
            elif "features" in data and len(data["features"]) > 0:
                usgs = data["features"][0]
                place = usgs["properties"]["place"]
                mag = usgs["properties"]["mag"]
                time_ms = usgs["properties"]["time"] // 1000
                from datetime import datetime
                t = datetime.utcfromtimestamp(time_ms).strftime('%Y.%m.%d %H:%M:%S').split()
                return {
                    "tarih": t[0],
                    "saat": t[1],
                    "yer": place,
                    "buyukluk": float(mag)
                }
        except Exception as e:
            print(f"{url} HATASI:", e)

    return {"tarih": "", "saat": "", "yer": "", "buyukluk": 0}

# === ANA FONKSİYON ===
def start_bot():
    print("start_bot() çalıştı.")
    last_earthquake = ""
    send_start_message()
    try:
        quake = get_latest_earthquake()
        if quake["buyukluk"] >= 4.0:
            location = quake["yer"]
            lower_loc = location.lower()
            harita_linki = generate_map_link(location)

            # RENKLİ MESAJ AYARI
            renkli = "\ud83d\udd34 <b>ACİL!</b>" if quake["buyukluk"] >= 5 else "\ud83d\udfe1 <b>Bilgilendirme</b>"

            message = (
                f"{renkli}\n"
                f"\ud83d\udccd <b>Yer:</b> {quake['yer']}\n"
                f"\ud83d\udd4f <b>Büyüklük:</b> {quake['buyukluk']}\n"
                f"\ud83d\udd52 <b>Saat:</b> {quake['saat']} ({quake['tarih']})\n"
                f"\ud83d\udccd <a href='{harita_linki}'>Google Harita ile Aç</a>\n"
                f"\ud83d\udce1 <b>Kaynak:</b> Otomatik API"
            )

            if "istanbul" in lower_loc or "marmara" in lower_loc or "sakarya" in lower_loc or "kocaeli" in lower_loc or "bursa" in lower_loc:
                send_telegram(message)
                send_whatsapp(message)
                last_earthquake = quake["yer"]
            else:
                print("Deprem farklı şehirde: mesaj gönderilmedi.")
        else:
            print("Deprem 4.0 altı: mesaj gönderilmedi.")
    except Exception as e:
        print("Genel HATA:", e)

# === ÇALIŞTIR ===
if __name__ == "__main__":
    print("Bot başlıyor...")
    start_bot()
