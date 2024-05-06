from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + '/home/voldermort/task-api/tasks.db'
db = SQLAlchemy(app)

tasks = []

task_example = {
    "id": 1,
    "title": "Learn Flask",
    "description": "Build a basic API",
    "completed": False
}

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, nullable=False)

@app.route('/')
def hello_world():
    return 'Hello from your Task API!'

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    output = []
    for task in tasks:
        task_data = {"id": task.id, "title": task.title, "description": task.description, "completed": task.completed}
        output.append(task_data)
    return jsonify(output)

@app.route('/tasks', methods=['POST'])
def create_task():
    task_data = request.get_json()
    new_task = Task(title=task_data['title'], description=task_data.get('description'), completed=False)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'id': new_task.id}), 201

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.title, task.description, task.completed)

if __name__ == '__main__':
    app.run(debug=True)