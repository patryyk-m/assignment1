from pymongo import MongoClient

from app.config import DATABASE_NAME, MONGODB_URI

_mongo_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGODB_URI)
    return _mongo_client


def get_database():
    return get_mongo_client()[DATABASE_NAME]


def close_client() -> None:
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
