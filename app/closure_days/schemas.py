from pydantic import BaseModel
from datetime import date

class ClosedDayOut(BaseModel):
    id: int
    day: date

class CreateClosedDayRequest(BaseModel):
    day: date
