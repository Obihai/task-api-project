from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + '/home/voldermort/task-api-project/tasks.db'
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
    username = db.Column(db.string(80), unique=True, nullable=False)
    password_hash = db.Column(db.string(120), nullable=False)

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

@app.route('/tasks/<int:task_id>', methods=['GET', 'PUT'])
def update_task(task_id):
    task_data = request.get_json()
    task = Task.query.get_or_404(task_id)
    task.title = task_data.get('title', task.title)
    task.description = task_data.get('description')
    task.completed = task_data.get('completed')
    db.session.add(task)
    db.session.commit()
    return jsonify({'id': task.id}), 200

@app.route('/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted'}), 200
    except Exception as e:
        return jsonify({'error': 'Somethig went wrong while deleting the task'}), 500

@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def handle_internal_error(error):
    return jsonify({'error': 'Something went wrong'}), 500

if __name__ == '__main__':
    app.run(debug=True)