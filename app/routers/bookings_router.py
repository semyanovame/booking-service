from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List
from ..database import get_db
from ..models import Booking, Slot, Room, User, UserRole
from ..schemas import BookingCreate, BookingResponse, BookingDetailedResponse
from ..dependencies import get_current_user, get_admin_user

router = APIRouter(prefix="/api/bookings", tags=["Бронирования"])

@router.get("/slots/{room_id}")
def get_free_slots(room_id: int, booking_date: date = Query(...), db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room: raise HTTPException(404, "Комната не найдена")
    dt = datetime.combine(booking_date, datetime.min.time())
    booked = {b.slot_id for b in db.query(Booking).filter(Booking.date == dt, Booking.slot_id.in_([s.id for s in room.slots])).all()}
    return {"room_id": room.id, "room_name": room.name, "date": booking_date.isoformat(),
            "slots": [{"slot_id": s.id, "start_time": s.start_time, "end_time": s.end_time, "available": s.id not in booked} for s in room.slots]}

@router.get("/", response_model=List[BookingDetailedResponse])
def get_my_bookings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _detailed(db.query(Booking).filter(Booking.user_id == current_user.id).all(), current_user)

@router.get("/all", response_model=List[BookingDetailedResponse])
def get_all_bookings(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    return _detailed(db.query(Booking).all())

@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(data: BookingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    slot = db.query(Slot).filter(Slot.id == data.slot_id).first()
    if not slot: raise HTTPException(404, "Слот не найден")
    bd = datetime.combine(data.date, datetime.min.time())
    if bd < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
        raise HTTPException(400, "Нельзя забронировать прошедшую дату")
    if db.query(Booking).filter(Booking.slot_id == data.slot_id, Booking.date == bd).first():
        raise HTTPException(409, "Слот занят")
    b = Booking(user_id=current_user.id, slot_id=data.slot_id, date=bd)
    db.add(b); db.commit(); db.refresh(b)
    return b

@router.delete("/{booking_id}")
def cancel_booking(booking_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b: raise HTTPException(404, "Бронь не найдена")
    if b.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "Нельзя отменить чужую бронь")
    db.delete(b); db.commit()
    return {"message": "Бронирование отменено"}

def _detailed(bookings, user=None):
    result = []
    for b in bookings:
        slot = b.slot
        room = slot.room if slot else None
        u = b.user
        result.append({
            "id": b.id,
            "user_id": b.user_id,
            "slot_id": b.slot_id,
            "date": b.date.isoformat()[:10] if hasattr(b.date, 'isoformat') else str(b.date)[:10],
            "created_at": str(b.created_at),
            "username": u.username if u else None,
            "room_name": room.name if room else None,
            "start_time": slot.start_time if slot else None,
            "end_time": slot.end_time if slot else None
        })
    return result