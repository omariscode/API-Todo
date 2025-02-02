from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask-cors import CORS



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
CORS(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "completed": self.completed,
            "date_created": self.date_created
        }

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Todo.query.order_by(Todo.date_created).all()
    return make_response(jsonify([task.to_dict() for task in tasks]), 200)

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    if not data or 'content' not in data:
        return make_response(jsonify({"error": "Content is required"}), 400)
    
    new_task = Todo(content=data['content'], completed=data.get('completed', False))
    try:
        db.session.add(new_task)
        db.session.commit()
        return make_response(jsonify(new_task.to_dict()), 201)
    except:
        return make_response(jsonify({"error": "Could not add task"}), 500)

@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Todo.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return make_response(jsonify({"message": "Task deleted"}), 200)
    except:
        return make_response(jsonify({"error": "Could not delete task"}), 500)

@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Todo.query.get_or_404(id)
    data = request.get_json()
    if not data or 'content' not in data:
        return make_response(jsonify({"error": "Content is required"}), 400)
    
    task.content = data['content']
    task.completed = data.get('completed', task.completed)
    try:
        db.session.commit()
        return make_response(jsonify(task.to_dict()), 200)
    except:
        return make_response(jsonify({"error": "Could not update task"}), 500)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000, host='0.0.0.0')

