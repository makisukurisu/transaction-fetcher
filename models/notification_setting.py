import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums.notification_setting import NotificationType
from models.base import BaseModel
from repository import settings
from services.currency import get_currency_by_numerical_code

if TYPE_CHECKING:
    from models.account_chat_model import AccountChatModel
    from models.transaction import TransactionModel
    from schemas.account import BalanceSchema


class NotificationSettingsModel(BaseModel):
    __tablename__ = "notification_settings"

    account_chat_id: Mapped[int] = mapped_column(
        ForeignKey("account_chats.id"),
        nullable=False,
    )

    account_chat: Mapped["AccountChatModel"] = relationship(
        back_populates="notification_settings",
    )

    # Crontab schedule for sending notifications
    schedule: Mapped[str | None] = mapped_column(
        nullable=True,
        default=None,
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        "notification_type",
        Enum(NotificationType),
        nullable=False,
    )

    last_sent_at: Mapped[str | None] = mapped_column(
        nullable=True,
        default=None,
    )

    def transaction_message(
        self,
        transaction: "TransactionModel",
    ) -> str:
        currency = get_currency_by_numerical_code(
            numerical_code=transaction.currency,
        )

        message = f"""
{self.account_chat.account.name}: <b>{transaction.amount_as_string} {currency.alpha3}</b>

Комментарий: {transaction.description}

<b>{transaction.at_time.strftime("%Y-%m-%d | %H:%M")}</b>
"""
        return message.strip()

    def balance_message(
        self,
        balance_data: "BalanceSchema",
    ) -> str:
        at_time = balance_data.at_time or datetime.datetime.now(
            tz=settings.settings.default_timezone,
        )
        currency = get_currency_by_numerical_code(
            numerical_code=balance_data.currency,
        )

        deposit_withdrawal_stats = ""

        if balance_data.deposited and balance_data.withdrawn:
            deposit_withdrawal_stats = f"""
Приход: <b>{balance_data.deposited} {currency.alpha3}</b>
Расход: <b>{balance_data.withdrawn} {currency.alpha3}</b>
"""

        message = f"""
{self.account_chat.account.name}

Начало дня: <b>{balance_data.start_balance} {currency.alpha3}</b>
Конец дня: <b>{balance_data.end_balance} {currency.alpha3}</b>
{deposit_withdrawal_stats}
Итого: <b>{balance_data.end_balance - balance_data.start_balance} {currency.alpha3}</b>
<b>{at_time.strftime("%Y-%m-%d | %H:%M")}</b>
"""

        return message.strip()

    def active_message(
        self,
    ) -> str:
        return f"""
{self.account_chat.account.name}: <b>Активен</b>
""".strip()

    @property
    def last_sent_at_dt(self) -> datetime.datetime | None:
        if not self.last_sent_at:
            return None

        return datetime.datetime.fromisoformat(self.last_sent_at)

    def set_last_sent_at(self, dt: datetime.datetime) -> None:
        self.last_sent_at = dt.isoformat()
