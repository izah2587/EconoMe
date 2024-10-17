# EconoMe 💰
## The only finance app you need!!

# MySQL Database Management and CSV Export

This is a command-line application for managing a MySQL database with users, goals, expenses, and marketplace data. It creates tables, populates them with sample data, and exports the data into CSV files. There's no front end—just a few database management functions.

## Amazing Features

- Creates database tables for users, goals, expenses, and marketplace items
- Populates the tables with sample data
- Exports the data from the tables to CSV files for easy reporting

## Prerequisites

- **Python 3.7 or higher**
- **MySQL server** (set up locally or provided to you)
- **pip** (Python package manager)

## Setup

1. **Clone this repository** or download the source code:

   ```bash
   git clone https://github.com/izah2587/EconoMe.git
   ```

2. **Navigate to the project directory:**

    ```bash
    cd path/to/your-repository
    ```

3. **Set Up a Virtual Environment (Optional but Recommended)**

    ```bash
    python -m venv .venv
    ```

    **On Windows:**

    ```bash
    .venv\Scripts\activate
    ```

    **On macOS and Linux:**

    ```bash
    source .venv/bin/activate
    ```

4. **Install Required Packages**

    Once the virtual environment is activated, install the necessary dependencies from the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

5. **Set Up Your `.env` File**

    To securely store your MySQL database credentials, you need to set up a `.env` file in the root of the project directory:

    Create a new `.env` file in the project root:

    ```bash
    touch .env
    ```

    Open the `.env` file in a text editor and add your MySQL connection details in the following format:

    ```bash
    db_host=your_mysql_host
    db_user=your_mysql_username
    db_pass=your_mysql_password
    db_name=your_database_name
    ```

    Replace the placeholders with your actual MySQL connection details.


6. **Add `.env` to `.gitignore`**

    Ensure the `.env` file is excluded from version control by adding it to your `.gitignore` file. If you don't have a `.gitignore` file, create one and add the following line:

    ```bash
    .env
    ```

    This will prevent the `.env` file from being accidentally pushed to the repository.

7. **Run the Application**

    Once everything is set up, you can run the Python script to create tables, populate them with sample data, and export the data to CSV files:

    ```bash
    python main.py
    ```

8. **What Happens When You Run the Application**

    - **Creates tables**: The application will create the `Users`, `Goals`, `Expenses`, and `Marketplace` tables in your MySQL database.
    - **Populates tables**: Inserts sample data into each table.
    - **Exports data to CSV**: Exports the contents of each table into a CSV file, saving the files as `Users.csv`, `Goals.csv`, `Expenses.csv`, and `Marketplace.csv` in the project directory.

9. **Deactivate the Virtual Environment (Optional)**

    If you're done working on the project and want to deactivate the virtual environment, you can run:

    ```bash
    deactivate
    ```


# EconoMe API

## API Description and purpose 
The EconoMe User Management API is a RESTful service designed to manage user information within a MySQL database. It provides capabilities to create, read, update, and delete user data, facilitating administrative tasks and user data handling for applications requiring a robust user management system. 

## Setting up the Database

1. **Create the Database: Log into your MySQL server and create a new database named user_management:**
   
   ```sql
     CREATE DATABASE user_management;
  
2. **Initialize the Tables: Use the provided SQL script to create the necessary tables within the database:**
   
   ```bash
   mysql -u [your-username] -p user_management < database_setup.sql
   ```
## Install Dependencies
**Install the required dependencies by running:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the API
**To run the API, execute the following command in the project directory:**
   ```bash
uvicorn main:app --reload
   ```

**API Endpoints**
1. **GET /users/: Retrieves a list of all users**
   
   **Response example**
   ```json
        [
     {
       "name": "John Doe",
       "email": "john.doe@example.com",
       "dob": "1990-04-01",
       "income": 55000
     }
   ]

  
2. **GET /users/{user_id}: Retrieves a user by their unique ID**
   
   **Response example**
   ```json
   {
     "name": "John Doe",
     "email": "john.doe@example.com",
     "dob": "1990-04-01",
     "income": 55000
   }

   ```

3. **POST /users/: Adds a new user to the database**

      **Response example**
   ```json
   {
     "message": "User created successfully"
   }

   ```
4. **PUT /users/{user_id}: Updates an existing user's data**
   
      **Response example**
   ```json
   {
     "message": "User updated successfully"
   }

   ```
 5. **DELETE /users/{user_id}: Removes a user from the database**
    
      **Response example**
   ```json
   {
     "message": "User deleted successfully"
   }

   ```
## Using Postman to Test the API
**Import the EconoMe.postman_collection.json into Postman to test the various endpoints.**
1. **Creating a User:**
   
   ```http
   POST /users/
   Content-Type: application/json
   
   {
     "name": "John Doe",
     "email": "john.doe@example.com",
     "dob": "1990-04-01",
     "income": 55000
   }
      ```


  
2. **Retrieve All Users:**
   
   ```http
   GET /users/

   ```

3. **Update a User:**

   ```http
   PUT /users/1
   Content-Type: application/json
   
   {
     "name": "Johnathan Doe",
     "email": "johnathan.doe@example.com",
     "dob": "1990-04-01",
     "income": 57000
   }

   ```
4. **Delete a User:**
   
   ```http
   DELETE /users/1

   ```
    
    
