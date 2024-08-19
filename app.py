# File: app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from models import Task, Category, User
from database import create_tables, create_connection, reset_to_test_tables, list_tables
import datetime

# Get today's date
today = datetime.date.today()

# List the tables in the database (for debugging or initial setup purposes)
list_tables()

# Initialize the Flask application
app = Flask(__name__)

# Specify the folder for static files (e.g., CSS, JavaScript, images)
STATIC_FOLDER = 'templates/assets'
app = Flask(__name__, static_folder=STATIC_FOLDER)

# Set the secret key for session management
app.secret_key = 'your_secret_key_here'

# Reset the database to its test tables (for development or testing)
reset_to_test_tables()

# Establish a connection to the database
conn = create_connection()
cursor = conn.cursor()

# Retrieve all users from the database
cursor.execute('SELECT * FROM users')
results = cursor.fetchall()

# Close the database connection
conn.close()

@app.route('/logout', methods=['GET'])
def logout():
    # Clear all session data to log out the user
    session.clear()
    
    # Redirect the user to the index page after logging out
    return redirect(url_for('index'))

# Route for the home page which lists all tasks
@app.route('/')
def index():
    # Render the index.html template with the list of tasks
    return render_template('index.html')

@app.route('/see_reminders', methods=['GET'])
def see():
    # Update session to reset the 'reminded' flag to False
    session['reminded'] = False
    
    # Return a JSON response indicating that the session has been updated
    return jsonify({'message': 'Session updated'})

@app.route('/sort_by', methods=['GET'])
def sort_by():
    # Retrieve the 'category' parameter from the query string
    category = request.args.get('category')
    
    # Store the 'category' in the session under the 'sort_by' key
    session['sort_by'] = category
    
    # Redirect the user to the task list page to reflect the sorting change
    return redirect(url_for('tasklistpage'))


@app.route('/tasklist')
def tasklistpage():
    # Retrieve tasks from the session, defaulting to an empty list if not present
    tasks = session.get('tasks', [])  
    
    # Temporary list to hold tasks that match the sort criteria
    temp_holder = []
    
    try:
        # Reorder tasks based on the sorting criteria stored in the session
        for i in reversed(range(len(tasks))):
            if tasks[i][5] == session['sort_by']:
                temp_holder.append(tasks.pop(i))
    except:
        # Handle any errors that occur during reordering
        pass
    
    # Combine the reordered tasks with the remaining tasks
    tasks = temp_holder + tasks
    
    # Extract unique categories from the tasks
    categories = list(set(task[5] for task in tasks))
    
    # List to hold tasks that are due today
    approachingTasks = []
    
    # Get today's date
    today = datetime.date.today()
    
    # Identify tasks that are due today
    for i in tasks:
        date_obj = datetime.datetime.strptime(i[6], "%Y-%m-%d").date()
        if date_obj == today:
            approachingTasks.append(i)
    
    # Check if the user has already been reminded
    if not session.get('reminded'):
        
        # Mark the user as reminded in the session
        session['reminded'] = True
        
        # Render the task list page with tasks, approaching tasks, and categories
        return render_template('tasklist.html', tasks=tasks, approachingTasks=approachingTasks, categories=categories)
    else:
        # Clear approaching tasks if the user has already been reminded
        approachingTasks = []
        
        # Render the task list page with tasks and categories
        return render_template('tasklist.html', tasks=tasks, approachingTasks=approachingTasks, categories=categories)


@app.route('/edit', methods=['POST'])
def edit():
    
    # Retrieve task details from the form submission
    task_id = request.form.get('task_id')
    task_name = request.form.get('task_name')
    category = request.form.get('category')
    due_date = request.form.get('due')
    description = request.form.get('description')
    reminder = request.form.get('reminder')
    
    # Retrieve the current user ID from the session
    user_id = session['user']

    # Establish a connection to the database
    with create_connection() as conn:
        cursor = conn.cursor()
        
        # Execute the SQL command to update the task details
        cursor.execute("""
            UPDATE tasks
            SET title = ?,
                description = ?,
                due_date = ?,
                category = ?,
                reminder = ?
            WHERE id = ?
        """, (task_name, description, due_date, category, reminder, task_id))
        
        # Commit the transaction to save changes
        conn.commit()

    # Retrieve the updated list of tasks for the current user
    tasks = User.get_tasks_for_user(user_id)
    
    # Update the session with the new list of tasks
    session['tasks'] = tasks
    
    # Redirect to the task list page with the updated tasks
    return redirect(url_for('tasklistpage', tasks=tasks))


# Route to mark a task as complete
@app.route('/mark_complete', methods=['POST'])
def mark_complete():
    
    # Retrieve the list of task IDs from the form submission
    task_ids = request.form.getlist('task_id') 
    
    # Establish a connection to the database
    conn = create_connection()
    cursor = conn.cursor()
    
    for i in task_ids:
        try:
            # Fetch the current status of the task
            cursor.execute('SELECT status FROM tasks WHERE id = ?', (i,))
            current_status = cursor.fetchone()
            
            # Check if the task status was retrieved
            if current_status is not None:
                # Toggle the status between 0 and 1
                new_status = 0 if current_status[0] == 1 else 1
                
                # Update the task status in the database
                cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (new_status, i))
                # Commit the transaction to save changes
                conn.commit()
        
        except Exception as e:
            # Handle any exceptions that occur during the update
            print(f"Error updating task status: {e}")
            pass
    
    # Retrieve the updated list of tasks for the current user
    tasks = User.get_tasks_for_user(session['user'])
    # Update the session with the new list of tasks
    session['tasks'] = tasks

    # Redirect to the task list page
    return redirect(url_for('tasklistpage'))


@app.route('/delete', methods=['POST'])
def delete():
    
    # Retrieve list of task IDs from the form submission
    task_ids = request.form.getlist('task_id')  
    
    # Convert list of task IDs to a string and remove commas
    task_ids = str(task_ids)
    task_ids = task_ids.replace(",", "")

    # Establish a connection to the database
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        # Iterate through each task ID and delete the corresponding task from the database
        for i in task_ids:
            cursor.execute('DELETE FROM tasks WHERE id = ?', (i,))
        # Commit the transaction to save changes
        conn.commit()
    except Exception as e:
        # Rollback the transaction in case of an error
        conn.rollback()
        print(f"Error deleting tasks: {e}")
    finally:
        # Close the database connection
        conn.close()

    # Retrieve updated list of tasks for the current user and update the session
    tasks = User.get_tasks_for_user(session['user'])
    session['tasks'] = tasks

    # Redirect to the task list page
    return redirect(url_for('tasklistpage'))


@app.route('/add_task', methods=['POST'])
def add():
    # Retrieve task details from the form submission
    task_name = request.form.get('task_name')
    category = request.form.get('category')
    due_date = request.form.get('due')
    description = request.form.get('description')
    reminder = request.form.get('reminder')
    
    # Retrieve the current user ID from the session
    user_id = session['user']   
    
    # Establish a connection to the database
    conn = create_connection()
    cursor = conn.cursor()
    
    # Insert the new task into the 'tasks' table
    cursor.execute('''
    INSERT INTO tasks (title, description, due_date, category, reminder, user_id)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (task_name, description, due_date, category, reminder, user_id))  
    
    # Query the database to fetch all tasks for the current user
    cursor.execute('SELECT * FROM tasks WHERE user_id = ?;', (user_id,))
    rows = cursor.fetchall()
    
    
    # Commit the transaction to save changes and close the connection
    conn.commit()
    conn.close()
    
    # Retrieve updated tasks for the user and store them in the session
    tasks = User.get_tasks_for_user(user_id)
    session['tasks'] = tasks
    
    # Redirect to the task list page with the updated tasks
    return redirect(url_for('tasklistpage', tasks=tasks))



@app.route('/loginpage.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve username and password from the form submission
        username = request.form['username']
        password = request.form['password']
        
        # Clear any existing session data
        session.clear()

        # Establish a connection to the database
        with create_connection() as conn:
            cursor = conn.cursor()
            # Query the database for a user with the provided username and password
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()

        # Check if a user was found with the given credentials
        if user:
            # Extract the user ID (assuming it's the first column in the result)
            user_id = user[0]
            
            # Retrieve tasks for the user and store them in the session
            tasks = User.get_tasks_for_user(user_id)
            session['tasks'] = tasks
            session['user'] = user[0]
            
            # Redirect the user to the task list page
            return redirect(url_for('tasklistpage', tasks=tasks))

        # Render the login page with an error message if the credentials are invalid
        return render_template('loginpage.html', error="Invalid username or password")

    # Render the login page for GET requests
    return render_template('loginpage.html')


@app.route('/signup.html', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        # Retrieve user information from the form submission
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cpass = request.form['cpass']
        
        # Check if the password and confirm password match
        if password != cpass:
            # Redirect to the signup page if passwords do not match
            return redirect(url_for('create_user'))
        
        # Establish a connection to the database
        conn = create_connection()
        cursor = conn.cursor()
        
        # Check if the username is already taken
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            conn.close()
            # Redirect to the signup page if username is already taken
            return redirect(url_for('create_user'))
        
        # Check if the email is already taken
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user:
            conn.close()
            # Redirect to the signup page if email is already taken
            return redirect(url_for('create_user'))
        
        # Insert the new user into the database
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        conn.commit()
        
        # Close the database connection
        conn.close()
        
        # Redirect to the login page after successful signup
        return redirect(url_for('login'))
    
    # Render the signup page for GET requests
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
