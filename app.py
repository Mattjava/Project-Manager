from flask import Flask, render_template, redirect, request
import sqlite3

currentId = 0
tasks = []

app = Flask(__name__)

@app.route('/')
def index():  # put application's code here
    global currentId, tasks

    connection = sqlite3.connect("taskdatabase.db")
    cursor = connection.cursor()

    tasks = cursor.execute("SELECT task FROM tasks").fetchall()

    allIds = cursor.execute("SELECT id FROM tasks").fetchall()
    currentId = allIds[len(allIds) - 1][0]

    connection.close()

    tasks = {task[0] for task in tasks}

    print(str(tasks) + "| Highest Id: " + str(currentId))

    return render_template('index.html', tasks=tasks)


@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/delete')
def delete():
    return render_template('delete.html')

@app.route('/postadd', methods=['POST'])
def postadd():
    if request.method == 'POST':
        task = request.form['task']
        if task not in tasks:
            print("Adding new task")
            connection = sqlite3.connect("taskdatabase.db")
            cursor = connection.cursor()
            new_id = currentId + 1
            cursor.execute("INSERT INTO tasks VALUES(?, ?)", (new_id, task))
            connection.commit()
            connection.close()
    return redirect('/')

@app.route('/postdelete', methods=['POST'])
def postdelete():
    if request.method == 'POST':
        removed_task = request.form.get('task')
        if removed_task in tasks:
            connection = sqlite3.connect("taskdatabase.db")
            cursor = connection.cursor()
            cursor.execute("DELETE FROM tasks WHERE task = ?", (removed_task,))
            connection.commit()
            connection.close()

    return redirect('/')


if __name__ == '__main__':
    app.run()
