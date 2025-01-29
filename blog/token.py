from typing import Optional
from fastapi import status, HTTPException
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from . import models
#from .schemas import TokenData


SECRET_KEY = "bcdbf9c6c5a32200cd5268fc68ed133ae579f79eb140f008b886579e7db4a1b1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode  = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encode_jwt


def verify_token(token: str, credentials_exception, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        id: int = payload.get("id")

        if email is None:
            raise credentials_exception
        
        #token_data = TokenData(email=email)

    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'User with the id {id} is not available.'
        )

    return user