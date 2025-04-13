from typing import TYPE_CHECKING

import db
from models.chat import ChatModel
from providers.notification.get import get_chat_provider_class
from repository import settings
from repository.chat import ChatRepository
from schemas.chat import ListChatSchema

if TYPE_CHECKING:
    from models.account_chat_model import AccountChatModel
    from schemas.chat import CreateChatSchema


class ChatService:
    def __init__(self, chat_repository: "ChatRepository") -> None:
        self.chat_repository = chat_repository

    def add_chat(
        self,
        data: "CreateChatSchema",
    ) -> ChatModel:
        """Adds a chat to the database."""
        return self.chat_repository.create_chat(data)

    def get_chat_by_id(
        self,
        chat_id: int,
    ) -> ChatModel | None:
        """Returns a chat by id."""
        return self.chat_repository.get_chat_by_id(chat_id)

    def get_chats(
        self,
        filters: ListChatSchema | None = None,
    ) -> list["ChatModel"]:
        if not filters:
            filters = ListChatSchema()

        return self.chat_repository.get_chats(
            page=filters.page,
            limit=filters.page_size,
            provider=filters.provider,
        )

    def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
    ) -> tuple[str, str]:
        """Returns the provider chat id and message id."""
        chat = self.chat_repository.get_chat_by_id(
            chat_id=chat_id,
        )

        if not chat:
            raise ValueError(f"Chat with {chat_id=} not found")

        provider_class = get_chat_provider_class(chat.provider)
        integration = provider_class(
            chat=chat,
        )

        message_id = integration.send_message(
            text=text,
            parse_mode=parse_mode,
        )

        return chat.external_id, message_id

    def add_account_to_chat(
        self,
        chat_id: int,
        account_id: int,
    ) -> None:
        """Adds an account to the chat."""
        chat = self.chat_repository.get_chat_by_id(chat_id)

        if not chat:
            raise ValueError(f"Chat with {chat_id=} not found")

        self.chat_repository.add_account_to_chat(
            chat_id=chat.id,
            account_id=account_id,
        )

    def get_accounts_by_chat(self, chat: ChatModel) -> list["AccountChatModel"]:
        """Returns a list of account ids by chat id."""
        return self.chat_repository.get_accounts_by_chat_id(chat.id)

    def get_account_chat_by_id(
        self,
        account_chat_id: int,
    ) -> "AccountChatModel":
        """Returns a chat by id."""
        return self.chat_repository.get_account_chat_by_id(
            account_chat_id=account_chat_id,
        )

    def delete_account_chat(
        self,
        account_chat_id: int,
    ) -> None:
        """Deletes an account chat."""
        self.chat_repository.delete_account_chat(
            account_chat_id=account_chat_id,
        )


def get_chat_service() -> ChatService:
    database = db.get_engine(settings.settings.DB_URL)
    chat_repository = ChatRepository(database)
    return ChatService(chat_repository=chat_repository)
