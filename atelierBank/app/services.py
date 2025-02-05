from dall import *

from etl import *

class AdminManage:
    def __init__(self,cnx) -> None:
        self.adminDao = AdminDao(cnx)
        
    def insert_in_db(self,email:str,balance:float,type:str,password:str)->bool:
        return self.adminDao.insert_in_db(email,balance,type,password)
    def count_Accounts_by_type(self):
        return self.adminDao.count_Accounts_by_type()
    
    def Archive(self,email:str)->list[Archive]:
        return self.adminDao.Archive(email)
    
    def getAccountsbyemail(self,email:str):
        return self.adminDao.getAccountsbyemail(email)
    
    def loguser(self,email:str,password:str):
        return self.adminDao.loguser(email,password)
    
    def withdraw(self,email:str,amount:float)->bool:
        return self.adminDao.withdraw(email,amount)
    def deposit(self,email:str,amount:float)->bool:
        return self.adminDao.deposit(email,amount)
    def transfer(self,email:str,email2:str,amount:float)->bool:
        return self.adminDao.transfer(email,email2,amount)
    def delete(self,email:str)->bool:
        return self.adminDao.delete(email)
    def getAccounts(self):
        return self.adminDao.getAccounts()
    def count_Accounts_by_year(self):
        return self.adminDao.count_Accounts_by_year()
    def count_Accounts_by_balance(self):
        return self.adminDao.count_Accounts_by_balance()
    
class Etl:
    @staticmethod
    def load():
        return EtlDao.load()
    
class Database:
    @staticmethod
    def get_connection():
        return DataBase.get_connection()
    
class accmanger:
    def __init__(self,cnx) -> None:
        self.adminDao = AccountManager(cnx)
        
    def apply_monthly_updates(self):
        return self.adminDao.apply_monthly_updates()
    
    

    
    