 # Food Journal (Backend)     
 The Food Journal Backend is a robust FastAPI application serving as the API layer for a social food review and journal application. It manages user authentication, user profiles, food post reviews, and maintenance tasks, including JWT blacklisting and cleanup.   
 
 ## API docs  
 https://foodjournal-backend.onrender.com/docs

 ### 🚀 Features    
 * User Management: Secure user registration, login, and profile updates.
 * Token-Based Authentication: Uses JWTs (JSON Web Tokens) for authentication.
 * Review Posts: CRUD (Create, Read, Update, Delete) operations for food review posts.
 * CORS Configuration: Securely allows requests from specified frontend domains (localhost, Vercel, Render).
 * Background Scheduler: Utilizes apscheduler for running recurring database maintenance jobs.
 * Secure Token Blacklisting: Implements token blacklisting for immediate session revocation.

 ### ⚙️ Technology Stack
 | Component | Technology | Description |
 | :--- | :---: | :--- |
 | API Framework | FastAPI | High-performance, modern, fast web framework for Python. |
 | Database | PostgreSQL / Supabase | Robust and scalable relational database. |
 | ORM | SQLAlchemy |  Python SQL toolkit and Object Relational Mapper. |
 | Scheduling | APSchedulerTask | scheduler for running background jobs (token cleanup). |
 | Security | PyJWT, Passlib (Bcrypt) | Handling JWTs and password hashing. |
 | Deployment | Render | Hosting. | 
 
 ### 📦 Setup and Installation
 Prerequisites
 1. Python 3.9+
 2. PostgreSQL/Supabase Database instance
 3. Virtual environment (recommended)       
 
 Installation Steps
 1. Clone the repository: 
    > git clone [repository-url]   
    > cd foodjournal-backend
 2. Create and activate a virtual environment:
    > python -m venv venv
    > source venv/bin/activate  # On macOS/Linux
    > venv\Scripts\activate     # On Windows
 3. Install dependencies:
    > pip install -r requirements.txt
 4. Database Setup:Ensure your PostgreSQL/Supabase database is running and apply the schema found in the database setup file (or use the one provided in the chat history, ensuring the use of SERIAL, BYTEA, and TIMESTAMP).
 5. Environment Variables: Create a file named .env in the root directory and populate it with your configuration details.
 > #Database Connection (PostgreSQL/Supabase)
 > DB_USER=your_db_user
 > DB_PASSWORD=your_db_password
 > DB_HOST=your_db_host 
 > DB_PORT=5432
 > DB_NAME=postgres
 > SECRET_KEY="a_very_long_and_secure_secret_key"
 > ALGORITHM="HS256"
   
▶️ Running the Application Development. In the terminal run:
> py main.py    

Your API will be available at http://localhost:6542/docs. 
