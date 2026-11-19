from fastapi import APIRouter, Query, Depends, status, HTTPException 
from sqlmodel import Session
from app.database import get_session
from typing import Annotated
from app.products import services
from app.shared.schemas import PaginatedResponse
from app.products.schemas import ProductOut, GetProductsQuery, CreateProductRequest, UpdateProductRequest

productRoutes = APIRouter(prefix="/products")

@productRoutes.get("", response_model=PaginatedResponse[ProductOut], status_code=status.HTTP_200_OK)
def getProducts(session: Annotated[Session, Depends(get_session)], query: Annotated[GetProductsQuery, Query()]):
    return services.getAllProducts(session, query.limit, query.offset)

@productRoutes.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def createProduct(session: Annotated[Session, Depends(get_session)], payload: CreateProductRequest):
    try:
        return services.createProduct(session, payload.name, payload.price_cents, payload.stock)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@productRoutes.patch("/{product_id}", response_model=ProductOut, status_code=status.HTTP_200_OK)
def modifyProduct(session: Annotated[Session, Depends(get_session)], product_id: int, payload: UpdateProductRequest):
    try:
        return services.patchProduct(session, product_id, payload.name, payload.price_cents, payload.stock_change)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@productRoutes.delete("/{product_id}", response_model=None,status_code=status.HTTP_204_NO_CONTENT)
def deleteProduct(session: Annotated[Session, Depends(get_session)], product_id: int):
    try:
        return services.softDeleteProduct(session, product_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@productRoutes.patch("/{product_id}/restore", response_model=ProductOut, status_code=status.HTTP_200_OK)
def restoreProduct(session: Annotated[Session, Depends(get_session)], product_id: int):
    try:
        return services.restoreProduct(session, product_id)
    except LookupError as e:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))