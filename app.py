from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from sqlalchemy import Table, Column, MetaData, Sequence, Identity, String
from sqlalchemy.sql import text
import os

from wtforms.validators import DataRequired

currentId = 0

meta = MetaData()



app = Flask(__name__)
bootstrap = Bootstrap5(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255))

    def __init__(self, task):
        self.task = task

class TaskForm(FlaskForm):
    task = StringField('Task', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def index():  # put application's code here
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


@app.route('/add')
def add():
    return render_template('add.html', form=TaskForm())

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

@app.route('/postdelete/<int:id>', methods=['GET', 'POST'])
def postdelete(id):
    db.session.execute(text('DELETE FROM task WHERE id=:oldid'), {"oldid": id})
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()
