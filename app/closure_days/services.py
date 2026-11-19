from sqlmodel import Session, select
from datetime import date
from app.models import ClosedDay

def getAllClosedDays(session: Session):
    closedDays = session.exec(select(ClosedDay).order_by(ClosedDay.day)).all()
    return closedDays

def createClosedDay(session: Session, day: date):
    existing = session.exec(select(ClosedDay).where(ClosedDay.day == day)).first()
    if existing is not None:
        raise ValueError("This day is already marked as close")

    if day<date.today():
        raise ValueError("Cannot close a date in the past")

    closedDay = ClosedDay(day=day)
    session.add(closedDay)
    session.commit()
    session.refresh(closedDay)

    return closedDay

def deletedClosedDay(session: Session, closedDayId: int):
    closedDay = session.get(ClosedDay, closedDayId)
    if closedDay is  None:
        raise LookupError("Closure day not found")

    session.delete(closedDay)
    session.commit()