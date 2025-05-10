import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # kalo pake pw  MySQL
        database="radio_untar"
    )
