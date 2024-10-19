from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy


# to view the database, install the sqlite extension from 'extensions'
# then, do cmd/ctr + shift + P (command palette), and then 'open database' ("instance/sql_database.db")
# in 'explorer' there should be a dropdown called 'sqlite explorer'
# a table called 'task' should be under the dropdown, click on that and click on play button
db = SQLAlchemy()


class Task(db.Model):  # task database model
    id = db.Column(db.Integer, primary_key=True)  # using integers as primary key
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
DB_NAME = "sql_database.db"
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # Set the URI for SQLAlchemy to connect to the SQLite database
db.init_app(app)  # Initialize SQLAlchemy instance (db) with Flask
AEST_OFFSET = timedelta(hours=10)  # Australia timezone

with app.app_context():
    db.create_all()  # Create all tables defined in the models
    usernames = ['admin', 'alicia', 'ryani', 'abi', 'thisangi', 'jaimee', 'xin']

    for username in usernames:
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username=username, password='123')
            db.session.add(new_user)
    db.session.commit()


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
    session.clear()  # clear session
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

        aest_time = datetime.utcnow() + AEST_OFFSET
        created_at = aest_time.strftime("%A %d %B, %I:%M %p")

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
    if 'username' in session and session['username'] == 'admin': # check if user logged in as admin
        new_username = request.form['new_username']
        new_password = request.form['new_password']
        existing_user = User.query.filter_by(username=new_username).first() # check if user with same username alrady exists
        if existing_user:
            flash('Username already exists', category='error')
        else:
            new_user = User(username=new_username, password=new_password) # create new user
            db.session.add(new_user)
            db.session.commit()
            flash('User created!', category='success')
        return redirect(url_for('create_user_page'))
    
@app.route('/change_username', methods=['POST'])
def change_username():
    if 'username' in session and session['username'] == 'admin':
        old_username = request.form['old_username'] # retrieve 'old' username
        new_username_change = request.form['new_username_change'] # retrieve new username
        user = User.query.filter_by(username=old_username).first()
        if user:
            if User.query.filter_by(username=new_username_change).first(): # check if username already exists in db
                flash('New username already exists', category='error')
            else:
                user.username = new_username_change # update username
                db.session.commit()
                flash('Username updated!', category='success')
        else:
            flash('Username not found', category='error') # if user with username doesn't exist
        return redirect(url_for('change_username_page'))
    
@app.route('/change_password', methods=['POST'])
def change_password():
    if 'username' in session and session['username'] == 'admin':
        username = request.form['username']
        new_password_change = request.form['new_password_change']
        user = User.query.filter_by(username=username).first() # find user by username
        if user:
            user.password = new_password_change
            db.session.commit()
            flash('Password updated!', category='success')
        else:
            flash('Username not found', category='error') # if user not found
        return redirect(url_for('change_password_page'))

if __name__ == '__main__':
    app.run(debug=True)
