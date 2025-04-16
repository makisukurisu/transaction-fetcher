import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums.transaction import TransactionType
from models.base import BaseModel
from repository import settings

if TYPE_CHECKING:
    from models.account import AccountModel


class TransactionModel(BaseModel):
    __tablename__ = "transactions"

    account_id: Mapped[int] = mapped_column(
        "account_id",
        ForeignKey("accounts.id"),
        nullable=False,
    )

    account: Mapped["AccountModel"] = relationship(
        back_populates="transactions",
    )

    unique_id: Mapped[str] = mapped_column(
        "unique_id",
        nullable=False,
    )

    type: Mapped[TransactionType] = mapped_column(
        "type",
        Enum(TransactionType),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        "amount",
        nullable=False,
    )
    # ISO 4217 (NUM) currency code
    currency: Mapped[int] = mapped_column(
        "currency",
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        "description",
        nullable=False,
        default="No description",
    )
    at_time: Mapped[datetime.datetime] = mapped_column(
        "at_time",
        nullable=False,
        default=lambda: datetime.datetime.now(
            tz=settings.settings.default_timezone,
        ),
    )

    @property
    def amount_as_string(self) -> str:
        transaction_amount = round(self.amount, 2)
        if transaction_amount > 0:
            transaction_amount = f"+{transaction_amount}"
        else:
            transaction_amount = str(transaction_amount)

        return transaction_amount
