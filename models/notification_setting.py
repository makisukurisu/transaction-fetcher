from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums.notification_setting import NotificationType
from models.base import BaseModel
from services.currency import get_currency_by_numerical_code

if TYPE_CHECKING:
    from models.account_chat_model import AccountChatModel
    from models.transaction import TransactionModel


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

<b>{transaction.created_at.strftime("%Y-%m-%d | %H:%M")}</b>
"""
        return message.strip()
