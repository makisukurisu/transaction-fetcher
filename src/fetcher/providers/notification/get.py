from enums.chat import ChatProvider
from providers.notification.base import BaseChatProvider
from providers.notification.telegram import TelegramChatProvider


def get_chat_provider_class(provider: ChatProvider) -> type[BaseChatProvider]:
    return {
        ChatProvider.TELEGRAM: TelegramChatProvider,
    }[provider]
