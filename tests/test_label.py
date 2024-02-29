import pytest

# Register for label
def test_register_label_should_return_success(user_client, login_token):
    add_label_to_note = {
        "name": "Urgent Work"
    }
    response = user_client.post('/api/labels', json=add_label_to_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 201

# Delete label
def test_delete_label(user_client, login_token):
    add_label_to_note = {
        "name": "Urgent Work"
    }
    response = user_client.post('/api/labels', json=add_label_to_note, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 201
    
    # Retrieving the ID of the added label
    label_id = response.json['data']['label_id']

    # Deleting the label
    response = user_client.delete(f'/api/labels/{label_id}', headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 200

# Update label
def test_get_label(user_client, login_token):
    update_label = {
        "name":"This is my work"
    }
    response = user_client.post('/api/labels', json=update_label, headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 201
    
    label_id = response.json['data']['label_id']

    response = user_client.get(f'/api/labels/{label_id}', headers={"Content-Type": "application/json", "Authorization": login_token})
    assert response.status_code == 200