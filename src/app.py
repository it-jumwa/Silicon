from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug import Response

db = SQLAlchemy()


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


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'  # setting a secret key for encrypting session data and cookies
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sql_database.db'
db.init_app(app)

with app.app_context():
    db.create_all()  # Create all tables defined in the models
    usernames = ['admin', 'alicia', 'ryani', 'abi', 'thisangi', 'jaimee', 'xin']

    for username in usernames:
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username=username, password='123')
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


def is_logged_in() -> Response:
    """
    Check if a user is currently logged in.

    Returns:
        Response: Redirects to login page if not logged in.
    """
    if 'username' not in session:
        return redirect(url_for('login'))


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
    if 'username' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))


# for logging in, enter either your first name in lowercase (e.g. 'alicia') or 'abc' for the username, and '123' for the password
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form.get('password')

        user: User = User.query.filter_by(username=username).first()  # query the username
        if user:  # if username exists in database
            if user.password == password:  # correct password
                flash('Login successful!', category='success')
                session['username'] = username  # store username in session
                session['from_login'] = True
                return redirect(url_for('home'))  # redirect to home page
            else:
                flash('Incorrect password, please try again', category='error')  # incorrect password
        else:  # username does not exist
            flash('Username does not exist', category='error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin')
def admin_page():
    if 'username' in session and session['username'] == 'admin':
        if session.get('from_login'):
            session.pop('_flashes', None)
            session.pop('from_login')
        return render_template('admin.html')


@app.route('/create-user')
def create_user_page():
    if 'username' in session and session['username'] == 'admin':
        return render_template('create_user.html')
    return redirect(url_for('login'))


@app.route('/change-username')
def change_username_page():
    if 'username' in session and session['username'] == 'admin':
        return render_template('change_username.html')
    return redirect(url_for('login'))


@app.route('/change-password')
def change_password_page():
    if 'username' in session and session['username'] == 'admin':
        return render_template('change_password.html')
    return redirect(url_for('login'))


@app.route('/add_task', methods=['POST'])
def add_task():
    try:
        # Get the task data from the AJAX request
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        story_point = data.get('story_point') or 0
        development_bit_vector = data.get('development_bit_vector')
        priority_tag = data.get('priority_tag')
        progress_tag = data.get('progress_tag')
        user = session.get('username')

        created_at = get_aest_time()

        new_task = Task(title=title, description=description, story_point=story_point,
                        development_bit_vector=development_bit_vector,
                        priority_tag=priority_tag, progress_tag=progress_tag, user=user, created_at=created_at)

        db.session.add(new_task)  # Add the new task to the SQLAlchemy session
        db.session.commit()  # Commit to database

        # Return the newly added task as JSON
        return jsonify({
            'id': new_task.id,
            'title': new_task.title,
            'description': new_task.description,
            'story_point': new_task.story_point,
            'development_bit_vector': new_task.development_bit_vector,
            'priority_tag': new_task.priority_tag,
            'progress_tag': new_task.progress_tag,
            'user': new_task.user,
            'created_at': new_task.created_at
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)  # Get task via id
    if task:
        db.session.delete(task)
        db.session.commit()
    # Returns the list of tasks even if it has not been found
    tasks_list = get_tasks()
    return jsonify(tasks_list)  # Return the list of tasks as JSON


@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    tasks_list = [{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'story_point': task.story_point,
        'development_bit_vector': task.development_bit_vector,
        'priority_tag': task.priority_tag,
        'progress_tag': task.progress_tag,
        'user': task.user,
        'created_at': task.created_at
    } for task in tasks]
    return jsonify({'tasks': tasks_list})


@app.route('/get_task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task:
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'story_point': task.story_point,
            'development_bit_vector': task.development_bit_vector,
            'priority_tag': task.priority_tag,
            'progress_tag': task.progress_tag,
            'user': task.user,
            'created_at': task.created_at
        })
    return jsonify({'error': 'Task not found'}), 404


@app.route('/edit_task/<int:task_id>', methods=['PUT'])
def edit_task(task_id):
    try:
        # Get the task from the database
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        # Get the updated data from the request
        data = request.get_json()
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.story_point = data.get('story_point', task.story_point)
        task.development_bit_vector = data.get('development_bit_vector', task.development_bit_vector)
        task.priority_tag = data.get('priority_tag', task.priority_tag)
        task.progress_tag = data.get('progress_tag', task.progress_tag)

        # Save the changes to the database
        db.session.commit()

        # Return the updated task as JSON
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'story_point': task.story_point,
            'development_bit_vector': task.development_bit_vector,
            'priority_tag': task.priority_tag,
            'progress_tag': task.progress_tag,
            'user': task.user,
            'created_at': task.created_at
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/create_user', methods=['POST'])
def create_user():
    if 'username' in session and session['username'] == 'admin':  # check if user logged in as admin
        new_username = request.form['new_username']
        new_password = request.form['new_password']
        existing_user = User.query.filter_by(
            username=new_username).first()  # check if user with same username alrady exists
        if existing_user:
            flash('Username already exists', category='error')
        else:
            new_user = User(username=new_username, password=new_password)  # create new user
            db.session.add(new_user)
            db.session.commit()
            flash('User created!', category='success')
        return redirect(url_for('create_user_page'))


@app.route('/change_username', methods=['POST'])
def change_username():
    if 'username' in session and session['username'] == 'admin':
        old_username = request.form['old_username']  # retrieve 'old' username
        new_username_change = request.form['new_username_change']  # retrieve new username
        user = User.query.filter_by(username=old_username).first()
        if user:
            if User.query.filter_by(username=new_username_change).first():  # check if username already exists in db
                flash('New username already exists', category='error')
            else:
                user.username = new_username_change  # update username
                db.session.commit()
                flash('Username updated!', category='success')
        else:
            flash('Username not found', category='error')  # if user with username doesn't exist
        return redirect(url_for('change_username_page'))


@app.route('/change_password', methods=['POST'])
def change_password():
    if 'username' in session and session['username'] == 'admin':
        username = request.form['username']
        new_password_change = request.form['new_password_change']
        user = User.query.filter_by(username=username).first()  # find user by username
        if user:
            user.password = new_password_change
            db.session.commit()
            flash('Password updated!', category='success')
        else:
            flash('Username not found', category='error')  # if user not found
        return redirect(url_for('change_password_page'))


if __name__ == '__main__':
    app.run(debug=True)
