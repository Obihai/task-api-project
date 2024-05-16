from flask import Flask
from flask import jsonify
from flask import request
from flask import flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user
from flask_login import UserMixin
from flask_login import LoginManager
from flask_login import login_required
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + '/home/voldermort/task-api-project/tasks.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

tasks = []

task_example = {
    "id": 1,
    "title": "Learn Flask",
    "description": "Build a basic API",
    "completed": False
}

class Task(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return Task.query.get(int(user_id))

@app.route('/')
def hello_world():
    return 'Hello from your Task API!'

@app.route('/tasks', methods=['GET'])
@login_required
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
@login_required
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

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

    user = Task.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 400
    
@app.route('/logout')
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def handle_internal_error(error):
    return jsonify({'error': 'Something went wrong'}), 500

if __name__ == '__main__':
    app.run(debug=True)