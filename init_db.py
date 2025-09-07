# init_db.py
import sqlite3

# Connect to the database file (it will be created if it doesn't exist)
connection = sqlite3.connect('database.db')

# Open the schema.sql file and execute the commands within it
with open('schema.sql') as f:
    connection.executescript(f.read())

print("Database has been initialized successfully.")
connection.close()