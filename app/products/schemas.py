from pydantic import BaseModel, Field
from app.shared.schemas import PaginationQuery


class ProductOut(BaseModel):
    id: int
    name: str
    stock: int
    price_cents: int
    is_deleted: bool

class GetProductsQuery(PaginationQuery):
    pass

class CreateProductRequest(BaseModel):
    name: str = Field(..., min_length=1)
    price_cents: int = Field(...,gt=0)
    stock: int = Field(default=0, ge=0) 

class UpdateProductRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    price_cents: int | None = Field(default=None, gt=0)
    stock_change: int | None = None



