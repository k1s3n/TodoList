import json
import pytest
from app import app, db, Todo

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_task.db'
    with app.app_context():  # Skapa applikationskontext
        db.create_all()
    with app.test_client() as client:
        yield client
    with app.app_context():  # Avsluta applikationskontext
        db.drop_all()

def test_home_route(client):
    with app.app_context():
        response = client.get('/')
    assert response.status_code == 200
    assert b"My To Do List" in response.data

def test_add_task(client):
    with app.app_context():
        response = client.post('/new_task', data={'content': 'Test task', 'categories': 'Test category'})
    assert response.status_code == 302
    with app.app_context():
        tasks = Todo.query.all()
        assert len(tasks) == 1
        assert tasks[0].content == 'Test task'
        assert tasks[0].categories == 'Test category'

def test_load_task_by_id(client):
    # Lägg till en task i databasen för att testa
    with app.app_context():
        task = Todo(content="Test task", completed=False, categories="Test category")
        db.session.add(task)
        db.session.commit()
        
    with app.app_context():
        response = client.get('/tasks/1')
        assert response.status_code == 200
        data = json.loads(response.data.decode('utf-8'))
        assert data['id'] == 1
        assert data['content'] == "Test task"
        assert data['completed'] is False
        assert data['categories'] == "Test category"

def test_delete_task_by_id(client):
    # Lägg till en task i databasen för att testa
    with app.app_context():
        task = Todo(content="Test task", completed=False, categories="Test category")
        db.session.add(task)
        db.session.commit()

    with app.app_context():
        response = client.delete('/tasks/1')
        assert response.status_code == 200
        data = json.loads(response.data.decode('utf-8'))
        assert data['msg'] == "Task deleted successfully"

    # Kontrollera att tasken har tagits bort från databasen
    with app.app_context():
        deleted_task = Todo.query.get(1)
        assert deleted_task is None

def test_update_task(client):
    # Lägg till en task i databasen för att testa
    with app.app_context():
        task = Todo(content="Test task", completed=False, categories="Test category")
        db.session.add(task)
        db.session.commit()

    new_data = {
        "content": "Updated task",
        "categories": "Updated category"
    }
    with app.app_context():
        response = client.put('/tasks/1', data=json.dumps(new_data), content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['content'] == "Updated task"
    assert data['categories'] == "Updated category"

    # Kontrollera att tasken har uppdaterats i databasen
    with app.app_context():
        updated_task = Todo.query.get(1)
        assert updated_task.content == "Updated task"
        assert updated_task.categories == "Updated category"

def test_complete_task(client):
    # Lägg till en task i databasen för att testa
    with app.app_context():
        task = Todo(content="Test task", completed=False, categories="Test category")
        db.session.add(task)
        db.session.commit()

    with app.app_context():
        response = client.put('/tasks/1/complete')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['msg'] == "Task marked as completed successfully"

    # Kontrollera att tasken är markerad som slutförd i databasen
    with app.app_context():
        completed_task = Todo.query.get(1)
        assert completed_task.completed is True

def test_get_unique_categories(client):
    # Lägg till kategorierna i testdatabasen
    with app.app_context():
        category1 = Todo(content="Content for Category1", categories="Category1")
        category2 = Todo(content="Content for Category2", categories="Category2")
        category3 = Todo(content="Content for Category3", categories="Category3")
        db.session.add(category1)
        db.session.add(category2)
        db.session.add(category3)
        db.session.commit()

    # Gör förfrågan för att hämta unika kategorier
    with app.app_context():
        response = client.get('/tasks/categories/')
    data = json.loads(response.data)
    assert response.status_code == 200
    # Ange de förväntade kategorierna här
    expected_categories = ['Category1', 'Category2', 'Category3']
    assert data['unique_categories'] == expected_categories


def test_get_list_category_name(client):
    with app.app_context():
        response = client.get('/tasks/categories/Category1')
    data = json.loads(response.data)
    assert response.status_code == 200
    # Ange de förväntade uppgifterna som du har lagt till i kategorin 'Category1'.


#API-Tester
def test_add_task_invalid_data(client):
    # Testar att försöka lägga till en uppgift med ogiltiga data (t.ex. saknas content eller categories).
    with app.app_context():
        response = client.post('/new_task', data={'content': '', 'categories': ''})
    assert response.status_code == 302  # Förväntar oss en felkod 400 (Bad Request)

def test_add_task_missing_data(client):
    # Testar att försöka lägga till en uppgift utan att skicka med nödvändig data.
    with app.app_context():
        response = client.post('/new_task', data={})
    assert response.status_code == 400  # Förväntar oss en felkod 400 (Bad Request)

def test_load_invalid_task_id(client):
    # Testar att försöka hämta en uppgift med en ogiltig ID.
    with app.app_context():
        response = client.get('/tasks/999')  
    assert response.status_code == 404  # Förväntar oss en felkod 404 (Not Found)

def test_delete_invalid_task_id(client):
    # Testa att försöka ta bort en uppgift med en ogiltig ID.
    with app.app_context():
        response = client.delete('/tasks/999')  # Antag att ID 999 inte finns.
    assert response.status_code == 404  # Förväntar oss en felkod 404 (Not Found)

def test_update_invalid_task_id(client):
    # Testa att försöka uppdatera en uppgift med en ogiltig ID.
    with app.app_context():
        response = client.put('/tasks/999', data=json.dumps({"content": "Updated task"}), content_type='application/json')
    assert response.status_code == 404  # Förväntar oss en felkod 404 (Not Found)

