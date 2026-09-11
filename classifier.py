# classifier.py
import os
import json
import time
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import APIError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")


class Category(str, Enum):
    AUTOMATION = "автоматизація"
    INTEGRATION = "інтеграція"
    REPORT_ANALYTICS = "звіт/аналітика"
    BUG_SUPPORT = "баг/підтримка"
    CONSULTATION = "питання/консультація"
    OUT_OF_SCOPE = "поза скоупом"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RequestAnalysis(BaseModel):
    category: Category = Field(description="Категорія запиту")
    target_department: Optional[str] = Field(None, description="HR, Sales, Marketing, PM, Analytics або null")
    priority: Priority = Field(description="Терміновість запиту: low, medium, high")
    short_summary: str = Field(description="Коротка суть одним реченням")
    requested_actions: List[str] = Field(default_factory=list, description="Список конкретних дій")
    needs_clarification: bool = Field(description="true, якщо запит надто розмитий або неповний")
    urgency_reason: Optional[str] = Field(None, description="Чому обрано такий пріоритет")


def get_current_api_key() -> str:
    """Вичитує актуальний ключ безпосередньо перед запитом."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return cfg.get("gemini_api_key", "").strip()
        except Exception:
            pass
    return ""


def classify_request(raw_text: str, stop_checker=None) -> dict:
    """
    Відправляє текст у Gemini і повертає структурований словник.
    При помилці робить повторні спроби або чекає оновлення налаштувань.
    """
    system_instruction = (
        "Ти — AI-асистент для внутрішнього AI-юніту компанії Netpeak. "
        "Твоє завдання — класифікувати вхідні повідомлення та витягнути структуровані дані. "
        "Якщо запит надто неконкретний (наприклад, 'зробіть мені бота') — обов'язково став needs_clarification=True. "
        "Запити не пов'язані з AI чи автоматизацією маркуй як 'поза скоупом'."
    )

    while True:
        if stop_checker and stop_checker():
            return None

        api_key = get_current_api_key()
        if not api_key:
            print("[!] API-ключ відсутній у config.json. Очікування оновлення...")
            time.sleep(2)
            continue

        try:
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=f"Вхідний текст звернення:\n{raw_text}",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=RequestAnalysis,
                    temperature=0.1,
                ),
            )

            parsed = RequestAnalysis.model_validate_json(response.text)
            return parsed.model_dump(mode="json")

        except APIError as e:
            print(f"\n[!] Помилка Gemini API: {e.message}")
            print("[*] Очікуємо 4 секунди перед повторною спробою...")
            for _ in range(8):
                if stop_checker and stop_checker():
                    return None
                time.sleep(0.5)

        except Exception as e:
            print(f"[!] Непередбачена помилка аналізу: {e}")
            return {
                "category": "поза скоупом",
                "target_department": None,
                "priority": "low",
                "short_summary": "Помилка розпізнавання",
                "requested_actions": [],
                "needs_clarification": True,
                "urgency_reason": str(e)
            }