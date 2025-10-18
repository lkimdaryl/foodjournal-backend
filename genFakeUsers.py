from faker import Faker
from sqlalchemy.orm import Session
from auth.model import UserModel  # Import your model
from database import engine, SessionLocal  # Import your database connection

fake = Faker()

def generate_users(db: Session, num_users: int = 10):
    for _ in range(num_users):
        user = UserModel(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            username=fake.user_name(),
            password=fake.password(length=12),  # Hash passwords in production!
            email=fake.email(),
            profile_picture=fake.image_url(),  # Optional
        )
        db.add(user)
    db.commit()
    print(f"{num_users} users added to the database.")

# Setup database connection and call the function
if __name__ == "__main__":
    with SessionLocal() as db:
        generate_users(db, num_users=50)  # Change number of users as needed
