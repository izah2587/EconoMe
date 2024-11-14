import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import csv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv()

db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pass = os.getenv("db_pass")
db_name = os.getenv("db_name")

# Initialize FastAPI app
app = FastAPI()

# Pydantic model for Users
class User(BaseModel):
    name: str
    email: str
    dob: str
    income: float

### DATABASE CONNECTION ###

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

### FASTAPI ROUTES FOR USERS ###

# Create a new user
@app.post("/users/")
async def create_user(user: User):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = "INSERT INTO Users (name, email, dob, income) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (user.name, user.email, user.dob, user.income))
        conn.commit()
        return {"message": "User created successfully"}
    except Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Get all users
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

# Get a user by ID
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

# Update a user by ID
@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User):
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

# Delete a user by ID
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
