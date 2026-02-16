import responses
from src.apis.serp import fetch_restaurants

@responses.activate
def test_fetch_restaurants_success():
    url = "https://serpapi.com/search.json"

    responses.add(
        responses.GET,
        url,
        json={
            "local_results": [
                {
                    "title": "Hotel A",
                    "rating": 4.2,
                    "address": "Street 1",
                    "price": "₹₹",
                },
                {
                    "title": "Hotel B",
                    "rating": 4.0,
                    "address": "Street 2",
                    "price": "₹",
                },
            ]
        },
        status=200,
    )

    restaurants = fetch_restaurants(
        13.0827, 80.2707,
        serpapi_key="dummy",
        diet="Any",
        limit=10
    )

    assert len(restaurants) == 2
    assert restaurants[0]["title"] == "Hotel A"
    assert restaurants[1]["title"] == "Hotel B"
