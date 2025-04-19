from uuid import uuid4

from zeep import Client

client = Client("https://business.novapay.ua/Services/ClientAPIService.svc?wsdl")

response = client.service.PreUserAuthentication(
    {
        "request_ref": str(uuid4()),
        "login": input("Enter login: "),
        "password": input("Enter password: "),
    }
)

print(response)  # noqa: T201


second_response = client.service.UserAuthentication(
    {
        "request_ref": str(uuid4()),
        "temp_principal": response["temp_principal"],
        "code_operation_otp": response["code_operation_otp"],
        "otp_password": input("Enter OTP: "),
    }
)

print(second_response)  # noqa: T201
