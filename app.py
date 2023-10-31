from flask import Flask, request, render_template, url_for

app = Flask(__name__)
#dkhejdawda
@app.route("/")
def home():
    return render_template("base.html")

#backend

#GET /tasks Hämtar alla tasks. För VG: lägg till en parameter completed som kan filtrera på färdiga eller ofärdiga tasks.

@app.route("/tasks", methods=['GET'])
def get_tasks():
    return "get all tasks"

#POST /tasks Lägger till en ny task. Tasken är ofärdig när den först läggs till.

@app.route("/tasks", methods=['POST'])
def add_task():
    return "create task"

# GET /tasks/{task_id} Hämtar en task med ett specifikt id.

@app.route("/tasks/<int:task_id>", methods=['GET'])
def get_specific_task():
    return {"msg": "task_id"}

# DELETE /tasks/{task_id} Tar bort en task med ett specifikt id.

@app.route("/tasks/<int:task_id>", methods=['DELETE'])
def delete_task():
    return {"msg": "task_id"}

# PUT /tasks/{task_id} Uppdaterar en task med ett specifikt id.

@app.route("/tasks/<int:task_id>", methods=['PUT'])
def update_task():
    return {"msg": "task_id"}

# PUT /tasks/{task_id}/complete Markerar en task som färdig.



# GET /tasks/categories/ Hämtar alla olika kategorier.



# GET /tasks/categories/{category_name} Hämtar alla tasks från en specifik kategori.

if __name__ == "__main__":
    app.run(debug=True)