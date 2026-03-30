import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "products.csv"
JSON_PATH = ROOT / "products.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import DATABASE_NAME, MONGODB_URI, PRODUCTS_COLLECTION

from pymongo import MongoClient


def main() -> None:
    if not CSV_PATH.is_file():
        print(f"Missing {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    rows: list[dict] = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "ProductID": int(row["ProductID"]),
                    "Name": row["Name"],
                    "UnitPrice": float(row["UnitPrice"]),
                    "StockQuantity": int(row["StockQuantity"]),
                    "Description": row["Description"],
                }
            )

    with JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"Wrote {len(rows)} products to {JSON_PATH}")

    client = MongoClient(MONGODB_URI)
    coll = client[DATABASE_NAME][PRODUCTS_COLLECTION]
    coll.delete_many({})
    if rows:
        coll.insert_many(rows)
    print(f"Inserted {len(rows)} documents into {DATABASE_NAME}.{PRODUCTS_COLLECTION}")


if __name__ == "__main__":
    main()
