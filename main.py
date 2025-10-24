from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from auth.router import router_auth
from post_review.router import router_post_review

from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from datetime import datetime
from db_jobs import delete_expired_blacklisted_tokens

# ----------------- Scheduler Configuration -----------------
scheduler = BackgroundScheduler()

# Define the job: run the cleanup function once every 24 hours
scheduler.add_job(
    delete_expired_blacklisted_tokens, 
    'interval', 
    hours=24, 
    id='blacklist_cleanup_job',
    name='Blacklist Token Cleanup',
    # Optional: Run immediately when the app starts
    next_run_time=datetime.now() 
)
# Start the scheduler
scheduler.start()

# Ensure the scheduler shuts down when the Python process exits (crucial for clean restarts)
atexit.register(lambda: scheduler.shutdown())

# ----------------- App Configuration -----------------
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:6542",
    "https://foodjournal-backend.onrender.com",
    "https://foodjournal-p9bypxj9x-lkimdaryls-projects.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.get("/")
def root():
    return {
            "Environ": os.getenv("APP_ENV", default="main"),
            "Project": "Food Journal"
            }

app.include_router(router_auth)
app.include_router(router_post_review)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=6542, reload=True)
