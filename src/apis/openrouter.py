import requests
from typing import Any, Dict, List


def chat_completions(
    openrouter_api_key: str,
    model: str,
    messages: List[Dict[str, str]],
    timeout: int = 40,
) -> Dict[str, Any]:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Meal Recommendation App",
    }
    payload: Dict[str, Any] = {"model": model, "messages": messages}

    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
