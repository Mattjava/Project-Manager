from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, String, ForeignKey, DateTime
from datetime import datetime

db = SQLAlchemy()

# This class creates a project object in the Postgres database
# It has three columns
# The project_id column stores its unique key
# The name column stores the name of the project
# The user_id column stores the foreign key that connects the project to a user.
class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

# This class is used to create an object that can be saved to the Postresql database
# It has four columns.
# The ID column contains the primary key of the object.
# The task column contains the description of the task.
# The project_id connects the task to its respective project or goal
# The due date contains the due date where the task must be finished.
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255))
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'))
    due_date = db.Column(db.DateTime)

    def __init__(self, task, project_id, due_date):
        self.task = task
        self.project_id = project_id
        self.due_date = due_date

# This class manages the user table in Postgres.
# It has three columns
# The id column refers to the user id
# The name column is the username of the account
# The password column stores the hashesd password to the account.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))

    def __init__(self, name, password):
        self.name = name
        self.password = password

