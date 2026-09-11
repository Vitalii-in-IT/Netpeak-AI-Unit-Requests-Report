# reader.py
import os
import json
import csv
import time
from typing import Generator, Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def update_last_processed_text(raw_text: str):
    """Записує точний текст обробленого рядка в config.json."""
    cfg = load_config()
    cfg["last_processed_text"] = raw_text
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[!] Помилка запису в {CONFIG_FILE}: {e}")


def stream_csv_lines(poll_interval: float = 2.0) -> Generator[Dict[str, Any], None, None]:
    cfg = load_config()
    csv_path = cfg.get("csv_path", "input_requests.csv")
    last_text = cfg.get("last_processed_text", "").strip()

    while not os.path.exists(csv_path):
        print(f"[!] Очікування файлу {csv_path}...")
        time.sleep(poll_interval)

    # 1. Читаємо всі рядки файлу
    with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
        rows = list(csv.DictReader(f))

    # 2. Знаходимо стартову позицію
    start_pos = 0
    if last_text:
        found = False
        for idx, r in enumerate(rows):
            if r.get("raw_text", "").strip() == last_text:
                start_pos = idx + 1
                found = True
                break
        if not found:
            print("[*] Збереженого тексту не знайдено у файлі. Починаємо з самого початку.")
            start_pos = 0
        else:
            print(f"[*] Продовжуємо обробку після збереженого рядка (з рядка #{start_pos + 1}).")
    else:
        print("[*] Конфіг чистий. Починаємо з першого рядка зверху.")

    # 3. Віддаємо існуючі рядки строго по порядку
    for i in range(start_pos, len(rows)):
        yield {
            "id": rows[i].get("id", "").strip(),
            "channel": rows[i].get("channel", "").strip(),
            "timestamp": rows[i].get("timestamp", "").strip(),
            "raw_text": rows[i].get("raw_text", "").strip()
        }

    # 4. Моніторимо появу нових записів у кінці файлу
    seen_count = len(rows)
    while True:
        time.sleep(poll_interval)
        with open(csv_path, mode="r", encoding="utf-8", errors="ignore") as f:
            current_rows = list(csv.DictReader(f))

        if len(current_rows) > seen_count:
            for i in range(seen_count, len(current_rows)):
                yield {
                    "id": current_rows[i].get("id", "").strip(),
                    "channel": current_rows[i].get("channel", "").strip(),
                    "timestamp": current_rows[i].get("timestamp", "").strip(),
                    "raw_text": current_rows[i].get("raw_text", "").strip()
                }
            seen_count = len(current_rows)