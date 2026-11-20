from fastapi import APIRouter, Depends, status, HTTPException 
from sqlmodel import Session
from app.database import get_session
from typing import Annotated
from app.menus import services
from app.menus.schemas import MenuOut, CreateMenuRequest, UpdateMenuRequest

menuRoutes = APIRouter(prefix="/menus")

@menuRoutes.get("", response_model=list[MenuOut], status_code=status.HTTP_200_OK)
def getAllMenus(session: Annotated[Session, Depends(get_session)]):
    return services.getAllMenus(session)

@menuRoutes.post("", response_model=MenuOut, status_code=status.HTTP_201_CREATED)
def createMenu(session: Annotated[Session, Depends(get_session)], payload: CreateMenuRequest):
    try:
        return services.createMenu(session, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@menuRoutes.patch("/{menu_id}", response_model=MenuOut, status_code=status.HTTP_200_OK)
def patchMenu(session: Annotated[Session, Depends(get_session)], menu_id:int, payload: UpdateMenuRequest):
    try:
        return services.updateMenu(session, menu_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))