from datetime import date
from typing import Optional
from pydantic import BaseModel, model_validator, Field
from typing_extensions import Self
import json


class PaymentInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    date: date
    asset: Optional[int] = 0  # in microcents
    liability: Optional[int] = 0  # in microcents
    currency: str = Field(min_length=1, max_length=3)


class Payment(PaymentInput):
    id: int
    attachment: str = ""


class PaygroupInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class Paygroup(PaygroupInput):
    id: int
    payments: Optional[list[Payment]] = []


class ProjectInput(BaseModel):
    name: str


class ProjectResponse(ProjectInput):
    id: int


class Project(ProjectResponse):
    is_deleted: bool = False


class ProjectWithPayments(ProjectResponse):
    paygroups: list[Paygroup]


class ProjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(type(obj), BaseModel):
            return obj.model_dump()
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


class NewItemResponse(BaseModel):
    id: int
