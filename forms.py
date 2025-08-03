from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired


# This class is used to set up the form to take in new tasks
class TaskForm(FlaskForm):
    task = StringField('Task', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class FileForm(FlaskForm):
    file = FileField('Project File', validators=[FileAllowed(['txt', 'csv'])])
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')