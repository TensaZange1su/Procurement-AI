import requests
import os
import json

AI_URL = "https://nitec-ai.kz/api"
API_KEY = os.getenv("AI_KEY")
MODEL = "openai/gpt-oss-120b"


SYSTEM_PROMPT = """
Ты AI аналитик государственных закупок Казахстана.

Твоя задача:
- анализировать результаты закупок
- выявлять аномалии цен
- объяснять fair price
- анализировать объем закупок

Отвечай кратко, профессионально и понятно.
"""


def generate_llm_response(prompt):

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Ты аналитический агент госзакупок."},
                {"role": "user", "content": prompt}
            ]
        }

        try:

            r = requests.post(
                AI_URL,
                headers=headers,
                json=payload,
                timeout=10
            )

            return r.json()

        except Exception as e:

            return {
                "error": "LLM timeout",
                "details": str(e)
            }