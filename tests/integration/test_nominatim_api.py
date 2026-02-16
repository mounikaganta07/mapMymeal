import responses
from src.apis.nominatim import geocode_location

@responses.activate
def test_geocode_location_success():
    # 1) We intercept the Nominatim API URL
    url = "https://nominatim.openstreetmap.org/search"

    # 2) We return a fake response (mock)
    responses.add(
        responses.GET,
        url,
        json=[{"lat": "13.0827", "lon": "80.2707"}],
        status=200,
    )

    # 3) Call your real function (but it receives the fake response)
    lat, lon = geocode_location("Chennai")

    # 4) Check output is correct
    assert float(lat) == 13.0827
    assert float(lon) == 80.2707
