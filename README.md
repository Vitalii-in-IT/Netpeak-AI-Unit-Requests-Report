# Netpeak-AI-Unit-Requests-Report
Автоматизований сервіс для потокового збору, інтелектуальної класифікації та маршрутизації вхідних запитів за допомогою **Google Gemini API**, зі збереженням структурованих даних, синхронізацією з **Google Sheets** та сповіщеннями в **Telegram**.

## 📌 Основний функціонал

* **Графічний інтерфейс (Tkinter):** Зручне вікно налаштування ключів, файлів та моніторингу статусу (СТАРТ / СТОП) у багатопотоковому режимі.
* **Потокова обробка CSV (Stream Reader):**
  * Порядкове читання вхідного файлу в реальному часі.
  * Запам'ятовування останнього обробленого повідомлення (`last_processed_text`) — захист від повторної обробки при перезапусках.
  * Live-моніторинг додавання нових рядків (режим `tail`).
* **AI-класифікація (Google GenAI SDK):**
  * Модель: `gemini-3.5-flash-lite`.
  * **Structured Outputs:** Строга типізація вихідних відповідей за схемою **Pydantic**.
  * Визначення категорії: *автоматизація, інтеграція, звіт/аналітика, баг/підтримка, питання/консультація, поза скоупом*.
  * Оцінка пріоритету (*low / medium / high*), визначення відділу-замовника та формування короткої суті запиту.
  * Детекція неконкретних запитів (`needs_clarification: true`).
* **Збереження та аналітика:**
  * Повна база результатів у форматі `output.json`.
  * Автоматична генерація аналітичного звіту `report.md` з агрегацією за категоріями, пріоритетами, відділами та списком проблемних тікетів.
* **Інтеграції:**
  * **Telegram Bot API:** Автоматична відправка згенерованого звіту в канал/чат команди при зупинці пайплайну.
  * **Google Sheets API (`gspread`):** Автоматичне форматування та перезапис таблиці актуальними структурованими даними.

---

## 🏗 Архітектура проекту

```text
├── main.py              # GUI застосунок (Tkinter), оркестрація потоків
├── reader.py            # Потокове читання CSV, відстеження прогресу
├── classifier.py        # Інтеграція з Gemini API, Pydantic-схеми
├── storage.py           # Збереження та оновлення output.json
├── reporter.py          # Генерація Markdown-звіту з агрегатами
├── notifier.py          # Модуль відправки звітів у Telegram
├── sheets_sync.py       # Синхронізація та форматування Google Таблиці
├── check_models.py      # Утиліта для перевірки доступних моделей Gemini
├── config.json          # Файл конфігурації (створюється автоматично)
└── credentials.json     # Сервісний акаунт Google Cloud (для Sheets API)


<img width="698" height="388" alt="image" src="https://github.com/user-attachments/assets/9f2d8ebe-db35-4066-8147-8e3cf18ac415" />
<img width="977" height="743" alt="image" src="https://github.com/user-attachments/assets/3aa70542-64b3-4cee-b56d-ca7f14711aa6" />
<img width="611" height="1028" alt="image" src="https://github.com/user-attachments/assets/40f6cb71-b2af-4733-b18a-64df899f1e13" />
<img width="1916" height="763" alt="image" src="https://github.com/user-attachments/assets/9a9f91ec-3b02-44f9-b743-3676d5b17036" />
<img width="1625" height="963" alt="image" src="https://github.com/user-attachments/assets/44f98fed-5383-49e5-a606-e80abe693ff9" />

---

## 📸 Результати роботи та інтерфейс

### Панель керування (GUI)
![Панель керування](https://github.com/user-attachments/assets/9f2d8ebe-db35-4066-8147-8e3cf18ac415)

### Логування та обробка черги
![Консоль обробки](https://github.com/user-attachments/assets/3aa70542-64b3-4cee-b56d-ca7f14711aa6)

### Звіт у Telegram-каналі
![Звіт Telegram](https://github.com/user-attachments/assets/40f6cb71-b2af-4733-b18a-64df899f1e13)

### Синхронізація з Google Sheets
![Google Таблиця](https://github.com/user-attachments/assets/9a9f91ec-3b02-44f9-b743-3676d5b17036)

### Повна аналітика та структуровані дані
![Аналітика запитів](https://github.com/user-attachments/assets/44f98fed-5383-49e5-a606-e80abe693ff9)




