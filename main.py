"""
Executable for the bot.

Run it with:
```bash
python main.py
```
or
```bash
uv run main.py
```
"""

import threading

import typer

import db
from repository import settings
from repository.account import AccountRepository
from repository.notification import NotificationRepository
from repository.transaction import TransactionRepository
from services.account import AccountService
from services.notification import NotificationService
from services.transaction import TransactionService

app = typer.Typer()


@app.command(name="bot")
def run() -> None:
    """
    Run the bot.

    This command starts the bot and runs the transaction and notification services in separate threads.
    """  # noqa: E501
    from bot import bot

    database = db.get_engine(settings.settings.DB_URL)

    transaction_repository = TransactionRepository(database)
    notification_repository = NotificationRepository(database)
    account_repository = AccountRepository(database)

    transaction_service = TransactionService(
        transaction_repository=transaction_repository,
    )
    threading.Thread(
        target=transaction_service.run,
        daemon=True,
    ).start()

    notification_service = NotificationService(
        notification_repository=notification_repository,
    )
    threading.Thread(
        target=notification_service.run,
        daemon=True,
    ).start()

    account_service = AccountService(
        account_repository=account_repository,
    )
    threading.Thread(
        target=account_service.run,
        daemon=True,
    ).start()

    bot.infinity_polling()


@app.command(name="migrate")
def migrate() -> None:
    """
    Run the migrations.
    """
    from models.base import BaseModel

    BaseModel.metadata.create_all(
        db.get_engine(settings.settings.DB_URL),
    )


if __name__ == "__main__":
    app()
