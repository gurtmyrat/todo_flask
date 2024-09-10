FROM python:3.12-slim

WORKDIR /api

COPY pyproject.toml poetry.lock /api/

RUN pip install poetry

RUN poetry install --no-dev

COPY api /api

EXPOSE 5001

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=5001"]