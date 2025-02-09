from io import BytesIO
from dal.admin_dal import *

class AdminManage:
    def __init__(self, cnx) -> None:
        self.adminDao = AdminDao(cnx)

    def insert_in_db(self, email: str, balance: float, type: str, password: str) -> bool:
        return self.adminDao.insert_in_db(email, balance, type, password)

    def count_Accounts_by_type(self):
        return self.adminDao.count_Accounts_by_type()

    def count_Accounts_by_year(self):
        return self.adminDao.count_Accounts_by_year()

    def count_Accounts_by_balance(self):
        return self.adminDao.count_Accounts_by_balance()

    def generate_otp(self, email: str) -> str | None:
        return self.adminDao.generate_otp(email)

    def get_otp(self, email: str) -> str | None:
        return self.adminDao.get_otp(email)

    def verify_otp(self, email: str, otp: str) -> bool:
        return self.adminDao.verify_otp(email, otp)

    def Archive(self, email: str) -> list:
        return self.adminDao.Archive(email)

    def is_password_valid(self, email: str, password: str):
        return self.adminDao.is_password_valid(email, password)

    def getAccountsbyemail(self, email: str):
        return self.adminDao.getAccountsbyemail(email)

    def getAccounts(self) -> list:
        return self.adminDao.getAccounts()

    def loguser(self, email: str, password: str) -> dict | None:
        return self.adminDao.loguser(email, password)

    def log_user_location(self, email: str, ip_address: str, location: str) -> bool:
        return self.adminDao.log_user_location(email, ip_address, location)

    def delete(self, email: str) -> bool:
        return self.adminDao.delete(email)

    def deposit(self, email: str, amount: float) -> bool:
        return self.adminDao.deposit(email, amount)

    def withdraw(self, email: str, amount: float) -> bool:
        return self.adminDao.withdraw(email, amount)

    def transfer(self, email: str, email2: str, amount: float) -> bool:
        return self.adminDao.transfer(email, email2, amount)

    def addip(self, email: str) -> bool:
        return self.adminDao.addip(email)

    def authip(self, email: str) -> bool:
        return self.adminDao.authip(email)

    def create_login_attempt(self, email: str) -> bool:
        return self.adminDao.create_login_attempt(email)

    def is_first_login(self, email: str) -> bool:
        return self.adminDao.is_first_login(email)

    def get_latest_login_attempt(self, email: str) -> dict | None:
        return self.adminDao.get_latest_login_attempt(email)

    def approve_login(self, email: str) -> bool:
        return self.adminDao.approve_login(email)

    def decline_login(self, email: str) -> bool:
        return self.adminDao.decline_login(email)
    
    def generate_pdf(self,archives, email: str) -> BytesIO:
        return self.adminDao.generate_pdf(archives, email)


class accmanager:
    def __init__(self,cnx) -> None:
        self.adminDao = AccountManager(cnx)
        
    def apply_monthly_updates(self):
        return self.adminDao.apply_monthly_updates()