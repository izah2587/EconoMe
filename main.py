import mysql.connector
from mysql.connector import Error

# Database connection parameters
db_host = '34.44.42.132'
db_name = 'econome'
db_user = 'econome'
db_pass = ')Leb}|JtH0D4b4xh'

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

        # Create Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
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

        # Create Expenses table with a category field
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Expenses (
            expense_id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            category VARCHAR(50) NOT NULL,
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

        print("All tables created successfully")

        # close the cursor and connection
        cursor.close()
        conn.close()

except Error as error:
    print(f"Error: {error}")
