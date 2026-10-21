import random
import sqlite3


def checksum(prefix):
    digits = [int(digit) * (2 if i % 2 == 0 else 1) for i, digit in enumerate(prefix)]
    return str(-sum(digit - 9 if digit > 9 else digit for digit in digits) % 10)


class BankingSystem:
    def __init__(self):
        self.db = sqlite3.connect('card.s3db')
        self.db.execute('CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT UNIQUE, pin TEXT, balance INTEGER DEFAULT 0)')
        self.db.commit()

    def get_account(self, number):
        return self.db.execute('SELECT id, number, pin, balance FROM card WHERE number = ?', (number,)).fetchone()

    def create_account(self):
        while True:
            prefix = f'400000{random.randrange(10**9):09d}'
            card = prefix + checksum(prefix)
            if self.get_account(card) is None:
                break
        pin = f'{random.randrange(10000):04d}'
        with self.db:
            self.db.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (card, pin))
        print('Your card has been created')
        print('Your card number:')
        print(card)
        print('Your card PIN:')
        print(pin)

    def add_income(self, card):
        print('Enter income:')
        try:
            amount = int(input())
        except ValueError:
            print('Incorrect amount!')
            return
        if amount < 0:
            print('Incorrect amount!')
            return
        with self.db:
            self.db.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (amount, card))
        print('Income was added!')

    def transfer(self, card):
        print('Transfer\nEnter card number:')
        receiver = input().strip()
        if receiver == card:
            print("You can't transfer money to the same account!")
            return
        if len(receiver) != 16 or not receiver.isascii() or not receiver.isdigit() or checksum(receiver[:-1]) != receiver[-1]:
            print('Probably you made a mistake in the card number. Please try again!')
            return
        if self.get_account(receiver) is None:
            print('Such a card does not exist.')
            return
        print('Enter how much money you want to transfer:')
        try:
            amount = int(input())
        except ValueError:
            print('Incorrect amount!')
            return
        if amount < 0:
            print('Incorrect amount!')
            return
        with self.db:
            result = self.db.execute('UPDATE card SET balance = balance - ? WHERE number = ? AND balance >= ?', (amount, card, amount))
            if result.rowcount != 1:
                print('Not enough money!')
                return
            self.db.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (amount, receiver))
        print('Success!')

    def login(self):
        print('Enter your card number:')
        card = input().strip()
        print('Enter your PIN:')
        pin = input().strip()
        account = self.get_account(card)
        if account is None or account[2] != pin:
            print('Wrong card number or PIN!')
            return False
        print('You have successfully logged in!')
        while True:
            print('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
            choice = input().strip()
            if choice == '1':
                print(f'Balance: {self.get_account(card)[3]}')
            elif choice == '2':
                self.add_income(card)
            elif choice == '3':
                self.transfer(card)
            elif choice == '4':
                with self.db:
                    self.db.execute('DELETE FROM card WHERE number = ?', (card,))
                print('The account has been closed!')
                return False
            elif choice == '5':
                print('You have successfully logged out!')
                return False
            elif choice == '0':
                return True

    def run(self):
        try:
            while True:
                print('1. Create an account\n2. Log into account\n0. Exit')
                choice = input().strip()
                if choice == '1':
                    self.create_account()
                elif choice == '2':
                    if self.login():
                        break
                elif choice == '0':
                    break
            print('Bye!')
        except EOFError:
            pass
        finally:
            self.db.close()


if __name__ == '__main__':
    BankingSystem().run()
