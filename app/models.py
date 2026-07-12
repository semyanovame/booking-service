from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .database import Base

class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    slots = relationship("Slot", back_populates="room", cascade="all, delete-orphan")

class Slot(Base):
    __tablename__ = "slots"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    room = relationship("Room", back_populates="slots")
    bookings = relationship("Booking", back_populates="slot", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("room_id", "start_time", "end_time", name="uq_room_slot_time"),)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    slot_id = Column(Integer, ForeignKey("slots.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="bookings")
    slot = relationship("Slot", back_populates="bookings")
    __table_args__ = (UniqueConstraint("user_id", "slot_id", "date", name="uq_user_slot_date"),)