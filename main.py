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
import openai
import pandas as pd

# Load environment variables
load_dotenv()

db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pass = os.getenv("db_pass")
db_name = os.getenv("db_name")

#openai key
openai.api_key = os.getenv("OPENAI_API_KEY")

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

# Function to read products from a CSV file using Pandas
def read_products_from_csv(file_path: str) -> pd.DataFrame:
    """Reads product data from a CSV file and returns it as a Pandas DataFrame."""
    try:
        # Load the CSV into a DataFrame
        df = pd.read_csv(file_path)

        # Clean the 'price' column by removing non-numeric characters and converting it to float
        df['price'] = df['price'].replace({r'[^\d.]': ''}, regex=True)  # Keep only digits and decimal points
        df['price'] = pd.to_numeric(df['price'], errors='coerce')  # Convert to float, invalid values become NaN

        # Remove rows where price is NaN (invalid data)
        df = df.dropna(subset=['price'])

        return df[['product_name', 'price']]  # Return only the necessary columns
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"CSV file '{file_path}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Price comparison function using OpenAI
def generate_price_comparison_summary(target_df: pd.DataFrame, trader_joes_df: pd.DataFrame) -> str:
    # Convert DataFrames to a string format for OpenAI
    target_products_str = target_df.to_dict(orient='records')
    trader_joes_products_str = trader_joes_df.to_dict(orient='records')

    prompt = f"""
    You are a price comparison assistant. I will provide you with product prices from two stores, Target and Trader Joe's.

    Please compare the prices of the following products between the two stores. You do not need to rely on exact product names but instead use your understanding to evaluate if two products are similar. For example, "Red Onion" and "Onion" can be considered the same. Use keywords, context, and common product categories to determine similarity. If two products are different but belong to the same category (e.g., onions, tomatoes, garlic, herbs), treat them as similar.

    If a product is found in both stores, calculate the percentage price difference. If a product is only found in one store, try to find a similar product from the other store and treat it as part of the same category. If no equivalent product is found in the other store, ignore it in your comparison.

    For the summary, display **5 example products** that are available in both stores, showing their price differences and the percentage difference between them. Each example should include the following:
    - Product Name
    - Target Price
    - Trader Joe's Price
    - Percentage Price Difference (rounded to 2 decimal places)

    Ensure that the examples reflect a range of price differences:
    1. One example where Target is more expensive.
    2. One example where Trader Joe's is more expensive.
    3. One example where the prices are equal.
    4. The other examples should show diverse products with varied price differences.

    Please also provide a general **overall summary** comparing the two stores:
    - Which store generally has better prices (Target or Trader Joe's)?
    - What is the approximate percentage difference in prices across all products compared (if applicable)?

    Here is the data you should consider:

    Target Products:
    {target_products_str}

    Trader Joe's Products:
    {trader_joes_products_str}

    Please provide the results in an HTML format. Use the following structure:

    <h3>Example Products:</h3>
    <ul>
        <li><strong>Product Name:</strong> Product1 <br> <strong>Target Price:</strong> $5.89 <br> <strong>Trader Joe's Price:</strong> $2.29 <br> <strong>Percentage Price Difference:</strong> 61.16%</li>
        <!-- Add other products here -->
    </ul>

    <h3>Overall Summary</h3>
    <p>Trader Joe's generally has better prices as seen in the provided examples. The average savings when shopping at Trader Joe's compared to Target is approximately 33.05%.</p>

    Please format the output using <strong>HTML tags</strong> to improve readability.

    Dont include ```html or anything. Include a brief text in <p> in the beginning along the lines 'Let's have a look at the data we obtained this week'

    Please provide a concise and professional summary, avoiding unnecessary details.
    """
    print('woop')
    
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a price comparison assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        print('womp')
        print(response['choices'][0]['message']['content'])  # Access the AI's response
    except Exception as e:
        print("API Call Failed:", str(e))

    # Get the OpenAI response (summary)
    summary = response['choices'][0]['message']['content'].strip()

    print(summary)
    return summary

# API endpoint to compare prices between Target and Trader Joe's
@app.post("/compare_prices")
async def compare_prices():
    # Define file paths for the CSV files
    print("im here")
    target_file_path = "scraped_products.csv"  # Path to your Target CSV file
    trader_joes_file_path = "trader_joes_products.csv"  # Path to your Trader Joe's CSV file

    # Read products from both CSV files using Pandas
    target_df = read_products_from_csv(target_file_path)
    trader_joes_df = read_products_from_csv(trader_joes_file_path)
    # Generate the price comparison summary using OpenAI
    try:
        summary = generate_price_comparison_summary(target_df, trader_joes_df)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
