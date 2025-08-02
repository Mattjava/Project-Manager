from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, String, ForeignKey

db = SQLAlchemy()

class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

# This class is used to create an object that can be saved to the Postresql database
# It has two columns.
# The ID column contains the primary key of the object.
# The task column contains the description of the task.
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255))
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'))

    def __init__(self, task, project_id):
        self.task = task
        self.project_id = project_id

