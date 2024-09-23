from sqlite3.dbapi2 import Date
from typing import Optional
from pydantic import BaseModel, model_validator, ValidationInfo
from typing_extensions import Self
import json


class PaymentInput(BaseModel):
    name: str
    date: Date
    asset: Optional[int] = 0  # in cents
    liability: Optional[int] = 0  # in cents

    @model_validator(mode="after")
    def must_have_either_asset_or_liability(
        self,
    ) -> Self:
        if self.asset == 0 and self.liability == 0:
            raise ValueError("Must specify either asset or liability")
        return self


class Payment(PaymentInput):
    id: int


class PaygroupInput(BaseModel):
    name: str


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
        if isinstance(obj, Date):
            return obj.isoformat()
        return super().default(obj)


class NewItemResponse(BaseModel):
    id: int
