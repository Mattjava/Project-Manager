import os
from model import db, Task, Project


DOWNLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {'txt', 'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_tasks(file_path, project_id):
    with open(file_path, 'r') as file:
        tasks = file.readlines()
    tasks = [task[:-1] if "\n" in task else task for task in tasks]

    for task in tasks:
        new_task = Task(task, project_id=project_id)
        db.session.add(new_task)
        db.session.commit()


def process_file(filename, filedata, project_id):
    filedata.save(os.path.join(DOWNLOAD_FOLDER, filename))
    save_tasks(os.path.join(DOWNLOAD_FOLDER, filename), project_id)
    os.remove(os.path.join(DOWNLOAD_FOLDER, filename))



