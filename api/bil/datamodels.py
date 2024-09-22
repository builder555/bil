from sqlite3.dbapi2 import Date
from typing import Optional
from pydantic import BaseModel, model_validator, ValidationInfo
from typing_extensions import Self
import json


class PaymentInput(BaseModel):
    name: str
    date: Date
    asset: Optional[int] = 0
    liability: Optional[int] = 0

    @model_validator(mode="after")
    def must_have_either_asset_or_liability(
        self,
    ) -> Self:
        if self.asset == 0 and self.liability == 0:
            raise ValueError("Must specify either asset or liability")
        return self


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
    paygroups: list[Paygroup]


class ProjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(type(obj), BaseModel):
            return obj.model_dump()
        return super().default(obj)
