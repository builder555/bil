FROM python:3.10-slim

EXPOSE 8000

WORKDIR /app

COPY api/pyproject.toml /app/pyproject.toml
COPY api/poetry.lock /app/poetry.lock

RUN apt update && apt install -y git && pip install --upgrade pip && pip install --no-cache-dir --upgrade poetry poetry-plugin-export && poetry export --format=requirements.txt --output=requirements.txt --without-hashes && pip install --no-cache-dir -r requirements.txt

CMD uvicorn bil.main:app --host 0.0.0.0 --port 8000 --reload
