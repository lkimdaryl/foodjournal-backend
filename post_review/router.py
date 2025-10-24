from fastapi import APIRouter, Depends, Cookie, HTTPException, status, Request
from sqlalchemy.orm.session import Session
from service_database import get_db
from schemas import PostReviewBase
import post_review.service as _service
from typing import Annotated
from auth.utils import get_current_user


router_post_review = APIRouter(
    prefix="/api/v1/post_review",
    tags=["post_review"]
)

@router_post_review.post("/create_post_review")
async def create_post_review(post_review: PostReviewBase, user_id: Annotated[int, Depends(get_current_user)], db: Session = Depends(get_db)):
    """ 
    Create a new post review in the database. Requires a JSON string with 
    post review information.

    Authentication:
    - The user's access token is automatically extracted from the `Authorization` header.

    Args:
    - post_review (PostReviewBase): The post review data to create.
    - user_id (int): The ID of the authenticated user (extracted from the token in headers).
    - db (Session): The database session dependency.

    Returns:
    - A dictionary indicating whether the post review was created successfully.

    Raises:
    - HTTPException: If the user is not found or if an error occurs while creating the review.
    """
    return await _service.create_post_review(post_review, db, user_id)


@router_post_review.post("/update_post_review")
async def update_post_review(
    post_review: PostReviewBase,  
    post_id: int, 
    user_id: Annotated[int, Depends(get_current_user)], 
    db: Session = Depends(get_db)):
    """ 
    Updates an existing post review in the database. Requires a JSON string with 
    post review information.     

    Authentication:
    - The user's access token is automatically extracted from the `Authorization` header.

    Args:
    - post_review (PostReviewBase): The updated post review data.
    - post_id (int): The ID of the post to update.
    - user_id (int): The ID of the authenticated user (extracted from the token in headers).
    - db (Session): The database session dependency.

    Returns:
    - A dictionary indicating whether the post review was updated successfully.

    Raises:
    - HTTPException: If the user or post is not found, or if an error occurs during the update.
    """
    return await _service.update_post_review(post_review, post_id, user_id, db)

@router_post_review.post("/delete_post_review")
async def delete_post_review(post_id: int, user_id: Annotated[int, Depends(get_current_user)], db: Session = Depends(get_db)):
    """ 
    Delete a post review from the database.
    
    Authentication:
    - The user's access token is automatically extracted from the `Authorization` header.

    Args:
    - post_id (int): The ID of the post to delete.
    - user_id (int): The ID of the authenticated user (extracted from the token in headers).
    - db (Session): The database session dependency.

    Returns:
    - A dictionary indicating whether the post review was deleted successfully.

    Raises:
    - HTTPException: If the user or post is not found, or if an error occurs while deleting.
   """
    return await _service.delete_post_review(post_id, user_id, db)
  
@router_post_review.get("/get_post_review")
async def get_post_reviews(db: Session = Depends(get_db)):
    """ 
    Get all post reviews from the database.     
    
    Args:       
    - db (Session, optional): The database session. Defaults to Depends(get_db).      
    
    Returns:        
    - A list of dictionaries containing a post review and the user who created it.
    
    Raises HTTPException:
    - If no posts are found in the database
    - If there is an error retrieving the posts from the database
    """
    return await _service.get_post_reviews(db)

@router_post_review.get("/get_posts_by_id")
async def get_posts_by_id(user_id: int, db: Session = Depends(get_db)):
    """ 
    Get all post reviews from the database for a specific user.     
    
    Args:       
    - user_id (int): The ID of the user to get posts for.     
    - db (Session, optional): The database session. Defaults to Depends(get_db).      
    
    Returns:        
    - A list of posts from the specified user.

    Raises HTTPException:
    - If no posts are found for the specified user
    - If there is an error retrieving the posts from the database
    """
    return await _service.get_posts_from_id(user_id, db)
