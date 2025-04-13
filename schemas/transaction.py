import datetime
from decimal import Decimal

from enums.transaction import TransactionType
from schemas.base import BaseSchema
from schemas.currency import CurrencySchema


class TransactionSchema(BaseSchema):
    unique_id: str | None = None

    type: TransactionType

    amount: Decimal
    currency: CurrencySchema | None = None
    description: str | None = None
    at_time: datetime.datetime | None = None
