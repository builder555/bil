from sqlite3.dbapi2 import Date
from typing import Optional
from pydantic import BaseModel
import json


class Project(BaseModel):
    id: int
    name: str
    is_deleted: bool = False


class ProjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Project):
            return obj.model_dump()
        return super().default(obj)


class PaygroupBase(BaseModel):
    name: str
    project: int


class Paygroup(PaygroupBase):
    id: Optional[int]
    total: float
    owed: float


class Payment(BaseModel):
    name: str
    when: Date
    paygroup: int
    amount: float
    owed: float
