from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from enum import Enum
from app.menus.schemas import MenuProductOut, MenuProductItem
from app.shared.schemas import PaginationQuery

class OrderStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    DONE = "done"
    CANCELLED = "cancelled"

class ProductOrderOut(BaseModel):
    id: int
    name: str
    quantity: int

class MenuOrderItem(BaseModel):
    menu_id: int
    quantity: int = Field(..., gt=0)

class MenuOrderOut(BaseModel):
    id: int
    name: str
    quantity: int
    products: list[MenuProductOut]

class UserOrderOut(BaseModel):
    id: int
    name: str

class OrderOut(BaseModel):
    id: int
    retrieval_date: datetime
    created_at: datetime
    status: OrderStatus
    user: UserOrderOut

class OrderOutDetail(BaseModel):
    id: int
    retrieval_date: datetime
    created_at: datetime
    status: OrderStatus
    total_price_cents: int
    user: UserOrderOut
    products: list[ProductOrderOut]
    menus: list[MenuOrderOut]

class OrderQuery(PaginationQuery):
    pass

class CreateOrderRequest(BaseModel):
    retrieval_date: datetime 
    user_id : int | None = None
    products: list[MenuProductItem] = Field(default_factory=list)
    menus: list[MenuOrderItem] = Field(default_factory=list) 

    @model_validator(mode="after")
    def checkAtLeastOneItem(self):
        if not self.products and not self.menus:
            raise ValueError("An order must contain at least one product or one menu")
        return self


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus