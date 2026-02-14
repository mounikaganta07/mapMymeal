import requests
from typing import Optional, Tuple


def geocode_location(query: str) -> Optional[Tuple[float, float]]:
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "meal-recommendation-app (educational use)"}
    params = {"format": "json", "q": query}

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if not data:
        return None

    return float(data[0]["lat"]), float(data[0]["lon"])
