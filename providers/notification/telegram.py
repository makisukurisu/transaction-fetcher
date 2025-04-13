from typing import TYPE_CHECKING

import telebot

from providers.notification.base import BaseChatProvider
from repository import settings

if TYPE_CHECKING:
    from models.chat import ChatModel


class TelegramChatProvider(BaseChatProvider):
    def __init__(self, chat: "ChatModel") -> None:
        super().__init__(chat)

        self.bot_token = settings.settings.TELEGRAM_BOT_TOKEN

    def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
    ) -> str:
        bot = telebot.TeleBot(
            self.bot_token,
            parse_mode=parse_mode,
        )

        message = bot.send_message(
            chat_id=self._chat.external_id,
            text=text,
        )

        return str(message.id)
