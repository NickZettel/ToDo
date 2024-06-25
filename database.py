# File: database.py
import sqlite3

def create_connection():
    conn = sqlite3.connect('todo_app.db')
    return conn


def list_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    for i in tables:
        print (i)

def reset_to_test_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS task_categories')
    cursor.execute('DROP TABLE IF EXISTS categories')
    cursor.execute('DROP TABLE IF EXISTS tasks')
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS user')
    cursor.execute('DROP TABLE IF EXISTS task')
    
    create_tables()
    
    cursor.execute('''
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    ''', ('a', 'example_email', 'a'))
    cursor.execute('''
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    ''', ('b', 'example_email2', 'b'))
    cursor.execute('''
        INSERT INTO tasks (title,
            description,
            due_date,
            status,
            category,
            reminder,
            user_id)
        VALUES (?,?,?,?,?,?,?)
    ''', ('title1', 'description1', '2024-06-17',0,'category1','2024-06-18',1))
    cursor.execute('''
        INSERT INTO tasks (title,
            description,
            due_date,
            status,
            category,
            reminder,
            user_id)
        VALUES (?,?,?,?,?,?,?)
    ''', ('title2', 'description2', '2024-06-11',1,'category2','2024-06-19',1))
    
    conn.commit()
    conn.close()
    
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL, 
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_categories (
            task_id INTEGER,
            category_id INTEGER,
            FOREIGN KEY(task_id) REFERENCES tasks(id),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')
    conn.commit()
    conn.close()