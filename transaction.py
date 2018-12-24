import datetime
from decimal import *


class Transaction:
    def __init__(self, date: datetime.datetime, IBAN: str, amount: Decimal, category: str, text: str):
        self.date = date
        self.IBAN = IBAN
        self.amount = Decimal(amount) # decimal for accuracy
        self.category = category
        self.text = text

    def __str__(self) -> str:
        return "Transaction: (" + str(self.date) + ", " + str(self.IBAN) + ", " + str(self.amount) + ")"

    def toCsvRow(self) -> str:
        return '"{}","{}","{}","{}","{}"\n'.format(self.date, self.IBAN, self.amount, self.category, self.text)
