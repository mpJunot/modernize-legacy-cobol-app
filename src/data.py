class DataProgram:
    def __init__(self, initial=1000.00):
        self.storage_balance = float(initial)

    def read(self):
        return float(self.storage_balance)

    def write(self, balance):
        self.storage_balance = float(balance)
