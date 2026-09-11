# main.py
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from reader import stream_csv_lines

from reader import stream_csv_lines, update_last_processed_text
from classifier import classify_request
from reporter import generate_report
from notifier import send_report_to_telegram
from sheets_sync import sync_report_to_google_sheet

CONFIG_FILE = "config.json"

class ConfigApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Налаштування")
        self.geometry("560x280")
        self.resizable(False, False)

        self.is_running = False
        self.worker_thread = None

        self._build_ui()
        self._load_config()

    def _build_ui(self):
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        # 1. Gemini Key
        ttk.Label(frame, text="Gemini API Key:").grid(row=0, column=0, sticky="w", pady=3)
        self.ent_key = ttk.Entry(frame, show="*")
        self.ent_key.grid(row=0, column=1, columnspan=2, sticky="we", pady=3)

        # 2. Шлях до CSV
        ttk.Label(frame, text="Шлях до CSV:").grid(row=1, column=0, sticky="w", pady=3)
        self.ent_csv = ttk.Entry(frame)
        self.ent_csv.grid(row=1, column=1, sticky="we", pady=3)
        ttk.Button(frame, text="Огляд...", width=8, command=self._browse_file).grid(row=1, column=2, padx=4)

        # 3. TG Bot Token
        ttk.Label(frame, text="TG Bot Token:").grid(row=2, column=0, sticky="w", pady=3)
        self.ent_tg_token = ttk.Entry(frame)
        self.ent_tg_token.grid(row=2, column=1, columnspan=2, sticky="we", pady=3)

        # 4. TG Chat ID
        ttk.Label(frame, text="TG Chat ID:").grid(row=3, column=0, sticky="w", pady=3)
        self.ent_tg_chat = ttk.Entry(frame)
        self.ent_tg_chat.grid(row=3, column=1, columnspan=2, sticky="we", pady=3)

        # 5. Google Sheet URL
        ttk.Label(frame, text="Google Sheet URL:").grid(row=4, column=0, sticky="w", pady=4)
        self.ent_sheet = ttk.Entry(frame)
        self.ent_sheet.grid(row=4, column=1, columnspan=2, sticky="we", pady=3)

        frame.columnconfigure(1, weight=1)

        # Кнопка збереження (зелена)
        btn_save = tk.Button(
            self, text="Зберегти налаштування", bg="#2E7D32", fg="white",
            font=("Arial", 10, "bold"), pady=4, command=self._save_config
        )
        btn_save.pack(fill="x", padx=12, pady=(8, 4))

        # Кнопка СТАРТ / СТОП
        self.btn_start = tk.Button(
            self, text="▶ СТАРТ", bg="#D32F2F", fg="white",
            font=("Arial", 10, "bold"), pady=6, command=self._start_pipeline
        )
        self.btn_start.pack(fill="x", padx=12, pady=(0, 8))

    def _browse_file(self):
        f = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if f:
            self.ent_csv.delete(0, tk.END)
            self.ent_csv.insert(0, f)

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.ent_key.insert(0, cfg.get("gemini_api_key", ""))
                    self.ent_csv.insert(0, cfg.get("csv_path", "input_requests.csv"))
                    self.ent_tg_token.insert(0, cfg.get("telegram_token", ""))
                    self.ent_tg_chat.insert(0, cfg.get("telegram_chat_id", ""))
                    self.ent_sheet.insert(0, cfg.get("google_sheet_url", ""))
            except Exception:
                pass
        else:
            self.ent_csv.insert(0, "input_requests.csv")

    def _save_config(self):
        old_cfg = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    old_cfg = json.load(f)
            except Exception:
                pass

        data = {
            "gemini_api_key": self.ent_key.get().strip(),
            "csv_path": self.ent_csv.get().strip(),
            "telegram_token": self.ent_tg_token.get().strip(),
            "telegram_chat_id": self.ent_tg_chat.get().strip(),
            "google_sheet_url": self.ent_sheet.get().strip(),
            "last_processed_text": old_cfg.get("last_processed_text", "")
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[✓] Налаштування збережено в {CONFIG_FILE}")

    def _start_pipeline(self):
        # Якщо вже працює — натискання діє як СТОП
        if self.is_running:
            print("[*] Зупинка... Завершуємо поточну ітерацію.")
            self.is_running = False
            self.btn_start.config(text="▶ СТАРТ", bg="#D32F2F")
            return

        # Якщо зупинено — зберігаємо налаштування і запускаємо
        self._save_config()
        self.is_running = True
        self.btn_start.config(text="⏹ СТОП", bg="#E65100")
        print("[*] Запуск обробки у фоновому потоці...")

        self.worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.worker_thread.start()

    def _run_loop(self):
        import time
        from reader import stream_csv_lines, update_last_processed_text
        from classifier import classify_request
        from storage import append_analysis_result  # <--- Додано імпорт
        
        print("[*] Пайплайн активовано. Очікування та читання рядків...")
        for row in stream_csv_lines():
            if not self.is_running:
                break

            print(f"\n[Взято в роботу]: {row['id']} | {row['raw_text']}")
            print(f"[->] Відправляємо в Gemini: {row['id']} | {row['raw_text'][:50]}...")
            
            result_data = classify_request(row["raw_text"], stop_checker=lambda: not self.is_running)
            
            if not self.is_running or result_data is None:
                break
            
            print(f"[✓] Отримано відповідь:")
            print(f"    Категорія:  {result_data['category']}")
            print(f"    Пріоритет:  {result_data['priority']}")
            print(f"    Суть:       {result_data['short_summary']}")
            print(f"    Уточнення:  {result_data['needs_clarification']}")
            
            # Зберігаємо в output.json
            append_analysis_result(row, result_data)

            # Записуємо оброблений рядок у конфіг
            update_last_processed_text(row["raw_text"])

            time.sleep(1.5)

            if not self.is_running:
                break

        self.is_running = False
        self.btn_start.config(text="▶ СТАРТ", bg="#D32F2F")
        generate_report()
        send_report_to_telegram()
        sync_report_to_google_sheet()
        print("[*] Цикл зупинено.")


if __name__ == "__main__":
    app = ConfigApp()
    app.mainloop()