
import getpass
import mysql.connector

# Enter your MySQL login details
mysql_user = input("Enter MySQL username (usually root): ").strip()
if not mysql_user:
    mysql_user = "root"

mysql_password = getpass.getpass("Enter MySQL password: ")

connection = None
cursor = None

try:
    # Connect to MySQL Server
    connection = mysql.connector.connect(
        host="localhost",
        user=mysql_user,
        password=mysql_password
    )

    cursor = connection.cursor()

    # Create the project database
    cursor.execute("CREATE DATABASE IF NOT EXISTS gk_enterprises")
    cursor.execute("USE gk_enterprises")

    # Create the customer registration table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            phone VARCHAR(15) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print("\nDatabase created or already exists!")
    print("Customer table created or already exists!")
    print("G.K. Enterprises database setup completed.")

except mysql.connector.Error as error:
    print("\nMySQL error:", error)
    print("Check your username, password and MySQL permissions.")

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()
