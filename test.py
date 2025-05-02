import datetime
from decimal import Decimal
from uuid import uuid4
from xml.etree import ElementTree as ET

import pytz
from zeep import Client

from schemas.account import BalanceSchema

nova_pay_timezone = pytz.timezone("Europe/Kyiv")

# principal = "A7D102029DAA75C6FE34BD628136EBED1A980F4C521FFCEAB3764FB6A7A83E588EDBE4F75141888884D11F6F304CA5A7AB998B90E9CEC98523FAF6691A275E94E62D32D0C7B70291C3A45606A4FF97DECA09DCA3DF473EC9B37C64D2ECE2ECFD2042A58DF02042ED72139E3EA1C49E7CE5385B7C8F149CBCE0D058D74B7E236010FA82A82E05C912536E94CB43C8D2244B1504B9D49D207DAEA5B8FB1BAEF51B5589A71C2A8E8571C4210BA2C8C36D97CDA2438787BF632B12F45F5193876DB1D926F7499CF41DD771EFCEBA94DDAA04C02BA37C54A913128804DEC0D2608305ED93F8476C2B8FDDD26D0ED874132B56A6C33D9C0132BB068870254334C9369EBF584FB7D1E83647D2BA4C84776CE853F5F1376DB2649A4847F05648A47F184226BF3DA8C7B9F8BA00C2469C6CB4F59833077A746172B9B59E5A74BBCD7032B9BBBF82C05BDDAD1FC16BA9D62DC42254193CDBBF405F912C6EC0317B46B43250D7A096DF6A7C7272E8712B1B502F9682D5C9B182F5C8592F639A647242F0D4711DFFE87F1C80A315610C8337CB0B5BDA62741918F35B114E90096A6D345736EEACC1618E01A601C8AAA38073B6F99CB5B3704DB0B414C7019EC3BA5BBDBC7854288223D6202BB6B0C623FE0F1451B0790AAE51CFCE1577E0FAC5186C5EDE02172BDD7D12584CA6F2D0D7880AA73C5B8037BF7EB4D040828AAE9FFCC87501A7D0"
# account_id = "28424"

# client = Client("https://business.novapay.ua/Services/ClientAPIService.svc?wsdl")

# now = datetime.datetime.now(tz=nova_pay_timezone)
# one_day_ago = now - datetime.timedelta(days=1)

# account_extract = client.service.GetAccountExtract(
#     {
#         "request_ref": str(uuid4()),
#         "principal": principal,
#         "account_id": account_id,
#         "date_to": now.strftime("%d.%m.%Y"),
#         "date_from": one_day_ago.strftime("%d.%m.%Y"),
#     }
# )

extract_data = """<Extract xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n  <ExtractHead>\r\n    <GetExtractForXML>\r\n      <Date>01.05.2025</Date>\r\n      <Account>67320000016593</Account>\r\n      <IBAN>UA339358710000067320000016593</IBAN>\r\n      <Name>ФОП Біслімакі Олена Віталіївна</Name>\r\n      <InCome>53961.7100</InCome>\r\n      <MainInCome>53961.7100</MainInCome>\r\n      <DebitAmount>0</DebitAmount>\r\n      <MainDebitAmount>0</MainDebitAmount>\r\n      <CreditAmount>3017.0600</CreditAmount>\r\n      <MainCreditAmount>3017.0600</MainCreditAmount>\r\n      <OutCome>56978.7700</OutCome>\r\n      <MainOutCome>56978.7700</MainOutCome>\r\n      <LastTurn>01.05.2025</LastTurn>\r\n      <LastTurnBeforeFrom>30.04.2025</LastTurnBeforeFrom>\r\n      <Docs Amount="1636.56" CurrencyTag="UAH">\r\n        <OrgDate>01.05.2025</OrgDate>\r\n        <DayDate>01.05.2025</DayDate>\r\n        <Code>BO14700536</Code>\r\n        <CreditBankCode>935871</CreditBankCode>\r\n        <CreditAccount>67320000016593</CreditAccount>\r\n        <CreditCodeIBAN>UA339358710000067320000016593</CreditCodeIBAN>\r\n        <CreditName>Фізична особа-підприємець  Біслімакі О.В.</CreditName>\r\n        <CreditStateCode>2535718964</CreditStateCode>\r\n        <DebitBankCode>935871</DebitBankCode>\r\n        <DebitAccount>68603000000022</DebitAccount>\r\n        <DebitCodeIBAN>UA669358710000068603000000022</DebitCodeIBAN>\r\n        <DebitName>НоваПей</DebitName>\r\n        <DebitStateCode>38324133</DebitStateCode>\r\n        <Purpose>Переказ коштів по платежам, прийнятим від населення за товари/послуги згідно реєстру № 3466868 від 01.05.2025  та із Заявою № 455192535718964 про приєднання до умов Договору про надання платіжних послуг з переказу коштів (для суб’єктів господарювання)  від  17.08.2024 р., без/з ПДВ</Purpose>\r\n      </Docs>\r\n      <Docs Amount="1380.50" CurrencyTag="UAH">\r\n        <OrgDate>01.05.2025</OrgDate>\r\n        <DayDate>01.05.2025</DayDate>\r\n        <Code>BO14709360</Code>\r\n        <CreditBankCode>935871</CreditBankCode>\r\n        <CreditAccount>67320000016593</CreditAccount>\r\n        <CreditCodeIBAN>UA339358710000067320000016593</CreditCodeIBAN>\r\n        <CreditName>Фізична особа-підприємець  Біслімакі О.В.</CreditName>\r\n        <CreditStateCode>2535718964</CreditStateCode>\r\n        <DebitBankCode>935871</DebitBankCode>\r\n        <DebitAccount>68603000000022</DebitAccount>\r\n        <DebitCodeIBAN>UA669358710000068603000000022</DebitCodeIBAN>\r\n        <DebitName>НоваПей</DebitName>\r\n        <DebitStateCode>38324133</DebitStateCode>\r\n        <Purpose>Переказ коштів по платежам, прийнятим від населення за товари/послуги згідно реєстру № 3475358 від 01.05.2025  та із Заявою № 455192535718964 про приєднання до умов Договору про надання платіжних послуг з переказу коштів (для суб’єктів господарювання)  від  17.08.2024 р., без/з ПДВ</Purpose>\r\n      </Docs>\r\n    </GetExtractForXML>\r\n  </ExtractHead>\r\n</Extract>"""

extract = ET.fromstring(extract_data)

data = extract.find("ExtractHead/GetExtractForXML")

bs = BalanceSchema(
    currency=980,
    start_balance=Decimal(data.find("InCome").text),
    end_balance=Decimal(data.find("OutCome").text),
    deposited=Decimal(data.find("CreditAmount").text),
    withdrawn=Decimal(data.find("DebitAmount").text),
)

print(bs)
