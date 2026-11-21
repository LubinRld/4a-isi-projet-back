from fastapi import APIRouter, Query, Depends, status, HTTPException 
from sqlmodel import Session
from app.database import get_session
from app.orders import services
from typing import Annotated
from app.models import User
from app.users.schemas import UserRole
from app.auth.dependencies import getCurrentUser
from app.shared.schemas import PaginatedResponse
from app.orders.schemas import OrderOut, OrderOutDetail, OrderQuery, CreateOrderRequest, UpdateOrderStatusRequest

orderRoutes = APIRouter(prefix="/orders")

@orderRoutes.get("/{order_id}", response_model=OrderOutDetail, status_code=status.HTTP_200_OK)
def getOrderById(
    session: Annotated[Session, Depends(get_session)], 
    order_id:int,
    currentUser: Annotated[User, Depends(getCurrentUser)]):
    try:
        orderDetail = services.getOrderById(session, order_id)
        if currentUser.role!= UserRole.ADMIN.value and orderDetail.user.id != currentUser.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this order")
        return orderDetail
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@orderRoutes.get("", response_model=PaginatedResponse[OrderOut], status_code=status.HTTP_200_OK)
def getAllOrders(
    session: Annotated[Session, Depends(get_session)], 
    query: Annotated[OrderQuery, Query()],
    currentUser: Annotated[User, Depends(getCurrentUser)]):
    userIdFilter = None if currentUser.role == UserRole.ADMIN.value else currentUser.id
    return services.getAllOrders(session, query.limit, query.offset, userId=userIdFilter)

@orderRoutes.post("", response_model=OrderOutDetail, status_code=status.HTTP_201_CREATED)
def postOrder(
    session: Annotated[Session, Depends(get_session)], 
    payload: CreateOrderRequest,
    currentUser: Annotated[User, Depends(getCurrentUser)]):
    if currentUser.role == UserRole.ADMIN.value:
        targetUserId = payload.user_id if payload.user_id is not None else currentUser.id
    else:
        if payload.user_id is not None and payload.user_id != currentUser.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only create your own orders")
        targetUserId = currentUser.id
    try:
        return services.createOrder(session, payload, userId= targetUserId)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@orderRoutes.patch("/{order_id}", response_model=OrderOutDetail, status_code=status.HTTP_200_OK)
def patchOrder(
    session: Annotated[Session, Depends(get_session)], 
    order_id:int,
    payload: UpdateOrderStatusRequest,
    currentUser: Annotated[User, Depends(getCurrentUser)]):
    try:
        return services.updateOrderStatus(session, order_id, payload.status, currentUser)
    except LookupError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        