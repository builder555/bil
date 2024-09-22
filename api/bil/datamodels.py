from sqlite3.dbapi2 import Date
from typing import Optional
from pydantic import BaseModel
import json


class PaygroupBase(BaseModel):
    name: str


class Paygroup(PaygroupBase):
    id: int


class ProjectResponse(BaseModel):
    id: int
    name: str


class Project(ProjectResponse):
    is_deleted: bool = False


class ProjectWithPayments(ProjectResponse):
    paygroups: dict[int, Paygroup]


class ProjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(type(obj), BaseModel):
            return obj.model_dump()
        return super().default(obj)


class Payment(BaseModel):
    name: str
    when: Date
    paygroup: int
    amount: float
    owed: float
