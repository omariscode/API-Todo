from flask import Flask, request, jsonify, make_response
import json
import os
from datetime import datetime

app = Flask(__name__)
TASKS_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return make_response(jsonify(tasks), 200)

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    if not data or 'content' not in data:
        return make_response(jsonify({"error": "Content is required"}), 400)
    
    tasks = load_tasks()
    new_task = {
        "id": len(tasks) + 1,
        "content": data['content'],
        "completed": data.get('completed', False),
        "date_created": datetime.utcnow().isoformat()
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return make_response(jsonify(new_task), 201)

@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task["id"] != id]
    save_tasks(tasks)
    return make_response(jsonify({"message": "Task deleted"}), 200)

@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    tasks = load_tasks()
    data = request.get_json()
    if not data or 'content' not in data:
        return make_response(jsonify({"error": "Content is required"}), 400)
    
    for task in tasks:
        if task["id"] == id:
            task["content"] = data["content"]
            task["completed"] = data.get("completed", task["completed"])
            save_tasks(tasks)
            return make_response(jsonify(task), 200)
    
    return make_response(jsonify({"error": "Task not found"}), 404)

if __name__ == '__main__':
    if not os.path.exists(TASKS_FILE):
        save_tasks([])
    app.run(debug=True, port=8000, host='0.0.0.0')
