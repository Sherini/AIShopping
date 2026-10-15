
from pathlib import Path
from backend.product_sources import search_and_compare

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.products import products
from backend.assistant import (
    understand_request,
    recommend_from_request,
    predict_intent,
)

app = FastAPI(
    title="AI Shopping Assistant",
    description="Our own intelligent shopping assistant",
    version="1.0.0",
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
IMAGES_DIR = FRONTEND_DIR / "images"
FRONTEND_FILE = FRONTEND_DIR / "index.html"

# Serve local product photographs at /images/filename.jpg
app.mount(
    "/images",
    StaticFiles(directory=str(IMAGES_DIR)),
    name="images",
)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(FRONTEND_FILE)


@app.get("/products")
def get_products():
    return products


@app.get("/search")
def search_products(q: str):
    results = [
        product for product in products
        if (
            q.lower() in product["name"].lower()
            or q.lower() in product["category"].lower()
            or q.lower() in product["description"].lower()
        )
    ]

    return {
        "query": q,
        "total_results": len(results),
        "products": results,
    }


@app.get("/recommend")
def recommend_products(q: str, max_price: float = None):
    results = [
        product for product in products
        if (
            (
                q.lower() in product["name"].lower()
                or q.lower() in product["category"].lower()
                or q.lower() in product["description"].lower()
            )
            and (
                max_price is None
                or product["price"] <= max_price
            )
        )
    ]

    return {
        "query": q,
        "max_price": max_price,
        "total_results": len(results),
        "recommended_products": results,
    }


@app.get("/understand")
def understand_shopping_request(message: str):
    return understand_request(message)


@app.get("/shopping-assistant")
def shopping_assistant(message: str):
    return recommend_from_request(message)


@app.get("/predict-intent")
def predict_shopping_intent(message: str):
    return predict_intent(message)

@app.get("/compare")
def compare_shopping_products(message: str):
    return search_and_compare(message)
