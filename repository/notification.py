import datetime
from typing import TYPE_CHECKING

from sqlalchemy import literal
from sqlalchemy.orm import Session, joinedload

from enums.notification_setting import NotificationType
from models.account_chat_model import AccountChatModel
from models.notification import NotificationModel
from models.notification_setting import NotificationSettingsModel
from schemas.notification import CreateNotificationSchema

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

    from models.transaction import TransactionModel


class NotificationRepository:
    def __init__(self, db: "Engine") -> None:
        self.db = db

    def get_notification_settings(self) -> list["NotificationSettingsModel"]:
        with Session(self.db) as session:
            q = (
                session.query(NotificationSettingsModel)
                .options(
                    joinedload(
                        NotificationSettingsModel.account_chat,
                    ).joinedload(
                        AccountChatModel.account,
                    )
                )
                .filter(
                    NotificationSettingsModel.schedule.is_not(None),
                    NotificationSettingsModel.notification_type.not_in(
                        [
                            NotificationType.DEPOSIT,
                            NotificationType.WITHDRAWAL,
                        ]
                    ),
                )
            )

            return q.all()

    def mark_notification_setting_as_ran(
        self,
        setting: "NotificationSettingsModel",
    ) -> None:
        with Session(self.db) as session:
            setting.last_sent_at = datetime.datetime.now(tz=datetime.UTC).isoformat()
            session.add(setting)
            session.commit()

    def notification_exists(self, transaction_id: str) -> bool:
        with Session(self.db) as session:
            q = session.query(NotificationModel).filter(
                NotificationModel.transaction_id == transaction_id,
            )
            return (
                session.query(literal(True))  # noqa: FBT003
                .filter(
                    q.exists(),
                )
                .scalar()
            )

    def get_settings(
        self,
        notification_type: NotificationType,
        account_id: int | None = None,
        chat_id: int | None = None,
    ) -> list["NotificationSettingsModel"]:
        with Session(self.db) as session:
            q = (
                session.query(NotificationSettingsModel)
                .options(
                    joinedload(
                        NotificationSettingsModel.account_chat,
                    ).joinedload(
                        AccountChatModel.account,
                    )
                )
                .filter(
                    NotificationSettingsModel.notification_type == notification_type,
                )
            )

            if account_id:
                q = q.join(
                    AccountChatModel,
                    AccountChatModel.id == NotificationSettingsModel.account_chat_id,
                ).filter(
                    AccountChatModel.account_id == account_id,
                )
            if chat_id:
                q = q.join(
                    AccountChatModel,
                    AccountChatModel.id == NotificationSettingsModel.account_chat_id,
                ).filter(
                    AccountChatModel.chat_id == chat_id,
                )

            return q.all()

    def create_transaction_notification(
        self,
        transaction: "TransactionModel",
        notification_setting: "NotificationSettingsModel",
        external_chat_id: str,
        external_message_id: str,
    ) -> NotificationModel:
        with Session(self.db) as session:
            notification = NotificationModel(
                transaction_id=transaction.id,
                account_chat_id=notification_setting.account_chat_id,
                external_chat_id=external_chat_id,
                external_message_id=external_message_id,
                is_replied=False,
            )
            session.add(notification)
            session.commit()

            session.refresh(notification)

            return notification

    def mark_as_replied(
        self,
        external_chat_id: str,
        external_message_id: str,
    ) -> None:
        with Session(self.db) as session:
            q = session.query(NotificationModel).filter(
                NotificationModel.external_chat_id == external_chat_id,
                NotificationModel.external_message_id == external_message_id,
            )
            q.update({"is_replied": True})
            session.commit()

    def unanswered_notifications(
        self,
        external_chat_id: str | None = None,
    ) -> list["NotificationModel"]:
        with Session(self.db) as session:
            q = session.query(NotificationModel).filter(
                NotificationModel.is_replied.is_(False),
            )

            if external_chat_id:
                q = q.filter(
                    NotificationModel.external_chat_id == external_chat_id,
                )

            return q.all()

    def create_notification(
        self,
        account_chat_id: int,
        notification_data: CreateNotificationSchema,
    ) -> NotificationModel:
        with Session(self.db) as session:
            notification_setting = NotificationSettingsModel(
                account_chat_id=account_chat_id,
                notification_type=notification_data.notification_type,
                schedule=notification_data.schedule,
            )
            session.add(notification_setting)
            session.commit()

            session.refresh(notification_setting)

            return notification_setting

    def get_notifications_by_account_chat_id(
        self,
        account_chat_id: int,
    ) -> list["NotificationSettingsModel"]:
        with Session(self.db) as session:
            q = session.query(NotificationSettingsModel).filter(
                NotificationSettingsModel.account_chat_id == account_chat_id,
            )
            return q.all()

    def delete_notification_setting(
        self,
        notification_setting_id: int,
    ) -> None:
        with Session(self.db) as session:
            q = session.query(NotificationSettingsModel).filter(
                NotificationSettingsModel.id == notification_setting_id,
            )
            q.delete()
            session.commit()
