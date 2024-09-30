from datetime import date
from typing import Optional
from pydantic import BaseModel, model_validator, Field
from typing_extensions import Self
import json


class PaymentInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    date: date
    asset: Optional[int] = 0  # in cents
    liability: Optional[int] = 0  # in cents
    currency: str = Field(min_length=1, max_length=3)

    @model_validator(mode="after")
    def must_have_either_asset_or_liability(
        self,
    ) -> Self:
        if self.asset == 0 and self.liability == 0:
            raise ValueError("Must specify either asset or liability")
        return self


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
