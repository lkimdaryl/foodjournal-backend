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
            return []

        # Convert the SQLAlchemy query result to a list of dictionaries
        posts = [
            {
                "id": post.PostReviewModel.id,
                "user_id": post.PostReviewModel.user_id,
                "food_name": post.PostReviewModel.food_name,
                "image": post.PostReviewModel.image,
                "restaurant_name": post.PostReviewModel.restaurant_name,
                "rating": post.PostReviewModel.rating,
                "review": post.PostReviewModel.review,
                "tags": post.PostReviewModel.tags,
                "created_at": str(post.PostReviewModel.created_at) if post.PostReviewModel.created_at else None,
                "username": post.UserModel.username,
                "profile_pic": post.UserModel.profile_picture,
            }
            for post in posts
        ]
        return posts
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Posts could not be retrieved: {e}")

async def create_post_review(post_review: PostReviewBase, db: _orm.Session, user_id: int):
    """
    Creates a new post review in the database.
    Args:
    - post_review: Post review information
    - db: Database session
    - user_id: ID of the user creating the post review
    Returns: 
    - Message indicating whether the post was created successfully
    Raises:
    - HTTPException: If the user is not found or if the post could not be added
    """

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

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=400, detail=f"Post could not be added: {str(e)}")
    
async def update_post_review(post_review: PostReviewBase, post_id: int, user_id: int, db: _orm.Session):
    """
    Update an existing post review in the database.
    Args:
    - post_review (PostReviewBase): The updated post review information.
    - post_id (int): The ID of the post review to update.
    - user_id (int): The ID of the user making the update.
    - db (_orm.Session): The database session.

    Returns:
    - dict: A dictionary with a message indicating the post was updated.
    Raises:
    - HTTPException: If the user is not found or if the post could not be updated.
    """

    try:
        post = db.query(PostReviewModel).filter(PostReviewModel.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this post")

        db.query(PostReviewModel).filter(PostReviewModel.id == post_id).update({
            'food_name': post_review.food_name,
            'image': post_review.image,
            'restaurant_name': post_review.restaurant_name,
            'rating': post_review.rating,
            'review': post_review.review,
            'tags': post_review.tags})

        db.commit()

        return {'message': f"Post {post_id} updated"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=400, detail=f"Post could not be updated: {str(e)}")

async def delete_post_review(post_id: int, user_id:int, db: _orm.Session):
    """
    Deletes a post review from the database.
    Args:
    - post_id: ID of the post to delete 
    - user_id: ID of the user requesting the deletion
    - db: Database session

    Returns: 
    - Message indicating whether the post was deleted successfully
    Raises:
    - HTTPException: If the user or the post is not found or if the post could not be deleted
    """

    try:
        post = db.query(PostReviewModel).filter(PostReviewModel.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")

        db.delete(post)
        db.commit()

        return {'message': f"Post {post_id} deleted"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
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
            return []

        # Convert the SQLAlchemy query result to a list of dictionaries
        posts = [
            {
                "id": post.PostReviewModel.id,
                "user_id": post.PostReviewModel.user_id,
                "food_name": post.PostReviewModel.food_name,
                "image": post.PostReviewModel.image,
                "restaurant_name": post.PostReviewModel.restaurant_name,
                "rating": post.PostReviewModel.rating,
                "review": post.PostReviewModel.review,
                "tags": post.PostReviewModel.tags,
                "created_at": str(post.PostReviewModel.created_at) if post.PostReviewModel.created_at else None,
                "username": post.UserModel.username,
                "profile_pic": post.UserModel.profile_picture,
            }
            for post in posts
        ]
        return posts[:MAX_POSTS_TO_FETCH]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=400, detail=f"Post could not be retrieved")