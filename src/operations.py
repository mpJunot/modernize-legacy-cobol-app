import math

class Operations:
    def __init__(self, data_program):
        self._data = data_program

    def total(self):
        return round(self._data.read(), 2)

    def credit(self, amount):
        amount = float(amount)
        if math.isnan(amount) or amount < 0:
            raise ValueError('Invalid amount')
        new_balance = round(self._data.read() + amount, 2)
        self._data.write(new_balance)
        return new_balance

    def debit(self, amount):
        amount = float(amount)
        if math.isnan(amount) or amount < 0:
            raise ValueError('Invalid amount')
        balance = self._data.read()
        if amount > balance:
            raise ValueError('Insufficient funds')
        new_balance = round(balance - amount, 2)
        self._data.write(new_balance)
        return new_balance

def create_operations(data_program):
    return Operations(data_program)
