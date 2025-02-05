from dall import *
from sqlalchemy import create_engine
import pandas as ps
import mysql.connector

class EtlDao:

    url:str = "/Users/zakariaradi/Desktop/atelierBank/Accounts.csv"
    @staticmethod
    def extract():
       
        df = ps.read_csv(EtlDao.url, header=0)
        df = df.dropna()
        df = df.drop(columns=df.columns[[1, 4]])
        df['balance'] = ps.to_numeric(df['balance'])
        df['balance'] = df['balance'].fillna(0)
        return df
        
    @staticmethod    
    def load():
        df = EtlDao.extract()
        df.columns = ['Email','balance', 'Account_type','password']
        cnx = create_engine('mysql+mysqlconnector://root:zakaria1234radi%40@localhost/db_Bank')
        
        existing_accounts = ps.read_sql('SELECT Email FROM T_Accounts', con=cnx)
        df = df[~df['Email'].isin(existing_accounts['Email'])]
        
        df.to_sql(name = 'T_Accounts',con=cnx,if_exists='append',index=False)#index


    





































""" from app import *
from dall import *

result = []
def transforme(account):
    results = []
    for acc in account:
        try:
            Account_id = int(acc['account_number'])
            balance = float(acc['balance'])  
            account_type = str(acc['Account_type'])
            results.append((balance,account_type,Account_id))
        except KeyError as e:
            print(f"Missing key: {e}")
        except ValueError as e:
            print(f"Error processing account data: {e}")
    return results

def load():
    global result 
    admin = AdminDao()
    result = transforme(accounts)
    print("Transformed results:", result)
    DataBase.get_connection()
    admin.insert_in_db(result)


if __name__ == "__main__":
 
    admin = AdminDao()
    account1 = CheckingAccount(500)
    account2 = SavingAccount(0.03, 900)
    account3 = CheckingAccount(2000)
    account4 = SavingAccount(0.2,100000)
    Bank.create(account1)
    Bank.create(account2)
    Bank.create(account3)
    Bank.create(account4)
    Bank.create(CheckingAccount(9000))
    Bank.create(SavingAccount(0.2,300))
    #Main.check_value(2)
    #Main.check_value(1) 
    #account1.deposit(100)
    #account2.withdraw(100)
    #account1.transfer(account2,40)
    #account2.delete()
    #Bank.list()
    #account1.receipt()
    #print(archive)
    #print(bank.Search(1)) 
    #print(bank.search(2))
    #Main.check_value(3)
    #Main.check_value(5)
    #Main.check_value(1)
    #Main.check_value(8)
    #bank.create(3)    
    load()
    l=[(9000,'Checkingaccount',5)]
    admin.add_acc_in_db(l)
    print(result) """