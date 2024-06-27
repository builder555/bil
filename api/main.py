from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dbfile import DBAdaptor
import json

app = FastAPI()

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


db = DBAdaptor('data/')

@app.get('/projects')
async def list_projects():
    return db.get_projects()

@app.post('/projects')
async def add_a_new_project(name: str):
    return db.add_project(name)


# @app.put('/projects/{project_id}')
# async def update_project(project_id: int, details: Project):
#     return db.update_project(project_id, details.dict())

# @app.delete('/projects/{project_id}')
# async def delete_project(project_id: int):
#     return db.delete_project(project_id)

# @app.get('/projects/{project_id}/groups')
# async def payment_groups_in_a_project(project_id: int):
#     return db.get_paygroups(project_id)

# @app.post('/groups')
# async def add_a_new_payment_group(details: PaygroupBase):
#     return db.add_payment_group(details.dict())

# @app.put('/groups/{group_id}')
# async def update_payment_group(group_id: int, details: PaygroupBase):
#     return db.update_group(group_id, details.dict())

# @app.delete('/groups/{group_id}')
# async def delete_payment_group(group_id: int):
#     return db.delete_group(group_id)

# @app.get('/groups/{group_id}/payments')
# async def individual_group_payments(group_id: int):
#     return db.get_payments(group_id)

# @app.post('/payments')
# async def add_new_payment(details: Payment):
#     return db.add_payment(details.dict())

# @app.put('/payments/{pay_id}')
# async def update_payment(pay_id: int, details: Payment):
#     return db.update_payment(pay_id, details.dict())

# @app.delete('/payments/{pay_id}')
# async def delete_payment(pay_id: int):
#     return db.delete_payment(pay_id)

app.mount("/css", StaticFiles(directory="dist/css"), name="static")
app.mount("/js", StaticFiles(directory="dist/js"), name="static")
app.mount("/img", StaticFiles(directory="dist/img"), name="static")
app.mount("/fonts", StaticFiles(directory="dist/fonts"), name="static")

@app.get('/manifest.json')
async def srvwork():
    with open('dist/manifest.json', 'r') as f:
        return json.loads(f.read())

@app.get('/')
@app.get('/{id}')
async def root():
    with open('dist/index.html', 'r') as f:
        return HTMLResponse(f.read())
