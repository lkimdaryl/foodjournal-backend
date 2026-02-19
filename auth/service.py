from auth.model import UserModel, TokenBlacklistModel
from auth.utils import verify, create_access_token
from fastapi import HTTPException, status
from email_validator import validate_email, EmailNotValidError
from auth.utils import bcrypt
from sqlalchemy import or_, update
from datetime import timedelta
import sqlalchemy.orm as _orm
import schemas as _schemas

def email_exists(db: _orm.Session, email: str):
    """
    Check if a given email already exists in the database.
    Args:
    - db: Database session
    - email: Email address to check
    Returns: 
    -True if the email already exists, False otherwise
    """
    rslt = db.query(UserModel).filter(UserModel.email == email).first()
    return True if rslt is not None else False

def is_login(db: _orm.Session, email: str):
    """
    Check if a given email is logged in by querying the database.
    Args:
    - db: Database session
    - email: Email address to check
    Returns: 
    - True if the email is logged in, False otherwise
    """
    rslt = db.query(UserModel).filter(UserModel.email == email).first()
    return True if rslt is not None else False


async def create_user(user, db: _orm.Session):
    """ 
    Create a new user in the database, also check
    if user fields such as email already exist
    Args:
    - db: Database engine, will be converted to session
    - user: User information to create, should be a dict
    Returns: 
    - Created user. If an error is raised, return None
    """
    if (email_exists(db, user.email)):
        raise HTTPException(status_code=400, detail=f"Email {user.email} already exists")
    try:
        validate_email(user.email, check_deliverability=False)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email address")
    if (user_exists(user.username, db)):
        raise HTTPException(status_code=400, detail=f"User {user.username} already exists")

    try:
        hash = bcrypt(user.password)
        user_obj = UserModel( first_name=user.first_name, 
                            last_name=user.last_name,
                            username=user.username, 
                            password=hash, 
                            email=user.email,
                            profile_picture=user.profile_picture )
        db.add(user_obj)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"User could not be added: {e}")

    return {"user": user}

async def login(request, db: _orm.Session):
    """
    Authenticate a user based on the provided request and database session.
    Args:
    - request: Request object containing user credentials
    - db: Database session
    Returns: 
    - User access token and information upon successful authentication
    """
    # grabs information in regards to user per request
    user = db.query(UserModel).filter(
        or_(
            UserModel.username == request.username,
            UserModel.email == request.username
        )
    ).first()
    # return unauth if no user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or username, try again."
        )
    # case for inputting a wrong password
    if not verify(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password, try again."
        )
    access_token = create_access_token(
        data={
            "email": user.email,
            "user_id": str(user.id)
        },
        expires_delta=timedelta(hours=24)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "profile_picture": user.profile_picture,
    }

async def get_user_by_id(user_id: int, db: _orm.Session):
    """
    Retrieve a user based on the provided user ID.
    Args:
    - user_id: User ID to retrieve
    - db: Database session
    Returns: 
    - User information
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user.username

async def update_user(request: _schemas.UpdateUserBase, user_id: int, db: _orm.Session):
    """
    Update a user's information based on the provided request and the user id associated with it.
    Args:
    - request: An instance of the UpdateUserBase schema containing the updated user information.
    - user_id: ID of the user to update
    - db: The database session.
    Returns: 
    - A dictionary with a message indicating that the user was updated.
    """
    try:
        update_data = request.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail=f"No fields to update")
        if update_data.get("email"):
            if (email_exists(db, update_data.get("email"))):
                raise HTTPException(status_code=400, detail=f'Email {update_data.get("email")} already exists')
            try:
                validate_email(update_data.get("email"), check_deliverability=False)
            except EmailNotValidError:
                raise HTTPException(status_code=400, detail="Invalid email address")
        if update_data.get("username"):
            username = update_data.get("username")
            if (user_exists(username, db)):
                raise HTTPException(status_code=400, detail=f'User {username} already exists')
        if update_data.get("password"):
            update_data["password"] = bcrypt(update_data.get("password"))
        stmt = (
            update(UserModel).
            where(UserModel.id == user_id).
            values(**update_data)
        )
        result = db.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException (
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "User not found"
            )
        db.commit()
        return {"message":"User was updated"}
    except HTTPException as http_exception:
        raise http_exception  # Re-raise HTTPException with custom message and status code

    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

def user_exists(username: str, db: _orm.Session):
    """
    Check if a user with the given username exists in the database.
    Args:
    - username: The username to check.
    - db: The database session.
    Returns:
    - True if the user exists, False otherwise.
    """
    result = db.query(UserModel).filter(UserModel.username == username).first()
    return True if result is not None else False

async def get_user_profile_info(user_id: int, db: _orm.Session):
    """
    Retrieves a user from the database based on their access token.
    Args:
    - user_id: The ID of the user to retrieve.
    - db: The database session.
    Returns: 
    - The user object.
    """
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_picture,
        }
    except HTTPException as http_exception:
        raise http_exception  # Re-raise HTTPException with custom message and status code

async def logout(token: str, db: _orm.Session):
    """
    Invalidate the given access token by adding it to the blacklist.
    Args:
    - access_token: The access token of the user.
    - db: The database session.
    Returns:
    - A dictionary with a message indicating that the access token was added to the blacklist.
    """
    try:
        token_obj = TokenBlacklistModel( access_token=token )
        db.add(token_obj)
        db.commit()

        return {'message': f"Access token {token} added to blacklist"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Access token could not be added: {e}")
