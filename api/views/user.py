from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from pydantic import ValidationError
from api.models.base import get_session
from api.models.user import User
from api.schemas import UserInSchema
from api.schemas.user import UserOutSchema
from sqlalchemy.exc import IntegrityError

users_bp = Blueprint("users", __name__)

@users_bp.route("/register", methods=["POST"])
def register():
    try:
        user_data = request.get_json()
    except BadRequest:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        user_in = UserInSchema(**user_data)
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 422

    user = User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        username=user_in.username,
        email=user_in.email
    )
    user.password = user_in.password

    session = get_session()
    try:
        with session.begin():
            session.add(user)
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "A user with this email or username already exists"}), 422

    return jsonify({"message": "User registered successfully"}), 201


@users_bp.route("/login", methods=["POST"])
def login():
    try:
        user_data = request.get_json()
    except BadRequest:
        return jsonify({"error": "Invalid JSON"}), 400

    username = user_data.get("username")
    password = user_data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    session = get_session()
    user = session.query(User).filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401



@users_bp.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    session = get_session()
    with session.begin():
        users = session.query(User).all()
    users_out = [UserOutSchema.model_validate(user) for user in users]
    return [user.model_dump(mode="json") for user in users_out]


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id: int):
    session = get_session()
    current_user_id = get_jwt_identity()

    # Update this line to use session.get
    user = session.get(User, user_id)  # Updated to Session.get()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.id != current_user_id:
        return jsonify({"error": "Unauthorized to delete this user"}), 403

    with session.begin_nested():
        session.delete(user)
        session.commit()

    return jsonify({"message": "User deleted successfully"}), 200