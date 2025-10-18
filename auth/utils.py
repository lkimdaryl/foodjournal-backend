from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Annotated, Optional
from sqlalchemy.orm import Session
import os
from sqlalchemy import or_
from service_database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "ef1ebfdd60c45c7f3ed13196999b43d8df60409c3b6ca2ac428b886cbc82beed"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def bcrypt(password: str):
    """
    Hashes a given password using the Bcrypt algorithm.
    Args:
    - password (str): The password to hash.
    Returns:
    - The hashed password.
    """

    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    """
    Verifies a given plain password against a given hashed password.
    Args:
    - plain_password (str): The plain password to verify.
    - hashed_password (str): The hashed password to verify against.
    Returns:
    - True or False depending on whether the plain password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a JSON Web Token (JWT) encoded with the provided data and expiration time.
    Args:
    - data (dict): The data to include in the token payload.
    - expires_delta (Optional[timedelta]): The time duration after which the token will expire. 
        If not provided, defaults to 24 hours.
    Returns:
    - The encoded JWT as a string.
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Cookie(None), 
                     db: Session = Depends(get_db)):
    """
    Retrieves the user ID associated with the provided JSON Web Token (JWT).
    Args:
    - token (str): The JWT to validate and extract the user ID from.
    - db (Session): The database session to query the user from.
    Returns:
    - The ID of the user associated with the JWT.
    Raises:
    - HTTPException: If the JWT is invalid or the associated user could not be found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("email")
        if username is None:
            raise credentials_exception
        return payload.get("user_id")
    except Exception as e:
        raise credentials_exception
