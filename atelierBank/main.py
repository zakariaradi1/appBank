from Models import BankAccount
from app import *




    

    
    
if __name__ == '__main__':
    tawfir_1:BankAccount = SavingAccount(0.01,200)
    t:BankAccount = SavingAccount(0.01,500)
    print(tawfir_1.id,tawfir_1.balance,tawfir_1.withdraw(50),tawfir_1.balance)
   # print(tawfir_1.balance,tawfir_1.withdraw(100),tawfir_1.balance)
    #print(tawfir_1.balance,tawfir_1.withdraw(100),tawfir_1.balance)
    #main = Main()
    #main.check_value(3)

