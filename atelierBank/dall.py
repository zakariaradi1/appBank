import mysql.connector as my
from etl import * 
from Models import *
from datetime import datetime
from flask import request
import requests
class DataBase:
    cnx = None

    @staticmethod
    def get_connection():
        if DataBase.cnx is None:
            try:
                DataBase.cnx = my.connect(
                    user="root",
                    password="zakaria1234radi@",
                    host="10000",
                    database="db_Bank"
                )
                print('Connection OK')
            except Exception as e:
                print(f'Connection Error: {e}')
                return None
        return DataBase.cnx

class AdminDao:
    def __init__(self, cnx):
        self.cnx = cnx
        self.account_manager = AccountManager(cnx)

    def getAccounts(self)->list[Account]:
        users:list[Account]=[]
        query:str = "SELECT * FROM T_Accounts"
        if self.cnx != None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows :
                users.append(Account(**row)) # type: ignore
            return users 
        return []
      
      
    def getAccountsbyemail(self,email:str):
        query:str = "SELECT email FROM T_Accounts where Email = %s"
        if self.cnx != None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query,(email,))
            row = cursor.fetchone()
            if row != None:
                return row 
            return None   

    def loguser(self, email: str, password: str) -> dict | None:
        query = "SELECT Account_type FROM T_Accounts WHERE Email=%s AND password=%s;"
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query, (email, password))
            row = cursor.fetchone()
            if row is not None:
                return row
            return None
        return None


    
    def Archive(self,email:str)->list[Archive]:
        Archives:list[Archive]=[]
        query:str = "SELECT * FROM T_Archive WHERE Email = %s"
        if self.cnx != None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query,(email,))
            rows = cursor.fetchall()
            for row in rows :
                Archives.append(Archive(**row)) # type: ignore
            return Archives
        return []
           
    

    def deposit(self, email: str, amount: float) -> bool:
        query = """
            UPDATE T_Accounts 
            SET balance = balance + %s, transaction_count = transaction_count + 1 
            WHERE email = %s;
        """
        self.account_manager.archive_transaction(email, amount, "deposit")
        if self.cnx is not None:
            cursor = self.cnx.cursor()
            cursor.execute(query, (amount, email))
            self.cnx.commit()
            self.account_manager.apply_monthly_updates()
            
            return True
        return False

    def withdraw(self, email: str, amount: float) -> bool:
        query = "SELECT Account_type, balance FROM T_Accounts WHERE Email = %s;"
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query, (email,))
            account = cursor.fetchone()

            if account:
                account_type = account["Account_type"]
                balance = float(account["balance"])
                amount = float(amount)  

                if account_type == "saving" and (balance - amount) < 100:
                    print("Erreur : Le solde du compte saving ne peut pas être inférieur à 100 après un retrait.")
                    return False
                elif account_type == "checking" and (balance - amount) < 0:
                    print("Erreur : Solde insuffisant pour effectuer le retrait.")
                    return False

                update_query = """
                    UPDATE T_Accounts 
                    SET balance = balance - %s, transaction_count = transaction_count + 1 
                    WHERE email = %s;
                """
                cursor.execute(update_query, (amount, email))
                self.cnx.commit()
                self.account_manager.archive_transaction(email, amount, "withdraw")
                self.account_manager.apply_monthly_updates()
                return True
            else:
                return False
        return False

    def transfer(self, email: str, email2: str, amount: float) -> bool:
        query = "SELECT Account_type, balance FROM T_Accounts WHERE Email = %s;"
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query, (email,))
            source_account = cursor.fetchone()

            if source_account:
                source_account_type = source_account["Account_type"]
                source_balance = float(source_account["balance"])  
                amount = float(amount)  

                if source_account_type == "saving" and (source_balance - amount) < 100:
                    print("Erreur : Le solde du compte saving ne peut pas être inférieur à 100 après le transfert.")
                    return False
                elif source_balance < amount:
                    print("Erreur : Solde insuffisant pour effectuer le transfert.")
                    return False

                update_query_source = """
                    UPDATE T_Accounts 
                    SET balance = balance - %s, transaction_count = transaction_count + 1 
                    WHERE email = %s;
                """
                update_query_destination = """
                    UPDATE T_Accounts 
                    SET balance = balance + %s, transaction_count = transaction_count + 1 
                    WHERE email = %s;
                """
                cursor.execute(update_query_source, (amount, email))
                cursor.execute(update_query_destination, (amount, email2))
                self.cnx.commit()
                self.account_manager.archive_transaction(email, amount, "transfer_out")
                self.account_manager.archive_transaction(email2, amount, "transfer_in")
                self.account_manager.apply_monthly_updates()
                return True
            else:
                return False
        return False

    def insert_in_db(self, email: str, balance: float, Account_type: str, password: str, interest: float = 0, transaccoun: int = 0, last: datetime = datetime.now()) -> bool:
        cnx = create_engine('mysql+mysqlconnector://root:zakaria1234radi%40@localhost/db_Bank')
        data = {
            "Email": [email],
            "Balance": [balance],
            "Account_type": [Account_type],
            "password": [password],
            "interestRate": [interest],
            "transaction_count": [transaccoun],
            "last_transaction_reset": [last]
        }
        df = ps.DataFrame(data)
        df.to_sql(name='T_Accounts', con=cnx, if_exists='append', index=False)
        self.account_manager.archive_transaction(email, balance, "creation")
        if self.cnx is not None:
            self.cnx.commit()
            return True
        return False


    def delete(self, email: str) -> bool:
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            query = "SELECT Account_id, balance FROM T_Accounts WHERE Email = %s;"
            cursor.execute(query, (email,))
            account_data = cursor.fetchone()
            if account_data:
                self.account_manager.archive_transaction(email, 0, "deletion")
                delete_query = "DELETE FROM T_Accounts WHERE Email = %s;"
                cursor.execute(delete_query, (email,))
                self.cnx.commit()
                return True
        return False
 
    def get_accounts(self):
        accounts = []
        query = "SELECT * FROM T_Accounts"
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query)
            rows = cursor.fetchall()
            accounts = [dict(row) for row in rows]  # type: ignore
        else:
            print("Connection not available")
        return accounts

class AccountManager:
    FREE_TRANSACTIONS = 5 
    TRANSACTION_FEE = 1.0 
    MINIMUM_BALANCE = 100.0 

    def __init__(self, cnx):
        self.cnx = cnx


    def apply_monthly_updates(self):
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            query = """
                SELECT Email, balance, Account_type, interestRate, transaction_count, created_at, last_transaction_reset
                FROM T_Accounts;
            """
            cursor.execute(query)
            accounts = cursor.fetchall()

            for account in accounts:
                email = account["Email"]
                balance = account["balance"]
                account_type = account["Account_type"]
                interest_rate = account.get("interestRate", 0.0)
                transaction_count = account.get("transaction_count", 0)
                created_at = account["created_at"]
                last_transaction_reset = account.get("last_transaction_reset")

                if account_type == "saving":
                    current_date = datetime.now().date()  
                    account_age = (current_date - created_at.date()).days // 365
                    if account_age > 0:
                        interest = balance * interest_rate
                        balance += interest
                        self.archive_transaction(email, interest, "annual_interest")

                elif account_type == "checking":
                    current_date = datetime.now().date()
                    if last_transaction_reset is not None:
                        last_reset_date = last_transaction_reset.date() if isinstance(last_transaction_reset, datetime) else last_transaction_reset
                    else:
                        last_reset_date = None

                    if last_reset_date is None or (current_date - last_reset_date).days >= 30:
                        if transaction_count > AccountManager.FREE_TRANSACTIONS:
                            excess = transaction_count - AccountManager.FREE_TRANSACTIONS
                            fees = excess * AccountManager.TRANSACTION_FEE
                            balance -= fees
                            self.archive_transaction(email, fees, "transaction_fees")
                        transaction_count = 0
                        last_transaction_reset = current_date

                        update_query = """
                            UPDATE T_Accounts
                            SET balance = %s,interestRate = %s, transaction_count = %s, last_transaction_reset = %s
                            WHERE Email = %s;
                        """
                        cursor.execute(update_query, (balance,AccountManager.TRANSACTION_FEE, transaction_count, last_transaction_reset, email))
                        self.cnx.commit()

    def archive_transaction(self, email: str, amount: float, operation: str):
        cnx = create_engine('mysql+mysqlconnector://root:zakaria1234radi%40@localhost/db_Bank')
        data = {
            "Email": [email],
            "Balance": [amount],
            "Operation": [operation]
        }
        df = ps.DataFrame(data)
        df.to_sql(name='T_Archive', con=cnx, if_exists='append', index=False)

        
   
        




""" def main():
    print("--- Gestion des Comptes Bancaires ---")

    # Initialisation de AdminDao
    admin_dao = AdminDao()

    while True:
        print("\nOptions disponibles :")
        print("1. Créer et insérer des données dans la table T_Accounts")
        print("2. Compter les comptes par type")
        print("3. Compter les comptes par année (2020-2025)")
        print("4. Compter les comptes par balance")
        print("5. Afficher tous les comptes")
        print("6. Quitter")

        choice = input("Veuillez choisir une option : ")

        if choice == "1":
            #admin_dao.insert_in_db(result)
            pass
        elif choice == "2":
            results = admin_dao.count_Accounts_by_type()
            if results:
                print("\nComptes par type :")
                for account_type, count in results:
                    print(f"{account_type}: {count}")
            else:
                print("Aucun résultat trouvé.")
        elif choice == "3":
            results = admin_dao.count_Accounts_by_year()
            if results:
                print("\nComptes par année :")
                for account_type, count in results:
                    print(f"{account_type}: {count}")
            else:
                print("Aucun résultat trouvé.")
        elif choice == "4":
            results = admin_dao.count_Accounts_by_balance()
            if results:
                print("\nComptes par balance :")
                for balance_range, count in results:
                    print(f"{balance_range}: {count}")
            else:
                print("Aucun résultat trouvé.")
        elif choice == "5":
            accounts = admin_dao.get_accounts()
            if accounts:
                print("\nListe des comptes :")
                for account in accounts:
                    print(account)
            else:
                print("Aucun compte trouvé.")
        elif choice == "6":
            print("Fermeture du programme.")
            break
        else:
            print("Option invalide. Veuillez réessayer.")
            

if __name__ == "__main__":
    
    main()
 """
