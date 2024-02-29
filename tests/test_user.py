import pytest


def test_register_user_should_return_sucess_response(user_client):
    register_data = {
        "username":"sharwan",
        "email":"yadavsharwan28@gmail.com",
        "password":"Sonu123@#$",
        "location":"Mumbai"
    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    print(response.data)
    assert response.status_code == 201
    

# Password Incorrect
def test_register_user_should_return_failed_response(user_client):
    register_data = {
        "username":"sharwan",
        "email":"yadavsharwan28@gmail.com",
        "password":"Sonu",
        "location":"Mumbai"
    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    print(response.data)
    assert response.status_code == 400
    
# Invalid Username
def test_register_user_invalid_username_should_return_failed_response(user_client):
    register_data = {
        "username":"sha",
        "email":"yadavsharwan28@gmail.com",
        "password":"Sonu",
        "location":"Mumbai"
    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    print(response.data)
    assert response.status_code == 400
    

# Duplicate Username
def test_register_user_duplicate_username_should_return_failed_response(user_client):
    register_data = {
        "username":"Ram",
        "email":"yadavsharwan28@gmail.com",
        "password":"Sonu123@#$",
        "location":"Mumbai"
    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    # print(response.data)
    assert response.status_code == 201
    register_data = {
        "username":"Ram",
        "email":"yadavsharwan27@gmail.com",
        "password":"Monu123@#$",
        "location":"Gurgaon"
    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    assert response.status_code == 409
    
# Correct Login
def test_login_should_return_success_response(user_client):
    register_data = {
        "username":"sharwannnn",
        "email":"yadavsharwan28@gmail.com",
        "password":"Sonu123@#$",
        "location":"Mumbai"
    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    assert response.status_code == 201
    login_user = {
        "username":"sharwannnn",
        "password":"Sonu123@#$"
    }
    response = user_client.post('/api/login', json = login_user, headers = {"Content-Type":"application/json"})
    assert response.status_code == 200
    
# Incorrect Login (wrong password)
def test_login_wrong_password_should_return_failed_response(user_client):
    register_data = {
        "username":"sharwannnn",
        "email":"yadavsharwan28@gmail.com",
        "password":"Sonu123@#$",
        "location":"Mumbai"
    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    assert response.status_code == 201
    login_user = {
        "username":"sharwannnn",
        "password":"Son23@#$34"
    }
    response = user_client.post('/api/login', json = login_user, headers = {"Content-Type":"application/json"})
    assert response.status_code == 401
    
# Incorrect Login (wrong username)
def test_login_wrong_username_should_return_failed_response(user_client):
    register_data = {
        "username":"sharwannnn",
        "email":"yadavsharwan28@gmail.com",
        "password":"Sonu123@#$",
        "location":"Mumbai"
    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    assert response.status_code == 201
    login_user = {
        "username":"sharwann",
        "password":"Sonu123@#$"
    }
    response = user_client.post('/api/login', json = login_user, headers = {"Content-Type":"application/json"})
    assert response.status_code == 401
    
# Missing field password
def test_register_missing_field_password_should_return_failed_response(user_client):
    register_data = {
        "username":"sharwannnn",
        "email":"yadavsharwan28@gmail.com",
        "location":"Mumbai"
    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    assert response.status_code == 400
    
# Missing field location
def test_register_missing_field_location_should_return_failed_response(user_client):
    register_data = {
        "username":"sharwannnnabc",
        "email":"yadavsharwan27@gmail.com",
        "password":"Sonu123@#$"

    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    assert response.status_code == 409
    
# Incorrect Email
def test_register_Incorrect_email_should_return_failed_response(user_client):
    register_data = {
        "username":"sharwannnnabc",
        "email":"yadavsharwan27@.com",
        "password":"Sonu123@#$",
        "location":"Mumbai"

    }
    response = user_client.post('/api/register', json = register_data, headers = {"Content-Type":"application/json"})
    assert response.status_code == 400
    

def test_email_without_special_characters_should_return_failed_response(user_client):
    register_data = {
        "username": "sharwannnn",
        "email": "yadavsharwangmail.com",
        "password": "Sonu123@#$",
        "location": "Gurgaon"
    }
    response = user_client.post('/api/register', json=register_data, headers={"Content-Type": "application/json"})
    assert response.status_code == 400

def test_short_email_should_return_failed_response(user_client):
    register_data = {
        "username": "sharwannnn",
        "email": "sh@.com",
        "password": "Sonu123@#$",
        "location": "Mumbai"
    }
    response = user_client.post('/api/register', json=register_data, headers={"Content-Type": "application/json"})
    assert response.status_code == 400