import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='34.44.42.132',
        user='econome',
        password=')Leb}|JtH0D4b4xh',
        database='econome'
    )

    if connection.is_connected():
        print("Connected to MySQL database")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM EconoMe")  # Replace with your table name
        result = cursor.fetchall()

        for row in result:
            print(row)

except Error as e:
    print("Error while connecting to MySQL", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
