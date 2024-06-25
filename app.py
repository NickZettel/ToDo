# File: app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from models import Task, Category, User
from database import create_tables,create_connection,reset_to_test_tables,list_tables

list_tables()

# Initialize the Flask application
app = Flask(__name__)

STATIC_FOLDER = 'templates/assets'
app = Flask(__name__,static_folder=STATIC_FOLDER)

app.secret_key = 'your_secret_key_here'

reset_to_test_tables()

conn = create_connection()
cursor = conn.cursor()
cursor.execute('SELECT * FROM users')
results = cursor.fetchall()
conn.close

# Route for the home page which lists all tasks
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/category.html')
def category():
    return render_template('category.html')

@app.route('/tasklist')
def tasklistpage():
    tasks = session.get('tasks', [])  # Get tasks data from session, default to empty list if not present
    for i in tasks:
        for j in i:
            print('task', j)
    return render_template('tasklist.html', tasks=tasks)

@app.route('/edit', methods=['POST'])
def edit():
    print ('edit')
    task_id = request.form.get('task_id')
    task_name = request.form.get('task_name')
    category = request.form.get('category')
    due_date = request.form.get('due')
    description = request.form.get('description')
    reminder = request.form.get('reminder')
    user_id = session['user']
    
    print ('id',task_id)
    print ('name',task_name)
    print('category',category)
    print('due_date',due_date)
    print('description',description)
    print('reminder',reminder)
    
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET title = ?,
            description = ?,
            due_date = ?,
            category = ?,
            reminder = ?
        WHERE id = ?
    """, (task_name, description, due_date, category, reminder, task_id))

    conn.commit()
    
    tasks = User.get_tasks_for_user(user_id)
    session['tasks'] = tasks
    
    return redirect(url_for('tasklistpage', tasks=tasks))
    


@app.route('/delete', methods=['POST'])
def delete():
    task_id = request.form.get('task_id')
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    # Update the session tasks
    user_id = session['user']
    tasks = User.get_tasks_for_user(user_id)
    session['tasks'] = tasks
    return redirect(url_for('tasklistpage'))

@app.route('/add_task', methods=['POST'])
def add():
    task_name = request.form.get('task_name')
    category = request.form.get('category')
    due_date = request.form.get('due')
    description = request.form.get('description')
    reminder = request.form.get('reminder')
    user_id = session['user']   
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO tasks (title,description,due_date,category,reminder, user_id)
        VALUES (?,?,?,?,?,?)
    ''', (task_name,description,due_date,category,reminder,session['user']))  
    cursor.execute('SELECT * FROM tasks WHERE user_id = ?;', (user_id,))
    rows = cursor.fetchall()
    for i in rows:
        print ('row ',i)
    conn.commit()
    conn.close()
    tasks = User.get_tasks_for_user(user_id)
    session['tasks'] = tasks
    return redirect(url_for('tasklistpage', tasks=tasks))

@app.route('/loginpage.html', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        print ('login attempt')
        print (request.form)
        print (request.form)
        # Check username and password (mocked for demonstration)
        username = request.form['username']
        password = request.form['password']
        session.clear()
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        print (user)
        if user:
            user_id = user[0]  # Assuming the user ID is the first column in the users table
            tasks = User.get_tasks_for_user(user_id)  # Pass user ID to the method
            session['tasks'] = tasks
            session['user'] = user[0]
            print ('successfull login')
            print (tasks)
            return redirect(url_for('tasklistpage', tasks=tasks))
    #         'tasklistpage'
        if username == 'admin' and password == 'password':
            # Mocking tasks for the admin user
            tasks = ['Task 1', 'Description 1', 'Due Date 1', True, 'Category 1', 'Reminder 1']
            return redirect(url_for('tasklistpage', tasks=tasks))

        # Handle invalid login (e.g., display error message)
        return render_template('loginpage.html', error="Invalid username or password")
    print ('empty form')
    return render_template('loginpage.html')


@app.route('/signup.html', methods=['GET','POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cpass = request.form['cpass']
        
        if password != cpass: #if password does not match confirm password
            return redirect(url_for('create_user'))
        
        conn = create_connection() #if username is taken
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            conn.close()
            return redirect(url_for('create_user'))
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,)) #if email is taken
        user = cursor.fetchone()
        if user:
            conn.close()
            return redirect(url_for('create_user'))
        
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password)) #create new user
        conn.commit()
        
        conn.close()
        print (username,email,password,cpass)
        return redirect(url_for('login'))
    #GET
    return render_template('signup.html')

# Route to edit an existing task
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if request.method == 'POST':
        # Get the updated form data from the request
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        # Update the task in the database
        Task.update(task_id, title, description, due_date)
        # Redirect to the home page
        return redirect(url_for('index'))
    # Fetch the task details for the given task_id
    task = Task.get(task_id)
    # Render the edit_task.html template with the task details
    return render_template('edit_task.html', task=task)

# Route to delete a task
@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    # Delete the task from the database
    Task.delete(task_id)
    # Redirect to the home page
    return redirect(url_for('index', task_id=task_id))

# Route to mark a task as complete
@app.route('/complete/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    # Mark the task as complete in the database
    Task.mark_complete(task_id)
    # Redirect to the home page
    return redirect(url_for('index'))

# Route to manage task categories
@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        # Get the new category name from the form data
        name = request.form['name']
        # Create a new Category object and save it to the database
        category = Category(name)
        category.save()
        # Redirect to the categories management page
        return redirect(url_for('manage_categories'))
    # Fetch all categories from the database
    categories = Category.all()
    # Render the categories.html template with the list of categories
    return render_template('categories.html', categories=categories)

# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)
