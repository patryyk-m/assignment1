import os

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")

import mongomock
import pytest

from app.config import PRODUCTS_COLLECTION
from app.db import get_database, reset_mongo_client, set_mongo_client_for_tests


@pytest.fixture(scope="module", autouse=True)
def seed_products():
    set_mongo_client_for_tests(mongomock.MongoClient())
    coll = get_database()[PRODUCTS_COLLECTION]
    coll.delete_many({})
    coll.insert_many(
        [
            {
                "ProductID": 9001,
                "Name": "Samsung Test SSD",
                "UnitPrice": 99.99,
                "StockQuantity": 10,
                "Description": "Test product for unit tests.",
            },
            {
                "ProductID": 9002,
                "Name": "Sony Test Monitor",
                "UnitPrice": 199.0,
                "StockQuantity": 5,
                "Description": "Another test product.",
            },
            {
                "ProductID": 9100,
                "Name": "Zebra Cable",
                "UnitPrice": 12.5,
                "StockQuantity": 100,
                "Description": "Starts with Z.",
            },
        ]
    )
    yield
    coll.delete_many({})
    reset_mongo_client()
