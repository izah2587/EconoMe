import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
from datetime import datetime
import re
from typing import Optional

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

# class GoalRequest(BaseModel):#class for goal adding
#     name: str
#     target_amount: float
#     current_amount: float
#     deadline: str
#     user_id: int 


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

# Function to upload data from CSV to the database
def upload_csv_data():
    # List of CSV files to process
    csv_files = [
        "trader_joes_products.csv",  # Trader Joe's products
        "scraped_products.csv"       # Target products
    ]

    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")
        cursor = conn.cursor()

        for csv_file_path in csv_files:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Clean the 'price' field to remove any non-numeric characters
                    price_str = row['price']
                    cleaned_price = re.sub(r'[^\d.]', '', price_str)  # Keep only digits and decimal points

                    # Convert the cleaned price to a float
                    try:
                        price = float(cleaned_price)
                    except ValueError:
                        print(f"Invalid price format for product {row['product_name']}: {price_str}")
                        continue  # Skip this row if the price is invalid

                    # Check for existing entry to avoid duplicates
                    cursor.execute("""
                        SELECT COUNT(*) FROM Marketplace WHERE product_name = %s AND store_name = %s
                    """, (row['product_name'], row['store_name']))
                    count = cursor.fetchone()[0]

                    if count == 0:  # Insert only if the entry doesn't already exist
                        query = """
                        INSERT INTO Marketplace (store_name, product_name, url, price, last_checked_at)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(query, (
                            row['store_name'],
                            row['product_name'],
                            row['url'],
                            price,  # Insert the cleaned numeric price
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ))

        conn.commit()
        print(f"Data from all CSV files uploaded successfully")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Error as error:
        print(f"Error during CSV upload: {error}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Combined endpoint to upload CSV data and return all products
@app.get("/products/")
async def get_products(search: str = None):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        if search:
            # Use SQL wildcard for exact word match
            query = "SELECT * FROM Marketplace WHERE product_name LIKE %s"
            cursor.execute(query, (f"% {search} %",))
        else:
            query = "SELECT * FROM Marketplace"
            cursor.execute(query)

        products = cursor.fetchall()
        return products
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
