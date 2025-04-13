import pydantic

from enums.notification_setting import NotificationType
from schemas.base import BaseSchema


class CreateNotificationSchema(BaseSchema):
    schedule: str | None = pydantic.Field(
        default=None,
        description="Schedule for the notification. Can be a cron expression or null",
    )
    notification_type: NotificationType
