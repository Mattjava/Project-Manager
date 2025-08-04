import os
from model import db, Task, Project


DOWNLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {'txt', 'csv'}

# Checks if the file has the correct extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Saves the task into the database
def save_tasks(file_path, project_id):
    # Saves each individual line into an array
    # This array will be used to create the tasks in a for-loop
    with open(file_path, 'r') as file:
        tasks = file.readlines()
    tasks = [task[:-1] if "\n" in task else task for task in tasks]

    for task in tasks:
        # Splits the task into two parts: the task and the due date
        # If the task does not have a due date, a task object will be created with a null due date.
        # Otherwise, it saves the objects into the database
        task_arr = task.split(',')
        if len(task_arr) == 2:
            new_task = Task(task_arr[0], project_id=project_id, due_date=task_arr[1])
        else:
            new_task = Task(task_arr[0], project_id=project_id, due_date=None)
        db.session.add(new_task)
        db.session.commit()


# Processes the input file and saves it to the system
# It then deletes it when it finishes processing.
# This ensures it won't run out of space when processing files.
def process_file(filename, filedata, project_id):
    filedata.save(os.path.join(DOWNLOAD_FOLDER, filename))
    save_tasks(os.path.join(DOWNLOAD_FOLDER, filename), project_id)
    os.remove(os.path.join(DOWNLOAD_FOLDER, filename))



