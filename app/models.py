from pydantic import BaseModel, Field, field_validator, model_validator


class ProductCreate(BaseModel):
    """All five attributes for /addNew."""

    ProductID: int = Field(..., gt=0, description="Unique product identifier")
    Name: str = Field(..., min_length=1, max_length=500)
    UnitPrice: float = Field(..., ge=0)
    StockQuantity: int = Field(..., ge=0)
    Description: str = Field(..., min_length=1, max_length=2000)


class ProductOut(BaseModel):
    ProductID: int
    Name: str
    UnitPrice: float
    StockQuantity: int
    Description: str


class SingleProductQuery(BaseModel):
    product_id: int = Field(..., gt=0)


class DeleteOneQuery(BaseModel):
    product_id: int = Field(..., gt=0)


class StartsWithQuery(BaseModel):
    letter: str = Field(..., min_length=1, max_length=1)

    @field_validator("letter")
    @classmethod
    def one_letter(cls, v: str) -> str:
        return v.strip().lower()


class PaginateQuery(BaseModel):
    start_id: int = Field(..., gt=0, description="Product ID to start from (inclusive)")
    end_id: int = Field(..., gt=0, description="Product ID to end at (inclusive)")

    @model_validator(mode="after")
    def end_after_start(self):
        if self.end_id < self.start_id:
            raise ValueError("end_id must be >= start_id")
        return self


class ConvertQuery(BaseModel):
    product_id: int = Field(..., gt=0)
