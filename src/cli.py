import sys
from data import DataProgram
from operations import create_operations

def fmt_balance(b):
    # match COBOL PIC 9(6)V99 formatting like "001000.00"
    return f"{b:09.2f}"

def input_check(amount):
    if amount.isalpha() or float(amount) > 999999.99:
        amount = 0.0
    return abs(float(amount))

def main():
    data = DataProgram(1000.00)
    ops = create_operations(data)

    try:
        while True:
            print("--------------------------------")
            print("Account Management System")
            print("1. View Balance")
            print("2. Credit Account")
            print("3. Debit Account")
            print("4. Exit")
            print("--------------------------------")
            print("Enter your choice (1-4): ")
            choice = input().strip()

            if choice == "1":
                bal = ops.total()
                print(f"Current balance: {fmt_balance(bal)}")
            elif choice == "2":
                print("Enter credit amount: ")
                s = input().strip()
                s = input_check(s)
                new = ops.credit(float(s))
                print(f"Amount credited. New balance: {fmt_balance(new)}")
            elif choice == "3":
                print("Enter debit amount: ")
                s = input().strip()
                s = input_check(s)
                try:
                    new = ops.debit(abs(float(s)))
                    print(f"Amount debited. New balance: {fmt_balance(new)}")
                except ValueError as e:
                    if "Insufficient" in str(e):
                        print("Insufficient funds for this debit.")
                    else:
                        print(str(e))
            elif choice == "4":
                break
            else:
                print("Invalid choice, please select 1-4.")
    except KeyboardInterrupt:
        print("^C")
        print("interrupt from keyboard (signal)")
        sys.exit(1)

    print("Exiting the program. Goodbye!")

if __name__ == "__main__":
    main()
