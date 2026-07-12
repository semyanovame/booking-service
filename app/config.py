import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://booking_user:booking_pass@db:5432/booking_db")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
APP_TITLE = "Booking Service API"
APP_DESCRIPTION = "Сервис бронирования переговорных комнат"
APP_VERSION = "1.0.0"
DEFAULT_SLOTS = [("09:00", "11:00"), ("11:00", "13:00"), ("13:00", "15:00"), ("15:00", "17:00"), ("17:00", "19:00")]