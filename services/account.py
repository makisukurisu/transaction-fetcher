import db
from logger import db_logger
from models.account import AccountModel
from repository import settings
from repository.account import AccountRepository
from schemas.account import CreateAccountSchema


class AccountService:
    def __init__(
        self,
        account_repository: AccountRepository,
    ) -> None:
        self.account_repository = account_repository

    def get_account_by_id(
        self,
        account_id: str,
    ) -> AccountModel | None:
        return self.account_repository.get_by_id(
            account_id=account_id,
        )

    def get_accounts(
        self,
        page: int = 1,
        page_size: int = 25,
        fetch_all: bool = False,
    ) -> list[AccountModel]:
        accounts, total = self.account_repository.get_all(
            page=page,
            page_size=page_size,
            fetch_all=fetch_all,
        )

        db_logger.info(
            {
                "msg": f"Showing {len(accounts)}/{total} accounts",
            },
        )
        db_logger.debug(
            {
                "msg": "Received the following accounts",
                "accounts": accounts,
            },
        )

        return accounts

    def create_account(
        self,
        account_data: CreateAccountSchema,
    ) -> AccountModel:
        return self.account_repository.create(
            account_data=account_data,
        )

    def edit_account(
        self,
        account_id: int,
        account_data: CreateAccountSchema,
    ) -> AccountModel:
        return self.account_repository.update(
            account_id=account_id,
            account_data=account_data,
        )

    def delete_account(
        self,
        account_id: int,
    ) -> bool:
        return self.account_repository.delete(
            account_id=account_id,
        )


def get_account_service() -> AccountService:
    """
    Get the account service instance.
    """
    database = db.get_engine(settings.settings.DB_URL)
    account_repository = AccountRepository(database)
    return AccountService(account_repository=account_repository)
