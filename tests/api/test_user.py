import pytest
import uuid
from flask_jwt_extended import create_access_token


@pytest.mark.parametrize("user_data, expected_status, expected_message", [
    ({
         "first_name": "John",
         "last_name": "Doe",
         "username": f"johndoe_{uuid.uuid4()}",
         "email": f"john_{uuid.uuid4()}@example.com",
         "password": "password123"
     }, 201, "User registered successfully"),

    ({
         "first_name": "John",
         "last_name": "Doe",
         "username": "johndoe_duplicate",
         "email": "john@example.com",
         "password": "password123"
     }, 422, "A user with this email or username already exists"),

    ("Invalid JSON", 400, "Invalid JSON")
])
def test_register_user(client, user_data, expected_status, expected_message):
    if isinstance(user_data, str):
        response = client.post("/api/register", data=user_data, content_type="application/json")
    else:
        response = client.post("/api/register", json=user_data)

    assert response.status_code == expected_status

    if response.content_type == "application/json":
        json_data = response.get_json()
        assert json_data is not None, "Response JSON data should not be None"
        assert json_data.get("message", json_data.get("error")) == expected_message
    else:
        assert response.content_type == "text/html; charset=utf-8", "Response should be HTML for invalid JSON"
        assert 'Invalid JSON' in response.data.decode(), f"Expected message: {expected_message}, but got: {response.data.decode()}"


@pytest.mark.parametrize("user_data, expected_status, expected_message", [

    ({
         "username": "johndoe_unique",
         "password": "wrongpassword"
     }, 401, "Invalid credentials"),

    ({
         "password": "password123"
     }, 400, "Username and password are required"),

    ({
         "username": "johndoe_unique"
     }, 400, "Username and password are required"),

    ("Invalid JSON", 400, "Invalid JSON")
])
def test_login(client, user_data, expected_status, expected_message, setup_test_user):
    if isinstance(user_data, str):
        response = client.post("/api/login", data=user_data, content_type="application/json")
    else:
        response = client.post("/api/login", json=user_data)

    assert response.status_code == expected_status, f"Expected status code {expected_status} but got {response.status_code}. Response data: {response.data.decode()}"

    if response.content_type == "application/json":
        json_data = response.get_json()
        assert json_data is not None, "Response JSON data should not be None"

        if expected_message:
            assert json_data.get("error") == expected_message
        else:
            assert 'access_token' in json_data
            assert 'refresh_token' in json_data
    else:
        assert response.content_type == "text/html; charset=utf-8", "Response should be HTML for invalid JSON"
        assert 'Invalid JSON' in response.data.decode(), f"Expected message: {expected_message}, but got: {response.data.decode()}"

@pytest.mark.parametrize("auth_token, expected_status, expected_message", [
    ("valid_token", 200, None),

    (None, 401, "Missing Authorization Header"),

    ("invalid_token", 422, "Not enough segments")
])
def test_get_users(client, auth_token, expected_status, expected_message, setup_test_user):
    headers = {}

    if auth_token == "valid_token":
        valid_token = create_access_token(identity=setup_test_user.id)
        headers["Authorization"] = f"Bearer {valid_token}"
    elif auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    response = client.get("/api/users", headers=headers)

    assert response.status_code == expected_status, f"Expected status {expected_status}, but got {response.status_code}"

    if response.status_code == 200:
        json_data = response.get_json()
        assert isinstance(json_data, list), "Response should be a list of users"
        assert len(json_data) > 0, "There should be at least one user in the response"
    else:
        json_data = response.get_json()
        assert json_data is not None, "Error response should contain JSON"
        assert json_data.get("msg", json_data.get("error")) == expected_message


@pytest.mark.parametrize("auth_user, expected_status, expected_message", [
    ("johndoe", 200, "User deleted successfully"),

    ("johndoe", 403, "Unauthorized to delete this user"),

    ("johndoe", 404, "User not found")
])
def test_delete_user(client, setup_test_users, auth_user, expected_status, expected_message):
    user1, user2 = setup_test_users

    if expected_status == 200:
        user_id = user1.id
    elif expected_status == 403:
        user_id = user2.id
    else:
        user_id = 999

    if auth_user == "johndoe":
        current_user = user1
    else:
        current_user = user2

    token = create_access_token(identity=current_user.id)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.delete(f"/api/users/{user_id}", headers=headers)

    assert response.status_code == expected_status, f"Expected status code {expected_status}, got {response.status_code}"

    json_data = response.get_json()
    assert json_data is not None, "Response JSON data should not be None"
    assert json_data.get("message", json_data.get("error")) == expected_message
