FROM python:3.12-slim

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false
ENV FLASK_APP=api.app

WORKDIR /api

COPY pyproject.toml poetry.lock /api/

RUN poetry install --no-dev

COPY api /api

EXPOSE 5001

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=5001"]
