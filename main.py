import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
from datetime import datetime, date
import re
import bcrypt

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
    password: str

# Goal Request Model
class GoalRequest(BaseModel):
    user_id: int
    status: str
    set_date: date
    due_date: date
    goal_type: str
    current_amount: float
    target_amount: float

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
            print("Database connection established.")
            return conn
    except Error as error:
        print(f"Error: {error}")
        return None

@app.post("/login")
async def login(request: LoginRequest):
    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed.")
        cursor = conn.cursor(dictionary=True)

        # Check if user exists in the database
        cursor.execute("SELECT * FROM Users WHERE email = %s", (request.email,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(request.password.encode('utf-8'), user['password'].encode('utf-8')):
            # Return a success message with user details (no password)
            return {"message": "Login successful", "user": {k: v for k, v in user.items() if k != 'password'}}
        
        raise HTTPException(status_code=401, detail="Invalid email or password")
    except Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.post("/register")
async def register(request: RegisterRequest):
    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed.")
        cursor = conn.cursor(dictionary=True)

        # Check if user already exists
        cursor.execute("SELECT * FROM Users WHERE email = %s", (request.email,))
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists.")

        # Hash the password
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())

        # Register new user
        query = "INSERT INTO Users (name, email, dob, income, password) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (request.name, request.email, request.dob, request.income, hashed_password.decode('utf-8')))
        conn.commit()

        return {"message": "Registration successful"}
    except Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Function to upload data from CSV to the database
def upload_csv_data():
    csv_file_paths = [
        "trader_joes_products.csv",  # Trader Joe's products
        "scraped_products.csv"       # Target products
    ]

    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed.")
        cursor = conn.cursor()

        for csv_file_path in csv_file_paths:
            if not os.path.exists(csv_file_path):
                print(f"CSV file '{csv_file_path}' not found, skipping.")
                continue

            print(f"Processing file: {csv_file_path}")
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Clean the 'price' field to remove any non-numeric characters
                    price_str = row['price']
                    cleaned_price = re.sub(r'[^\d.]', '', price_str)

                    # Convert the cleaned price to a float
                    try:
                        price = float(cleaned_price)
                    except ValueError:
                        print(f"Invalid price format for product {row['product_name']}: {price_str}")
                        continue

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
                            price,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ))
                        print(f"Inserted product: {row['product_name']} from {row['store_name']}")

        conn.commit()
        print("CSV data uploaded successfully.")
    except Error as error:
        print(f"Error during CSV upload: {error}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Endpoint to fetch products
@app.get("/products/")
async def get_products(search: str = None):
    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed.")
        cursor = conn.cursor(dictionary=True)

        if search:
            query = "SELECT * FROM Marketplace WHERE LOWER(product_name) LIKE %s"
            cursor.execute(query, (f"%{search.lower()}%",))
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

# Function to ensure the Goals table exists
def ensure_goals_table():
    """Ensures that the Goals table exists in the database."""
    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed.")
        cursor = conn.cursor()
        
        # SQL query to create the Goals table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Goals (
            goal_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            status VARCHAR(50) NOT NULL,
            set_date DATE NOT NULL,
            due_date DATE NOT NULL,
            goal_type VARCHAR(255) NOT NULL,
            current_amount FLOAT NOT NULL,
            target_amount FLOAT NOT NULL
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("Checked/Created Goals table.")
    except Error as error:
        print(f"Error ensuring Goals table exists: {error}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Fetch all goals for a user
@app.get("/goals/{user_id}")
async def get_goals(user_id: int):
    try:
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed.")
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Goals WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        goals = cursor.fetchall()
        return goals
    except Error as error:
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Create a new goal
@app.post("/goals/")
async def create_goal(goal: GoalRequest):
    try:
        print(f"Received goal: {goal}")  # Log the incoming goal data
        conn = create_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed.")
        cursor = conn.cursor()

        query = """
        INSERT INTO Goals (user_id, status, set_date, due_date, goal_type, current_amount, target_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            goal.user_id,
            goal.status,
            goal.set_date,
            goal.due_date,
            goal.goal_type,
            goal.current_amount,
            goal.target_amount,
        ))
        conn.commit()

        print(f"Goal inserted with ID: {cursor.lastrowid}")  # Log success
        return {"message": "Goal created successfully", "goal_id": cursor.lastrowid}
    except Error as error:
        print(f"Error inserting goal: {error}")  # Log the error
        raise HTTPException(status_code=500, detail=str(error))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



# Upload CSV data at startup
@app.on_event("startup")
async def startup_event():
    print("Starting CSV upload...")
    upload_csv_data()
    print("Ensuring Goals table exists...")
    ensure_goals_table()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
