from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class SlotCreate(BaseModel):
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")

    @field_validator("end_time")
    @classmethod
    def validate_time_order(cls, v, info):
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("Время окончания должно быть позже времени начала")
        return v

class SlotResponse(BaseModel):
    id: int
    start_time: str
    end_time: str
    class Config: from_attributes = True

class RoomCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    slots: List[SlotCreate] = []

class RoomResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    slots: List[SlotResponse] = []
    class Config: from_attributes = True

class BookingCreate(BaseModel):
    slot_id: int
    date: date

class BookingResponse(BaseModel):
    id: int
    user_id: int
    slot_id: int
    date: date
    created_at: datetime
    class Config: from_attributes = True

class BookingDetailedResponse(BookingResponse):
    username: Optional[str] = None
    room_name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None