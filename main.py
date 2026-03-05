import os
from datetime import date as DateType

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field, field_validator

from database import init_db
from exchange import get_rate_in_eur

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


def verify_api_key(key: str = Security(API_KEY_HEADER)):
    if not key or key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    return key


class ConvertRequest(BaseModel):
    currency: str = Field(..., description="ISO 4217 currency code, e.g. 'USD'")
    amount: float = Field(..., gt=0)
    date: DateType

    @field_validator("currency")
    @classmethod
    def currency_must_be_valid(cls, v):
        if len(v) != 3 or not v.isalpha():
            raise ValueError("Currency must be a 3-letter ISO code, e.g. 'USD'.")
        return v.upper()


class ConvertResponse(BaseModel):
    currency: str
    original_amount: float
    date: str
    rate: float
    amount_eur: float


@app.post("/convert", response_model=ConvertResponse)
async def convert(request: ConvertRequest, _: str = Depends(verify_api_key)):
    date_str = request.date.isoformat()

    try:
        rate = await get_rate_in_eur(request.currency, date_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"External API error: {e.response.status_code}")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Could not reach the exchange rate API.")

    amount_eur = round(request.amount * rate, 2)

    return ConvertResponse(
        currency=request.currency,
        original_amount=request.amount,
        date=date_str,
        rate=rate,
        amount_eur=amount_eur,
    )


@app.get("/health")
def health():
    return {"status": "ok"}