from decimal import *


class Transaction:
    def __init__(self, date, IBAN, amount, category, text):
        self.date = date
        self.IBAN = IBAN
        self.amount = Decimal(amount)
        self.category = category
        self.text = text

    def __str__(self):
        return "Transaction: (" + str(self.date) + ", " + str(self.IBAN) + ", " + str(self.amount) + ")"

    def toCsvRow(self):
        return '"{}","{}","{}","{}","{}"\n'.format(self.date, self.IBAN, self.amount, self.category, self.text)
