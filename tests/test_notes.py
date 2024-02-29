import pytest

# @pytest.mark.test_fix
def test_fixture_login(user_client, login_token):
    # print(login_token)
    add_note = {
            "title":"Homework for today",
            "description":"This need to be completed",
            "color":"Orange"
    }
    response = user_client.post('/api/notes', json = add_note, headers = {"Content-Type":"application/json", "Authorization":login_token})
    assert response.status_code == 201

# @pytest.mark.test_fix
# update a note
def test_update_note_should_return_success_response(user_client, login_token):
    add_note = {
            "title":"Homework for today",
            "description":"This need to be completed",
            "color":"Orange"
    }
    response = user_client.post('/api/notes', json=add_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 201

    # Retrieving the ID of the added note
    note_id = response.json['data']['note_id']

    # Updating the note
    update_note = {
        "title": "Homework for tomorrow",
        "description": "No need to complete this today",
        "color": "Green"
    }
    response = user_client.put(f'/api/notes/{note_id}', json=update_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 200


# Delete a note   
def test_delete_note_should_return_success_response(user_client, login_token):
    add_note = {
            "title":"Homework for today",
            "description":"This need to be completed",
            "color":"Orange"
    }
    response = user_client.post('/api/notes', json=add_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 201

    # Retrieving the ID of the added note
    note_id = response.json['data']['note_id']

    # Deleting the note
    response = user_client.delete(f'/api/notes/{note_id}', headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 201

# Archive a note
def test_archive_note_should_return_success_response(user_client, login_token):
    add_note = {
            "title":"Homework for today",
            "description":"This need to be completed",
            "color":"Orange"
    }
    response = user_client.post('/api/notes', json=add_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 201

    # Retrieving the ID of the added note
    note_id = response.json['data']['note_id']

    # Archiving the note
    archive_note = {"note_id": note_id}
    response = user_client.put('/api/archive', json=archive_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 200
   
# Unarchive a note
def test_unarchive_note_should_return_success_response(user_client, login_token):
    add_note = {
            "title":"Homework for today",
            "description":"This need to be completed",
            "color":"Orange"
    }
    response = user_client.post('/api/notes', json=add_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 201

    # Retrieving the ID of the added note
    note_id = response.json['data']['note_id']

    # Archiving the note
    archive_note = {"note_id": note_id}
    response = user_client.put('/api/archive', json=archive_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 200

    # Unarchiving the note
    response = user_client.put('/api/archive', json=archive_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 200
    
# Trash a note
def test_trash_note_should_return_success_response(user_client, login_token):
    add_note = {
            "title":"Homework for today",
            "description":"This need to be completed",
            "color":"Orange"
    }
    response = user_client.post('/api/notes', json=add_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 201

    # Retrieving the ID of the added note
    note_id = response.json['data']['note_id']

    # Trashing the note
    trash_note = {"note_id": note_id}
    response = user_client.put('/api/trash', json=trash_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 200

# Restore a trashed note
def test_restore_trashed_note_should_return_success_response(user_client, login_token):
    add_note = {
            "title":"Homework for today",
            "description":"This need to be completed",
            "color":"Orange"
    }
    response = user_client.post('/api/notes', json=add_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 201

    # Retrieving the ID of the added note
    note_id = response.json['data']['note_id']

    # Trashing the note
    trash_note = {"note_id": note_id}
    response = user_client.put('/api/trash', json=trash_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 200

    # Restoring the trashed note
    response = user_client.put('/api/trash', json=trash_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 200


# Collaborate a note
def test_collaborate_api_should_share_note_successfully(user_client, fixture_collaborate):
    # Register user 3
    register_data_3 = {
        "username": "Shyam",
        "email": "yadavsharwan26@gmail.com",
        "password": "Sonu1234567@#$",
        "location": "Pune"
    }
    response = user_client.post('/api/register', json=register_data_3, headers={"Content-Type": "application/json"})
    assert response.status_code == 201

    # Create a note
    add_note = {
        "title": "Homework for today",
        "description": "This needs to be completed",
        "color": "Orange"
    }
    response = user_client.post('/api/notes', json=add_note,
                                headers={"Content-Type": "application/json", "Authorization": fixture_collaborate})
    assert response.status_code == 201
    note_id = response.json['data']['note_id']

    # Share the note with users 2 and 3
    collaborate_note = {
        "note_id": note_id,
        "user_ids": [2, 3]
    }
    response = user_client.post('/api/collaborate', json=collaborate_note,
                                headers={"Content-Type": "application/json", "Authorization": fixture_collaborate})
    assert response.status_code == 200
    assert response.json['message'] == "Note shared successfully"

# Delete Collaborate note
def test_collaborate_api_should_remove_collaborator_successfully(user_client, fixture_collaborate):
    # Login user 2 and get token
    login_user_2 = {
        "username": "Ram",
        "password": "Sonu12345@#$"
    }
    response = user_client.post('/api/login', json=login_user_2, headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    token_user_2 = response.json['token']

    # Create a note by user 1
    add_note = {
        "title": "Homework for today",
        "description": "This needs to be completed",
        "color": "Orange"
    }
    response = user_client.post('/api/notes', json=add_note,
                                headers={"Content-Type": "application/json", "Authorization": fixture_collaborate})
    assert response.status_code == 201
    note_id = response.json['data']['note_id']

    # Share the note with user 2
    collaborate_note = {
        "note_id": note_id,
        "user_ids": [2]  
    }
    response = user_client.post('/api/collaborate', json=collaborate_note,
                                headers={"Content-Type": "application/json", "Authorization": fixture_collaborate})
    assert response.status_code == 200
    assert response.json['message'] == "Note shared successfully"

    # Remove user 2 as a collaborator
    delete_collaborator_note = {
        "note_id": note_id, 
        "user_ids": [2]  
    }
    response = user_client.delete('/api/collaborate', json=delete_collaborator_note,
                                  headers={"Content-Type": "application/json", "Authorization": fixture_collaborate})
    assert response.status_code == 200
    assert response.json['message'] == "Collaborators removed successfully"
