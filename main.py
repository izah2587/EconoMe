import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import csv

load_dotenv()  # Loads variables from .env file into the environment

db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pass = os.getenv("db_pass")
db_name = os.getenv("db_name")


def create_tables(cursor):
    
    # Create Users table
    cursor.execute("DROP TABLE IF EXISTS Users;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        dob DATE NOT NULL,
        income DECIMAL(10, 2)
    );
    """)

    # Create Goals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Goals (
        goal_id INT AUTO_INCREMENT PRIMARY KEY,
        status VARCHAR(20) NOT NULL,
        set_date DATE NOT NULL,
        due_date DATE NOT NULL,
        goal_type VARCHAR(20) NOT NULL,  -- Savings or Debt
        current_amount DECIMAL(10, 2) NOT NULL,
        target_amount DECIMAL(10, 2) NOT NULL,
        user_id INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
    );
    """)

    # Create Expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Expenses (
        expense_id INT AUTO_INCREMENT PRIMARY KEY,
        date DATE NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        user_id INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
    );
    """)

    # Create Marketplace table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Marketplace (
        id INT AUTO_INCREMENT PRIMARY KEY,
        store_name VARCHAR(100) NOT NULL,
        product_name VARCHAR(100) NOT NULL,
        url VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        last_checked_at TIMESTAMP NOT NULL
    );
    """)


def populate_data(cursor):
    # Sample data for Users
    users = [
        ('Alice Johnson', 'alice.johnson@example.com', '1990-01-15', 70000.00),
        ('Bob Smith', 'bob.smith@example.com', '1985-05-23', 60000.00),
        ('Charlie Brown', 'charlie.brown@example.com', '1992-08-30', 80000.00),
    ]
    
    cursor.executemany("""
    INSERT INTO Users (name, email, dob, income) VALUES (%s, %s, %s, %s);
    """, users)

    # Sample data for Goals
    goals = [
        ('Active', '2024-01-01', '2025-01-01', 'Savings', 5000.00, 15000.00, 1),
        ('Active', '2024-03-15', '2025-03-15', 'Debt', 2000.00, 10000.00, 2),
        ('Inactive', '2023-06-01', '2024-06-01', 'Savings', 1000.00, 5000.00, 3),
    ]

    cursor.executemany("""
    INSERT INTO Goals (status, set_date, due_date, goal_type, current_amount, target_amount, user_id) 
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, goals)

    # Sample data for Expenses
    expenses = [
        ('2024-01-10', 50.00, 1),
        ('2024-01-15', 20.00, 1),
        ('2024-01-20', 100.00, 2),
    ]

    cursor.executemany("""
    INSERT INTO Expenses (date, amount, user_id) VALUES (%s, %s, %s);
    """, expenses)

    # Sample data for Marketplace
    marketplace = [
        ('Target', 'Apple', 'https://www.target.com/p/gala-apple-each/-/A-15014055#lnk=sametab', 0.5, '2024-01-05 12:00:00'),
        ("Trader Joe's", 'Banana', 'https://www.traderjoes.com/home/products/pdp/bananas-048053', 0.23, '2024-01-05 12:00:00'),
    ]

    cursor.executemany("""
    INSERT INTO Marketplace (store_name, product_name, url, price, last_checked_at) VALUES (%s, %s, %s, %s, %s);
    """, marketplace)

def export_to_csv(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()

    with open(f"{table_name}.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow([i[0] for i in cursor.description])
        # Write data
        writer.writerows(rows)

try:
    # Establish the connection
    conn = mysql.connector.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_pass
    )

    if conn.is_connected():
        print("Connected to the database")

        # Create a cursor object
        cursor = conn.cursor()


        # Commit changes
        conn.commit()
        print("Sample data populated successfully.")

        # Export data to CSV files
        for table in ['Users', 'Goals', 'Expenses', 'Marketplace']:
            export_to_csv(cursor, table)
            print(f"{table}.csv created successfully.")

        # Close the cursor and connection
        cursor.close()
        conn.close
except Error as error:
    print(f"Error: {error}")
