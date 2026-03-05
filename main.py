import os
from datetime import date as DateType

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from database import init_db
from exchange import get_rate_in_eur

load_dotenv()

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


class ConvertRequest(BaseModel):
    currency: str = Field(..., description="ISO 4217 currency code, e.g. 'USD'")
    amount: float = Field(..., gt=0)
    date: DateType


class ConvertResponse(BaseModel):
    currency: str
    original_amount: float
    date: str
    rate: float
    amount_eur: float


@app.post("/convert", response_model=ConvertResponse)
async def convert(request: ConvertRequest):
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