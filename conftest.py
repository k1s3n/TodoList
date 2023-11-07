import pytest
from app import create_app, db, app # Import your app and db objects

@pytest.fixture
def app():
    app = create_app()  # Replace with how you create your Flask app
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    with app.app_context():
        db.create_all()
        yield app
    db.drop_all()