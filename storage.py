import os
import json
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "output.json")


def ensure_output_file():
    """Створює output.json з порожнім списком, якщо файл відсутній."""
    if not os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            print(f"[*] Створено файл результатів: {OUTPUT_FILE}")
        except Exception as e:
            print(f"[!] Помилка створення {OUTPUT_FILE}: {e}")


def append_analysis_result(csv_row: Dict[str, Any], analysis: Dict[str, Any]):
    """
    Зберігає повні дані повідомлення разом із висновком AI в output.json.
    Якщо запис з таким id вже існує — оновлює його, інакше додає новий.
    """
    ensure_output_file()

    data = []
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
    except Exception:
        data = []

    # Об'єднуємо всі вихідні дані CSV та додаємо розбір AI
    record = {
        **csv_row,
        "analysis": analysis
    }

    # Оновлення існуючого або додавання нового
    item_id = csv_row.get("id")
    index_to_update = -1
    if item_id:
        for idx, item in enumerate(data):
            if item.get("id") == item_id:
                index_to_update = idx
                break

    if index_to_update >= 0:
        data[index_to_update] = record
    else:
        data.append(record)

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[✓] Запис збережено в {OUTPUT_FILE}")
    except Exception as e:
        print(f"[!] Помилка запису в {OUTPUT_FILE}: {e}")