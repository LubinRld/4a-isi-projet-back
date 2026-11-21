from fastapi import APIRouter, Query, Depends, status, HTTPException 
from sqlmodel import Session
from app.database import get_session
from app.orders import services
from typing import Annotated
from app.shared.schemas import PaginatedResponse
from app.orders.schemas import OrderOut, OrderOutDetail, OrderQuery, CreateOrderRequest, UpdateOrderStatusRequest

orderRoutes = APIRouter(prefix="/orders")

@orderRoutes.get("/{order_id}", response_model=OrderOutDetail, status_code=status.HTTP_200_OK)
def getOrderById(session: Annotated[Session, Depends(get_session)], order_id:int):
    try:
        return services.getOrderById(session, order_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@orderRoutes.get("", response_model=PaginatedResponse[OrderOut], status_code=status.HTTP_200_OK)
def getAllOrders(session: Annotated[Session, Depends(get_session)], query: Annotated[OrderQuery, Query()]):
    return services.getAllOrders(session, query.limit, query.offset)

@orderRoutes.post("", response_model=OrderOutDetail, status_code=status.HTTP_201_CREATED)
def postOrder(session: Annotated[Session, Depends(get_session)], payload: CreateOrderRequest):
    try:
        return services.createOrder(session, payload)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@orderRoutes.patch("/{order_id}", response_model=OrderOutDetail, status_code=status.HTTP_200_OK)
def patchOrder(session: Annotated[Session, Depends(get_session)], order_id:int, payload: UpdateOrderStatusRequest):
    try:
        return services.updateOrderStatus(session, order_id, payload.status)
    except LookupError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        