from pydantic import BaseModel, field_validator
from typing import Optional

# ===============================================================
# User schema
# ===============================================================

class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    email: str
    profile_picture: Optional[str] = None

class UpdateUserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    profile_picture: Optional[str] = None

# ===============================================================
# Post schema
# ===============================================================
class PostReviewBase(BaseModel):
    food_name: str
    image: Optional[str] = None
    restaurant_name: Optional[str] = None
    rating: float
    review: str
    tags: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: float) -> float:
        if not 1.0 <= v <= 5.0:
            raise ValueError("Rating must be between 1.0 and 5.0")
        return v

# ===============================================================
# Token Blacklist schema
# ===============================================================
class TokenBlacklistBase(BaseModel):
    access_token: str