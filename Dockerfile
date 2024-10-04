FROM python:3.10-slim

EXPOSE 8000
VOLUME /app/data

WORKDIR /app
COPY ./api/requirements.txt ./
COPY ./api/bil /app/bil
COPY ./bil-ui/dist /app/static
RUN apt-get update && apt-get install -y build-essential libmagic-dev git 
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt && git config --global user.name "bil" && git config --global user.email "bil@bil.local"

CMD uvicorn bil.main:app --host 0.0.0.0 --port 8000 --reload
