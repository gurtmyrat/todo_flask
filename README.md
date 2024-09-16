# Task Management API

## Overview

This project is a task management API built with Flask, SQLAlchemy, and PostgreSQL. It provides functionalities for user management, task management, and includes features like JWT authentication, CRUD operations, pagination, and task status management. Docker is used for containerization, Poetry for dependency management, and Alembic for database migrations.

## Features

- **User Management:** Register, log in, and manage users with JWT authentication.
- **Task Management:** Create, read, update, delete, and filter tasks.
- **Pagination:** Efficiently paginate task lists.
- **Task Status:** Update and filter tasks based on their status.
- **Database Management:** Managed with PostgreSQL and Alembic for migrations.
- **Containerization:** Docker setup for development and production environments.

## Table of Contents

1. [Installation Instructions](#installation-instructions)
2. [Configuration](#configuration)
3. [Database Migrations](#database-migrations)
4. [API Documentation](#api-documentation)
5. [Running Tests](#running-tests)
6. [Contributing](#contributing)

## Installation Instructions

### Prerequisites

- Python 3.10 or later
- Docker
- Docker Compose
- Poetry

### Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/your-repo.git
    cd your-repo
    ```

2. **Install Poetry (if not already installed):**

    Follow the [Poetry installation guide](https://python-poetry.org/docs/#installation) to install Poetry.

3. **Install dependencies using Poetry:**

    ```bash
    poetry install
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory with the following content:

    ```env
    PGADMIN_DEFAULT_EMAIL=example@gmail.com
    PGADMIN_DEFAULT_PASSWORD=example
    FLASK_APP=api.app
    FLASK_ENV=development
    FLASK_DEBUG=1

    SECRET_KEY=example
    JWT_SECRET_KEY=example

    DATABASE_URL=postgresql://example:example@localhost:5432/example_db

    POSTGRES_USER=example
    POSTGRES_PASSWORD=example
    POSTGRES_DB=example_db
    POSTGRES_PORT=5432

    # Test Environment
    TEST_DATABASE_URL=postgresql://example:example@localhost:5432/test_db
    ```

5. **Build and start Docker containers:**

    ```bash
    docker-compose up --build
    ```

6. **Run database migrations:**

    Alembic is used for managing database migrations. Run the following command to apply migrations:

    ```bash
    docker-compose exec web alembic upgrade head
    ```

7. **Access the application:**

    The application will be accessible at `http://localhost:5001`. You can also access PgAdmin at `http://localhost:pgadmin` with the credentials specified in the `.env` file.

## Configuration

### Docker

The Docker setup is defined in `Dockerfile` and `docker-compose.yml`. The `Dockerfile` specifies the image build process, and `docker-compose.yml` manages the multi-container setup including PostgreSQL, PgAdmin, and the Flask application.

### Flask Configuration

The Flask application configuration is managed through `config.py`, and environment variables are loaded from the `.env` file. Key configuration parameters include:

- `SECRET_KEY`: Used for session management and security.
- `JWT_SECRET_KEY`: Key for encoding JWT tokens.
- `JWT_ACCESS_TOKEN_EXPIRES` and `JWT_REFRESH_TOKEN_EXPIRES`: Expiry times for JWT tokens.

## Database Migrations

Alembic is used for managing database migrations. Here’s how to handle migrations:

1. **Generate a New Migration:**

    ```bash
    docker-compose exec web alembic revision -m "Describe your migration"
    ```

2. **Apply Migrations:**

    ```bash
    docker-compose exec web alembic upgrade head
    ```

3. **Downgrade Migrations:**

    ```bash
    docker-compose exec web alembic downgrade -1
    ```

4. **Check Migration Status:**

    ```bash
    docker-compose exec web alembic current
    ```

5. **Initialize the Database (First Time Setup):**

    ```bash
    docker-compose exec web alembic upgrade head
    ```

## API Documentation

### User Endpoints

#### Register

- **URL:** `/api/register`
- **Method:** `POST`
- **Description:** Register a new user.
- **Request Body:**

    ```json
    {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "email": "john.doe@example.com",
        "password": "your_password"
    }
    ```

- **Response:**

    ```json
    {
        "message": "User registered successfully"
    }
    ```

#### Login

- **URL:** `/api/login`
- **Method:** `POST`
- **Description:** Log in a user and obtain access and refresh tokens.
- **Request Body:**

    ```json
    {
        "username": "johndoe",
        "password": "your_password"
    }
    ```

- **Response:**

    ```json
    {
        "access_token": "your_access_token",
        "refresh_token": "your_refresh_token"
    }
    ```

### Task Endpoints

#### Create Task

- **URL:** `/api/tasks`
- **Method:** `POST`
- **Description:** Create a new task.
- **Request Body:**

    ```json
    {
        "title": "Task Title",
        "description": "Task Description",
        "status": "NEW"
    }
    ```

- **Response:**

    ```json
    {
        "id": 1,
        "title": "Task Title",
        "description": "Task Description",
        "status": "NEW",
        "user_id": 1
    }
    ```

#### Get All Tasks

- **URL:** `/api/tasks/all`
- **Method:** `GET`
- **Description:** Get a paginated list of all tasks.
- **Query Parameters:**
  - `page` (optional, default: 1)
  - `per_page` (optional, default: 10)

- **Response:**

    ```json
    {
        "tasks": [
            {
                "id": 1,
                "title": "Task Title",
                "description": "Task Description",
                "status": "NEW",
                "user_id": 1
            }
        ],
        "page": 1,
        "per_page": 10,
        "total_tasks": 1
    }
    ```

#### Get User Tasks

- **URL:** `/api/tasks`
- **Method:** `GET`
- **Description:** Get a paginated list of tasks for the authenticated user.
- **Query Parameters:**
  - `page` (optional, default: 1)
  - `per_page` (optional, default: 10)

- **Response:** Same as `Get All Tasks`.

#### Get Task by ID

- **URL:** `/api/tasks/<task_id>`
- **Method:** `GET`
- **Description:** Get details of a specific task by its ID.

- **Response:**

    ```json
    {
        "id": 1,
        "title": "Task Title",
        "description": "Task Description",
        "status": "NEW",
        "user_id": 1
    }
    ```

#### Update Task

- **URL:** `/api/task/<task_id>`
- **Method:** `PUT`
- **Description:** Update an existing task.
- **Request Body:** Same as `Create Task`.

- **Response:** Same as `Create Task`.

#### Delete Task

- **URL:** `/api/task/<task_id>`
- **Method:** `DELETE`
- **Description:** Delete a task by its ID.

- **Response:**

    ```json
    {
        "message": "Task deleted successfully"
    }
    ```

#### Mark Task as Completed

- **URL:** `/api/tasks/<task_id>/complete`
- **Method:** `PUT`
- **Description:** Mark a task as completed.

- **Response:** Same as `Update Task`, with status set to "COMPLETED".

#### Get Tasks by Status

- **URL:** `/api/tasks/status/<status>`
- **Method:** `GET`
- **Description:** Get tasks filtered by status.

- **Response:** Same as `Get All Tasks`, but filtered by the specified status.

## Running Tests

1. **Install testing dependencies:**

    ```bash
    poetry add --dev pytest pytest-flask
    ```

2. **Run the tests:**

    ```bash
    poetry run pytest
    ```

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a new Pull Request.


