from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_metrics():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert len(r.content) > 0


def test_get_single_product():
    r = client.get("/getSingleProduct", params={"product_id": 9001})
    assert r.status_code == 200
    data = r.json()
    assert data["ProductID"] == 9001
    assert "Samsung" in data["Name"]


def test_get_single_product_not_found():
    r = client.get("/getSingleProduct", params={"product_id": 1})
    assert r.status_code == 404


def test_get_single_product_invalid():
    r = client.get("/getSingleProduct", params={"product_id": -1})
    assert r.status_code == 422


def test_get_all():
    r = client.get("/getAll")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 3


def test_add_new_and_delete():
    body = {
        "ProductID": 99999,
        "Name": "New Test Item",
        "UnitPrice": 49.99,
        "StockQuantity": 3,
        "Description": "Created by test.",
    }
    r = client.post("/addNew", json=body)
    assert r.status_code == 201
    assert r.json()["ProductID"] == 99999
    d = client.delete("/deleteOne", params={"product_id": 99999})
    assert d.status_code == 200
    assert d.json()["deleted"] is True


def test_delete_one_standalone():
    client.post(
        "/addNew",
        json={
            "ProductID": 99998,
            "Name": "To Delete",
            "UnitPrice": 1.0,
            "StockQuantity": 1,
            "Description": "x",
        },
    )
    r = client.delete("/deleteOne", params={"product_id": 99998})
    assert r.status_code == 200


def test_starts_with():
    r = client.get("/startsWith", params={"letter": "s"})
    assert r.status_code == 200
    names = [p["Name"] for p in r.json()]
    assert any(n.lower().startswith("s") for n in names)


def test_paginate():
    r = client.get("/paginate", params={"start_id": 9001, "end_id": 9100})
    assert r.status_code == 200
    assert len(r.json()) <= 10


def test_paginate_invalid_range():
    r = client.get("/paginate", params={"start_id": 100, "end_id": 50})
    assert r.status_code == 422


def test_convert():
    """Uses live Frankfurter API (needs outbound HTTPS in CI)."""
    r = client.get("/convert", params={"product_id": 9001})
    assert r.status_code == 200
    data = r.json()
    assert data["ProductID"] == 9001
    assert "UnitPriceEUR" in data
    assert data["UnitPriceUSD"] == 99.99
