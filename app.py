from flask import Flask, request, render_template, url_for,jsonify, redirect
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


#frontend
@app.route("/category", methods=['GET'])
def cat_sort():
    cat_sort = db.session()
    return redirect(url_for('home_modified'))

@app.route("/")
def home():
    tasks = Todo.query.all()
    return render_template("base.html", tasks = tasks)

@app.route("/modified")
def home_modified():
    tasks = Todo.query.all()
    return render_template("modified.html", tasks = tasks)


@app.route("/new_task", methods=['POST'])
def new_task():
    content = request.form['content']
    completed = request.form.get('completed', False)
    categories = request.form['categories']
    

    new_task = Todo(content=content, completed=completed, categories=categories.capitalize())
    db.session.add(new_task)
    db.session.commit()

    referrer = request.referrer
    if referrer and referrer.endswith('/modified'):
        destination = 'home_modified'
    else:
        destination = 'home'
          
    return redirect(url_for(destination))

    
    
@app.route("/delete_task/<int:task_id>", methods=['POST'])
def delete_task(task_id):
    task = Todo.query.get(task_id)
    if task is not None:
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('home_modified'))
    else:
        return jsonify({"msg": "Task not found"},404)
    
    
@app.route("/update_tasks", methods=['POST'])
def update_tasks():
    task_ids = request.form.getlist('task_ids')
    
   
    for task in Todo.query.filter(Todo.id.in_(task_ids)):
        task.completed = not task.completed

    db.session.commit()

    return redirect(url_for('home'))


@app.route("/update_tasks/<int:task_id>", methods=['POST'])
def update_tasks_completed(task_id):
    task = Todo.query.get(task_id)
    
    task.completed = not task.completed

    db.session.commit()

    return redirect(url_for('home_modified'))




#Frontend ends


##backend STARTS


#GET /tasks Hämtar alla tasks. För VG: lägg till en parameter completed som kan filtrera på färdiga eller ofärdiga tasks.


@app.route("/tasks", methods=['GET'])
def get_tasks():
    completed_para = request.args.get('completed')
    
    if completed_para:
        if completed_para.lower() == "false":
            completed = False
        elif completed_para.lower() == "true":
            completed = True
        else:
            return jsonify({"msg": "ogiltig parameter för completed"}),400
    else:
        completed = None
    
    
    if completed is not None:
        tasks = Todo.query.filter_by(completed=completed).all()
    else:
        tasks = Todo.query.all()
    
    task_list = []
    
    for task in tasks:
        task_list.append(task.as_dict())
    
    return jsonify({'tasks': task_list})


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
        new_task = Todo(completed=completed, content=content,categories=categories.capitalize())
        db.session.add(new_task)
        db.session.commit()
    
    return jsonify({"msg": "Task added! "})


# GET /tasks/{task_id} Hämtar en task med ett specifikt id.
@app.route("/tasks/<int:task_id>", methods=['GET'])
def load_task_by_id(task_id):
    task = Todo.query.get(task_id)
    if task is not None:
        return jsonify({
            'id': task.id,
            'categories': task.categories,
            'content': task.content,
            'completed': task.completed,
            'date_created' : task.date_created
        })
    else:
        return jsonify({"msg": "could not find task id"}),404

# # DELETE /tasks/{task_id} Tar bort en task med ett specifikt id.

@app.route("/tasks/<int:task_id>", methods=['DELETE'])
def delete_task_by_id(task_id):
    task = Todo.query.get(task_id)
    if task is not None:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"msg": "Task deleted successfully"})
    else:
        return jsonify({"msg": "Task not found"}), 404

# # PUT /tasks/{task_id} Uppdaterar en task med ett specifikt id.
@app.route("/tasks/<int:task_id>", methods=['PUT'])
def update_task(task_id):
    task = Todo.query.get(task_id)
    
    data = request.json
    if 'content' in data:
        task.content = data['content']
    if 'categories' in data:
        task.categories = data['categories']
        
    db.session.commit()
             
    return jsonify({
            'id': task.id,
            'categories': task.categories,
            'content': task.content,
            'completed': task.completed,
            'date_created' : task.date_created
    })

# PUT /tasks/{task_id}/complete Markerar en task som färdig.
@app.route("/tasks/<int:task_id>/complete", methods=['PUT'])
def complete_task(task_id):
    task = Todo.query.get(task_id)
    if task is not None:
        task.completed = True
        db.session.commit()
        return jsonify({"msg": "Task marked as completed successfully"})
    else:
        return jsonify({"msg": "Task not found"}), 404


# GET /tasks/categories/ Hämtar alla olika kategorier.
@app.route("/tasks/categories/", methods=['GET'])
def get_unique_categories():
    unique_categories = db.session.query(Todo.categories).distinct().all()

    categories_list = []
    for category in unique_categories:
       categories_list.append(category[0])

    return jsonify({'unique_categories': categories_list})

# GET /tasks/categories/{category_name} Hämtar alla tasks från en specifik kategori.
@app.route("/tasks/categories/<string:category_name>", methods=['GET'])
def get_list_category_name(category_name):
    tasks = Todo.query.filter_by(categories=category_name).all()
    
    task_list = []
    if tasks:
        for task in tasks:
            task_list.append(task.as_dict())
        return jsonify(task_list)
    else:
        return jsonify({"msg": f"Could not find any with {category_name}"})
        

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)