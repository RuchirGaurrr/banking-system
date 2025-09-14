import getpass
from bank_core import Bank, Account, Transaction
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class BankApp:
    def __init__(self):
        self.bank = Bank()
        self.current_account = None
    
    def run(self):
        while True:
            print(Fore.CYAN + Style.BRIGHT + "\n========== WELCOME TO RUCHIR'S BANK ==========")
            print(Fore.YELLOW + "1. Create Account")
            print(Fore.YELLOW + "2. Login")
            print(Fore.YELLOW + "3. Exit")
            choice = input(Fore.CYAN + "Enter your choice (1-3): ").strip()

            if choice == "1":
                self.create_account_ui()
            elif choice == "2":
                self.login_ui()
            elif choice == "3":
                print(Fore.GREEN + Style.BRIGHT + "Thank you for banking with us. Goodbye!")
                break
            else:
                print(Fore.RED + Style.BRIGHT + "Invalid choice! Please select between 1-3.")
    
    def create_account_ui(self):
        while True:
            name = input(Fore.CYAN + "Enter your full name: ").strip()
            if not name:
                print(Fore.RED + "Name cannot be empty.")
                continue
            break

        while True:
            username = input(Fore.CYAN + "Enter a username: ").strip()
            if not username:
                print(Fore.RED + "Username cannot be empty.")
                continue
            if any(acc.username == username for acc in self.bank.accounts):
                print(Fore.RED + "Username already taken, try another.")
            else:
                break

        while True:
            password = getpass.getpass(Fore.CYAN + "Enter a password: ").strip()
            confirm = getpass.getpass(Fore.CYAN + "Confirm your password: ").strip()
            if not password:
                print(Fore.RED + "Password cannot be empty.")
                continue
            if password != confirm:
                print(Fore.RED + "Passwords don’t match. Try again.")
            else:
                break

        while True:
            balance_input = input(Fore.CYAN + "Enter initial balance: ").strip()
            if not balance_input:
                print(Fore.RED + "Balance cannot be empty.")
                continue
            try:
                balance = float(balance_input)
                if balance < 0:
                    print(Fore.RED + "Balance cannot be negative.")
                    continue
                break
            except ValueError:
                print(Fore.RED + "Please enter a valid number.")

        account = self.bank.create_account(username, password, name, balance)
        self.bank.save_accounts()
        print(Fore.GREEN + Style.BRIGHT + f"Account created successfully! Your account number is {account.account_no}")

        ans = input(Fore.CYAN + "Do you want to login now? (yes/no): ").strip().lower()
        if ans.startswith("y"):
            self.login_ui()
        else:
            print(Fore.GREEN + "Your account has been created successfully. Thank you.")

    
    def login_ui(self):
        attempts = 3
        while attempts > 0:
            username = input(Fore.CYAN + "Enter your username: ").strip()
            if not username:
                print(Fore.RED + "Username cannot be empty.")
                continue

            password = getpass.getpass(Fore.CYAN + "Enter your password: ").strip()
            if not password:
                print(Fore.RED + "Password cannot be empty.")
                continue

            try:
                account = self.bank.login(username, password)
                self.current_account = account
                print(Fore.GREEN + Style.BRIGHT + f"Login successful! Welcome {account.name}.")
                self.account_menu()
                return
            except ValueError as e:
                attempts -= 1
                if attempts > 0:
                    print(Fore.RED + f"{e} ({attempts} of 3 attempts left)")
                else:
                    print(Fore.RED + "Too many failed attempts. Returning to main menu.")

    def account_menu(self):
        while True:
            print(Fore.CYAN + Style.BRIGHT + "\n========== MAIN MENU ==========")
            print(Fore.YELLOW + "1. Deposit money")
            print(Fore.YELLOW + "2. Withdraw money")
            print(Fore.YELLOW + "3. Check Balance")
            print(Fore.YELLOW + "4. Mini Statement")
            print(Fore.YELLOW + "5. Monthly Statement")
            print(Fore.YELLOW + "6. Transfer Funds")
            print(Fore.YELLOW + "7. Change Password")
            print(Fore.YELLOW + "8. Close Account")
            print(Fore.YELLOW + "9. Logout")
            choice = input(Fore.CYAN + "Enter your choice (1-9): ").strip()

            if choice == "1":
                self.credit_ui()
            elif choice == "2":
                self.debit_ui()
            elif choice == "3":
                print(Fore.GREEN + Style.BRIGHT + f"Your balance: {self.current_account.check_balance():.2f}")
            elif choice == "4":
                self.mini_statement_ui()
            elif choice == "5":
                self.monthly_statement_ui()
            elif choice == "6":
                self.transfer_ui()
            elif choice == "7":
                self.change_password_ui()
            elif choice == "8":
                self.close_account_ui()
                break
            elif choice == "9":
                print(Fore.GREEN + "Logging out...")
                break
            else:
                print(Fore.RED + "Invalid choice! Please select between 1-9.")
    
    def credit_ui(self):
        while True:
            amount_input = input(Fore.CYAN + "Enter amount to deposit: ").strip()
            if not amount_input:
                print(Fore.RED + "Amount cannot be empty.")
                continue
            try:
                amount = float(amount_input)
                if amount <= 0:
                    print(Fore.RED + "Amount must be greater than 0.")
                    continue
                self.bank.credit(self.current_account, amount)
                print(Fore.GREEN + Style.BRIGHT + f"{amount:.2f} deposited. New balance: {self.current_account.balance:.2f}")
                break
            except ValueError as e:
                print(Fore.RED + Style.BRIGHT + f"Error: {e}")
    
    def debit_ui(self):
        while True:
            amount_input = input(Fore.CYAN + "Enter amount to withdraw: ").strip()
            if not amount_input:
                print(Fore.RED + "Amount cannot be empty.")
                continue
            try:
                amount = float(amount_input)
                self.bank.debit(self.current_account, amount)
                print(Fore.GREEN + Style.BRIGHT + f"{amount:.2f} Withdraw. New balance: {self.current_account.balance:.2f}")
                break
            except ValueError as e:
                print(Fore.RED + Style.BRIGHT + f"Error: {e}")
    
    def mini_statement_ui(self):
        txns = self.bank.mini_statement(self.current_account)
        if not txns:
            print(Fore.RED + "No transactions found.")
            return
        print(Fore.MAGENTA + Style.BRIGHT + "\n========== MINI STATEMENT ==========")
        print(Fore.CYAN + f"{'Date & Time':<20} {'Type':<10} {'Amount':>10} {'Balance':>12}")
        print(Fore.CYAN + "-"*54)
        for txn in txns:
            color = Fore.GREEN if txn.txn_type.lower() == "credit" else Fore.RED
            print(color + f"{txn.time:<20} {txn.txn_type.upper():<10} {txn.amount:>10.2f} {txn.balance:>12.2f}")
        print(Fore.MAGENTA + "="*54)
    
    def monthly_statement_ui(self):
        while True:
            month = input(Fore.CYAN + "Enter month (MM): ").strip()
            year = input(Fore.CYAN + "Enter year (YYYY): ").strip()
            if not (month and year and month.isdigit() and year.isdigit()):
                print(Fore.RED + "Month and Year cannot be empty and must be numbers.")
                continue
            if not (1 <= int(month) <= 12 and len(year) == 4):
                print(Fore.RED + "Invalid month/year format. Try again.")
                continue
            if len(month) == 1:
                month = "0"+month

            stmt = self.bank.monthly_statement(self.current_account, int(month), int(year))
            if not stmt:
                print(Fore.RED + "No transactions found for this month.")
            else:
                print(Fore.MAGENTA + Style.BRIGHT + "\n========== MONTHLY STATEMENT ==========")
                print(Fore.YELLOW + f"Account No: {self.current_account.account_no}")
                print(Fore.YELLOW + f"Month: {month}/{year}")
                print(Fore.CYAN + "-"*36)
                print(Fore.GREEN + f"Opening Balance: {stmt['opening_balance']:.2f}")
                print(Fore.GREEN + f"Closing Balance: {stmt['closing_balance']:.2f}")
                print(Fore.CYAN + "-"*36)
                print(Fore.CYAN + f"{'Date & Time':<20} {'Type':<10} {'Amount':>10} {'Balance':>12}")
                print(Fore.CYAN + "-"*54)
                for txn in stmt["transactions"]:
                    color = Fore.GREEN if txn.txn_type.lower() == "credit" else Fore.RED
                    print(color + f"{txn.time:<20} {txn.txn_type.upper():<10} {txn.amount:>10.2f} {txn.balance:>12.2f}")
                print(Fore.MAGENTA + "="*54 + "\n")
            break
    
    def transfer_ui(self):
        while True:
            receiver_no = input(Fore.CYAN + "Enter receiver account number: ").strip()
            amount_input = input(Fore.CYAN + "Enter amount to transfer: ").strip()
            if not receiver_no or not amount_input:
                print(Fore.RED + "Account number and amount cannot be empty.")
                continue
            try:
                receiver = self.bank.find_account_by_no(int(receiver_no))
                amount = float(amount_input)
                self.bank.transfer(self.current_account, receiver, amount)
                print(Fore.GREEN + Style.BRIGHT + f"{amount:.2f} transferred to {receiver.name}.")
                break
            except ValueError as e:
                print(Fore.RED + Style.BRIGHT + f"Error: {e}")
                continue
    
    def change_password_ui(self):
        while True:
            old_pw = getpass.getpass(Fore.CYAN + "Enter old password: ").strip()
            new_pw = getpass.getpass(Fore.CYAN + "Enter new password: ").strip()
            confirm = getpass.getpass(Fore.CYAN + "Confirm new password: ").strip()

            if not old_pw or not new_pw or not confirm:
                print(Fore.RED + "Password fields cannot be empty.")
                continue
            if new_pw != confirm:
                print(Fore.RED + "New passwords don’t match. Try again.")
                continue
            if old_pw == new_pw:
                raise ValueError(Fore.RED + "New and old passwords are the same. Please choose a different one.")

            try:
                self.bank.change_password(self.current_account, old_pw, new_pw)
                print(Fore.GREEN + Style.BRIGHT + "Password changed successfully.")
                break
            except ValueError as e:
                print(Fore.RED + Style.BRIGHT + f"Error: {e}")
                continue
    
    def close_account_ui(self):
        try:
            self.bank.close_account(self.current_account)
            print(Fore.GREEN + Style.BRIGHT + "✅ Account closed successfully.")
        except ValueError as e:
            print(Fore.RED + Style.BRIGHT + f"Error: {e}")
    
if __name__ == "__main__":
    app = BankApp()
    app.run()
