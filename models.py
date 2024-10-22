from database import create_connection

class Task:
    def __init__(self, title, description, due_date, category, reminder, user_id):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.category = category
        self.reminder = reminder
        self.user_id = user_id

    # Method to save a new task to the database
    def save(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, description, due_date, category, reminder, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.title, self.description, self.due_date, self.category, self.reminder, self.user_id))
        conn.commit()
        conn.close()

    # Static method to update an existing task in the database
    @staticmethod
    def update(task_id, title, description, due_date, category, reminder):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks
            SET title = ?, description = ?, due_date = ?, category = ?, reminder = ?
            WHERE id = ?
        ''', (title, description, due_date, category, reminder, task_id))
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
            SET status = 1
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
        # Initialize a User object with ID, username, email, and password
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def add_user(username, email, password):
        # Add a new user to the database
        conn = create_connection()
        cursor = conn.cursor()
        
        # Insert user details into the 'users' table
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        
        # Commit the transaction to save changes and close the connection
        conn.commit()
        conn.close()

    @staticmethod
    def get_user(username):
        # Retrieve user details from the database based on the username
        conn = create_connection()
        cursor = conn.cursor()
        
        # Query the 'users' table for the user with the given username
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        # Close the database connection and return the user details
        conn.close()
        return user

    @staticmethod
    def get_tasks_for_user(user_id):
        # Retrieve all tasks associated with a given user ID
        conn = create_connection()
        cursor = conn.cursor()
        
        # Query the 'tasks' table for tasks that belong to the specified user
        cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
        tasks = cursor.fetchall()
        
        # Close the database connection and return the list of tasks
        conn.close()
        return tasks
