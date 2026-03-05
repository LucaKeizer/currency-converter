# currency-converter

Converts receipt amounts to euros using historical exchange rates from [Frankfurter](https://frankfurter.dev/). Rates are cached locally in SQLite.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Add a `.env` file with:
```
API_KEY=your_key_here
```

```bash
uvicorn main:app --reload
```

## Usage

Send a `POST` request to `http://localhost:8000/convert` with the `X-API-Key` header and a JSON body:

```json
{
  "currency": "USD",
  "amount": 149.99,
  "date": "2024-03-15"
}
```

Response:
```json
{
  "currency": "USD",
  "original_amount": 149.99,
  "date": "2024-03-15",
  "rate": 0.9187,
  "amount_eur": 137.80
}
```