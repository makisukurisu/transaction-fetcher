from enums.account import AccountProvider
from providers.account.base import BaseAccountProvider
from providers.account.monobank import MonoBankProvider


def get_provider_class(
    provider_name: AccountProvider,
) -> type[BaseAccountProvider]:
    return {
        AccountProvider.MONOBANK: MonoBankProvider,
    }[provider_name]
