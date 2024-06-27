from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dbfile import DBAdaptor, ItemNotFoundError
import json

app = FastAPI(title="bil-api")

origins = [
    # "http://localhost",
    # "http://localhost:8080",
    # "http://localhost:8000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db = DBAdaptor("data/")


@app.get("/projects")
async def list_projects():
    return db.get_projects()


@app.post("/projects")
async def add_a_new_project(name: str):
    return db.add_project(name)


@app.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    try:
        return db.delete_project(project_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


app.mount("/css", StaticFiles(directory="dist/css"), name="static")
app.mount("/js", StaticFiles(directory="dist/js"), name="static")
app.mount("/img", StaticFiles(directory="dist/img"), name="static")
app.mount("/fonts", StaticFiles(directory="dist/fonts"), name="static")


@app.get("/manifest.json")
async def srvwork():
    with open("dist/manifest.json", "r") as f:
        return json.loads(f.read())


@app.get("/")
@app.get("/{id}")
async def root():
    with open("dist/index.html", "r") as f:
        return HTMLResponse(f.read())
