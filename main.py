import time
import requests
from bs4 import BeautifulSoup

# Telegram bilgileri
TELEGRAM_TOKEN = "7279104095:AAFnm5SHJs9ntWDmNF1IGUyapU8HurwCRs4"
TELEGRAM_CHAT_ID = "@GokDepremBot"

# WhatsApp bilgileri (CallMeBot)
WHATSAPP_PHONE = "905311021590"
WHATSAPP_APIKEY = "3115945"

# Kandilli sayfası
KANDILLI_URL = "https://www.koeri.boun.edu.tr/scripts/lst9.asp"

# Başlangıçta "aktifim" mesajı gönder
def send_start_message():
    message = "📡 Deprem uyarı botu aktif hale getirildi (Render)"
    send_telegram(message)
    send_whatsapp(message)

# Telegram mesajı gönder
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.get(url, params=payload)

# WhatsApp mesajı gönder
def send_whatsapp(text):
    text = text.replace(" ", "+").replace("\n", "%0A")
    url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={text}&apikey={WHATSAPP_APIKEY}"
    requests.get(url)

# Kandilli'den son depremi al
def get_latest_earthquake():
    html = requests.get(KANDILLI_URL).content
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("pre")[0].text.strip().split("\n")[6:]
    latest = rows[0].split()
    tarih, saat, enlem, boylam, derinlik, buyukluk, yer = latest[0], latest[1], latest[2], latest[3], latest[4], latest[6], " ".join(latest[7:])
    return {
        "tarih": tarih,
        "saat": saat,
        "yer": yer,
        "buyukluk": float(buyukluk.replace(",", ".")),
    }

# Ana bot döngüsü
def start_bot():
    last_quake = ""
    send_start_message()
    while True:
        try:
            quake = get_latest_earthquake()
            if quake["buyukluk"] >= 4.0 and quake["yer"] != last_quake:
                message = (
                    f"📢 DEPREM UYARISI\n"
                    f"📍 Yer: {quake['yer']}\n"
                    f"🕏 Büyüklük: {quake['buyukluk']}\n"
                    f"🕒 Saat: {quake['saat']} ({quake['tarih']})\n"
                    f"📡 Kaynak: Kandilli Rasathanesi"
                )
                send_telegram(message)
                send_whatsapp(message)
                last_quake = quake["yer"]
        except Exception as e:
            print("Hata:", e)
        time.sleep(60)

# Botu çalıştır
if __name__ == "__main__":
    start_bot()
