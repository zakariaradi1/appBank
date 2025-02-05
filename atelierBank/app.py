from Models import *
from datetime import datetime
from typing import Final


Acctype:str 

class SavingAccount(BankAccount):
    SAVING_AMOUNT: Final[float]=100
    
    def __init__(self,interestRate:float,balance:float) -> None:
        if balance >= SavingAccount.SAVING_AMOUNT :
            super().__init__(balance)
            self.interestRate  = interestRate
        else:
            print("ACCOUNT NOT CREATED")
            return None
    
           
    
    
    def withdraw(self, amount: float) -> float:
        if amount > self.balance:
            print(f"Insufficient balance you have{self.balance}")
        else:
            if self.balance - amount >= SavingAccount.SAVING_AMOUNT :
                self.balance = self.balance - amount
                x = datetime.now().strftime("%c")
                accounts_formation.append({"account_number": self.accid,"Account_type":"SavingAccount","balance": self.balance ,"operation_type": "Withdraw", "OPERATION TIME": x , "amount": amount})
                for account in accounts:
                    if account['account_number'] == self.accid : 
                        account['balance'] = self.balance    
                return amount
            available_amount:float = self.balance -  SavingAccount.SAVING_AMOUNT
            self.balance = SavingAccount.SAVING_AMOUNT
        
        return available_amount
    
    def addPeriodInterest(self)->float:
        interest:float=self.balance*self.interestRate
        self.balance=self.balance+interest
        return interest


class CheckingAccount(BankAccount):
    FREE_TRANSACTIONS:Final[int] = 3
    TRANSACTION_FEE:Final[float] = 0.2
    DRAFT_OVER = 500
    
    def __init__(self, balance: float = 0) -> None:
        super().__init__(balance)
        self.transaction_count = 0
        
    
    def deposit(self, amount: float) -> float:
        self.transaction_count += 1
        return super().deposit(amount)
    
    def transfer(self, other: BankAccount, amount: float) -> float:
        self.transaction_count += 1
        return super().transfer(other, amount) # type: ignore
    
    
    
    def withdraw(self, amount: float) -> float:
        if amount > self.balance:
            print(f"Insufficient balance you have{self.balance}")
        else:
            self.transaction_count += 1
            if self.balance + CheckingAccount.DRAFT_OVER - amount >= 0:
                self.balance = self.balance - amount
                x = datetime.now().strftime("%c")
                accounts_formation.append({"account_number": self.accid,"Account_type":"CheckingAccount","balance": self.balance , "operation_type": "Withdraw", "OPERATION TIME": x , "amount": amount}) 
                for account in accounts:
                    if account['account_number'] == self.accid : 
                        account['balance'] = self.balance   
                return amount
            available_amount:float = self.balance + CheckingAccount.DRAFT_OVER
            self.balance =- CheckingAccount.DRAFT_OVER
        return available_amount
    
    def deductFees(self)->float:
        fees:float = 0
        if self.transaction_count - CheckingAccount.FREE_TRANSACTIONS >= 0:
            fees = (self.transaction_count - CheckingAccount.FREE_TRANSACTIONS) *CheckingAccount.TRANSACTION_FEE
            self.balance = self.balance - fees
        self.transaction_count = 0
        return fees
    

class Bank(BankAccount):
    @staticmethod
    def search(num: int) -> str:
        for account in accounts_formation:
            if account['account_number'] == num:
                return f"Account number: {num}, Balance: {account['balance']}"
        return f"Account number {num} not found"
    
    @staticmethod
    def Search(num: int) -> bool:
        for account in accounts_formation:
            if account['account_number'] == num:
                return True
        return False       
    
    
    @staticmethod      
    def create( account:'BankAccount') -> None:
        if (Bank.Search(account.accid) == True): 
            print("Account already exists !!!!")
        else:
            if isinstance(account, CheckingAccount):
                accounts.append({"account_number": account.accid, "balance": account.balance,"Account_type":"CheckingAccount"})
                x = datetime.now().strftime("%c")
                accounts_formation.append({"account_number": account.accid,"Account_type":"CheckingAccount","balance": account.balance ,"operation_type": "CREATION", "OPERATION TIME": x , "amount": 0})   
                print("Account created successfully")
            else:
                accounts.append({"account_number": account.accid, "balance": account.balance,"Account_type":"SavingAccount"})
                x = datetime.now().strftime("%c")
                accounts_formation.append({"account_number": account.accid,"Account_type":"SavingAccount","balance": account.balance ,"operation_type": "CREATION", "OPERATION TIME": x , "amount": 0})
                print("Account created successfully")
            
    @staticmethod    
    def delete(account:'BankAccount') -> None:
       account.delete()
        
        
    @staticmethod         
    def deposit(account:'BankAccount', amount: float) -> None:
        account.deposit(amount)  
        
        
    @staticmethod
    def withdraw(account:'BankAccount', amount: float) -> None:
        account.withdraw(amount)    
        
    
    @staticmethod      
    def transfer(account:'BankAccount', amount: float, other: 'BankAccount') -> None:
        account.transfer(other,amount)
    
    
    @staticmethod        
    def list():
        accounts.sort(key=lambda account: account['balance'],reverse=True)
        print(accounts)    
                
              
    @staticmethod
    def receipt(account: 'BankAccount')->None:
        account.receipt()
             
          
class Main:
    @staticmethod
    def menu():
        while True:
            print("\n--- Bank System Menu ---")
            print("1. List all accounts sorted by balance")
            print("2. Search for an account")
            print("3. Create a new account")
            print("4. Delete an account")
            print("5. Deposit to an account")
            print("6. Withdraw from an account")
            print("7. Transfer funds between accounts")
            print("8. View account receipt")
            print("9. View archive of Account Deleted")
            print("10. Exit")

            choice = int(input("Choose an option: "))

            if choice == 1:
                Bank.list()
            elif choice ==2:
                num:int = int(input("enter the id of account you want to search"))
                Bank.search(num)
            elif choice == 3:
                acctype:int = int(input("enter the type of account you want to create 1 for SAVING 2 for Checking : "))
                balance:float = float(input("enter your balance : "))
                while acctype != 1 and  acctype != 2 :
                    acctype:int = int(input("invalid choice !!! enter the type of account you want to create 1 for SAVING 2 for Checking : "))
                if acctype == 1:
                    while (balance < 99):
                        balance:float = float(input("for SAVING the balance must be greater than 99 !!! enter your new  balance : "))
                    else:
                        account:BankAccount = SavingAccount(0.2,balance)
                else:
                    account:BankAccount = CheckingAccount(balance)
                Bank.create(account)
            elif choice == 4:
                num:int = int(input("enter the id of account you want to delete : "))
                if not Bank.Search(num):
                    print("Account Not found")
                account:BankAccount
                account.accid = num
                account.delete()
            elif choice == 5:
                num:int = int(input("enter the id of account you want to deposit in : "))
                balance_depo:float = float(input("enter the amount you want to deposit : "))
                if not Bank.Search(num):
                    print("Account Not found")
                account:BankAccount
                account.accid = num
                account.deposit(balance_depo)
            elif choice == 6:
                num:int = int(input("enter the id of account you want to withdraw from : "))
                balance_withd:float = float(input("enter the amount you want to withdraw : "))
                if not Bank.Search(num):
                    print("Account Not found")
                account:BankAccount
                account.accid = num
                account.withdraw(balance_withd)
            elif choice == 7:
                num:int = int(input("enter the id of account you want to transfer from : "))
                num2:int = int((input("enter the id of account you want to transfer to : ")))
                balance_trans:float = float(input("enter the amount you want to transfer : "))
                if not Bank.Search(num):
                    print(f"Account {num} Not found")
                elif not Bank.Search(num2):
                    print(f"Account {num2} Not found")
                account:BankAccount
                account.accid = num 
                x:BankAccount = account
                account.accid = num2
                y:BankAccount = account
                x.transfer(y,balance_trans)
            elif choice == 8:
                num:int = int(input("enter the id of account you want to show it's details : "))
                if not Bank.Search(num):
                    print("Account Not found")
                account:BankAccount
                account.accid = num
                account.receipt()
            elif choice == 9:
                Acc_arch:list = []
                num = int(input("enter the id of account you want to show it's archive : "))
                for acount in archive:
                    if acount['account_number'] == num:
                        Acc_arch.append(acount)
                print("Account not found")
            elif choice == 10:
                return 0
                        
                
             
if __name__ == "__main__":
    Main.menu()
    
    