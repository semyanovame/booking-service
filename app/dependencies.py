from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User, UserRole
from .auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
        user_id: int = payload.get("sub")
        if user_id is None: raise HTTPException(status_code=401)
    except:
        raise HTTPException(status_code=401)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None: raise HTTPException(status_code=401)
    return user

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return current_user