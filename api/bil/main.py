from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from bil.datamodels import PaygroupBase, ProjectInput, ProjectResponse, ProjectWithPayments
from bil.dbfile import DBAdaptor, ItemNotFoundError
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


def get_db():
    db = DBAdaptor("data/")
    return db


app.mount("/css", StaticFiles(directory="dist/css"), name="static")
app.mount("/js", StaticFiles(directory="dist/js"), name="static")
app.mount("/img", StaticFiles(directory="dist/img"), name="static")
app.mount("/fonts", StaticFiles(directory="dist/fonts"), name="static")


@app.get("/projects", response_model=list[ProjectResponse])
async def list_projects(db=Depends(get_db)):
    return db.get_projects()


@app.post("/projects", response_model=ProjectResponse)
async def add_a_new_project(project: ProjectInput, db=Depends(get_db)):
    new_id = db.add_project(project.name)
    return ProjectResponse(id=new_id, name=project.name)


@app.delete("/projects/{project_id}")
async def delete_project(project_id: int, db=Depends(get_db)):
    try:
        return db.delete_project(project_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.get("/projects/{project_id}", response_model=ProjectWithPayments)
async def get_project(project_id: int, db=Depends(get_db)):
    try:
        return db.get_project(project_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.post("/projects/{project_id}/paygroups")
async def add_new_paygroup(project_id: int, name: str, db=Depends(get_db)):
    db.add_paygroup(project_id, name)


@app.get("/manifest.json")
async def serve_manifest():
    with open("dist/manifest.json", "r") as f:
        return json.loads(f.read())


@app.get("/ping")
async def ping():
    return "pong"


@app.get("/")
@app.get("/{id}")
async def root():
    with open("dist/index.html", "r") as f:
        return HTMLResponse(f.read())
