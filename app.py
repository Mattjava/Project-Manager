from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from sqlalchemy import Table, Column, MetaData, Sequence, Identity, String
from sqlalchemy.sql import text
from model import db, Task, Project
from forms import TaskForm, ProjectForm, FileForm
from file import process_file, allowed_file, DOWNLOAD_FOLDER
import os


meta = MetaData()

# App Start-up
app = Flask(__name__)

# Bootstrap Start-Up
bootstrap = Bootstrap5(app)

# Environment Variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Database connection
db.init_app(app)

current_project_id = 0


# This URL loads the home page of the website
# It also grabs all the tasks in the database and displays it to the user.
@app.route('/')
def index():
    global current_project_id


    projects = db.session.execute(text('SELECT name FROM project')).fetchall()

    allIds = db.session.execute(text('SELECT project_id FROM project')).fetchall()

    current_project_id = len(allIds)

    projects_dict = []
    for i in range(len(projects)):
        project_dict = {}
        project_dict['id'] = allIds[i][0]
        project_dict['name'] = projects[i][0]
        projects_dict.append(project_dict)

    return render_template('index.html', task_dict=projects_dict, project_page=False)

@app.route('/project/<int:id>')
def project(id):
    project = Project.query.get_or_404(id)

    tasks = Task.query.filter_by(project_id=id).all()
    task_names = [task.task for task in tasks]

    allIds = [task.id for task in tasks]

    tasks_dict = []
    for i in range(len(tasks)):
        task_dict = {}
        task_dict['id'] = allIds[i]
        task_dict['task'] = task_names[i]
        tasks_dict.append(task_dict)

    return render_template('index.html', task_dict=tasks_dict, project_page=True, project=project)

# Loads page to add new tasks
@app.route('/addproject')
def addproject():
    return render_template('add.html', form=ProjectForm(), project_page=False)

@app.route('/addtask/<int:id>', methods=['GET', 'POST'])
def addtask(id):
    current_project = db.session.query(Project).get(id)
    return render_template('add.html', form=TaskForm(), project_page=True, project=current_project)

# This URL handles POST request with new tasks
# The function connected saves new data into the Postresql database and redirects the user to the home page

@app.route('/posttask/<int:project_id>', methods=['POST'])
def posttask(project_id):
    if request.method == 'POST':
        task = request.form['task']
        all_tasks = db.session.execute(text('select task from task where project_id=id'), {"id": project_id}).fetchall()
        if task not in all_tasks:
            new_task = Task(task, project_id)
            db.session.add(new_task)
            db.session.commit()
        return redirect(f"/project/{project_id}")
@app.route('/postproject', methods=['POST'])
def postproject():

    if request.method == 'POST':
        project = request.form['name']
        projects = db.session.execute(text('SELECT name FROM project')).fetchall()
        if project not in projects:
            print("Adding new project")

            new_project = Project(project)
            db.session.add(new_project)
            db.session.commit()
    return redirect('/')

@app.route('/file/<int:id>', methods=['GET', 'POST'])
def file(id):
    file_form = FileForm()
    if request.method == 'POST' and file_form.validate_on_submit():
        filedata = file_form.file.data
        filename = secure_filename(filedata.filename)
        process_file(filename, filedata, id)
        return redirect(f'/project/{id}')
    return render_template("file.html", project_page=True, project=Project.query.get(id), form=file_form)

@app.route('/deleteproject/<int:id>')
def deleteproject(id):
    db.session.execute(text('DELETE FROM task WHERE project_id=:id'), {"id": id})
    db.session.execute(text('DELETE FROM project WHERE project_id=:id'), {"id": id})
    db.session.commit()
    return redirect('/')

# This route handles POST request to delete a post.
# It deletes a submission from the database and redirects the user to the home page
@app.route('/deletetask/<int:id>', methods=['GET', 'POST'])
def deletetask(id):
    task = Task.query.get_or_404(id)
    project = Project.query.get(task.project_id)

    db.session.execute(text('DELETE FROM task WHERE id=:oldid'), {"oldid": id})
    db.session.commit()

    return redirect(f'/project{project.project_id}')


if __name__ == '__main__':
    app.run(debug=True)
