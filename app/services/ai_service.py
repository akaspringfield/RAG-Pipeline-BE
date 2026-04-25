'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import requests
from app.config import Config


def generate_ai_response(messages):

    # 🟢 MOCK MODE
    if Config.AI_PROVIDER == "mock":
        return "Mock AI: " + messages[-1]["content"]

    # 🟡 OLLAMA MODE
    if Config.AI_PROVIDER == "ollama":
        response = requests.post(
            f"{Config.OLLAMA_URL}/api/chat",
            json={
                "model": "llama3",
                "messages": messages,
                "stream": False
            }
        )
        return response.json()["message"]["content"]

    # 🔵 fallback
    return "AI not configured"


import time
import requests
from app.config import Config

def call_ai(payload, retries=2):

    for attempt in range(retries + 1):
        try:
            response = requests.post(
                Config.AI_API_URL,
                json=payload,
                timeout=Config.AI_RESPONSE_TIMEOUT
            )
            response.raise_for_status()
            return response.json(), None

        except requests.exceptions.ConnectionError:
            error = "AI service not reachable"

        except requests.exceptions.Timeout:
            error = "AI timeout"

        except Exception as e:
            error = str(e)

        time.sleep(1)  # small backoff

    return None, error