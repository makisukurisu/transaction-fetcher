import datetime
from decimal import Decimal

import pydantic
import pydantic.alias_generators

from enums.transaction import TransactionType
from providers.account.base import BaseAccountProvider, BaseAccountProviderConfiguration
from schemas.base import BaseSchema
from schemas.transaction import TransactionSchema
from services.currency import get_currency_by_numerical_code


class MonoBankProviderConfiguration(BaseAccountProviderConfiguration):
    account_id: str
    api_token: str

    use_to_timestamp: bool = False


class MonoBankTransaction(BaseSchema):
    id: str
    time: int
    description: str
    mcc: int
    original_mcc: int | None = None
    hold: bool
    amount: int
    operation_amount: int | None = None
    currency_code: int
    commission_rate: int | None = None
    cashback_amount: int | None = None
    balance: int
    comment: str | None = None
    receipt_id: str | None = None
    invoice_id: str | None = None
    counter_edrpou: str | None = None
    counter_iban: str | None = None
    counter_name: str | None = None

    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.AliasGenerator(
            validation_alias=pydantic.alias_generators.to_camel,
        )
    )

    def to_transaction_schema(self) -> TransactionSchema:
        return TransactionSchema(
            unique_id=self.id,
            type=TransactionType.DEPOSIT if self.amount > 0 else TransactionType.WITHDRAWAL,
            amount=Decimal(self.amount) / 100,
            currency=get_currency_by_numerical_code(
                self.currency_code,
            ),
            description=self.comment or self.description,
            at_time=datetime.datetime.fromtimestamp(
                self.time,
                tz=datetime.UTC,
            ),
        )


class MonoBankProvider(BaseAccountProvider):
    @property
    def base_url(self) -> str:
        return "https://api.monobank.ua"

    @property
    def account_id(self) -> str:
        return self.configuration.account_id

    @property
    def auth_headers(self) -> dict[str, str]:
        return {
            "X-Token": self.configuration.api_token,
        }

    def get_configuration_type(self) -> MonoBankProviderConfiguration:
        return MonoBankProviderConfiguration

    @property
    def configuration(self) -> MonoBankProviderConfiguration:
        return self._configuration

    def get_transactions(self) -> list["TransactionSchema"]:
        to_time = datetime.datetime.now(tz=datetime.UTC)
        from_time = to_time - datetime.timedelta(seconds=self._account.interval_seconds)

        path_arguments = [
            self.account_id,
            int(from_time.timestamp()),
        ]

        if self.configuration.use_to_timestamp:
            path_arguments.append(
                int(to_time.timestamp()),
            )

        path = "/personal/statement/"

        path += "/".join(map(str, path_arguments))

        response = self.http_client.get(
            url=path,
            headers=self.auth_headers,
        )
        response.raise_for_status()

        response_data = response.json()

        monobank_transactions = [
            MonoBankTransaction.model_validate(transaction) for transaction in response_data
        ]

        return [transaction.to_transaction_schema() for transaction in monobank_transactions]
