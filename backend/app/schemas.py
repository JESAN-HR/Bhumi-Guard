from typing import Literal
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .rules import number


class Fields(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seller_id: str | None = Field(default=None, max_length=80)
    holding_id: str | None = Field(default=None, max_length=80)
    mouza_id: str = Field(max_length=80)
    survey: str | None = Field(default=None, max_length=80)
    dag: str | None = Field(default=None, max_length=80)
    area: str | None = Field(default=None, max_length=40)
    date: str | None = None
    unit: Literal["decimal"] = "decimal"

    @field_validator("area")
    @classmethod
    def area_valid(cls, value):
        if value not in (None, "") and number(value) <= 0:
            raise ValueError("invalid_number")
        return value

    @field_validator("date")
    @classmethod
    def date_valid(cls, value):
        if value:
            date.fromisoformat(value)
        return value


class Edit(BaseModel):
    fields: Fields
    confirmed: bool
    version: int


class NewCase(BaseModel):
    scenario_id: str | None = None
    mouza_id: str
    fictional: bool


class Login(BaseModel):
    username: str
    password: str


class ReviewDecision(BaseModel):
    analysis_id: str
    action: Literal["reviewed", "more_information"]
    notes: str = Field(min_length=5, max_length=5000)
