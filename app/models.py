from datetime import date, datetime
from pydantic import NaiveDatetime
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=32)
    role: str = "user"          #'user' | 'admin'
    status: str = "active"      #'active' | 'blocked'
    password: str


class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    is_deleted: bool = False
    stock: int = 0
    price_cents: int


class Menu(SQLModel, table=True):
    __tablename__ = "menus"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    is_available: bool = True
    is_deleted: bool = False
    starting_date: NaiveDatetime
    ending_date: NaiveDatetime
    price_cents: int


class MenuProduct(SQLModel, table=True):
    __tablename__ = "menu_products"
    menu_id: int = Field(foreign_key="menus.id", primary_key=True)
    product_id: int = Field(foreign_key="products.id", primary_key=True)
    quantity: int = 1


class ClosedDay(SQLModel, table=True):
    __tablename__ = "closed_days"
    id: int | None = Field(default=None, primary_key=True)
    day: date


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    created_at: NaiveDatetime = Field(default_factory=datetime.now)
    retrieval_date: NaiveDatetime
    status: str = "pending"     #'pending' | 'ready'


class OrderProduct(SQLModel, table=True):
    __tablename__ = "order_products"
    order_id: int = Field(foreign_key="orders.id", primary_key=True)
    product_id: int = Field(foreign_key="products.id", primary_key=True)
    quantity: int = 1


class OrderMenu(SQLModel, table=True):
    __tablename__ = "order_menus"
    order_id: int = Field(foreign_key="orders.id", primary_key=True)
    menu_id: int = Field(foreign_key="menus.id", primary_key=True)
    quantity: int = 1
