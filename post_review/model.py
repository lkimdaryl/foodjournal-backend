from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func
from database import Base

class PostReviewModel(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("fd_users.id", ondelete="CASCADE"), nullable=False, index=True)
    food_name = Column(String, nullable=False)
    image = Column(String, nullable=True)
    restaurant_name = Column(String, nullable=True)
    rating = Column(Float, nullable=False)
    review = Column(String, nullable=False)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
