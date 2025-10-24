from faker import Faker
from sqlalchemy.orm import Session
from post_review.model import PostReviewModel  # Import your model
from database import engine, SessionLocal  # Import your database connection
import random

fake = Faker()

def generate_post_reviews(db: Session, num_posts: int = 10):
    for _ in range(num_posts):
        post = PostReviewModel(
            user_id=random.randint(2, 10),  # Example range for post IDs
            food_name=fake.word(),
            image=fake.image_url(),  # Optional, may leave null
            restaurant_name=fake.company(),  # Fake restaurant names
            rating=round(random.uniform(1.0, 5.0), 1),  # Random rating from 1.0 to 5.0
            review=fake.paragraph(nb_sentences=5),
            tags=", ".join(fake.words(nb=3)),  # Example: 'spicy, vegan, tasty'
        )
        db.add(post)
    db.commit()

# Setup database connection and call the function
if __name__ == "__main__":
    with SessionLocal() as db:
        generate_post_reviews(db, num_posts=50)  # Adjust number of posts as needed
