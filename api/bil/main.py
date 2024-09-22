from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datamodels import PaygroupBase, ProjectResponse
from dbfile import DBAdaptor, ItemNotFoundError
import json

app = FastAPI(title="bil-api")

origins = [
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

app.mount("/css", StaticFiles(directory="dist/css"), name="static")
app.mount("/js", StaticFiles(directory="dist/js"), name="static")
app.mount("/img", StaticFiles(directory="dist/img"), name="static")
app.mount("/fonts", StaticFiles(directory="dist/fonts"), name="static")


@app.get("/projects", response_model=list[ProjectResponse])
async def list_projects():
    return db.get_projects()


@app.post("/projects", response_model=None)
async def add_a_new_project(name: str):
    db.add_project(name)


@app.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    try:
        return db.delete_project(project_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.get("/projects/{project_id}")
async def get_project(project_id: int):
    try:
        return db.get_project(project_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.post("/projects/{project_id}/paygroups")
async def add_new_paygroup(project_id: int, name: str):
    db.add_paygroup(project_id, name)


@app.get("/manifest.json")
async def serve_manifest():
    with open("dist/manifest.json", "r") as f:
        return json.loads(f.read())


@app.get("/")
@app.get("/{id}")
async def root():
    with open("dist/index.html", "r") as f:
        return HTMLResponse(f.read())
