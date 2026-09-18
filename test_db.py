from db_connection import get_connection

connection = get_connection()

if connection.is_connected():
    print("MySQL connection successful!")

connection.close()