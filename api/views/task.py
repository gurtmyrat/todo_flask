import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError
from api.models.base import get_session
from api.models.task import Task
from api.schemas.task import TaskOutSchema, TaskInSchema

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/tasks/all", methods=["GET"])
def get_all_tasks():
    session = get_session()
    with session.begin():
        tasks = session.query(Task).all()

    tasks_out = [TaskOutSchema.model_validate(task) for task in tasks]
    return jsonify([task.model_dump(mode="json") for task in tasks_out]), 200

@tasks_bp.route("/tasks", methods=["GET"])
@jwt_required()
def get_user_tasks():
    session = get_session()
    current_user_id = get_jwt_identity()

    with session.begin():
        tasks = session.query(Task).filter_by(user_id=current_user_id).all()

    tasks_out = [TaskOutSchema.model_validate(task) for task in tasks]
    return jsonify([task.model_dump(mode="json") for task in tasks_out]), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    session = get_session()
    current_user_id = get_jwt_identity()

    with session.begin():
        task = session.query(Task).filter_by(id=task_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task.user_id != current_user_id:
        return jsonify({"error": "You are not authorized to view this task"}), 403

    task_out = TaskOutSchema.model_validate(task)
    return jsonify(task_out.model_dump(mode="json")), 200

@tasks_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    try:
        task_data = request.json

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400
    try:
        task_in = TaskInSchema(**task_data)
    except ValidationError as e:
        return jsonify({e.errors()}), 422

    current_user_id = get_jwt_identity()
    new_task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        user_id=current_user_id
    )

    session = get_session()
    with session.begin_nested():
        session.add(new_task)
        session.commit()

    task_out = TaskOutSchema.model_validate(new_task)
    return jsonify(task_out.model_dump(mode="json")), 201

@tasks_bp.route("/task/<int:task_id>",  methods=["PUT"])
@jwt_required()
def update_task(task_id):
    session = get_session()
    task = session.query(Task).get(task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    current_user_id = get_jwt_identity()

    if task.user_id != current_user_id:
        return jsonify({"error": "Access denied"}), 403

    try:
        task_data = request.json
        task_in = TaskInSchema(**task_data)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400
    except ValidationError as e:
        return jsonify(e.errors()), 422

    task.title = task_in.title
    task.description = task_in.description
    task.status = task_in.status

    session.commit()

    task_out = TaskOutSchema.model_validate(task)

    return jsonify(task_out.model_dump(mode="json")), 200


@tasks_bp.route('/task/<int:task_id>', methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    session = get_session()
    task = session.query(Task).get(task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404
    current_user_id = get_jwt_identity()

    if task.user_id != current_user_id:
        return jsonify({"error": "Access denied"}), 403

    with session.begin_nested():
        session.delete(task)
        session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200



