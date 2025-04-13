import time
from typing import TYPE_CHECKING

import db
from logger import main_logger
from repository import settings
from repository.transaction import TransactionRepository
from services.notification import get_notification_service

if TYPE_CHECKING:
    from models.transaction import TransactionModel


class TransactionService:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
    ) -> None:
        self.transaction_repository = transaction_repository

    def run(self) -> None:
        while True:
            main_logger.info("Fetching transactions...")
            transactions = self.fetch_transactions()
            for transaction in transactions:
                self.process_transaction(transaction)
            time.sleep(60)

    def get_transaction_by_id(self, transaction_id: int) -> "TransactionModel | None":
        return self.transaction_repository.get_transaction_by_id(
            transaction_id=transaction_id,
        )

    def fetch_transactions(self) -> list:
        return self.transaction_repository.fetch_transactions()

    def make_notification(self, transaction: "TransactionModel") -> None:
        notification_service = get_notification_service()

        if notification_service.notification_exists(transaction):
            return

        notification_service.make_transaction_notifications(transaction)

    def process_transaction(self, transaction: "TransactionModel") -> None:
        self.make_notification(transaction)


def get_transaction_service() -> TransactionService:
    database = db.get_engine(settings.settings.DB_URL)
    transaction_repository = TransactionRepository(db=database)
    return TransactionService(transaction_repository=transaction_repository)
