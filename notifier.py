import os
import json
import urllib.request
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
REPORT_FILE = os.path.join(BASE_DIR, "report.md")


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def send_telegram_message(text: str) -> bool:
    """Відправляє текстове повідомлення в Telegram канал через Bot API."""
    cfg = load_config()
    token = cfg.get("telegram_token", "").strip()
    chat_id = cfg.get("telegram_chat_id", "").strip()

    if not token or not chat_id:
        print("[!] Telegram Token або Chat ID відсутні в налаштуваннях.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Telegram підтримує максимум 4096 символів на одне повідомлення
    max_len = 4000
    chunks = [text[i:i + max_len] for i in range(0, len(text), max_len)]

    success = True
    for chunk in chunks:
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "Markdown"
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status != 200:
                    success = False
        except Exception as e:
            print(f"[!] Помилка відправки звіту в Telegram: {e}")
            success = False

    if success:
        print("[✓] Звіт успішно надіслано в Telegram-канал!")
    return success


def send_report_to_telegram():
    """Зчитує report.md та надсилає його в підключений канал."""
    if not os.path.exists(REPORT_FILE):
        print(f"[!] Файл звіту {REPORT_FILE} не знайдено.")
        return

    try:
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            report_text = f.read()
    except Exception as e:
        print(f"[!] Помилка читання файлу звіту: {e}")
        return

    if not report_text.strip():
        print("[!] Файл звіту порожній.")
        return

    send_telegram_message(report_text)


if __name__ == "__main__":
    send_report_to_telegram()