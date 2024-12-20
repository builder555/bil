from typing import Callable
from fastapi import FastAPI, HTTPException, Depends, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from bil.datamodels import (
    PaygroupInput,
    Payment,
    PaymentInput,
    ProjectInput,
    ProjectResponse,
    ProjectWithPayments,
    NewItemResponse,
    TagModel,
)
from bil.dbfile import DBAdaptor, ItemNotFoundError
import uvicorn
import magic
import os

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


def get_db() -> DBAdaptor:
    db = DBAdaptor("data/")
    return db


def only_allow_types(content_types: list[str]) -> Callable[[UploadFile], UploadFile]:
    async def inner(file: UploadFile) -> UploadFile:
        sample_bytes = await file.read(2048)
        await file.seek(0)
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(sample_bytes)
        if mime_type not in content_types:
            raise HTTPException(status_code=415, detail="Unsupported media type")
        return file

    return inner


@app.get("/projects", response_model=list[ProjectResponse])
async def list_projects(db: DBAdaptor = Depends(get_db)):
    return db.get_projects()


@app.post("/projects", response_model=NewItemResponse)
async def add_a_new_project(project: ProjectInput, db: DBAdaptor = Depends(get_db)):
    new_id = db.add_project(project.name)
    return {"id": new_id}


@app.delete("/projects/{project_id}")
async def delete_project(project_id: int, db: DBAdaptor = Depends(get_db)):
    try:
        return db.delete_project(project_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.put("/projects/{project_id}/restore")
async def restore_deleted_project(project_id: int, db: DBAdaptor = Depends(get_db)):
    try:
        return db.restore_project(project_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.get("/projects/{project_id}", response_model=ProjectWithPayments)
async def get_project(project_id: int, db: DBAdaptor = Depends(get_db)):
    try:
        return db.get_project(project_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.put("/projects/{project_id}")
async def update_project(project_id: int, project: ProjectInput, db: DBAdaptor = Depends(get_db)):
    try:
        return db.update_project(project_id, project.name)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.get("/projects/{project_id}/history")
async def get_project_history(project_id: int, db: DBAdaptor = Depends(get_db)):
    try:
        return db.get_project_history(project_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.get("/projects/{project_id}/history/{history_id}", response_model=ProjectWithPayments)
async def get_past_project_state(project_id: int, history_id: str, db: DBAdaptor = Depends(get_db)):
    try:
        return db.get_project_state(project_id, history_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.get("/projects/{project_id}/tags", response_model=list[TagModel])
async def get_project_tags(project_id: int, db: DBAdaptor = Depends(get_db)):
    try:
        return db.get_tags(project_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.post("/projects/{project_id}/paygroups", response_model=NewItemResponse)
async def add_new_paygroup(project_id: int, group: PaygroupInput, db: DBAdaptor = Depends(get_db)):
    try:
        group_id = db.add_paygroup(project_id, group.name)
        return {"id": group_id}
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.delete("/projects/{project_id}/paygroups/{group_id}")
async def delete_paygroup(project_id: int, group_id: int, db: DBAdaptor = Depends(get_db)):
    try:
        return db.delete_paygroup(project_id, group_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.put("/projects/{project_id}/paygroups/{group_id}")
async def update_paygroup(project_id: int, group_id: int, group: PaygroupInput, db: DBAdaptor = Depends(get_db)):
    try:
        return db.update_paygroup(project_id, group_id, group.name)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.post("/projects/{project_id}/paygroups/{group_id}/payments", response_model=NewItemResponse)
async def add_new_payment(project_id: int, group_id: int, payment: PaymentInput, db: DBAdaptor = Depends(get_db)):
    try:
        payment_id = db.add_payment(project_id, group_id, payment)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)
    return {"id": payment_id}


@app.delete("/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}")
async def delete_payment(project_id: int, group_id: int, payment_id: int, db: DBAdaptor = Depends(get_db)):
    try:
        return db.delete_payment(project_id, group_id, payment_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.put("/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}")
async def update_payment(
    project_id: int, group_id: int, payment_id: int, payment: PaymentInput, db: DBAdaptor = Depends(get_db)
):
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


@app.get("/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}/files", response_class=FileResponse)
async def get_files_from_payment(project_id: int, group_id: int, payment_id: int, db: DBAdaptor = Depends(get_db)):
    try:
        file_path = db.get_files_from_payment(project_id, group_id, payment_id)
        extension = os.path.splitext(file_path)[1]
        media_type = magic.from_file(file_path, mime=True)
        return FileResponse(
            path=file_path,
            filename=f"payment_{payment_id}{extension}",
            content_disposition_type="inline",
            media_type=media_type,
        )
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.delete("/projects/{project_id}/paygroups/{group_id}/payments/{payment_id}/files")
async def delete_file_from_payment(project_id: int, group_id: int, payment_id: int, db: DBAdaptor = Depends(get_db)):
    try:
        return db.delete_file_from_payment(project_id, group_id, payment_id)
    except ItemNotFoundError:
        raise HTTPException(status_code=404)


@app.get("/{id:int}")
def get_index_html(id: int):
    return FileResponse("./static/index.html")


app.mount("/", StaticFiles(directory="static", html=True, check_dir=False), name="static")


def start_app():
    uvicorn.run("bil.main:app", host="0.0.0.0", port=8000, reload=True)
