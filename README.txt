Inventory API - README (auto-generated)
============================================

FastAPI documentation: https://fastapi.tiangolo.com/

API endpoints and parameters
----------------------------

GET /health
  no parameters

GET /metrics
  no parameters

GET /getSingleProduct
  product_id (integer, query)

GET /getAll
  no parameters

POST /addNew
  JSON body: ProductID, Name, UnitPrice, StockQuantity, Description (all required)

DELETE /deleteOne
  product_id (integer, query)

GET /startsWith
  letter (single character, query)

GET /paginate
  start_id (integer, query), end_id (integer, query)

GET /convert
  product_id (integer, query)
