from dal.user_dal import *

class UserManage:
    def __init__(self, cnx) -> None:
        self.userDao = UserDao(cnx)

    def delete(self, email: str) -> bool:
        return self.userDao.delete(email)
    
    def loguser(self, email: str, password: str) -> dict | None:
        return self.userDao.loguser(email, password)
    
    def transfer(self, email: str, email2: str, amount: float) -> bool:
        return self.userDao.transfer(email, email2, amount)
    
    def addip(self, email: str) -> bool:
        return self.userDao.addip(email)
    
    def authip(self, email: str) -> bool:
        return self.userDao.authip(email)
    
    def create_login_attempt(self, email: str) -> bool:
        return self.userDao.create_login_attempt(email)
    
    def is_first_login(self, email: str) -> bool:
        return self.userDao.is_first_login(email)
    
    def get_latest_login_attempt(self, email: str) -> dict | None:
        return self.userDao.get_latest_login_attempt(email)
    
    def generate_otp(self, email: str) -> str | None:
        return self.userDao.generate_otp(email)
    
    def get_otp(self, email: str) -> str | None:
        return self.userDao.get_otp(email)
    
    def verify_otp(self, email: str, otp: str) -> bool:
        return self.userDao.verify_otp(email, otp)
    
    def approve_login(self, email: str) -> bool:
        return self.userDao.approve_login(email)
    
    def decline_login(self, email: str) -> bool:
        return self.userDao.decline_login(email)
    
    def is_password_valid(self,email:str,password:str):
        return self.userDao.is_password_valid(email, password)
    
    def log_user_location(self, email: str, ip_address: str, location: str) -> bool:
        return self.userDao.log_user_location(email, ip_address, location)
    
    def apply_monthly_updates(self):
        return self.userDao.account_manager.apply_monthly_updates()
    
    def archive_transaction(self, email: str, amount: float, operation: str):
        return self.userDao.account_manager.archive_transaction(email, amount, operation)
    
    
    def generate_pdf(self,archives, email: str) -> BytesIO:
        return self.userDao.generate_pdf(archives, email)
    
class accmanager:
    def __init__(self,cnx) -> None:
        self.userDao = AccountManager(cnx)
        
    def apply_monthly_updates(self):
        return self.userDao.apply_monthly_updates()