import random
import hashlib
import getpass
from datetime import datetime

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Bank: # manages all accounts and handles the persistence. 
    def __init__(self,accounts_file = "accounts.txt",transaction_file = "transactions.txt"):
        self.accounts_file = accounts_file
        self.transaction_file = transaction_file
        self.accounts =[] # list of account objects.
        self.load_accounts()

    def load_accounts(self):
        self.accounts = [] #reseting accounts list

        with open(self.accounts_file,"r") as file:
            for line in file:
                if line.startswith("#") or not line.strip():
                    continue
                account_no,username,password,name,balance = line.split(",")
                account = Account(int(account_no),username,password,name,float(balance))
                self.accounts.append(account)
        
    def save_accounts(self):
        line = [f"{account.account_no},{account.username},{account.password},{account.name},{account.balance}" for account in self.accounts]
        with open(self.accounts_file,"w") as file:
            file.write("#account_no,username,password,name,balance\n")
            file.write("\n".join(line)+"\n")
        
    def log_transaction(self, txn):
        with open(self.transaction_file,"a") as file:
            file.write(txn.to_csv()+"\n")
    
    def generate_account_no(self):
        while True:
            account_no = random.randint(100000,999999)
            if not any(account.account_no == account_no for account in self.accounts):
                return account_no
    
    def create_account(self, username,password,name,balance):
        if any(account.username == username for account in self.accounts):
            raise ValueError("Username already exists.")
        
        account_no = self.generate_account_no()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        account = Account(account_no,username,hashed_password,name,balance)

        self.accounts.append(account)
        self.save_accounts()
        return account
    
    def login(self,username,password):
        for account in self.accounts:
            if account.username == username:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if account.password == hashed_password:
                    return account
                else:
                    raise ValueError("Incorrect password.")
        raise ValueError("username not found.")
    
    def find_account_by_no(self,account_no):
        for account in self.accounts:
            if account.account_no == account_no:
                return account
        raise ValueError("Account not found.")
            
    def mini_statement(self,account):
        transactions = []
        with open(self.transaction_file,"r") as file:
            for line in file:
                if not line or line.startswith("#"):
                    continue
                account_no,txn_type,amount,balance,time = line.strip().split(",")
                if account.account_no == int(account_no):
                    txn = Transaction(int(account_no),txn_type,float(amount),float(balance),time)
                    transactions.append(txn)
        if not transactions:
            return None
            
        if len(transactions)<=10:
            return transactions
        else:
            return transactions[-10:]
    
    def monthly_statement(self, account, month, year):
        transactions = []
        with open(self.transaction_file, "r") as file:
            for line in file:
                if not line or line.startswith("#"):
                    continue
                account_no, txn_type, amount, balance, time = line.strip().split(",")

                if account.account_no == int(account_no):
                # check month/year match using substring
                    if time.startswith(f"{year}-{int(month):02d}"):
                        txn = Transaction(
                            int(account_no),
                            txn_type,
                            float(amount),
                            float(balance),
                            time
                        )
                        transactions.append(txn)

        if not transactions:
            return None

        # infer opening balance from the first transaction of this month
        first_txn = transactions[0]
        if first_txn.txn_type.lower() == "credit":   # deposit
            opening_balance = first_txn.balance - first_txn.amount
        elif first_txn.txn_type.lower() == "debit":  # withdrawal
            opening_balance = first_txn.balance + first_txn.amount
        else:  # closure
            opening_balance = 0.0

        closing_balance = transactions[-1].balance

        return {
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "transactions": transactions
        }

    
    def change_password(self,account,old_password,new_password):
        account.change_password(old_password,new_password)
        self.save_accounts()
    
    def close_account(self,account):
        if account.can_be_closed():
            self.accounts.remove(account)
            self.save_accounts()
            txn = Transaction(account.account_no,"closure",0,0,now())
            self.log_transaction(txn)
    
    def debit(self, account, amount: float):
        account.debit(amount)
        txn = Transaction(account.account_no, "debit", amount, account.balance, now())
        self.log_transaction(txn)
        self.save_accounts()
    
    def credit(self, account, amount: float):
        account.credit(amount)
        txn = Transaction(account.account_no, "credit", amount, account.balance, now())
        self.log_transaction(txn)
        self.save_accounts()

    def transfer(self, sender, receiver, amount: float):
        sender.debit(amount)    # money out
        receiver.credit(amount)   # money in
        txn_out = Transaction(sender.account_no, "debit", amount, sender.balance, now())
        txn_in  = Transaction(receiver.account_no, "credit", amount, receiver.balance, now())
        self.log_transaction(txn_out)
        self.log_transaction(txn_in)
        self.save_accounts()    

class Account:
    def __init__(self, account_no: int, username: str, password: str, name: str, balance: float):
        self.account_no = account_no
        self.username = username
        self.password = password  # hashed password
        self.name = name
        self.balance = balance

    def credit(self,amount):
        if amount<=0.0:
            raise ValueError("Amount must be greater than 0.0") 
        self.balance += amount
    
    def debit(self,amount):
        if amount<=0.0:
            raise ValueError("Amount must be greater than 0.0") 
        if amount > self.balance:
            raise ValueError("Insufficient Balance")
        self.balance -= amount
    
    def change_password(self,old_password,new_password):
        hashed_old = hashlib.sha256(old_password.encode()).hexdigest()
        if self.password != hashed_old:
            raise ValueError("Incorrect password.")
        
        if not new_password:
            raise ValueError("Password cannot be empty.")
        self.password = hashlib.sha256(new_password.encode()).hexdigest()
    
    def can_be_closed(self):
        if self.balance !=  0:
            raise ValueError("Balance is not empty. Acount cannot be closed.")
        return True

    def check_balance(self):
        return self.balance

class Transaction: #Represents a single transaction entry.
    DEBIT = "debit"
    CREDIT = "credit"
    ACCOUNT_CLOSURE = "closure"

    def __init__(self,account_no,txn_type,amount,balance,time = None):
        self.account_no = account_no
        self.txn_type = txn_type
        self.amount = amount
        self.balance = balance
        self.time = time or now()
    
    def to_csv(self):
        return f"{self.account_no},{self.txn_type},{self.amount},{self.balance},{self.time}"