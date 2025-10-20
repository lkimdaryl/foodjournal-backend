from datetime import datetime, timedelta
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from auth.model import TokenBlacklistModel
import os

# --- 1. Replicate Database Engine Setup ---
DATABASE_URL = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/postgres'

# Create the Engine
engine = create_engine(DATABASE_URL)

# Create a manual Session factory (SessionLocal)
# The scheduler job will use this to create its own DB connection.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 2. Corrected Cleanup Function ---

def delete_expired_blacklisted_tokens():
    """
    Deletes blacklisted token records that are older than their expiration window.
    This scheduled job manually manages its database session.
    """
    
    CUTOFF_HOURS = 25 
    cutoff_time = datetime.now() - timedelta(hours=CUTOFF_HOURS)
    
    print(f"[{datetime.now()}] Running blacklist cleanup. Deleting tokens revoked before: {cutoff_time}")

    # Manually create and use the DB session here
    db = SessionLocal() 
    
    try:
        # We delete tokens that were revoked before the cutoff time.
        deleted_count = db.query(TokenBlacklistModel).filter(
            TokenBlacklistModel.created_at < cutoff_time
        ).delete(synchronize_session='fetch')
        
        db.commit()
        print(f"[{datetime.now()}] Successfully deleted {deleted_count} expired blacklisted tokens.")
    
    except Exception as e:
        db.rollback()
        print(f"Error during token cleanup: {e}")
        
    finally:
        # Always close the session manually
        db.close()