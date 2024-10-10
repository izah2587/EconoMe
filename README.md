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

1. **Clone this repository** or download the source code.

   ```bash
   git clone https://github.com/your-username/your-repository.git

2. **Navigate to the project directory:**

    ```bash
    cd path/to/your-repository

3. **Set Up a Virtual Environment (Optional but Recommended)**

   
   python -m venv .venv

    **On Windows:**

   ```bash
    .venv\Scripts\activate


   **On macOS and Linux:**

    ```bash
    Copy code
    source .venv/bin/activate

5. **Install Required Packages**
    Once the virtual environment is activated, install the necessary dependencies from the requirements.txt file:

    bash
    Copy code
    pip install -r requirements.txt
   
6. **Set Up Your .env File**
    To securely store your MySQL database credentials, you need to set up a .env file in the root of the project directory:

    Create a new .env file in the project root:

    bash
    Copy code
    touch .env
    Open the .env file in a text editor and add your MySQL connection details in the following format:

    bash
    Copy code

   - **DB_HOST=your_mysql_host**
   - **DB_USER=your_mysql_username**
   - **DB_PASS=your_mysql_password**
   - **DB_NAME=your_database_name**
    Replace the placeholders with your actual MySQL connection details.

    Note: The .env file contains sensitive information. Make sure it's included in your .gitignore file to prevent it from being committed to version control. 

7. **Add .env to .gitignore**
    Ensure the .env file is excluded from version control by adding it to your .gitignore file. If you don't have a .gitignore file, create one and add the following line:

    bash
    Copy code
    .env
    This will prevent the .env file from being accidentally pushed to the repository.

8. **Run the Application**
    Once everything is set up, you can run the Python script to create tables, populate them with sample data, and export the data to CSV files:

    bash
    Copy code
    python main.py
    What Happens When You Run the Application:
    Creates tables: The application will create the Users, Goals, Expenses, and Marketplace tables in your MySQL database.
    Populates tables: Inserts sample data into each table.
    Exports data to CSV: Exports the contents of each table into a CSV file, saving the files as Users.csv, Goals.csv, Expenses.csv, and Marketplace.csv in the project directory.

9. **Deactivate the Virtual Environment (Optional)**
    If you're done working on the project and want to deactivate the virtual environment, you can run:

    bash
    Copy code
    deactivate
