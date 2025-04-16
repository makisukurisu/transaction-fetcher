import datetime
import time
from typing import TYPE_CHECKING

from cron_converter import Cron

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
            try:
                main_logger.info("Starting notification service")
                settings = self.get_notification_settings_for_processing()

                main_logger.info(
                    {
                        "msg": "Found notification settings for processing",
                        "count": len(settings),
                    }
                )

                for notification in settings:
                    self.process_notification(notification)
                time.sleep(60)
            except Exception as e:  # noqa: BLE001
                main_logger.critical(
                    f"Error in notification service: {e}",
                    stack_info=True,
                    exc_info=True,
                )
                get_chat_service().notify_management(
                    text="Error in notification service",
                    exception=e,
                )
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

    def get_notification_settings_for_processing(self) -> list["NotificationSettingsModel"]:
        current_time = datetime.datetime.now(tz=settings.settings.default_timezone)
        need_processing: list[NotificationSettingsModel] = []

        notifications = self.notification_repository.get_notification_settings()

        for notification in notifications:
            cron = Cron()
            cron.from_string(notification.schedule)

            schedule = cron.schedule(
                start_date=notification.last_sent_at_dt or datetime.datetime.min,  # noqa: DTZ901
            )
            next_call = schedule.next()
            next_call = next_call.replace(tzinfo=settings.settings.default_timezone)

            if current_time >= next_call:
                need_processing.append(notification)

        return need_processing

    def _get_message_for_notification(
        self,
        notification_setting: "NotificationSettingsModel",
    ) -> str:
        if notification_setting.notification_type == NotificationType.BALANCE:
            from services.transaction import get_transaction_service

            transaction_service = get_transaction_service()
            balance = transaction_service.get_balance(
                account_id=notification_setting.account_chat.account_id,
            )

            if not balance:
                return "No balance data available"

            return notification_setting.balance_message(
                balance_data=balance,
            )

        if notification_setting.notification_type == NotificationType.ACTIVE:
            return notification_setting.active_message()

        raise NotImplementedError

    def process_notification(self, setting: "NotificationSettingsModel") -> None:
        main_logger.info(f"Processing notification: {setting}")

        chat_service = get_chat_service()

        chat_service.send_message(
            chat_id=setting.account_chat.chat_id,
            text=self._get_message_for_notification(
                notification_setting=setting,
            ),
        )

        self.notification_repository.mark_notification_setting_as_ran(setting=setting)

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
