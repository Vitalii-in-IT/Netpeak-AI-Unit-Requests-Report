# check_models.py
import json
from google import genai

with open("config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

client = genai.Client(api_key=cfg.get("gemini_api_key"))

print("Список доступних моделей для вашого ключа:")
for model in client.models.list():
    if "generateContent" in model.supported_actions:
        print(f" - {model.name}")
        