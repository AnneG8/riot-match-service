FROM python:3.11-slim

ENV \
    # poetry
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_ANSI=1

WORKDIR /app

RUN pip install poetry==1.8.3

COPY ./pyproject.toml ./poetry.lock* ./

RUN poetry config virtualenvs.create false

RUN poetry install --only main

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
