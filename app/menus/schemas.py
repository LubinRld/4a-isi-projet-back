from pydantic import BaseModel, Field
from datetime import datetime

class MenuProductOut(BaseModel):
    product_id:int
    name: str
    quantity: int

class MenuOut(BaseModel):
    id: int
    name: str
    price_cents: int
    is_available:bool
    starting_date: datetime | None
    ending_date: datetime | None
    products: list[MenuProductOut]

class MenuProductItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class CreateMenuRequest(BaseModel):
    name: str = Field(..., min_length=1)
    price_cents:int = Field(..., gt=0)
    is_available:bool = True
    starting_date: datetime | None = None
    ending_date: datetime | None = None
    products: list[MenuProductItem] = Field(..., min_length=1)


class UpdateMenuRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    price_cents: int| None = Field(default=None, gt=0)
    is_available: bool| None = None
    starting_date: datetime| None = None
    ending_date: datetime| None = None
    products: list[MenuProductItem]| None = Field(default=None, min_length=1)
