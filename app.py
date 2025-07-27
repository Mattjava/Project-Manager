from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy import Table, Column, MetaData, Sequence, Identity, String
from sqlalchemy.sql import text
from model import db, Task
from forms import TaskForm
import os


meta = MetaData()

# App Start-up
app = Flask(__name__)

# Bootstrap Start-Up
bootstrap = Bootstrap5(app)

# Environment Variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

# Database connection
db.init_app(app)


# This URL loads the home page of the website
# It also grabs all the tasks in the database and displays it to the user.
@app.route('/')
def index():
    global currentId, tasks


    tasks = db.session.execute(text('SELECT task FROM task')).fetchall()

    allIds = db.session.execute(text('SELECT id FROM task')).fetchall()

    tasks_dict = []
    for i in range(len(tasks)):
        task_dict = {}
        task_dict['id'] = allIds[i][0]
        task_dict['task'] = tasks[i][0]
        tasks_dict.append(task_dict)

    return render_template('index.html', task_dict=tasks_dict)


# Loads page to add new tasks
@app.route('/add')
def add():
    return render_template('add.html', form=TaskForm())

# This URL handles POST request with new tasks
# The function connected saves new data into the Postresql database and redirects the user to the home page
@app.route('/postadd', methods=['POST'])
def postadd():

    if request.method == 'POST':
        task = request.form['task']
        tasks = db.session.execute(text('SELECT task FROM task')).fetchall()
        if task not in tasks:
            print("Adding new task")

            new_task = Task(task)
            db.session.add(new_task)
            db.session.commit()
    return redirect('/')

# This route handles POST request to delete a post.
# It deletes a submission from the database and redirects the user to the home page
@app.route('/postdelete/<int:id>', methods=['GET', 'POST'])
def postdelete(id):
    db.session.execute(text('DELETE FROM task WHERE id=:oldid'), {"oldid": id})
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()
