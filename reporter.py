import os
import json
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "output.json")
REPORT_FILE = os.path.join(BASE_DIR, "report.md")


def generate_report():
    """
    Зчитує output.json, агрегує дані та генерує звіт report.md
    """
    if not os.path.exists(OUTPUT_FILE):
        print(f"[!] Файл {OUTPUT_FILE} не знайдено. Спочатку запустіть обробку запитів.")
        return

    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[!] Помилка читання {OUTPUT_FILE}: {e}")
        return

    if not isinstance(data, list) or not data:
        print("[!] output.json порожній або має невірний формат.")
        return

    total_requests = len(data)
    
    categories = Counter()
    priorities = Counter()
    departments = Counter()
    clarification_needed = []

    for item in data:
        analysis = item.get("analysis", {})
        
        # Агрегація категорій
        cat = analysis.get("category", "не вказано")
        categories[cat] += 1
        
        # Агрегація пріоритетів
        pri = analysis.get("priority", "не вказано")
        priorities[pri] += 1
        
        # Агрегація відділів
        dept = analysis.get("target_department") or "Не вказано / Загальний"
        departments[dept] += 1
        
        # Запити, що потребують уточнення
        if analysis.get("needs_clarification", False):
            clarification_needed.append(item)

    # Формування Markdown-звіту
    md_lines = [
        "# 📊 Аналітичний звіт по запитах Netpeak AI Unit",
        f"\n**Всього опрацьовано запитів:** `{total_requests}`\n",
        "---",
        "## 📂 Розподіл за категоріями"
    ]
    
    for cat, count in categories.most_common():
        md_lines.append(f"- **{cat}**: {count}")

    md_lines.append("\n## ⚡ Розподіл за пріоритетами")
    for pri, count in priorities.most_common():
        md_lines.append(f"- **{pri}**: {count}")

    md_lines.append("\n## 🏢 Розподіл за відділами-замовниками")
    for dept, count in departments.most_common():
        md_lines.append(f"- **{dept}**: {count}")

    md_lines.append(f"\n## ❓ Запити, що потребують уточнення (`{len(clarification_needed)}`)")
    if clarification_needed:
        for item in clarification_needed:
            req_id = item.get("id", "N/A")
            raw = item.get("raw_text", "")
            summary = item.get("analysis", {}).get("short_summary", "Немає опису")
            md_lines.append(f"- **[{req_id}]**: *\"{raw}\"*")
            md_lines.append(f"  - **Суть:** {summary}")
    else:
        md_lines.append("Немає запитів, що потребують уточнення. Всі звернення чіткі!")

    # Запис у файл
    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        print(f"[✓] Звіт успішно згенетовано у файл: {REPORT_FILE}")
    except Exception as e:
    
        print(f"[!] Помилка запису звіту {REPORT_FILE}: {e}")


if __name__ == "__main__":
    generate_report()