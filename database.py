# File: database.py
import sqlite3
import datetime

# Define some dates for use in task deadlines
today = datetime.date.today()
twodays = datetime.date.today() + datetime.timedelta(days=2)
nextweek = datetime.date.today() + datetime.timedelta(days=8)

def create_connection():
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('todo_app.db')
    return conn

def list_tables():
    # List all tables in the database for debugging or informational purposes
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    
    # Print the names of all tables in the database
    for i in tables:
        print(i)

def reset_to_test_tables():
    # Drop existing tables and reset the database to a known state for testing
    conn = create_connection()
    cursor = conn.cursor()
    
    # Drop tables if they exist
    cursor.execute('DROP TABLE IF EXISTS task_categories')
    cursor.execute('DROP TABLE IF EXISTS categories')
    cursor.execute('DROP TABLE IF EXISTS tasks')
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS user')
    cursor.execute('DROP TABLE IF EXISTS task')
    
    # Recreate tables
    create_tables()
    
    # Insert test data into the database
    cursor.execute('''
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    ''', ('a', 'example_email', 'a'))
    cursor.execute('''
        INSERT INTO tasks (title, description, due_date, user_id, reminder, status, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('Submit Assignment', 'Biology group project', '2024-06-17', 1, str(today), 1, 'School'))
    cursor.execute('''
        INSERT INTO tasks (title, description, due_date, user_id, reminder, status, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('Charlie\'s Bday', 'Remember to buy a cake', '2024-06-17', 1, str(today), 1, 'Family'))
    cursor.execute('''
        INSERT INTO tasks (title, description, due_date, user_id, reminder, status, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('Pay tuition', 'pay online', '2024-06-17', 1, str(nextweek), 0, 'Bills'))
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()

def create_tables():
    # Create tables in the database if they do not already exist
    conn = create_connection()
    cursor = conn.cursor()
    
    # Create the 'users' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL, 
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Create the 'tasks' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            status INT,
            category TEXT,
            reminder DATE,
            user_id INTEGER,             
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create the 'categories' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    
    # Create the 'task_categories' table to link tasks and categories
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_categories (
            task_id INTEGER,
            category_id INTEGER,
            FOREIGN KEY(task_id) REFERENCES tasks(id),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()
