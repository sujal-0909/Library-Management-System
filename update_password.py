#!/usr/bin/env python3
import bcrypt
import pymysql

# Generate password hash
password = "password"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Connect to database
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='sujal179',
    database='library_management'
)

try:
    with connection.cursor() as cursor:
        # Update admin password
        cursor.execute("UPDATE members SET password = %s WHERE username = 'admin'", (hashed,))
        connection.commit()
        print("Admin password updated successfully!")
        
        # Verify the update
        cursor.execute("SELECT username, password FROM members WHERE username = 'admin'")
        result = cursor.fetchone()
        print(f"Admin user: {result[0]}, Password hash: {result[1][:50]}...")
        
finally:
    connection.close()

