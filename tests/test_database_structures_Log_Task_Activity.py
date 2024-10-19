from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from src.project_management.Activity import Activity  # Import Activity model
from src.project_management.Log import Log
from src.app import User  # Import User and Task models from app.py

# Initialize Flask app without starting the server
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Use your actual DB URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def setup_database():
    """
    Creates all database tables and adds initial data if necessary.
    """
    with app.app_context():  # Ensure app context for SQLAlchemy operations
        # Create all tables
        db.create_all([Activity, Log, User])

        # Example of adding initial data
        if not User.query.first():
            new_user = User(username='test_user', password='password123')
            db.session.add(new_user)
            db.session.commit()

        print("Database tables created and initial data added.")

def run_queries():
    """
    Perform database queries or manipulations here.
    """
    return True

def reset_database():
    """
    Drop all tables and recreate the database.
    """
    with app.app_context():
        db.drop_all()  # Drop all existing tables
        db.create_all()  # Recreate all tables
        print("Database has been reset.")

if __name__ == "__main__":
    # Run any of the database-related functions as needed
    setup_database()  # Initializes and creates tables if needed
    run_queries()  # Runs queries and adds data
    # reset_database()  # Uncomment this line if you need to reset the database
