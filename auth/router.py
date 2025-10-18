import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Cookie
import schemas as _schemas
import sqlalchemy.orm as _orm
from sqlalchemy.orm.session import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
import auth.service as _service
from auth.model import UserModel #, VisitorModel
from service_database import get_db

router_auth = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"]
)

@router_auth.post("/create_user")
async def create_user(user: _schemas.UserBase, db: Session = Depends(get_db)):
    """
    Create a new user in the database.

    Args:       
    - user: The user information to create.       
    - db: The database session.     

    Returns:    
    - A dictionary indicating whether the user was successfully created.

    Raises HTTPException:    
    - If the email already exists in the database.
    - If the email address is invalid.
    - If the username already exists in the database.
    - If an error occurs while creating the user.
    """
    return await _service.create_user(user, db)  

@router_auth.post("/login")
async def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint for user login.    

    This endpoint receives a JSON string with user information and authenticates the user.
    It expects a POST request with the following JSON payload:      
    - {     
        "username": "string",   
        "password": "string"    
    }

    Args:
    - request (OAuth2PasswordRequestForm): The request object containing user credentials.
    - db (Session): The database session.

    Returns:
    - A dictionary containing the user's access token, token type, user ID, and email upon successful authentication.
    
    Raises HTTPException:
    - If email or username is invalid or does not exist in the database. 
    - If password is invalid.
    """
    return await _service.login(request, db)

@router_auth.patch("/update_user")
async def update_user(request: _schemas.UpdateUserBase, access_token: str=Cookie(None), db: Session = Depends(get_db)):
    """
    Updates a user's information in the database.

    Args:
    - request (json): The updated user information.
    - accessToken (str): The user's access token.
    -db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    - A dictionary with a message indicating the success of the update.

    Raises HTTPException:
    - If there are no fields to update.
    - If the email provided already exists in the database.
    - If the email address is invalid.
    - If the username provided already exists in the database.
    - If user does not exist in the database.
    - If an error occurs while updating the user.
    """
    return await _service.update_user(request, access_token, db)

@router_auth.get("/get_user")
async def get_user(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    """
    Get the user information from the database based on the provided access token.

    Args:
    - accessToken (str): The access token used to authenticate the user.
    - db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    - The user information from the database associated with the provided access token.
    """
    print("Received token:", access_token)
    return await _service.get_user_by_access_token(access_token, db)

@router_auth.post("/logout")
async def logout(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    """
    Logs out the user by invalidating their access token.

    Args:
    - accessToken (str): The access token used to authenticate the user.
         
    Returns:
    - A dictionary with a message indicating that the access token was invalidated.
    """
    return await _service.logout(access_token, db)
