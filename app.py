from flask import Flask, request, render_template, url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    categories = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
     
    def as_dict(self):
        
        task_dict = {}
        
        for column in self.__table__.columns:
            
            column_name = column.name
            column_value = getattr(self, column_name)
            
            task_dict[column_name] = column_value
        
        return task_dict
    


@app.route("/")
def home():
     return render_template("base.html")

# #backend

#GET /tasks Hämtar alla tasks. För VG: lägg till en parameter completed som kan filtrera på färdiga eller ofärdiga tasks.
@app.route("/tasks", methods=['GET'])
def get_tasks():
    tasks = Todo.query.all()
    if not tasks:
        return jsonify({"msg": "No task found."}), 404
    task_list = []
    for task in tasks:
        task_list.append(task.as_dict())
    return jsonify(task_list)


#POST /tasks Lägger till en ny task. Tasken är ofärdig när den först läggs till.
@app.route("/tasks", methods=['POST'])
def add_task():
    data = request.json
    content = data.get("content")
    completed = data.get("completed", False)
    categories = data.get("categories")
    
    if not data.get("content"):
        return jsonify({"msg": "You have write in content"})
    elif not data.get("categories"):
        return jsonify({"msg": "You have write in categories"})
    else:    
        new_task = Todo(categories=categories, completed=completed, content=content)
        db.session.add(new_task)
        db.session.commit()
    
    return jsonify({"msg": "Task added! "})


# GET /tasks/{task_id} Hämtar en task med ett specifikt id.
@app.route("/tasks/<int:task_id>", methods=['GET'])
def delete_task(task_id):
    task = Todo.query.get(task_id)
    if task is not None:
        return jsonify({
            'id': task.id,
            'categories': task.categories,
            'content': task.completed,
            'date_created' : task.date_created
        })
    else:
        return jsonify({"msg": "could not find task id"}),404
# @app.route("/tasks/<int:task_id>", methods=['GET'])
# def get_specific_task():
#     return {"msg": "task_id"}

# # DELETE /tasks/{task_id} Tar bort en task med ett specifikt id.

     
    
    #return jsonify({"msg": "Task deleted"})

# # PUT /tasks/{task_id} Uppdaterar en task med ett specifikt id.

# @app.route("/tasks/<int:task_id>", methods=['PUT'])
# def update_task():
#     return {"msg": "task_id"}

# # PUT /tasks/{task_id}/complete Markerar en task som färdig.



# # GET /tasks/categories/ Hämtar alla olika kategorier.



# GET /tasks/categories/{category_name} Hämtar alla tasks från en specifik kategori.

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
