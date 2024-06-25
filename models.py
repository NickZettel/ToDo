from database import create_connection

# Task model to represent tasks in the database
class Task:
    def __init__(self, title, description, due_date):
        self.title = title
        self.description = description
        self.due_date = due_date

    # Method to save a new task to the database
    def save(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, description, due_date)
            VALUES (?, ?, ?)
        ''', (self.title, self.description, self.due_date))
        conn.commit()
        conn.close()

    # Static method to update an existing task in the database
    @staticmethod
    def update(task_id, title, description, due_date):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks
            SET title = ?, description = ?, due_date = ?
            WHERE id = ?
        ''', (title, description, due_date, task_id))
        conn.commit()
        conn.close()

    # Static method to delete a task from the database
    @staticmethod
    def delete(task_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM tasks
            WHERE id = ?
        ''', (task_id,))
        conn.commit()
        conn.close()

    # Static method to mark a task as complete in the database
    @staticmethod
    def mark_complete(task_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks
            SET is_complete = 1
            WHERE id = ?
        ''', (task_id,))
        conn.commit()
        conn.close()

    # Static method to fetch all tasks from the database
    @staticmethod
    def all():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()
        conn.close()
        return tasks

    # Static method to fetch a single task by its ID from the database
    @staticmethod
    def get(task_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        conn.close()
        return task

# Category model to represent task categories in the database
class Category:
    def __init__(self, name):
        self.name = name

    # Method to save a new category to the database
    def save(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO categories (name)
            VALUES (?)
        ''', (self.name,))
        conn.commit()
        conn.close()

    # Static method to fetch all categories from the database
    @staticmethod
    def all():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories')
        categories = cursor.fetchall()
        conn.close()
        return categories

class User:
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def add_user(username, email, password):
        conn = create_connection()
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user(username):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user
    @staticmethod
    
    def get_tasks_for_user(user_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
        tasks = cursor.fetchall()
        conn.close()
        return tasks
