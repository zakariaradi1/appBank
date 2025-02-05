from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


accounts: list[dict] = []
accounts_formation:list =[]
archive:list = []


class BankAccount (ABC):
    id:int = 0
    
    def __init__(self,balance:float=0) -> None: 
        self.balance = balance
        BankAccount.id = BankAccount.id +1
        self.accid = BankAccount.id
          
    

    def deposit(self,amount:float) -> float:
        self.balance += amount 
        x = datetime.now().strftime("%c")
        accounts_formation.append({"account_number": self.accid,"Account_type":"","balance": self.balance , "created_at": x, "operation_type": "Deposit", "OPERATION TIME": x , "amount": amount})
        for account in accounts:
            if account['account_number'] == self.accid : 
                account['balance'] = self.balance 
               
        return amount  
    
    @abstractmethod
    def withdraw(self,amount:float) -> float:
        pass
         
    def transfer(self,other:'BankAccount',amount:float)->float:
        last_balance = self.balance
        last_bal_oth = other.balance
        if amount > self.balance:
            print(f"Issuficent balance you have {self.balance}") 
        else:
            withdraw_amount = self.withdraw(amount)
            balance =  self.balance - withdraw_amount 
            other.deposit(withdraw_amount)
            x = datetime.now().strftime("%c")
            accounts_formation.append({"account_number": self.accid,"Account_type":"","balance": last_balance - withdraw_amount ,"operation_type": "Transfer", "OPERATION TIME": x , "amount": amount}) 
            for accountt in accounts:
                if accountt['account_number'] == self.accid:
                    accountt['balance'] = self.balance
            for account in accounts:
                if account['account_number'] == other.accid:
                    account['balance'] =  last_bal_oth + withdraw_amount
        return withdraw_amount


    def archive(self):
            for accountt in accounts_formation[:]:  
                if accountt['account_number'] == self.accid:
                    archive.append(accountt) 

    def delete(self):
        leng = len(accounts_formation)
        self.archive()
        for accountt in accounts_formation[:]:  
            if accountt['account_number'] == self.accid:
                accounts_formation.remove(accountt)
            for account in accounts_formation:
                if account['account_number'] > self.accid:
                    account['account_number'] -= 1
        for account in accounts:
            if account['account_number'] == self.accid:
                accounts.remove(account)
            for accountt in accounts:
                if accountt['account_number'] > self.accid:
                    accountt['account_number'] -= 1
        if (leng == len(accounts_formation)):
            print("Account not found")


    def receipt(self) -> None:
        accou: list = [] 
        for accountt in accounts_formation:
            if accountt['account_number'] == self.accid:
                accou.append(accountt)
        if accou: 
            print(accou)
        else:
            print("Account not found")
            
@dataclass
class Account:
    Email:str
    Account_id:int
    balance:float
    Account_type:str
    created_at:datetime
    password:str
    interestRate:float
    transaction_count:int
    last_transaction_reset:datetime

    

@dataclass
class Archive:
    id:int
    Email:str
    Balance:float
    Operation:str   
    Operation_time:datetime




if __name__ == "__main__":
    """  account = BankAccount()
    account2 = BankAccount(1000) 
    print(vars(account))
    print(vars(account2)) """
    #print(BankAccount.accounts). 
    