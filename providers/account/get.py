from enums.account import AccountProvider
from providers.account.abank import ABankProvider
from providers.account.base import BaseAccountProvider
from providers.account.monobank import MonoBankProvider
from providers.account.novapay import NovaPayProvider
from providers.account.privatbank_fop import PrivatBankFOPProvider


def get_provider_class(
    provider_name: AccountProvider,
) -> type[BaseAccountProvider]:
    return {
        AccountProvider.MONOBANK: MonoBankProvider,
        AccountProvider.ABANK: ABankProvider,
        AccountProvider.PRIVATBANK_FOP: PrivatBankFOPProvider,
        AccountProvider.NOVAPAY: NovaPayProvider,
    }[provider_name]
