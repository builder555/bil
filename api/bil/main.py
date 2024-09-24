from fastapi import FastAPI, HTTPException, Depends, UploadFile, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from bil.datamodels import (
    PaygroupInput,
    Payment,
    PaymentInput,
    ProjectInput,
    ProjectResponse,
    ProjectWithPayments,
    NewItemResponse,
)
from bil.dbfile import DBAdaptor, ItemNotFoundError
import json
import magic

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


def only_allow_types(content_types):
    async def inner(file: UploadFile):
        sample_bytes = await file.read(2048)
        await file.seek(0)
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(sample_bytes)
        if mime_type not in content_types:
            raise HTTPException(status_code=415, detail="Unsupported media type")
        return file

    return inner


app.mount("/css", StaticFiles(directory="dist/css"), name="static")
app.mount("/js", StaticFiles(directory="dist/js"), name="static")
app.mount("/img", StaticFiles(directory="dist/img"), name="static")
app.mount("/fonts", StaticFiles(directory="dist/fonts"), name="static")


@app.get("/projects", response_model=list[ProjectResponse])
async def list_projects(db=Depends(get_db)):
    return db.get_projects()


@app.post("/projects", response_model=NewItemResponse)
async def add_a_new_project(project: ProjectInput, db=Depends(get_db)):
    new_id = db.add_project(project.name)
    return {"id": new_id}


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


@app.put("/projects/{project_id}")
async def update_project(project_id: int, project: ProjectInput, db=Depends(get_db)):
    try:
        return db.update_project(project_id, project.name)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.post("/projects/{project_id}/paygroups", response_model=NewItemResponse)
async def add_new_paygroup(project_id: int, group: PaygroupInput, db=Depends(get_db)):
    group_id = db.add_paygroup(project_id, group.name)
    return {"id": group_id}


@app.delete("/projects/{project_id}/paygroups/{group_id}")
async def delete_paygroup(project_id: int, group_id: int, db=Depends(get_db)):
    try:
        return db.delete_paygroup(project_id, group_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.put("/projects/{project_id}/paygroups/{group_id}")
async def update_paygroup(project_id: int, group_id: int, group: PaygroupInput, db=Depends(get_db)):
    try:
        return db.update_paygroup(project_id, group_id, group.name)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.post("/projects/{project_id}/paygroups/{group_id}/payments", response_model=NewItemResponse)
async def add_new_payment(project_id: int, group_id: int, payment: PaymentInput, db=Depends(get_db)):
    try:
        payment_id = db.add_payment(project_id, group_id, payment)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)
    return {"id": payment_id}


@app.delete("/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}")
async def delete_payment(project_id: int, group_id: int, payment_id: int, db=Depends(get_db)):
    try:
        return db.delete_payment(project_id, group_id, payment_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.put("/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}")
async def update_payment(project_id: int, group_id: int, payment_id: int, payment: PaymentInput, db=Depends(get_db)):
    try:
        return db.update_payment(project_id, group_id, Payment(id=payment_id, **payment.model_dump()))
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.post("/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}/files")
async def add_file_to_payment(
    project_id: int,
    group_id: int,
    payment_id: int,
    file: UploadFile = Depends(only_allow_types(["application/pdf", "image/jpeg"])),
    db: DBAdaptor = Depends(get_db),
):
    try:
        return db.add_file_to_payment(project_id, group_id, payment_id, file)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.get("/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}/files", response_model=bytes)
async def get_files_from_payment(project_id: int, group_id: int, payment_id: int, db=Depends(get_db)):
    try:
        return Response(content=db.get_files_from_payment(project_id, group_id, payment_id))
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


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
