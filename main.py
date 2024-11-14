import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables
load_dotenv()

db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pass = os.getenv("db_pass")
db_name = os.getenv("db_name")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to allow requests from localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from this origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Define request models for login and registration
class LoginRequest(BaseModel):
    email: str
    password: str  # Placeholder if needed

class RegisterRequest(BaseModel):
    name: str
    email: str
    dob: str
    income: float

# Database connection helper
def create_connection():
    """Creates and returns a connection to the database."""
    try:
        conn = mysql.connector.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_pass
        )
        if conn.is_connected():
            return conn
    except Error as error:
        print(f"Error: {error}")
        return None

# Endpoint for login (MySQL)
@app.post("/login")
async def login(request: LoginRequest):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if user exists in the database
        cursor.execute("SELECT * FROM Users WHERE email = %s", (request.email,))
        user = cursor.fetchone()
        
        if user:
            return {"message": "Login successful", "user": user}
        
        raise HTTPException(status_code=404, detail="User not found")
    
    except Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Endpoint for registration (MySQL)
@app.post("/register")
async def register(request: RegisterRequest):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if user already exists
        cursor.execute("SELECT * FROM Users WHERE email = %s", (request.email,))
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # Register new user
        query = "INSERT INTO Users (name, email, dob, income) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (request.name, request.email, request.dob, request.income))
        conn.commit()

        return {"message": "Registration successful", "user": {
            "name": request.name,
            "email": request.email,
            "dob": request.dob,
            "income": request.income
        }}

    except Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Get all users from the database
@app.get("/users/")
async def get_users():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users;")
        users = cursor.fetchall()
        return users
    except Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Get a user by ID from the database
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Update a user by ID in the database
@app.put("/users/{user_id}")
async def update_user(user_id: int, user: RegisterRequest):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = """
        UPDATE Users SET name = %s, email = %s, dob = %s, income = %s WHERE user_id = %s;
        """
        cursor.execute(query, (user.name, user.email, user.dob, user.income, user_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User updated successfully"}
    except Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Delete a user by ID from the database
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = "DELETE FROM Users WHERE user_id = %s;"
        cursor.execute(query, (user_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

### MAIN APP STARTUP ###

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
