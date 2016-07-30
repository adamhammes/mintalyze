import csv
from collections import namedtuple
from datetime import datetime
from decimal import *


class Transaction(namedtuple('Transaction',
    ['date', 'description', 'original_description', 'absolute_amount', 'type',
     'category', 'account', 'labels', 'notes'])):
    @property
    def is_debit(self):
        return self.type == 'debit'

    @property
    def is_transfer(self):
        return self.category == 'Transfer'

    @property
    def amount(self):
        if self.is_debit:
            return -self.absolute_amount
        return self.absolute_amount

    @staticmethod
    def parse_date(string):
        return datetime.strptime(string, '%m/%d/%Y').date()

    def __add__(self, other):
        return self.amount + other.amount

    def __radd__(self, other):
        return other + self.amount

    def __lt__(self, other):
        return self.amount < other.amount

    def __gt__(self, other):
        return self.amount > other.amount

    def __str__(self):
        return '{0}\n{1} | {2}'.format(self.description, self.date, self.amount)


class AccountHistory:
    @staticmethod
    def _parse_row(row):
        date = Transaction.parse_date(row[0])
        description = row[1]
        original_description = row[2]
        amount = Decimal(row[3])
        _type = row[4]
        category = row[5]
        account = row[6]
        labels = row[7]
        notes = row[8]

        return Transaction(date, description, original_description, amount,
                           _type, category, account, labels, notes)

    @staticmethod
    def from_csv(filename, include_transfers=False):
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            raw_data = [row for row in reader][1:]

        transactions = (AccountHistory._parse_row(row) for row in raw_data)
        return AccountHistory(transactions, include_transfers)

    def __init__(self, transactions, include_transfers=False):
        if include_transfers:
            self.transactions = list(transactions)
        else:
            self.transactions = [t for t in transactions if not t.is_transfer]

    def after(self, date):
        if isinstance(date, str):
            date = Transaction.parse_date(date)
        return AccountHistory(t for t in self.transactions if t.date > date)

    def on_or_after(self, date):
        if isinstance(date, str):
            date = Transaction.parse_date(date)
        return AccountHistory(t for t in self.transactions if t.date >= date)

    def before(self, date):
        if isinstance(date, str):
            date = Transaction.parse_date(date)
        return AccountHistory(t for t in self.transactions if t.date < date)

    def on_or_before(self, date):
        if isinstance(date, str):
            date = Transaction.parse_date(date)
        return AccountHistory(t for t in self.transactions if t.date <= date)

    @property
    def debits(self):
        return AccountHistory(t for t in self.transactions if t.is_debit)

    @property
    def deposits(self):
        return AccountHistory(t for t in self.transactions if not t.is_debit)

    def __len__(self):
        return len(self.transactions)

    def __iter__(self):
        return iter(self.transactions)

    def __str__(self):
        return '\n\n'.join(map(str, self.transactions))
