import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4
from xml.etree import ElementTree as ET

import pydantic
import pytz
from zeep import Client

from enums.transaction import TransactionType
from providers.account.base import BaseAccountProvider
from schemas.base import BaseSchema
from schemas.transaction import TransactionSchema
from services.currency import get_currency_by_alpha_code

if TYPE_CHECKING:
    from models.account import AccountModel

nova_pay_timezone = pytz.timezone("Europe/Kyiv")

CONDUCTED = 8


class ResponseError(Exception):
    response: dict
    message: str

    def __init__(self, response: dict, message: str) -> None:
        self.response = response
        self.message = message

        super().__init__(message)


class NovaPayProviderConfiguration(BaseSchema):
    account_id: str
    principal: str


class NovaPayPaymentType(StrEnum):
    DEBIT = "Debit"
    CREDIT = "Credit"

    @property
    def as_transaction_type(self) -> TransactionType:
        if self == NovaPayPaymentType.DEBIT:
            return TransactionType.WITHDRAWAL
        if self == NovaPayPaymentType.CREDIT:
            return TransactionType.DEPOSIT

        raise ValueError(f"Unknown payment type: {self}")


class NovaPayTransactionSchema(BaseSchema):
    amount: Decimal
    currency_name: str

    code: str
    purpose: str
    payment_type: NovaPayPaymentType
    status_document_id: int

    changed: datetime.datetime

    def to_transaction_schema(self) -> "TransactionSchema":
        currency = get_currency_by_alpha_code(
            alpha_code=self.currency_name,
        )

        return TransactionSchema(
            unique_id=self.code,
            amount=self.amount,
            currency_code=currency.numerical_code,
            type=self.payment_type.as_transaction_type,
            at_time=self.changed,
            description=self.purpose,
        )

    @pydantic.field_validator(
        "changed",
        mode="before",
    )
    @classmethod
    def validate_changed(cls, value: str) -> datetime.datetime:
        return datetime.datetime.strptime(
            value,
            "%d.%m.%Y %H:%M:%S",
        ).astimezone(nova_pay_timezone)


class NovaPayProvider(BaseAccountProvider):
    def __init__(self, account: "AccountModel") -> None:
        super().__init__(account=account)

        self.client = Client("https://business.novapay.ua/Services/ClientAPIService.svc?wsdl")

    @property
    def base_url(self) -> str:
        return "https://business.novapay.ua"

    @property
    def configuration(self) -> "NovaPayProviderConfiguration":
        return self._configuration

    def get_configuration_type(self) -> "type[NovaPayProviderConfiguration]":
        return NovaPayProviderConfiguration

    def get_transactions(self) -> list["TransactionSchema"]:
        current_time = datetime.datetime.now(tz=nova_pay_timezone)
        date_from = current_time - datetime.timedelta(
            seconds=self._account.interval_seconds,
        )

        response = self.client.service.GetPaymentsList(
            {
                "request_ref": str(uuid4()),
                "principal": self.configuration.principal,
                # "account_id": self.configuration.account_id,
                "date_from": date_from.strftime("%d.%m.%Y"),
                "date_to": current_time.strftime("%d.%m.%Y"),
            }
        )

        transactions_data = response["payments"]

        transactions = ET.fromstring(transactions_data)

        transactions = [
            NovaPayTransactionSchema.model_validate(
                {
                    "amount": document.attrib["Amount"],
                    "currency_name": document.attrib["CurrencyTag"],
                    "code": document.find("Code").text,
                    "purpose": document.find("Purpose").text,
                    "payment_type": NovaPayPaymentType(
                        document.find("PaymentType").text,
                    ),
                    "status_document_id": int(
                        document.find("StatusDocumentId").text,
                    ),
                    "changed": document.find("Changed").text,
                }
            )
            for document in transactions
        ]

        transactions = filter(
            lambda tr: tr.status_document_id == CONDUCTED,
            transactions,
        )

        return [transaction.to_transaction_schema() for transaction in transactions]

    def update_account_data(self) -> dict | None:
        refresh_response = self.client.service.RefreshUserAuthentication(
            {
                "request_ref": str(uuid4()),
                "principal": self.configuration.principal,
            }
        )

        if refresh_response["result"] != "ok":
            raise ResponseError(
                response=refresh_response,
                message="Failed to refresh authentication",
            )

        self.configuration.principal = refresh_response["new_principal"]

        return self.configuration.model_dump()
