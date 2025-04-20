from typing import TYPE_CHECKING

from sqlalchemy.orm import Session, joinedload

from logger import main_logger
from models.transaction import TransactionModel
from providers.account.get import get_provider_class
from schemas.transaction import DBTransactionSchema
from services.account import get_account_service

if TYPE_CHECKING:
    import sqlalchemy

    from models.account import AccountModel
    from schemas.account import BalanceSchema
    from schemas.transaction import TransactionSchema


class TransactionRepository:
    def __init__(self, db: "sqlalchemy.engine.Engine") -> None:
        self.db = db

    def get_transaction_by_id(
        self,
        transaction_id: int,
        db_session: "Session | None" = None,
    ) -> "TransactionModel | None":
        session = db_session if db_session else Session(self.db)

        transaction = (
            session.query(TransactionModel)
            .options(
                joinedload(
                    TransactionModel.account,
                )
            )
            .get(transaction_id)
        )

        if not db_session:
            session.close()

        return transaction

    def transaction_exists(
        self,
        account: "AccountModel",
        transaction: "TransactionSchema",
        db_session: "Session | None" = None,
    ) -> bool:
        session = db_session if db_session else Session(self.db)

        exists = (
            session.query(TransactionModel)
            .filter(
                TransactionModel.account_id == account.id,
                TransactionModel.unique_id == transaction.unique_id,
            )
            .count()
            > 0
        )

        if not db_session:
            session.close()

        return exists

    def fetch_transaction_by_account(
        self,
        account: "AccountModel",
    ) -> list["TransactionSchema"]:
        provider_class = get_provider_class(account.provider)

        integration = provider_class(account)

        try:
            return integration.get_transactions()
        except Exception as e:  # noqa: BLE001
            from services.chat import get_chat_service

            main_logger.exception(
                {
                    "msg": "Error fetching transactions",
                    "account": account,
                    "provider": account.provider,
                    "error": e,
                }
            )

            get_chat_service().notify_management(
                text=f"Could not fetch transactions for: {account.id=}",
                exception=e,
            )

            return []

    def fetch_transactions(self) -> list["DBTransactionSchema"]:
        new_transactions = []

        account_service = get_account_service()

        accounts = account_service.get_accounts(fetch_all=True)

        for account in accounts:
            account_transactions = self.fetch_transaction_by_account(account)

            with Session(self.db) as session:
                for transaction in account_transactions:
                    if self.transaction_exists(
                        account,
                        transaction,
                        db_session=session,
                    ):
                        continue

                    optional = {}
                    if transaction.description:
                        optional["description"] = transaction.description
                    if transaction.at_time:
                        optional["at_time"] = transaction.at_time

                    # Default to UAH
                    currency_code = 980
                    if transaction.currency:
                        currency_code = transaction.currency.numerical_code

                    transaction_model = TransactionModel(
                        account_id=account.id,
                        unique_id=transaction.unique_id,
                        currency=currency_code,
                        type=transaction.type,
                        amount=transaction.amount,
                        **optional,
                    )
                    session.add(transaction_model)

                    session.commit()

                    session.refresh(transaction_model)

                    new_transactions.append(DBTransactionSchema.model_validate(transaction_model))

        main_logger.info(
            {
                "msg": "Fetched transactions",
                "len(new_transactions)": len(new_transactions),
                "new_transactions": new_transactions,
            }
        )

        return new_transactions

    def get_balance(
        self,
        account_id: int,
    ) -> "BalanceSchema | None":
        account_service = get_account_service()
        account = account_service.get_account_by_id(account_id=account_id)

        if not account:
            return None

        provider_class = get_provider_class(account.provider)
        integration = provider_class(account)

        balance = integration.get_balance()

        if not balance:
            return None

        return balance
