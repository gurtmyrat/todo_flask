# Используем базовый образ Python
FROM python:3.12-slim

WORKDIR /api

COPY pyproject.toml poetry.lock /api/

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем зависимости с Poetry
RUN poetry install --no-dev

# Копируем исходный код в контейнер
COPY api /api

# Устанавливаем переменную окружения FLASK_APP
ENV FLASK_APP=app

EXPOSE 5001

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=5001"]