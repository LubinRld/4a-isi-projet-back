from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T") #déclare type générique abstrait

class PaginationQuery(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class PaginatedResponse(BaseModel, Generic[T]):
    total:int
    limit:int
    offset:int
    data: list[T]