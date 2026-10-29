
from app import get_db_connection

connection = get_db_connection()
cursor = connection.cursor()

cursor.execute("DESCRIBE jobs")

for column in cursor.fetchall():
    print(column)

cursor.close()
connection.close()
