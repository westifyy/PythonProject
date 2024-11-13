from flask import Flask, render_template, request, json, jsonify, redirect, url_for

app = Flask(__name__)

def load_tasks():
    try:
        with open('tasks.json') as f:
            tasks = json.load(f)
            return tasks if isinstance(tasks, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks):
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f, indent=4) 
    
@app.route("/")
def index():
    tasks = load_tasks()
    return render_template("index.html", tasks=tasks)

@app.route("/tasks", methods=["GET"])
def receive_json():
    tasks = load_tasks()
    return jsonify(tasks)
    
@app.route("/tasks", methods=["POST"])
def add_tasks():
    tasks = load_tasks()
    data = request.json
    description = data.get("description")
    category = data.get("category")
    if not description or not category:
        return jsonify({"error": "Description and Category are missing"}), 400
    
    new_task = {
        "id": max(task["id"] for task in tasks) + 1 if tasks else 1,
        "description": description,
        "category": category,
        "status": "pending"
    }
    
    tasks.append(new_task)
    
    save_tasks(tasks)
        
    return jsonify({"message": "Task was added successfully", "task": new_task}), 201

@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task_by_id(task_id):
    tasks = load_tasks()
        
    task = next((task for task in tasks if task["id"] == task_id), None)
    
    if task is None:
        return jsonify({"error": "ID is missing"}), 404
    
    return jsonify(task)

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task_by_id(task_id):
    tasks = load_tasks()
        
    task_to_delete = next((task for task in tasks if task["id"] == task_id), None)
    
    if task_to_delete is None:
        return jsonify({"error": "Task is missing"}), 404
    
    tasks.remove(task_to_delete)
    
    save_tasks(tasks)
        
    return jsonify({"message": "Task deleted successfully"})

@app.route("/tasks/delete", methods=["POST"])
def delete_task_by_post():
    task_id = request.form.get("task_id", type=int)
    
    tasks = load_tasks()
        
    task_to_delete = next((task for task in tasks if task["id"] == task_id), None)
    
    if task_to_delete is None:
        return jsonify({"error": "Task not Found"}), 404
    
    tasks.remove(task_to_delete)
    
    save_tasks(tasks)
        
    return redirect(url_for('index'))

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    tasks = load_tasks()
        
    task_to_edit = next ((task for task in tasks if task["id"] == task_id), None)
    
    if task_to_edit is None:
        return jsonify({"error": "Task ID is not correct  and/or is missing"}), 404
    
    data = request.json
    description = data.get("description", task_to_edit["description"])
    category = data.get("category", task_to_edit["category"])
    status = data.get("status", task_to_edit["status"])
    
    task_to_edit.update({
        "description": description,
        "category": category,
        "status": status
    })
    
    save_tasks(tasks)
    
    return jsonify({"message": "Task updated sucessfully", "task": task_to_edit}), 200

@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def complete_task(task_id):
    tasks = load_tasks()

    task_to_complete = next ((task for task in tasks if task["id"] == task_id), None)
    
    if task_to_complete is None:
        return jsonify({"error": "Task ID is not correct  and/or is missing"}), 404
    
    task_to_complete["status"] = "completed"
    
    save_tasks(tasks)
    
    return jsonify({"message": "Task comleted sucessfully", "task": task_to_complete}), 200

@app.route("/tasks/categories", methods=["GET"])
def get_categories():
    tasks = load_tasks()
    
    categories = list({task["category"] for task in tasks})
    
    return jsonify(categories)

@app.route("/tasks/categories/<category_name>", methods=["GET"])
def get_task_by_category(category_name):
    tasks = load_tasks()
    
    tasks_by_category = [task for task in tasks if task["category"] == category_name]
    
    if tasks_by_category is None:
        return jsonify({"error": "Category doesn't exist"}), 404
    
    
    return jsonify(tasks_by_category)


if __name__ == '__main__':
    app.run()