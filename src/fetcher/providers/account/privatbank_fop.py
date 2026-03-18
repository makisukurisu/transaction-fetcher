import datetime
from decimal import Decimal
from enum import StrEnum

import pydantic
import pytz

from enums.transaction import TransactionType
from providers.account.base import BaseAccountProvider, BaseAccountProviderConfiguration
from repository import settings
from schemas.account import BalanceSchema
from schemas.base import BaseSchema
from schemas.transaction import TransactionSchema
from services.currency import get_currency_by_alpha_code

privatbank_timezone = pytz.timezone("Europe/Kyiv")


class PrivatBankProviderConfiguration(BaseAccountProviderConfiguration):
    iban: str
    token: str

    id: str | None = None


class PrivatBankTransactionType(StrEnum):
    DEBIT = "D"
    CREDIT = "C"

    @property
    def as_transaction_type(self) -> TransactionType:
        if self == PrivatBankTransactionType.DEBIT:
            return TransactionType.WITHDRAWAL
        if self == PrivatBankTransactionType.CREDIT:
            return TransactionType.DEPOSIT
        raise ValueError(f"Unknown transaction type: {self}")


class PrivatBankTransaction(BaseSchema):
    unique_id: str = pydantic.Field(validation_alias="ID")
    amount: Decimal = pydantic.Field(validation_alias="SUM")
    currency: str = pydantic.Field(validation_alias="CCY")
    description: str = pydantic.Field(validation_alias="OSND")
    transaction_type: PrivatBankTransactionType = pydantic.Field(
        validation_alias="TRANTYPE",
    )

    processed_at: datetime.datetime = pydantic.Field(
        validation_alias="DATE_TIME_DAT_OD_TIM_P",
    )

    @pydantic.field_validator(
        "description",
        mode="after",
    )
    @classmethod
    def convert_description(cls, value: str) -> str:
        import re

        # As per request
        matches = re.search(
            r"(,\sквитанція\s(?:[\x00-\x7F]*\b))",
            value,
            re.IGNORECASE,
        )
        if matches:
            return value.replace(matches.group(1), "")

        return value

    @pydantic.field_validator(
        "processed_at",
        mode="before",
    )
    @classmethod
    def convert_time(cls, value: str) -> datetime.datetime:
        return datetime.datetime.strptime(value, "%d.%m.%Y %H:%M:%S").astimezone(
            tz=privatbank_timezone,
        )

    def to_transaction_schema(self) -> TransactionSchema:
        currency = get_currency_by_alpha_code(self.currency)

        return TransactionSchema(
            unique_id=self.unique_id,
            at_time=self.processed_at,
            description=self.description,
            amount=self.amount,
            currency=currency,
            type=self.transaction_type.as_transaction_type,
        )


class PrivatBankTransactionResponse(BaseSchema):
    transactions: list[PrivatBankTransaction]


class PrivatBankBalance(BaseSchema):
    iban: str = pydantic.Field(
        validation_alias="acc",
    )
    currency: str = pydantic.Field()

    balance_start: Decimal = pydantic.Field(
        validation_alias="balanceIn",
    )
    balance_end: Decimal = pydantic.Field(
        validation_alias="balanceOut",
    )
    turnover_debit: Decimal = pydantic.Field(
        validation_alias="turnoverDebt",
    )
    turnover_credit: Decimal = pydantic.Field(
        validation_alias="turnoverCred",
    )

    def as_balance_schema(self) -> BalanceSchema:
        currency = get_currency_by_alpha_code(self.currency)

        return BalanceSchema(
            currency=currency.numerical_code,
            start_balance=self.balance_start,
            end_balance=self.balance_end,
            deposited=self.turnover_credit,
            withdrawn=self.turnover_debit,
            at_time=datetime.datetime.now(
                tz=settings.settings.default_timezone,
            ),
        )


class PrivatBankBalanceResponse(BaseSchema):
    balances: list[PrivatBankBalance]


class PrivatBankFOPProvider(BaseAccountProvider):
    @property
    def base_url(self) -> str:
        return "https://acp.privatbank.ua/api"

    @property
    def iban(self) -> str:
        return self.configuration.iban

    def get_configuration_type(self) -> type[PrivatBankProviderConfiguration]:
        return PrivatBankProviderConfiguration

    @property
    def configuration(self) -> PrivatBankProviderConfiguration:
        return self._configuration

    def _headers(self) -> dict:
        base = {
            "Content-Type": "application/json;charset=utf-8",
            "User-Agent": "CardInfo/3.0",
            "token": self.configuration.token,
        }

        if self.configuration.id:
            base["id"] = self.configuration.id

        return base

    def get_transactions(self) -> list["TransactionSchema"]:
        path = "/statements/transactions"
        parameters = {
            "acc": self.iban,
            "startDate": (
                datetime.datetime.now(
                    tz=settings.settings.default_timezone,
                )
                - datetime.timedelta(
                    seconds=self._account.interval_seconds,
                )
            ).strftime("%d-%m-%Y"),
            "limit": 100,
        }

        response = self.http_client.get(
            path,
            params=parameters,
            headers=self._headers(),
        )

        response.raise_for_status()

        response_data = PrivatBankTransactionResponse.model_validate(
            response.json(),
        )

        return [transaction.to_transaction_schema() for transaction in response_data.transactions]

    def get_balance(self) -> "BalanceSchema | None":
        path = "/statements/balance"
        parameters = {
            "acc": self.iban,
            "startDate": datetime.datetime.now(
                tz=settings.settings.default_timezone,
            ).strftime("%d-%m-%Y"),
        }

        response = self.http_client.get(
            path,
            params=parameters,
            headers=self._headers(),
        )

        response.raise_for_status()

        response_data = PrivatBankBalanceResponse.model_validate(
            response.json(),
        )

        if not response_data.balances or len(response_data.balances) == 0:
            return None

        balance = response_data.balances[0]

        return balance.as_balance_schema()
