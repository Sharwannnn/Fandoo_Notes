import pytest
from core import init_app, db
from flask_restx import Api
from routes import user,notes,label
from pathlib import Path
import os




@pytest.fixture
def user_app():
    app = init_app("testing")
    with app.app_context():
        db.create_all()
    api = Api(app)
    api.add_resource(user.UserApi, '/api/register')
    api.add_resource(user.LoginApi, '/api/login')
    
    api.add_resource(notes.NotesApi, '/api/notes')
    api.add_resource(notes.NoteApiModification, '/api/notes/<int:note_id>')
    api.add_resource(notes.ArchiveApi, '/api/archive')
    api.add_resource(notes.TrashApi, '/api/trash')
    api.add_resource(notes.CollaborateApi, '/api/collaborate')
    
    api.add_resource(label.LabelRegisterApi, '/api/labels')
    api.add_resource(label.LabelApi, '/api/labels/<int:label_id>')
    
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def user_client(user_app):
    return user_app.test_client()


@pytest.fixture
def login_token(user_client):
    register_data = {
        "username":"sharwannnn",
        "email":"yadavsharwan28@gmail.com",
        "password":"Sonu123@#$",
        "location":"Mumbai"
    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    login_user = {
        "username":"sharwannnn",
        "password":"Sonu123@#$"
    }
    response = user_client.post('/api/login', json = login_user, headers = {"Content-Type":"application/json"})
    
    token = response.json['token']
    return token


@pytest.fixture
def fixture_collaborate(user_client):
    register_user_1 = {
        "username": "sharwannnn",
        "email": "yadavsharwan28@gmail.com",
        "password": "Sonu123@#$",
        "location": "Mumbai"
    }
    response = user_client.post('/api/register', json=register_user_1, headers={"Content-Type": "application/json"})
    assert response.status_code == 201

    login_user_1 = {
        "username": "sharwannnn",
        "password": "Sonu123@#$"
    }
    response = user_client.post('/api/login', json=login_user_1, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    token = response.json['token']

    # Register user 2
    register_user_2 = {
        "username": "Ram",
        "email": "yadavsharwan27@gmail.com",
        "password": "Sonu12345@#$",
        "location": "Gurgaon"
    }
    response = user_client.post('/api/register', json=register_user_2, headers={"Content-Type": "application/json"})
    assert response.status_code == 201
    return token


