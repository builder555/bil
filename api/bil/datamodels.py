from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
import json


class TagModel(BaseModel):
    name: str
    color: str


class PaymentInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    date: date
    asset: Optional[int] = Field(default=0, description="Amount in microcents")
    liability: Optional[int] = Field(default=0, description="Amount in microcents")
    currency: str = Field(min_length=1, max_length=3, json_schema_extra={"example": "USD"})
    tags: Optional[list[TagModel]] = Field(default_factory=list)


class Payment(PaymentInput):
    id: int
    attachment: str = ""


class PaygroupInput(BaseModel):
    name: str = Field(min_length=1, max_length=255, json_schema_extra={"example": "Renovation Expenses"})


class Paygroup(PaygroupInput):
    id: int
    payments: list[Payment] = []


class ProjectInput(BaseModel):
    name: str = Field(min_length=1, max_length=255, json_schema_extra={"example": "Household Budget"})


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
