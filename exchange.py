import httpx
from database import get_cached_rate, store_rate

FRANKFURTER_URL = "https://api.frankfurter.dev/v1"


async def get_rate_in_eur(currency: str, date: str) -> float:
    if currency.upper() == "EUR":
        return 1.0

    cached = get_cached_rate(currency.upper(), date)
    if cached is not None:
        return cached

    url = f"{FRANKFURTER_URL}/{date}"
    params = {"from": currency.upper(), "to": "EUR"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    rate = data["rates"]["EUR"]
    store_rate(currency.upper(), date, rate)

    return rate