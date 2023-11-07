from flask_session import Session
from flask import Flask, request, session, render_template, url_for,jsonify, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_current_user    
from flask_bcrypt import Bcrypt
import secrets
from config import TestConfig

app = Flask(__name__)
app.config.from_pyfile('config.py')  # Load the regular configuration
if app.config['TESTING']:
    app.config.from_pyfile('test_config.py')  
app.config.from_object(TestConfig)

secret_key = secrets.token_urlsafe(32)

def create_app(config_class=Config):
    app = Flask(__name__)

    # Load the application configuration from your config file
    app.config.from_object(config_class)

    # Initialize database with the Flask app
    db.init_app(app)

    # Import and register your blueprints, configure authentication, etc
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(32)
#app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

#app.config['SECRET_KEY'] = ""

Session(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    

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
@app.route('/logout')
def logout_user():
    session.clear()
    return redirect(url_for('home_modified'))


@app.route("/register", methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        bcrypt = Bcrypt()
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if not password2 == password:
            flash("Lösenordet stämmer inte överens", "error")
            return redirect('/register')
        else:
        
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('login')
    else:
        return render_template('register.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        bcrypt = Bcrypt()
        username = request.form.get('username')
        password = request.form.get('password')

        username_db = User.query.filter_by(username=username).first()

        if username_db and bcrypt.check_password_hash(username_db.password, password):
            session['user'] = username
            access_token = create_access_token(identity=username)
            return redirect(url_for('home_modified'))
        else:
            flash("Fel användarnamn eller lösenord. Försök igen", "error")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/")
def home():
    tasks = Todo.query.all()
    return render_template("base.html", tasks = tasks)

@app.route("/modified")
def home_modified():
    tasks = Todo.query.all()
    return render_template("modified.html", tasks = tasks)

    
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
@jwt.unauthorized_loader
def no_token(callback):
    return jsonify({"msg": "Du har inte behörighet"}), 401

@app.route("/users", methods=['GET'])
def get_users():
    users = User.query.all()

    user_list = []
    for user in users:
        user_list.append({"id": user.id, 'username': user.username, 'password': user.password})
    
    return jsonify({"users" : user_list})


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
    content = request.form['content']
    completed = request.form.get('completed', False)
    categories = request.form['categories']
    referrer = request.referrer
        
    if not content:
        flash("Du måste lägga till task", "info")
    elif not categories:
        flash("Du måste lägga till categories", "info")
        return redirect(url_for('home'))
    else:
        new_task = Todo(content=content, completed=completed, categories=categories.capitalize())
        db.session.add(new_task)
        db.session.commit()
   
    if referrer and referrer.endswith('/modified'):
        flash("Uppgiften tillagd", "info")
        destination = 'home_modified'
    else:
        flash("Uppgiften tillagd", "info")
        destination = 'home'    
              
    return redirect(url_for(destination))    


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
@jwt_required()
def delete_task_by_id(task_id):
    current_user = get_jwt_identity()
    
    if current_user:
        task = Todo.query.get(task_id)
        
        if task:
            db.session.delete(task)
            db.session.commit()
            return jsonify({"msg": "Task deleted successfully"})
        else:
            return jsonify({"msg": "Task not found"}), 404
            
    else:
        return jsonify({"msg": "du har inte behörighet"}), 407

# # PUT /tasks/{task_id} Uppdaterar en task med ett specifikt id.
@app.route("/tasks/<int:task_id>", methods=['PUT'])
def update_task(task_id):
    task = Todo.query.get(task_id)
    data = request.json
    if data:
        for key, value in data.items():
            if key == 'categories':
                value = value.capitalize()
            if hasattr(task, key):
                setattr(task, key, value)

        db.session.commit()
             
        return jsonify(task.as_dict())
    else:
        return ({"msg": "du måste skriva en nyckel och ett värde. ex. 'nyckeln': 'värdet' "})

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

@app.route("/login_user", methods=['POST'])
def login_user():
    bcrypt = Bcrypt()
    username = request.form.get('username')
    password = request.form.get('password')
    
    username_db = User.query.filter_by(username=username).first()
    
    if username and bcrypt.check_password_hash(username_db.password, password):
        access_token = create_access_token(identity=username)
        return jsonify({"access token": access_token})
    else:
        return jsonify({"msg": "wrong username or password"})
        

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)