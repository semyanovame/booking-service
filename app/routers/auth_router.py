from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import Token
from ..auth import verify_password, create_access_token, get_password_hash

router = APIRouter(prefix="/api/auth", tags=["Аутентификация"])

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    token = create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role.value})
    return Token(access_token=token)

@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    user = User(username=username, hashed_password=get_password_hash(password), role="employee")
    db.add(user); db.commit(); db.refresh(user)
    return {"message": "Пользователь зарегистрирован", "user_id": user.id}