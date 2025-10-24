from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Annotated, Optional
from sqlalchemy.orm import Session
import os
from sqlalchemy import or_
from service_database import get_db
from auth.model import TokenBlacklistModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status


from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bearer_scheme = HTTPBearer(
    description="Enter the raw JWT token (e.g., 'eyJ...'). The 'Authorization: Bearer' header is applied automatically."
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def bcrypt(password: str):
    """
    Hashes a given password using the Bcrypt algorithm.
    Args:
    - password: The password to hash.
    Returns:
    - The hashed password.
    """

    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    """
    Verifies a given plain password against a given hashed password.
    Args:
    - plain_password: The plain password to verify.
    - hashed_password: The hashed password to verify against.
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

def check_token_blacklist(token: str, db: Session = Depends(get_db)):
    """
    Checks if the given access token is blacklisted in the database.

    Args:
    - token: The JWT access token to check.
    - db: The database session dependency.

    Raises:
    - HTTPException (401 UNAUTHORIZED): If the token is found in the blacklist,
      indicating it is no longer usable and the user must log in again.
    
    Returns:
    - None: If the token is not blacklisted.
    """
    blacklisted_token = db.query(TokenBlacklistModel).filter(
        TokenBlacklistModel.access_token == token
    ).first()
    
    if blacklisted_token:
        # Raise an exception immediately if the token is blacklisted
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is no longer usable. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}, # Include for consistency
        )
    # Token is valid (not blacklisted)
    return None

def get_current_user(
    token_credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
    db: Session = Depends(get_db)
):
    """
    Retrieves the user ID associated with the provided JSON Web Token (JWT).
    Args:
    - token_credentials: The HTTP authorization credentials containing the JWT.
    - db: The database session.
    Returns:
    - The user ID extracted from the token payload.
    Raises HTTPException:
    - If the token is invalid, expired, or blacklisted.
    """
    
    # Extract the raw token string from the credentials object
    token = token_credentials.credentials 
    check_token_blacklist(token, db)

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