from fastapi import APIRouter, Depends, Cookie, HTTPException, status, Request
from sqlalchemy.orm.session import Session
from service_database import get_db
from schemas import PostReviewBase
import post_review.service as _service


router_post_review = APIRouter(
    prefix="/api/v1/post_review",
    tags=["post_review"]
)

@router_post_review.post("/create_post_review")
async def create_post_review(post_review: PostReviewBase, access_token: str = Cookie(None), db: Session = Depends(get_db)):
    """ 
    Create a new post review in the database. Endpoint receives an access token and
    a JSON string with post review information.     
    
    Args:       
    - post_review (_schemas.PostReviewBase): The post review information to create.   
    - access_token (str): The user's access token.    
    - db (Session, optional): The database session. Defaults to Depends(get_db).      
    
    Returns:    
    - A dictionary indicating whether the post was created successfully.

    Raises HTTPException:    
    - If the user is not found 
    - If an error occured whilst creating the post
    """
    return await _service.create_post_review(post_review, db, access_token)


@router_post_review.post("/update_post_review")
async def update_post_review(post_review: PostReviewBase,  id: int, access_token: str = Cookie(None), db: Session = Depends(get_db)):
    """ 
    Create a new post review in the database. Endpoint receives an access token and
    a JSON string with post review information.     
    
    Args:       
    - post_review (_schemas.PostReviewBase): The post review information to create.       
    - access_token (str): The user's access token.        
    - db (Session, optional): The database session. Defaults to Depends(get_db).        
    
    Returns:        
    - A dictionary indicating whether the post was updated successfully.
    
    Raises HTTPException:        
    - If the user or the post is not found 
    - If an error occured whilst updating the post
    """
    return await _service.update_post_review(post_review, db, access_token, id)

@router_post_review.post("/delete_post_review")
async def delete_post_review(id: int, access_token: str = Cookie(None), db: Session = Depends(get_db)):
    """ 
    Delete a post review from the database. Endpoint receives an access token and
    a post id. The ID recevied in the post request is the ID of the post to remove.     
    
    Args:   
    - id (int): The ID of the post to delete. 
    - access_token (str): The user's access token.    
    - db (Session, optional): The database session. Defaults to Depends(get_db).      
    
    Returns:    
    - A dictionary indicating whether the post was deleted successfully.
    
    Raises HTTPException:    
    - If the user or the post is not found 
    - If an error occured whilst deleting the post
    """
    return await _service.delete_post_review(id, db, access_token)
  
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
