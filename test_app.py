# tests/test_app.py
import pytest
import os
import shutil
from app import app, db# Ersätt "projektmapp" med namnet på din projektmapp

shutil.copy("instance/task.db", "instance/test_task.db")
# Konfigurera Flask-appen för att använda "test_task.db" när du kör pytest
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_task.db'

# Skapa en testdatabas om den inte redan finns
with app.app_context():
    db.create_all()
# Dina pytest-testfall

def test_example():
    # Här kan du definiera dina testfall
    pass

#Ta bort "test_task.db" när testerna är klara
#os.remove("instance/test_task.db")
