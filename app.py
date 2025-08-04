from re import split

from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from flask_login import login_user, logout_user, current_user
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from sqlalchemy import Table, Column, MetaData, Sequence, Identity, String
from sqlalchemy.sql import text
from model import db, Task, Project, User
from forms import TaskForm, ProjectForm, FileForm, UserForm
from file import process_file, allowed_file, DOWNLOAD_FOLDER
from user import login_manager, load_user, protect_route, verify_user, verify_user_task
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import os


meta = MetaData()

# App Start-up
app = Flask(__name__)
app.app_context().push()

# Bootstrap Start-Up
bootstrap = Bootstrap5(app)

# Environment Variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URI']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Database connection
db.init_app(app)

# Login Manager Set up
login_manager.init_app(app)

def check_if_late(input_date):
    if input_date is None:
        return False
    current_date = date.today()
    return input_date < current_date

@app.route('/')
def home():
    if current_user.is_authenticated:
        id = current_user.id
        return redirect(f'/{id}')
    else:
        return redirect('/login')

# This URL loads the home page of the website
# It also grabs all the tasks in the database and displays it to the user.
@app.route('/<int:user_id>')
@protect_route
def index(user_id):
    global current_project_id


    projects = db.session.execute(text('SELECT name FROM project WHERE user_id=:id'), {"id": user_id}).fetchall()

    allIds = db.session.execute(text('SELECT project_id FROM project WHERE user_id=:id'), {"id": user_id}).fetchall()

    current_project_id = len(allIds)

    projects_dict = []
    for i in range(len(projects)):
        project_dict = {}
        project_dict['id'] = allIds[i][0]
        project_dict['name'] = projects[i][0]
        projects_dict.append(project_dict)

    return render_template('index.html', task_dict=projects_dict, project_page=False, user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = UserForm()
    if register_form.validate_on_submit():
        username = register_form.username.data
        password = generate_password_hash(register_form.password.data, method='pbkdf2:sha256', salt_length=8)

        new_user = User(name=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect('/')

    return render_template("register.html", register_form=register_form, user=register_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = UserForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data

        if (User.query.filter_by(name=username).first() is not None
                and check_password_hash(User.query.filter_by(name=username).first().password, password)):
            login_user(User.query.filter_by(name=username).first())
            return redirect('/')

    return render_template("login.html", register_form=login_form, project_page=False, user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

@app.route('/project/<int:id>')
@protect_route
def project(id):
    project = Project.query.get_or_404(id)

    tasks = Task.query.filter_by(project_id=id).all()
    task_names = [task.task for task in tasks]

    allIds = [task.id for task in tasks]

    due_dates = [task.due_date for task in tasks]

    tasks_dict = []
    for i in range(len(tasks)):
        task_dict = {}
        task_dict['id'] = allIds[i]
        task_dict['task'] = task_names[i]
        task_dict['due_date'] = due_dates[i]
        task_dict['due_status'] = check_if_late(due_dates[i])
        tasks_dict.append(task_dict)

    return render_template('index.html', task_dict=tasks_dict, project_page=True, project=project, user=current_user)

# Loads page to add new tasks
@app.route('/addproject')
@protect_route
def addproject():
    return render_template('add.html', form=ProjectForm(), project_page=False, user=current_user)

@app.route('/addtask/<int:id>', methods=['GET', 'POST'])
@protect_route
def addtask(id):
    current_project = db.session.query(Project).get(id)
    return render_template('add.html', form=TaskForm(), project_page=True, project=current_project, user=current_user)

# This URL handles POST request with new tasks
# The function connected saves new data into the Postresql database and redirects the user to the home page

@app.route('/posttask/<int:project_id>', methods=['POST'])
@protect_route
def posttask(project_id):
    if request.method == 'POST':
        task = request.form['task']
        due_date = request.form['due_date']
        if due_date == '':
            due_date = None
        all_tasks = db.session.execute(text('select task from task where project_id=id'), {"id": project_id}).fetchall()
        if task not in all_tasks:
            new_task = Task(task, project_id, due_date)
            db.session.add(new_task)
            db.session.commit()
        return redirect(f"/project/{project_id}")
@app.route('/postproject', methods=['POST'])
@protect_route
def postproject():

    if request.method == 'POST':
        project = request.form['name']
        projects = db.session.execute(text('SELECT name FROM project')).fetchall()
        if project not in projects:
            print("Adding new project")

            new_project = Project(project, current_user.get_id())
            db.session.add(new_project)
            db.session.commit()
    return redirect('/')

@app.route('/file/<int:id>', methods=['GET', 'POST'])
@protect_route
def file(id):
    file_form = FileForm()
    if request.method == 'POST' and file_form.validate_on_submit():
        filedata = file_form.file.data
        filename = secure_filename(filedata.filename)
        process_file(filename, filedata, id)
        return redirect(f'/project/{id}')
    return render_template("file.html", project_page=True, project=Project.query.get(id), form=file_form, user=current_user)

@app.route('/deleteproject/<int:id>')
@verify_user
def deleteproject(id):
    db.session.execute(text('DELETE FROM task WHERE project_id=:id'), {"id": id})
    db.session.execute(text('DELETE FROM project WHERE project_id=:id'), {"id": id})
    db.session.commit()
    return redirect('/')

# This route handles POST request to delete a post.
# It deletes a submission from the database and redirects the user to the home page
@app.route('/deletetask/<int:id>', methods=['GET', 'POST'])
@verify_user_task
def deletetask(id):
    task = Task.query.get_or_404(id)
    project = Project.query.get(task.project_id)

    db.session.execute(text('DELETE FROM task WHERE id=:oldid'), {"oldid": id})
    db.session.commit()

    return redirect(f'/project/{project.project_id}')


if __name__ == '__main__':
    app.run(debug=True)
