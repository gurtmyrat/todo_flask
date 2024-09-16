import pytest
from api.models.task import Task, TaskStatusEnum
from flask_jwt_extended import create_access_token


@pytest.mark.parametrize("page, per_page, expected_status, expected_count", [
    (1, 10, 200, 5),
    (-1, 10, 400, None),
    (1, -10, 400, None)
])
def test_get_all_tasks(client, setup_test_users, db_session, page, per_page, expected_status, expected_count):
    user1, _ = setup_test_users

    for i in range(5):
        task = Task(
            title=f"Task {i + 1}",
            description="Test description",
            status=TaskStatusEnum.NEW,
            user_id=user1.id
        )
        db_session.add(task)
    db_session.commit()

    total_in_db = db_session.query(Task).count()
    print(f"Total tasks in DB: {total_in_db}")

    response = client.get(f"/api/tasks/all?page={page}&per_page={per_page}")

    print(f"API response: {response.get_json()}")

    assert response.status_code == expected_status
    json_data = response.get_json()

    if expected_count is not None:
        assert json_data["total_tasks"] == expected_count
        assert len(json_data["tasks"]) == expected_count
    else:
        assert "error" in json_data

@pytest.mark.parametrize("task_id, expected_status, expected_error", [
    (999, 404, "Task not found"),  # Invalid task ID
    (1, 403, "You are not authorized to view this task"),  # Unauthorized access
])
def test_get_task(client, setup_test_users, jwt_token, db_session, task_id, expected_status, expected_error):
    user1, _ = setup_test_users

    task = Task(
        title="Test Task",
        description="Test description",
        status=TaskStatusEnum.NEW,
        user_id=user1.id
    )
    db_session.add(task)
    db_session.commit()

    if task_id == 1:
        task_id = task.id

    response = client.get(f"/api/tasks/{task_id}", headers={"Authorization": f"Bearer {jwt_token}"})

    assert response.status_code == expected_status

    if expected_error:
        assert expected_error in response.get_json().get("error")
    else:
        json_data = response.get_json()
        assert json_data["id"] == task.id



@pytest.mark.parametrize("task_data, expected_status, expected_error", [
    ({"title": "New Task", "description": "Task description", "status": "NEW"}, 201, None),  # Valid task data
    ({}, 422, {"error": {"title": ["Field required"], "status": ["Field required"]}}),  # Missing required fields
    ({"title": "New Task", "status": "INVALID_STATUS"}, 422, {"error": {"status": ["Input should be 'NEW', 'IN_PROGRESS' or 'COMPLETED'"]}}),  # Invalid status value
])
def test_create_task(client, setup_test_users, db_session, task_data, expected_status, expected_error):
    user1, _ = setup_test_users
    token = create_access_token(identity=user1.id)

    response = client.post("/api/tasks", json=task_data, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == expected_status

    json_data = response.get_json()

    if expected_error:
        assert "error" in json_data
        assert json_data["error"] == expected_error["error"]
    else:
        assert "id" in json_data
        assert json_data["title"] == task_data["title"]
        assert json_data["description"] == task_data["description"]
        assert json_data["status"] == task_data["status"]

        task_in_db = db_session.query(Task).filter_by(id=json_data["id"]).first()
        assert task_in_db is not None
        assert task_in_db.title == task_data["title"]
        assert task_in_db.description == task_data["description"]
        assert task_in_db.status == TaskStatusEnum(task_data["status"])
        assert task_in_db.user_id == user1.id

    if expected_status == 201:
        db_session.query(Task).filter_by(id=json_data["id"]).delete(synchronize_session=False)
        db_session.commit()


@pytest.mark.parametrize("task_data, expected_status, expected_error", [
    ({"title": "Updated Task", "description": "Updated description", "status": "IN_PROGRESS"}, 200, None),
    ({"status": "INVALID_STATUS"}, 422, {"error": "Input should be 'NEW', 'IN_PROGRESS' or 'COMPLETED'"}),
    ({"title": ""}, 422, {"error": "String should have at least 1 character"}),
])
def test_update_task(client, setup_test_users, db_session, task_data, expected_status, expected_error):
    user1, user2 = setup_test_users
    token = create_access_token(identity=user1.id)

    task = Task(
        title="Old Task",
        description="Old description",
        status=TaskStatusEnum.NEW,
        user_id=user1.id
    )
    db_session.add(task)
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    if task_data is None:
        response = client.put(f"/api/task/{task.id}", data="Invalid JSON", headers={**headers, "Content-Type": "application/json"})
    else:
        response = client.put(f"/api/task/{task.id}", json=task_data, headers=headers)

    assert response.status_code == expected_status
    json_data = response.get_json()

    if expected_error:
        assert "error" in json_data or any(e["msg"] == expected_error["error"] for e in json_data)
    else:
        updated_task = db_session.query(Task).filter_by(id=task.id).first()
        db_session.refresh(updated_task)  # Refresh task data
        assert updated_task.title == task_data["title"]
        assert updated_task.description == task_data["description"]
        assert updated_task.status == TaskStatusEnum(task_data["status"])



@pytest.mark.parametrize("task_id, expected_status, expected_error", [
    (1, 200, None),
    (999, 404, {"error": "Task not found"}),
])
def test_delete_task(client, setup_test_users, db_session, task_id, expected_status, expected_error):
    user1, user2 = setup_test_users
    token = create_access_token(identity=user1.id)

    if task_id == 1:
        task = Task(
            title="Test Task",
            description="Task description",
            status=TaskStatusEnum.NEW,
            user_id=user1.id
        )
        db_session.add(task)
        db_session.commit()
        task_id = task.id

    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(f"/api/task/{task_id}", headers=headers)

    assert response.status_code == expected_status

    json_data = response.get_json()
    if expected_error:
        assert json_data == expected_error
    else:
        deleted_task = db_session.query(Task).filter_by(id=task_id).first()
        assert deleted_task is None

def test_delete_task_access_control(client, setup_test_users, db_session):
    user1, user2 = setup_test_users
    token_user2 = create_access_token(identity=user2.id)

    task = Task(
        title="Test Task",
        description="Task description",
        status=TaskStatusEnum.NEW,
        user_id=user1.id
    )
    db_session.add(task)
    db_session.commit()

    headers = {"Authorization": f"Bearer {token_user2}"}
    response = client.delete(f"/api/task/{task.id}", headers=headers)

    assert response.status_code == 403

    json_data = response.get_json()
    assert json_data["error"] == "Access denied"

    task_in_db = db_session.query(Task).filter_by(id=task.id).first()
    assert task_in_db is not None

@pytest.mark.parametrize("task_id, expected_status, expected_error", [
    (999, 404, {"error": "Task not found"}),
])
def test_mark_task_as_completed(client, setup_test_users, db_session, task_id, expected_status, expected_error):
    user1, user2 = setup_test_users
    token = create_access_token(identity=user1.id)

    if task_id == 1:
        task = Task(
            title="Test Task",
            description="Task description",
            status=TaskStatusEnum.NEW,
            user_id=user1.id
        )
        db_session.add(task)
        db_session.commit()
        task_id = task.id

    headers = {"Authorization": f"Bearer {token}"}

    response = client.put(f"/api/tasks/{task_id}/complete", headers=headers)

    assert response.status_code == expected_status

    json_data = response.get_json()
    if expected_error:
        assert json_data == expected_error
    else:
        assert json_data["status"] == "COMPLETED"
        updated_task = db_session.query(Task).filter_by(id=task_id).first()
        assert updated_task.status == TaskStatusEnum.COMPLETED


def test_mark_task_as_completed_access_control(client, setup_test_users, db_session):
    user1, user2 = setup_test_users
    token_user2 = create_access_token(identity=user2.id)

    task = Task(
        title="Test Task",
        description="Task description",
        status=TaskStatusEnum.NEW,
        user_id=user1.id
    )
    db_session.add(task)
    db_session.commit()

    headers = {"Authorization": f"Bearer {token_user2}"}
    response = client.put(f"/api/tasks/{task.id}/complete", headers=headers)

    assert response.status_code == 403

    json_data = response.get_json()
    assert json_data["error"] == "Access denied"

    task_in_db = db_session.query(Task).filter_by(id=task.id).first()
    assert task_in_db.status == TaskStatusEnum.NEW


@pytest.mark.parametrize("status, expected_status, expected_error", [
    ("NEW", 200, None),
    ("INVALID_STATUS", 400, {"error": "Invalid status"}),
])
def test_get_tasks_by_status(client, setup_test_users, db_session, status, expected_status, expected_error):
    user1, _ = setup_test_users
    token = create_access_token(identity=user1.id)

    if status == "NEW":
        task = Task(
            title="Test Task",
            description="Task description",
            status=TaskStatusEnum.NEW,
            user_id=user1.id
        )
        db_session.add(task)
        db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/tasks/status/{status}", headers=headers)

    assert response.status_code == expected_status
    json_data = response.get_json()

    if expected_error:
        assert json_data == expected_error
    else:
        assert isinstance(json_data, list)
        assert len(json_data) > 0
        assert all(task["status"] == status for task in json_data)

        for task_data in json_data:
            task = db_session.query(Task).filter_by(id=task_data["id"]).first()
            assert task.user_id == user1.id
            assert task.status == TaskStatusEnum[status]