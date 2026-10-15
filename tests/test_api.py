
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_homepage_opens():
    response = client.get("/")

    assert response.status_code == 200
    assert "AI Shopping Assistant" in response.text


def test_products_endpoint():
    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == 5


def test_headphones_within_budget():
    response = client.get(
        "/shopping-assistant",
        params={"message": "headphones under 1500"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["detected_product"] == "headphones"
    assert data["max_price"] == 1500
    assert data["total_recommendations"] == 1
    assert data["recommendations"][0]["price"] <= 1500


def test_backpack_within_budget():
    response = client.get(
        "/shopping-assistant",
        params={"message": "backpack under 1000"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_recommendations"] == 1
    assert data["recommendations"][0]["name"] == "Laptop Backpack"


def test_intent_classification():
    response = client.get(
        "/predict-intent",
        params={"message": "show me all products"},
    )

    assert response.status_code == 200
    assert response.json()["predicted_intent"] == "browse_products"


def test_product_image_is_served():
    response = client.get("/images/headphones.jpg")

    assert response.status_code == 200
