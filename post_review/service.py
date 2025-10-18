from fastapi import HTTPException
from auth.utils import get_current_user
from auth.model import UserModel
from schemas import PostReviewBase
from post_review.model import PostReviewModel
import sqlalchemy.orm as _orm


MAX_POSTS_TO_FETCH = 20

async def get_post_reviews(db: _orm.Session):
    """
    Retrieves a list of posts from the database.
    Args: 
    - db (_orm.Session): The database session.
    Returns:
        A list of dictionaries representing the posts. Each dictionary contains the following keys:
            - 'food_name' (str): The name of the food.
            - 'image' (str): The URL of the image.
            - 'restaurant_name' (str): The name of the restaurant.
            - 'rating' (int): The rating of the post.
            - 'review' (str): The review of the post.
            - 'tags' (str): The tags associated with the post.
            - 'username' (str): The username of the user who created the post.
            - 'profile_pic' (str or None): The URL of the user's profile picture, or None if no profile picture is available.
    Raises:
    - HTTPException: If no posts are found in the database.
    - HTTPException: If there is an error retrieving the posts from the database.
    """
    try:
        posts = db.query(PostReviewModel, UserModel)\
            .join(UserModel, PostReviewModel.user_id == UserModel.id)\
            .limit(MAX_POSTS_TO_FETCH)\
            .all()
        if not posts:
            raise HTTPException(status_code=404, detail="No posts found")
        
        # Convert the SQLAlchemy query result to a list of dictionaries
        posts = [
            {**post.PostReviewModel.__dict__, 
            "username": post.UserModel.username,
            "profile_pic": post.UserModel.profile_picture if hasattr(post.UserModel, 'profile_picture') else None}  # Add 'profile_pic' key and assign the value if available
                 for post in posts
        ]
        return posts
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Posts could not be retrieved: {e}")

async def create_post_review(post_review: PostReviewBase, db: _orm.Session, access_token: str):
    """
    Creates a new post review in the database.
    Args:
    - post_review: Post review information
    - db: Database session
    - access_token: User access token
    Returns: 
    - Message indicating whether the post was created successfully
    Raises:
    - HTTPException: If the user is not found or if the post could not be added
    """
    user_id = get_current_user(access_token, db)

    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        post_review = PostReviewModel(
            user_id=user_id,
            food_name=post_review.food_name,
            image=post_review.image,
            restaurant_name=post_review.restaurant_name,
            rating=post_review.rating,
            review=post_review.review,
            tags=post_review.tags
        )
        db.add(post_review)
        db.commit()

        return {'message': f"Post {post_review.id} created"}
    
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=400, detail=f"Post could not be added: {str(e)}")
    
async def update_post_review(post_review: PostReviewBase, db: _orm.Session, access_token: str, id: int):
    """
    Update an existing post review in the database.
    Args:
    - post_review (PostReviewBase): The updated post review information.
    - db (_orm.Session): The database session.
    - access_token (str): The user's access token.
    - id (int): The ID of the post review to update.
    Returns:
    - dict: A dictionary with a message indicating the post was updated.
    Raises:
    - HTTPException: If the user is not found or if the post could not be updated.
    """
    user_id = get_current_user(access_token, db)

    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # may not be the best solution. What if there are missing fields?
        db.query(PostReviewModel).filter(PostReviewModel.id == id).update({
            'food_name': post_review.food_name,
            'image': post_review.image,
            'restaurant_name': post_review.restaurant_name,
            'rating': post_review.rating,
            'review': post_review.review,
            'tags': post_review.tags})
        
        db.commit()

        return {'message': f"Post {id} updated"}
    
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")  # Log the error message
        raise HTTPException(status_code=400, detail=f"Post could not be updated: {str(e)}")

async def delete_post_review(id: int, db: _orm.Session, access_token: str):
    """
    Deletes a post review from the database.
    Args:
    - id: Post review ID
    - db: Database session
    - access_token: User access token
    Returns: 
    - Message indicating whether the post was deleted successfully
    Raises:
    - HTTPException: If the user or the post is not found or if the post could not be deleted
    """
    user_id = get_current_user(access_token, db)

    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        post = db.query(PostReviewModel).filter(PostReviewModel.id == id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
                
        db.query(PostReviewModel).filter(PostReviewModel.id == id).delete()
        db.commit()

        return {'message': f"Post {id} deleted"}
    
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")  # Log the error message
        raise HTTPException(status_code=400, detail=f"Post could not be deleted: {str(e)}")

async def get_posts_from_id(user_id: int, db: _orm.Session):
    """
    Retrieve a post review based on the provided user ID.
    Args:
    - user_id: The ID of the user associated with the post review
    - db: Database session
    Returns: 
    - A list of posts from the database that is associated with the provided user ID
    Raises:
    - HTTPException: If the post is not found or an error occurs
    """
    try:
        posts = db.query(PostReviewModel, UserModel)\
            .filter(PostReviewModel.user_id == user_id)\
            .join(UserModel, PostReviewModel.user_id == UserModel.id)\
            .all()
        if not posts:
            raise HTTPException(status_code=404, detail="No posts found")
        
        # Convert the SQLAlchemy query result to a list of dictionaries
        posts = [
            {**post.PostReviewModel.__dict__, 
            "username": post.UserModel.username,
            "profile_pic": post.UserModel.profile_picture if hasattr(post.UserModel, 'profile_picture') else None}  # Add 'profile_pic' key and assign the value if available
                 for post in posts
        ]
        return posts[:MAX_POSTS_TO_FETCH]
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=400, detail=f"Post could not be retrieved")