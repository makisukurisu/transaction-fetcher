from enum import StrEnum
from typing import TYPE_CHECKING

from enums.transaction import TransactionType

if TYPE_CHECKING:
    from models.transaction import TransactionModel


class NotificationType(StrEnum):
    BALANCE = "BALANCE"
    ACTIVE = "ACTIVE"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"

    @classmethod
    def from_transaction(
        cls,
        transaction: "TransactionModel",
    ) -> "NotificationType":
        if transaction.type == TransactionType.DEPOSIT:
            return cls.DEPOSIT
        if transaction.type == TransactionType.WITHDRAWAL:
            return cls.WITHDRAWAL

        raise NotImplementedError
