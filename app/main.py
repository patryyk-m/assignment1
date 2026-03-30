import httpx
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import ValidationError

from app.config import PRODUCTS_COLLECTION
from app.db import close_client, get_database
from app.models import (
    ConvertQuery,
    DeleteOneQuery,
    PaginateQuery,
    ProductCreate,
    ProductOut,
    SingleProductQuery,
    StartsWithQuery,
)

FRANKFURTER_URL = "https://api.frankfurter.app/latest"


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_client()


app = FastAPI(
    title="Inventory API",
    description="MongoDB + FastAPI inventory management (Assignment 1)",
    version="1.0.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)


@app.get("/health")
def health():
    """Simple liveness check for monitoring."""
    return {"status": "ok"}


@app.get("/getSingleProduct", response_model=ProductOut)
def get_single_product(
    product_id: int = Query(..., gt=0, description="Product ID to fetch"),
):
    try:
        SingleProductQuery(product_id=product_id)
    except ValidationError as e:
        raise RequestValidationError(e.errors()) from e

    db = get_database()
    doc = db[PRODUCTS_COLLECTION].find_one({"ProductID": product_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    doc.pop("_id", None)
    return ProductOut(**doc)


@app.get("/getAll", response_model=list[ProductOut])
def get_all():
    db = get_database()
    cursor = db[PRODUCTS_COLLECTION].find().sort("ProductID", 1)
    out: list[dict[str, Any]] = []
    for doc in cursor:
        doc.pop("_id", None)
        out.append(doc)
    return [ProductOut(**d) for d in out]


@app.post("/addNew", response_model=ProductOut, status_code=201)
def add_new(item: ProductCreate):
    db = get_database()
    coll = db[PRODUCTS_COLLECTION]
    existing = coll.find_one({"ProductID": item.ProductID})
    if existing:
        raise HTTPException(status_code=409, detail="ProductID already exists")
    payload = item.model_dump()
    coll.insert_one(payload)
    return ProductOut(**payload)


@app.delete("/deleteOne")
def delete_one(
    product_id: int = Query(..., gt=0, description="Product ID to delete"),
):
    try:
        DeleteOneQuery(product_id=product_id)
    except ValidationError as e:
        raise RequestValidationError(e.errors()) from e

    db = get_database()
    result = db[PRODUCTS_COLLECTION].delete_one({"ProductID": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return JSONResponse(content={"deleted": True, "ProductID": product_id})


@app.get("/startsWith", response_model=list[ProductOut])
def starts_with(
    letter: str = Query(..., min_length=1, max_length=1, description="First letter of product name"),
):
    try:
        q = StartsWithQuery(letter=letter)
    except ValidationError as e:
        raise RequestValidationError(e.errors()) from e

    prefix = q.letter
    db = get_database()
    cursor = db[PRODUCTS_COLLECTION].find(
        {"Name": {"$regex": f"^{prefix}", "$options": "i"}},
    ).sort("ProductID", 1)
    out: list[dict[str, Any]] = []
    for doc in cursor:
        doc.pop("_id", None)
        out.append(doc)
    return [ProductOut(**d) for d in out]


@app.get("/paginate", response_model=list[ProductOut])
def paginate(
    start_id: int = Query(..., gt=0),
    end_id: int = Query(..., gt=0),
):
    try:
        PaginateQuery(start_id=start_id, end_id=end_id)
    except ValidationError as e:
        raise RequestValidationError(e.errors()) from e

    db = get_database()
    cursor = (
        db[PRODUCTS_COLLECTION]
        .find({"ProductID": {"$gte": start_id, "$lte": end_id}})
        .sort("ProductID", 1)
        .limit(10)
    )
    out: list[dict[str, Any]] = []
    for doc in cursor:
        doc.pop("_id", None)
        out.append(doc)
    return [ProductOut(**d) for d in out]


@app.get("/convert")
def convert(
    product_id: int = Query(..., gt=0, description="Product ID (USD price converted to EUR)"),
):
    try:
        ConvertQuery(product_id=product_id)
    except ValidationError as e:
        raise RequestValidationError(e.errors()) from e

    db = get_database()
    doc = db[PRODUCTS_COLLECTION].find_one({"ProductID": product_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")

    usd = float(doc["UnitPrice"])
    with httpx.Client(timeout=15.0) as client:
        r = client.get(
            FRANKFURTER_URL,
            params={"from": "USD", "to": "EUR"},
        )
        if r.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Could not fetch exchange rate from Frankfurter API",
            )
        data = r.json()
    rate = float(data["rates"]["EUR"])
    eur = usd * rate
    return {
        "ProductID": product_id,
        "UnitPriceUSD": usd,
        "UnitPriceEUR": round(eur, 2),
        "rate_source": "Frankfurter (ECB)",
        "api": FRANKFURTER_URL,
    }
