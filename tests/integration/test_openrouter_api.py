import responses
from src.apis.openrouter import chat_completions

@responses.activate
def test_openrouter_chat_success():
    url = "https://openrouter.ai/api/v1/chat/completions"

    responses.add(
        responses.POST,
        url,
        json={
            "choices": [
                {
                    "message": {
                        "content": (
                            "🍲 Breakfast: Idli at X (~₹80)\n"
                            "🍛 Lunch: Veg thali at Y (~₹180)\n"
                            "🥪 Snacks: Tea & samosa at Z (~₹60)\n"
                            "🥗 Dinner: Dosa at A (~₹150)"
                        )
                    }
                }
            ]
        },
        status=200,
    )

    data = chat_completions(
        openrouter_api_key="dummy",
        model="inflection/inflection-3-pi",
        messages=[{"role": "user", "content": "hi"}],
        timeout=10,
    )

    assert "choices" in data
    assert "Breakfast" in data["choices"][0]["message"]["content"]
