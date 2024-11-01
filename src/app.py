from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# --- Configuration Class ---
class Config:
    SECRET_KEY = 'secret key'  # Use a secure random key in production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sql_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# --- Create Database Models ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    story_point = db.Column(db.Integer, nullable=False)
    development_bit_vector = db.Column(db.String(5), nullable=False)
    priority_tag = db.Column(db.String(9), nullable=False)
    progress_tag = db.Column(db.String(11), nullable=False)
    user = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.String(100), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


# --- Initialise App ---
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()  # Create all tables defined in the models
    usernames = ['admin', 'Alicia', 'Ryani', 'Abi', 'Thisangi', 'Jaimee', 'Xin']

    for username in usernames:
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username=username, password=generate_password_hash('123').decode('utf-8'))
            db.session.add(new_user)
    db.session.commit()


# --- User management ---
def get_current_user():
    """
    Retrieve the currently logged-in user from the session.

    Returns:
        str: Username of the current user, or None if no user is logged in.
    """
    return session.get('username')


def is_logged_in():
    """
    Check if a user is currently logged in.

    Returns:
        Redirects to login page if not logged in.
    """
    return 'username' in session


def is_admin():
    """
    Check if the current user is an administrator.

    Returns:
        bool: True if the current user is 'admin', otherwise False.
    """
    return get_current_user() == 'admin'


def check_user_exists(user: str) -> bool:
    """
    Check if a user with the given username exists in the database.

    Args:
        user (str): The username to search for.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    return User.query.filter_by(username=user).first() is not None


# --- Flash and Redirect
def flash_and_redirect(message, category, redirect_page):
    """
    Flash a message to the user and redirect to a specified page.

    Args:
        message (str): The message to display (e.g., 'Login successful!').
        category (str): Message category ('success' or 'error').
        redirect_page (str): Name of the route to redirect to (e.g., 'home').

    Returns:
        Response: A Flask redirect response to the given page.
    """
    flash(message, category)
    return redirect(url_for(redirect_page))


# --- Time Handling ---
def get_aest_time():
    """
    Get the current time in the Australia/Melbourne timezone, formatted as:
    'Full weekday name, day of the month, full month name, hour:minute AM/PM'.

    Example:
        Sunday 20 October, 09:15 PM

    Returns:
        str: The formatted current date and time in AEST.
    """
    return datetime.now(ZoneInfo('Australia/Melbourne')).strftime('%A %d %B, %I:%M %p')


# --- Database ---
def add_to_db(instance) -> None:
    """
    Add an instance to the database session and commit the changes.

    Args:
        instance (db.Model): The model instance to add and commit.
    """
    db.session.add(instance)
    db.session.commit()


def delete_from_db(instance):
    """
    Delete a model instance from the database and commit the changes.

    Args:
        instance (db.Model): The model instance to delete.
    """
    db.session.delete(instance)
    db.session.commit()


def get_model_instance(model, **kwargs):
    """
    Retrieve the first instance of a model that matches the given filter criteria.

    Args:
        model (db.Model): The SQLAlchemy model to query.
        **kwargs: Column-value pairs to filter by (e.g., username='admin').

    Returns:
        db.Model: The first matching model instance, or None if no match is found.
    """
    return model.query.filter_by(**kwargs).first()


def update_model_instance(instance, data: dict):
    """
    Update a model instance with the provided data.

    Args:
        instance (db.Model): The model instance to update.
        data (dict): A dictionary of attributes to update (e.g., {'title': 'New Title'}).
    """
    for key, value in data.items():
        if hasattr(instance, key):
            setattr(instance, key, value)
    db.session.commit()


# --- Task Management ---
def validate_task_data(data: dict) -> tuple[bool, str]:
    """
    Validate task data for required fields.

    Args:
        data (dict): Task data from the request.

    Returns:
        tuple[bool, str]: (True, "") if valid; (False, "Error message") if invalid.
    """
    required_fields = ['title', 'description', 'priority_tag', 'progress_tag', 'development_bit_vector']
    for field in required_fields:
        if not data.get(field):
            return False, f"'{field}' is required."
    return True, "Added task"


def get_task_schema(task):
    """
    Convert a Task model instance to a dictionary format.

    Args:
        task (Task): A task model instance.

    Returns:
        dict: A dictionary representation of the task.
    """
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'story_point': task.story_point,
        'development_bit_vector': task.development_bit_vector,
        'priority_tag': task.priority_tag,
        'progress_tag': task.progress_tag,
        'user': task.user,
        'created_at': task.created_at
    }


def get_tasks_list():
    """
    Retrieve all tasks from the database and return them in dictionary format.

    Returns:
        list[dict]: A list of all tasks in dictionary format.
    """
    tasks = Task.query.all()
    return [get_task_schema(task) for task in tasks]


# --- Routing ---
@app.route('/')
def home():
    """
    Render the home page if the user is logged in, otherwise redirect to the login page.

    :return: Rendered template for the home page or redirect to log in.
    """
    if is_logged_in():
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login by verifying credentials and managing session state.

    :return: Rendered login page or redirect to home page upon successful login.
    """
    if request.method == 'POST':
        form_username = request.form['username']
        password = request.form.get('password')

        user: User = User.query.filter_by(username=form_username).first()

        if not user:
            flash('Username does not exist', category='error')

        if check_password_hash(user.password, password):
            session['username'] = form_username
            session['from_login'] = True
            flash_and_redirect('Login successful!', 'success', 'home')
        else:
            flash('Incorrect password, please try again', category='error')
    return render_template('index.html')


@app.route('/logout')
def logout():
    """
    Clear the user session and redirect to the login page.

    :return: Redirect to the login page.
    """
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin')
def admin_page():
    """
    Render the admin page if the user is logged in and is an admin.

    :return: Rendered admin page or redirect to log in if unauthorized.
    """
    if is_logged_in() and is_admin():
        if session.get('from_login'):
            session.pop('_flashes', None)
            session.pop('from_login')
        return render_template('admin.html')


@app.route('/create-user')
def create_user_page():
    """
    Render the create user page if the user is logged in and is an admin.

    :return: Rendered create user page or redirect to log in if unauthorized.
    """
    if is_logged_in() and is_admin():
        return render_template('create_user.html')
    return redirect(url_for('login'))


@app.route('/change-username')
def change_username_page():
    """
    Render the change username page if the user is logged in and is an admin.

    :return: Rendered change username page or redirect to log in if unauthorized.
    """
    if is_logged_in() and is_admin():
        return render_template('change_username.html')
    return redirect(url_for('login'))


@app.route('/change-password')
def change_password_page():
    """
    Render the change password page if the user is logged in and is an admin.

    :return: Rendered change password page or redirect to log in if unauthorized.
    """
    if is_logged_in() and is_admin():
        return render_template('change_password.html')
    return redirect(url_for('login'))


@app.route('/add_task', methods=['POST'])
def add_task():
    """
    Add a new task to the database after validating the request data.

    :return: JSON response with the created task data or an error message.
    """
    try:
        data = request.get_json()
        is_valid, message = validate_task_data(data)
        if not is_valid:
            return jsonify({'error': message}), 400

        new_task = Task(
            title=data['title'],
            description=data['description'],
            story_point=data.get('story_point', 0),
            development_bit_vector=data['development_bit_vector'],
            priority_tag=data['priority_tag'],
            progress_tag=data['progress_tag'],
            user=get_current_user(),
            created_at=get_aest_time()
        )

        add_to_db(new_task)

        return jsonify(get_task_schema(new_task)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Delete a task from the database based on the task ID.

    :param task_id: The ID of the task to delete.
    :return: JSON response with the list of remaining tasks.
    """
    task = Task.query.get(task_id)
    if task:
        delete_from_db(task)
    return get_tasks()  # Assuming this function returns the updated task list.


@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    """
    Retrieve and return a list of all tasks in JSON format.

    :return: JSON response containing the list of tasks.
    """
    tasks = get_tasks_list()
    return jsonify({'tasks': tasks})


@app.route('/get_task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    Retrieve and return a specific task by its ID.

    :param task_id: The ID of the task to retrieve.
    :return: JSON response with the task data or an error message if not found.
    """
    task = Task.query.get(task_id)
    if task:
        return jsonify(get_task_schema(task))
    return jsonify({'error': 'Task not found'}), 404


@app.route('/edit_task/<int:task_id>', methods=['PUT'])
def edit_task(task_id):
    """
    Edit an existing task based on the task ID and provided data.

    :param task_id: The ID of the task to edit.
    :return: JSON response with the updated task data or an error message.
    """
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        data = request.get_json()
        update_model_instance(task, data)

        return jsonify(get_task_schema(task))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/create_user', methods=['POST'])
def create_user():
    """
    Create a new user with the provided username and password.

    :return: Redirect to the create user page with appropriate flash messages.
    """
    if is_logged_in() and is_admin():
        new_username = request.form['new_username']
        new_password = request.form['new_password']
        if check_user_exists(new_username):
            flash('Username already exists', category='error')
        else:
            user_to_create = User(username=new_username, password=new_password)
            add_to_db(user_to_create)
            flash('User created!', category='success')
        return redirect(url_for('create_user_page'))


@app.route('/change_username', methods=['POST'])
def change_username():
    """
    Change an existing user's username.

    :return: Redirect to the change username page with appropriate flash messages.
    """
    if is_logged_in() and is_admin():
        old_username = request.form['old_username']
        new_username_change = request.form['new_username_change']
        user = get_model_instance(User, username=old_username)
        if user:
            if check_user_exists(new_username_change):
                flash('New username already exists', category='error')
            else:
                user.username = new_username_change
                db.session.commit()
                flash('Username updated!', category='success')
        else:
            flash('Username not found', category='error')
        return redirect(url_for('change_username_page'))


@app.route('/change_password', methods=['POST'])
def change_password():
    """
    Change an existing user's password.

    :return: Redirect to the change password page with appropriate flash messages.
    """
    if is_logged_in() and is_admin():
        form_username = request.form['username']
        new_password_change = request.form['new_password_change']
        user = get_model_instance(User, username=form_username)
        if user:
            user.password = new_password_change
            db.session.commit()
            flash('Password updated!', category='success')
        else:
            flash('Username not found', category='error')
        return redirect(url_for('change_password_page'))


if __name__ == '__main__':
    app.run(debug=True)
