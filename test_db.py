
import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kashish17@",
        database="smarthire",
        port=3306
    )

    if connection.is_connected():
        print("MySQL connection successful!")
        print("SmartHire database connected.")

    connection.close()

except mysql.connector.Error as error:
    print("Connection failed:", error)
