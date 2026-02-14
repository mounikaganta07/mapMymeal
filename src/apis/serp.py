import requests
from typing import Any, Dict, List


def fetch_restaurants(
    lat: float,
    lon: float,
    serpapi_key: str,
    diet: str = "Any",
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if diet == "Vegetarian":
        query = "vegetarian restaurants"
    elif diet == "Vegan":
        query = "vegan restaurants"
    elif diet == "Non-Vegetarian":
        query = "non-veg restaurants"
    else:
        query = "restaurants"

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_maps",
        "q": query,
        "google_domain": "google.com",
        "hl": "en",
        "api_key": serpapi_key,
        "ll": f"@{lat},{lon},14z",
    }

    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("local_results", [])
    return results[:limit]


def extract_menus(restaurants: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    menus: Dict[str, List[str]] = {}
    for r in restaurants:
        name = r.get("title", "Unknown")
        menu_items: List[str] = []

        if "menu" in r and isinstance(r["menu"], list):
            menu_items = [item.get("name") for item in r["menu"] if isinstance(item, dict) and "name" in item]
        elif "menu_items" in r and isinstance(r["menu_items"], list):
            menu_items = [item.get("name") for item in r["menu_items"] if isinstance(item, dict) and "name" in item]

        menus[name] = menu_items[:20]

    return menus
