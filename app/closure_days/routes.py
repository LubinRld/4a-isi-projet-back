from fastapi import APIRouter, Depends, status, HTTPException 
from typing import Annotated
from sqlmodel import Session
from app.database import get_session
from app.closure_days import services
from app.auth.dependencies import requireAdmin
from app.closure_days.schemas import ClosedDayOut, CreateClosedDayRequest

closureDaysRoutes = APIRouter(prefix="/closures")


@closureDaysRoutes.get("", response_model=list[ClosedDayOut], status_code=status.HTTP_200_OK)
def getAllClosures(session: Annotated[Session, Depends(get_session)]):
    return services.getAllClosedDays(session)

@closureDaysRoutes.post("", response_model=ClosedDayOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(requireAdmin)])
def createClosure(session: Annotated[Session, Depends(get_session)], 
                  payload: CreateClosedDayRequest):
    try:
        return services.createClosedDay(session, payload.day)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@closureDaysRoutes.delete("/{closure_day_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(requireAdmin)])
def deleteClosureDay(session: Annotated[Session, Depends(get_session)], 
                     closure_day_id: int):
    try:
        return services.deletedClosedDay(session, closure_day_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))