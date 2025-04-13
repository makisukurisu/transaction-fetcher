import time
from typing import TYPE_CHECKING

import db
from enums.notification_setting import NotificationType
from logger import main_logger
from repository import settings
from repository.notification import NotificationRepository
from schemas.notification import CreateNotificationSchema
from services.chat import get_chat_service

if TYPE_CHECKING:
    from models.notification import NotificationModel
    from models.notification_setting import NotificationSettingsModel
    from models.transaction import TransactionModel


class NotificationService:
    def __init__(
        self,
        notification_repository: NotificationRepository,
    ) -> None:
        self.notification_repository = notification_repository

    def run(self) -> None:
        while True:
            notifications = self.fetch_notifications()
            for notification in notifications:
                self.process_notification(notification)
            time.sleep(60)

    def create_notification(
        self,
        account_chat_id: int,
        notification_data: CreateNotificationSchema,
    ) -> None:
        notification_setting = self.notification_repository.create_notification(
            account_chat_id=account_chat_id,
            notification_data=notification_data,
        )

        main_logger.info(f"Notification created: {notification_setting}")

    def fetch_notifications(self) -> list["NotificationModel"]:
        return self.notification_repository.fetch_notifications()

    def process_notification(self, notification: "NotificationModel") -> None:
        main_logger.info(f"Processing notification: {notification}")

    def notification_exists(self, transaction: "TransactionModel") -> bool:
        return self.notification_repository.notification_exists(
            transaction_id=transaction.id,
        )

    def get_notification_settings_by_account_chat_id(
        self,
        account_chat_id: int,
    ) -> list["NotificationSettingsModel"]:
        return self.notification_repository.get_notifications_by_account_chat_id(
            account_chat_id=account_chat_id,
        )

    def delete_notification_setting(self, notification_setting_id: int) -> None:
        self.notification_repository.delete_notification_setting(
            notification_setting_id=notification_setting_id,
        )

    def make_transaction_notifications(
        self,
        transaction: "TransactionModel",
    ) -> None:
        notification_type = NotificationType.from_transaction(transaction)

        notification_settings = self.notification_repository.get_settings(
            notification_type=notification_type,
        )

        chat_service = get_chat_service()

        for notification_setting in notification_settings:
            external_chat_id, external_message_id = chat_service.send_message(
                chat_id=notification_setting.account_chat.chat_id,
                text=notification_setting.transaction_message(transaction),
            )

            self.notification_repository.create_transaction_notification(
                transaction=transaction,
                notification_setting=notification_setting,
                external_chat_id=external_chat_id,
                external_message_id=external_message_id,
            )

    def mark_as_replied(
        self,
        external_chat_id: str,
        external_message_id: str,
    ) -> None:
        self.notification_repository.mark_as_replied(
            external_chat_id=external_chat_id,
            external_message_id=external_message_id,
        )

    def unanswered_notifications(
        self,
        external_chat_id: str,
    ) -> list["NotificationModel"]:
        return self.notification_repository.unanswered_notifications(
            external_chat_id=external_chat_id,
        )


def get_notification_service() -> NotificationService:
    database = db.get_engine(settings.settings.DB_URL)
    notification_repository = NotificationRepository(database)
    return NotificationService(
        notification_repository=notification_repository,
    )
