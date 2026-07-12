from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Room, Slot, User
from ..schemas import RoomCreate, RoomResponse
from ..dependencies import get_current_user, get_admin_user

router = APIRouter(prefix="/api/rooms", tags=["Комнаты"])

@router.get("/", response_model=List[RoomResponse])
def get_rooms(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Room).all()

@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room: raise HTTPException(404, "Комната не найдена")
    return room

@router.post("/", response_model=RoomResponse, status_code=201)
def create_room(room_data: RoomCreate, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    if db.query(Room).filter(Room.name == room_data.name).first():
        raise HTTPException(400, "Комната с таким названием уже существует")
    room = Room(name=room_data.name, description=room_data.description)
    db.add(room); db.flush()
    for s in room_data.slots or [SlotCreate(start_time="09:00", end_time="11:00")]:
        db.add(Slot(room_id=room.id, start_time=s.start_time, end_time=s.end_time))
    db.commit(); db.refresh(room)
    return room

@router.delete("/{room_id}")
def delete_room(room_id: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room: raise HTTPException(404, "Комната не найдена")
    db.delete(room); db.commit()
    return {"message": f"Комната '{room.name}' удалена"}