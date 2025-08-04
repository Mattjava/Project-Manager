from flask import abort
from flask_login import LoginManager, current_user
from model import User, Project, Task

# Login Manager Set up
login_manager = LoginManager()

# Defines the method that will be used to load users
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

# Protects a route from being accessed by clients who are not logged in.
def protect_route(func):
    def wrap(*args, **kwargs):
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        else:
            abort(403)
    wrap.__name__ = func.__name__
    return wrap

# Protects a task from being deleted from an unverified user.
def verify_user_task(func):
    def wrap(*args, **kwargs):
        task = Task.query.get_or_404(kwargs['id'])
        project = Project.query.get_or_404(task.project_id)
        if project.user_id != current_user.id:
            abort(403)
        else:
            return func(*args, **kwargs)
    wrap.__name__ = func.__name__
    return wrap

# Protects a project from being deleted from an unverified user.
def verify_user(func):
    def wrap(*args, **kwargs):
        project = Project.query.get_or_404(kwargs['id'])
        if project.user_id != current_user.id:
            abort(403)
        else:
            return func(*args, **kwargs)
    wrap.__name__ = func.__name__
    return wrap