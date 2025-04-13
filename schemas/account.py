import json
from datetime import timedelta

import pydantic

from enums.account import AccountProvider
from schemas.base import BaseSchema


class CreateAccountSchema(BaseSchema):
    name: str
    provider: AccountProvider

    configuration_parameters: dict

    interval: timedelta = timedelta(days=1)


class AccountSchema(BaseSchema):
    id: int
    name: str
    provider: AccountProvider

    configuration_parameters: dict

    interval: timedelta = timedelta(days=1)

    @pydantic.field_validator("configuration_parameters", mode="before")
    @classmethod
    def validate_configuration_parameters(cls, value: dict) -> dict:
        if isinstance(value, str):
            value = json.loads(value)
        return value
