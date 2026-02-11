from pydantic import BaseModel

class ProductCreate(BaseModel):
    title: str
    model: str | None = None
    price: float

class ProductUpdate(BaseModel):
    title: str | None = None
    model: str | None = None
    price: float | None = None