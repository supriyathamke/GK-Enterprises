import mysql.connector
from getpass import getpass

password = getpass("Enter your MySQL password: ")

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="gk_enterprises"
)

cursor = db.cursor()

cursor.execute("ALTER TABLE customers MODIFY email VARCHAR(150) NULL")
cursor.execute("ALTER TABLE customers MODIFY phone VARCHAR(15) NULL")

db.commit()

print("Database updated successfully!")

cursor.close()
db.close()