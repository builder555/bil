FROM node:16 AS build-stage

WORKDIR /app

COPY ./bil-ui/package*.json ./
RUN yarn
COPY ./bil-ui .
RUN yarn build


FROM python:3.10-slim

EXPOSE 8000
VOLUME /app/data

WORKDIR /app
COPY ./api/pyproject.toml /app/pyproject.toml
COPY ./api/poetry.lock /app/poetry.lock
COPY ./api/bil /app/bil
COPY --from=build-stage /app/dist ./static
RUN apt update && apt install -y libmagic-dev git && pip install --upgrade pip && pip install --no-cache-dir --upgrade poetry poetry-plugin-export && poetry export --format=requirements.txt --output=requirements.txt --without-hashes && pip install --no-cache-dir -r requirements.txt && git config --global user.name "bil" && git config --global user.email "bil@bil.local"

CMD uvicorn bil.main:app --host 0.0.0.0 --port 8000 --reload
