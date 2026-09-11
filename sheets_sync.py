import os
import json
import re
import traceback
import gspread

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "output.json")
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def extract_spreadsheet_id(url_or_id: str) -> str:
    """Витягує чистий ID таблиці з будь-якого формату посилання Google Sheets."""
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url_or_id)
    if match:
        return match.group(1)
    return url_or_id.strip()


def sync_report_to_google_sheet():
    """Повністю перезаписує перший аркуш Google Таблиці даними з output.json."""
    cfg = load_config()
    sheet_input = cfg.get("google_sheet_url", "").strip()

    if not sheet_input:
        print("[!] Google Sheet URL відсутній у config.json.")
        return

    if not os.path.exists(CREDENTIALS_FILE):
        print(f"[!] Файл ключів {CREDENTIALS_FILE} не знайдено в папці проекту.")
        return

    if not os.path.exists(OUTPUT_FILE):
        print(f"[!] Файл результатів {OUTPUT_FILE} не знайдено.")
        return

    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    except Exception as e:
        print(f"[!] Помилка читання {OUTPUT_FILE}: {e}")
        return

    try:
        sheet_id = extract_spreadsheet_id(sheet_input)
        gc = gspread.service_account(filename=CREDENTIALS_FILE)
        
        # Відкриваємо безпосередньо за ID
        sh = gc.open_by_key(sheet_id)
        worksheet = sh.get_worksheet(0)

        worksheet.clear()

        headers = [
            "ID",
            "Канал",
            "Пріоритет",
            "Категорія",
            "Відділ",
            "Потребує уточнення",
            "Суть",
            "Дії (requested_actions)",
            "Вихідний текст"
        ]

        rows_to_insert = [headers]

        for item in records:
            analysis = item.get("analysis", {})
            actions = ", ".join(analysis.get("requested_actions", []))
            
            rows_to_insert.append([
                item.get("id", ""),
                item.get("channel", ""),
                analysis.get("priority", ""),
                analysis.get("category", ""),
                analysis.get("target_department") or "Не вказано",
                "ТАК" if analysis.get("needs_clarification") else "НІ",
                analysis.get("short_summary", ""),
                actions,
                item.get("raw_text", "")
            ])

        worksheet.update(values=rows_to_insert, range_name="A1")

        worksheet.format("A1:I1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.85, "green": 0.92, "blue": 0.83}
        })

        print(f"[✓] Google Таблицю успішно перезаписано! (Записів: {len(records)})")

    except Exception as e:
        err_msg = str(e) or repr(e)
        print(f"[!] Помилка синхронізації з Google Sheets: {err_msg}")
        traceback.print_exc()


if __name__ == "__main__":
    sync_report_to_google_sheet()